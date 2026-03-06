#!/usr/bin/env python3
"""
Phase 4: Full Schema DDL + Semantic Evaluation
- Injects complete Snowflake schema DDL into prompt
- Uses sqlglot for semantic SQL comparison
- Measures structural equivalence, not string similarity
"""

import json
import os
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv

load_dotenv()

from langchain_groq import ChatGroq
import sqlglot
from sqlglot import parse_one, exp

from schema_ddl import get_schema_ddl

class GroqSQLEvaluatorV3:
    """Semantic evaluation with full schema DDL."""
    
    def __init__(self):
        """Initialize Groq and schema."""
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            raise ValueError("GROQ_API_KEY not set")
        
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            groq_api_key=groq_api_key,
            temperature=0.0,
            max_tokens=1024,
        )
        
        with open('backend/training_questions.json', 'r') as f:
            self.data = json.load(f)
        
        self.schema_ddl = get_schema_ddl()
        
        print("✓ Groq initialized (v3 - semantic evaluation)")
        print("✓ Full schema DDL loaded")
        print(f"✓ Dataset loaded: {len(self.data)} questions")
    
    def get_validation_set(self) -> List[Dict]:
        return [q for q in self.data if q.get('split') == 'validation' and q.get('expected_sql')]
    
    def get_train_set(self) -> List[Dict]:
        return [q for q in self.data if q.get('split') == 'train' and q.get('expected_sql')]
    
    def build_prompt_with_schema(self, question: str, schema_context: str, few_shot: str) -> str:
        """Build prompt with full schema DDL."""
        return f"""You are an expert Snowflake SQL developer. Generate clean, production-ready SQL.

{self.schema_ddl}

CRITICAL SNOWFLAKE RULES:
- Use DATE_TRUNC('year', CURRENT_DATE()) for YTD
- Use DATE_TRUNC('month', CURRENT_DATE()) for MTD
- Use DATEADD(year, -1, ...) for year-over-year
- Use QUALIFY ROW_NUMBER() OVER (...) <= N for top-N
- Use FULL OUTER JOIN for variance analysis
- Use WITH clauses for complex logic
- Use ROUND(..., 2) for percentages
- Use NULLIF(..., 0) for division by zero

PROVEN EXAMPLES:
{few_shot}

QUESTION:
{question}

Generate ONLY valid Snowflake SQL. No explanations, no markdown.
- Use ONLY tables/columns from schema above
- Return complete, executable SQL
- Start with SELECT or WITH
- End with semicolon

SQL:"""
    
    def format_schema_context(self, question_dict: Dict) -> str:
        """Format schema context."""
        tables = question_dict.get('relevant_tables', [])
        columns = question_dict.get('key_columns', [])
        
        context = "Available tables:\n"
        for table in tables:
            context += f"  - {table}\n"
        
        context += "\nKey columns:\n"
        for col in columns:
            context += f"  - {col}\n"
        
        return context
    
    def format_few_shot(self, examples: List[Dict]) -> str:
        """Format few-shot examples."""
        if not examples:
            return ""
        
        formatted = ""
        for i, ex in enumerate(examples, 1):
            nl = ex['natural_language_question']
            sql = ex.get('expected_sql', '')
            if sql:
                formatted += f"Example {i}:\nQ: {nl}\nSQL: {sql}\n\n"
        
        return formatted
    
    def generate_sql(self, question: str, schema_context: str, few_shot: str) -> Optional[str]:
        """Generate SQL with full schema."""
        try:
            prompt = self.build_prompt_with_schema(question, schema_context, few_shot)
            response = self.llm.invoke(prompt)
            sql = response.content.strip()
            
            # Clean markdown
            if sql.startswith("```"):
                sql = sql.split("```")[1]
                if sql.startswith("sql"):
                    sql = sql[3:]
            
            return sql.strip()
        except Exception as e:
            print(f"    ERROR: {str(e)[:80]}")
            return None
    
    def semantic_similarity(self, generated: str, expected: str) -> Tuple[float, str]:
        """
        Calculate semantic similarity using sqlglot AST comparison.
        Returns (similarity_score, reason)
        """
        try:
            # Parse both SQLs
            gen_ast = parse_one(generated, dialect="snowflake")
            exp_ast = parse_one(expected, dialect="snowflake")
            
            # Normalize both ASTs (lowercase, remove aliases)
            gen_normalized = self._normalize_ast(gen_ast)
            exp_normalized = self._normalize_ast(exp_ast)
            
            # Compare normalized SQL strings
            gen_sql_norm = gen_normalized.sql(dialect="snowflake").lower()
            exp_sql_norm = exp_normalized.sql(dialect="snowflake").lower()
            
            # Exact match
            if gen_sql_norm == exp_sql_norm:
                return 1.0, "Exact match"
            
            # Check if they select the same columns
            gen_selects = self._extract_select_columns(gen_ast)
            exp_selects = self._extract_select_columns(exp_ast)
            
            if gen_selects == exp_selects:
                return 0.85, "Same columns, different structure"
            
            # Check if they use the same tables
            gen_tables = self._extract_tables(gen_ast)
            exp_tables = self._extract_tables(exp_ast)
            
            if gen_tables == exp_tables:
                return 0.70, "Same tables, different columns"
            
            # Partial match
            if len(gen_tables & exp_tables) > 0:
                return 0.50, "Partial table overlap"
            
            return 0.0, "No semantic match"
            
        except Exception as e:
            return 0.0, f"Parse error: {str(e)[:50]}"
    
    def _normalize_ast(self, ast):
        """Normalize AST by removing aliases and lowercasing."""
        # Remove table aliases
        for table in ast.find_all(exp.Table):
            table.set("alias", None)
        
        # Remove column aliases (but keep function results)
        for col in ast.find_all(exp.Column):
            if col.alias and not isinstance(col.this, exp.Func):
                col.set("alias", None)
        
        return ast
    
    def _extract_select_columns(self, ast) -> set:
        """Extract column names from SELECT clause."""
        columns = set()
        for select in ast.find_all(exp.Select):
            for expr in select.expressions:
                if isinstance(expr, exp.Column):
                    columns.add(expr.name.lower())
                elif isinstance(expr, exp.Alias):
                    columns.add(expr.alias.lower())
        return columns
    
    def _extract_tables(self, ast) -> set:
        """Extract table names from FROM/JOIN clauses."""
        tables = set()
        for table in ast.find_all(exp.Table):
            tables.add(table.name.lower())
        return tables
    
    def evaluate_validation_set(self):
        """Evaluate with semantic comparison."""
        val_set = self.get_validation_set()
        train_set = self.get_train_set()
        
        print(f"\n{'=' * 80}")
        print(f"SEMANTIC EVALUATION - VALIDATION SET ({len(val_set)} questions)")
        print(f"With Full Schema DDL + sqlglot AST Comparison")
        print(f"{'=' * 80}\n")
        
        few_shot = self.format_few_shot(train_set[:5])
        
        similarities = []
        results = []
        
        for i, q in enumerate(val_set, 1):
            nl = q['natural_language_question']
            expected_sql = q['expected_sql']
            schema_context = self.format_schema_context(q)
            
            print(f"{i}. {nl[:65]}...")
            
            generated_sql = self.generate_sql(nl, schema_context, few_shot)
            
            if not generated_sql:
                print(f"   [FAIL] Could not generate SQL")
                continue
            
            sim, reason = self.semantic_similarity(expected_sql, generated_sql)
            similarities.append(sim)
            
            status = "[EXCELLENT]" if sim >= 0.85 else "[GOOD]" if sim >= 0.70 else "[OK]" if sim >= 0.50 else "[POOR]"
            print(f"   {status} Semantic Similarity: {sim:.2f} ({reason})")
            
            results.append({
                'question': nl,
                'similarity': sim,
                'reason': reason,
                'expected': expected_sql[:120],
                'generated': generated_sql[:120]
            })
        
        # Summary
        print(f"\n{'=' * 80}")
        print(f"SUMMARY - SEMANTIC EVALUATION")
        print(f"{'=' * 80}")
        print(f"Total: {len(val_set)}")
        print(f"Evaluated: {len(similarities)}")
        
        if similarities:
            avg = sum(similarities) / len(similarities)
            print(f"Average Semantic Similarity: {avg:.2f}")
            print(f"Min: {min(similarities):.2f}")
            print(f"Max: {max(similarities):.2f}")
            
            excellent = len([s for s in similarities if s >= 0.85])
            good = len([s for s in similarities if 0.70 <= s < 0.85])
            ok = len([s for s in similarities if 0.50 <= s < 0.70])
            poor = len([s for s in similarities if s < 0.50])
            
            print(f"\nDistribution:")
            print(f"  Excellent (>=0.85): {excellent}")
            print(f"  Good (0.70-0.85): {good}")
            print(f"  OK (0.50-0.70): {ok}")
            print(f"  Poor (<0.50): {poor}")
        
        # Show detailed results
        print(f"\n{'=' * 80}")
        print("DETAILED RESULTS (First 3 Questions)")
        print(f"{'=' * 80}\n")
        
        for i, result in enumerate(results[:3], 1):
            print(f"Q{i}: {result['question'][:60]}...")
            print(f"Semantic Similarity: {result['similarity']:.2f} - {result['reason']}\n")
            print(f"Expected:\n{result['expected']}...\n")
            print(f"Generated:\n{result['generated']}...\n")
            print("-" * 80 + "\n")
        
        print(f"{'=' * 80}")
        print("IMPROVEMENTS FROM FULL SCHEMA DDL:")
        print("- Groq now has exact table/column names")
        print("- Semantic evaluation ignores cosmetic differences")
        print("- Focus on structural correctness, not string matching")
        print(f"{'=' * 80}\n")


def main():
    """Run semantic evaluation."""
    try:
        evaluator = GroqSQLEvaluatorV3()
        evaluator.evaluate_validation_set()
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
