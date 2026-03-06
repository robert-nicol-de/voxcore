#!/usr/bin/env python3
"""
Improved Groq evaluation with better prompt engineering.
"""

import json
import os
from difflib import SequenceMatcher
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

from langchain_groq import ChatGroq

class GroqSQLEvaluatorV2:
    """Improved Groq SQL evaluator with better prompting."""
    
    def __init__(self):
        """Initialize Groq LLM."""
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
        
        print("✓ Groq initialized (v2 - improved prompting)")
        print(f"✓ Dataset loaded: {len(self.data)} questions")
    
    def get_validation_set(self) -> List[Dict]:
        return [q for q in self.data if q.get('split') == 'validation' and q.get('expected_sql')]
    
    def get_train_set(self) -> List[Dict]:
        return [q for q in self.data if q.get('split') == 'train' and q.get('expected_sql')]
    
    def build_improved_prompt(self, question: str, schema_context: str, few_shot: str) -> str:
        """Build improved prompt with Snowflake-specific instructions."""
        return f"""You are an expert Snowflake SQL developer. Your task is to generate clean, production-ready SQL.

CRITICAL SNOWFLAKE RULES:
- Use DATE_TRUNC('year', CURRENT_DATE()) for YTD, DATE_TRUNC('month', CURRENT_DATE()) for MTD
- Use DATEADD(year, -1, ...) for year-over-year comparisons
- Use QUALIFY ROW_NUMBER() OVER (...) <= N for top-N queries (NOT LIMIT)
- Use FULL OUTER JOIN for variance analysis
- Use WITH clauses (CTEs) for complex multi-step logic
- Use ROUND(..., 2) for percentage calculations
- Use NULLIF(..., 0) to prevent division by zero
- Use CASE WHEN for conditional logic
- Use SUM(...) FILTER (WHERE ...) for conditional aggregation
- NEVER use SQL Server syntax (TOP, GETDATE(), etc.)

SCHEMA CONTEXT:
{schema_context}

PROVEN EXAMPLES (use these patterns):
{few_shot}

QUESTION TO ANSWER:
{question}

INSTRUCTIONS:
1. Generate ONLY valid Snowflake SQL
2. No explanations, no markdown, no code blocks
3. Use the schema tables and columns provided
4. Follow the Snowflake rules above
5. Return complete, executable SQL that can run immediately
6. Start with SELECT or WITH
7. End with semicolon

SQL:"""
    
    def format_schema_context(self, question_dict: Dict) -> str:
        """Format schema context."""
        tables = question_dict.get('relevant_tables', [])
        columns = question_dict.get('key_columns', [])
        
        context = "Available tables:\n"
        for table in tables:
            context += f"  - {table}\n"
        
        context += "\nKey columns to use:\n"
        for col in columns:
            context += f"  - {col}\n"
        
        return context
    
    def format_few_shot_improved(self, examples: List[Dict]) -> str:
        """Format few-shot examples with full SQL."""
        if not examples:
            return ""
        
        formatted = ""
        for i, ex in enumerate(examples, 1):
            nl = ex['natural_language_question']
            sql = ex.get('expected_sql', '')
            if sql:
                # Show full SQL for better learning
                formatted += f"Example {i}:\nQuestion: {nl}\nSQL:\n{sql}\n\n"
        
        return formatted
    
    def sql_similarity(self, sql1: str, sql2: str) -> float:
        """Calculate SQL similarity."""
        sql1_norm = ' '.join(sql1.split()).lower()
        sql2_norm = ' '.join(sql2.split()).lower()
        return SequenceMatcher(None, sql1_norm, sql2_norm).ratio()
    
    def generate_sql(self, question: str, schema_context: str, few_shot: str) -> Optional[str]:
        """Generate SQL using improved prompt."""
        try:
            prompt = self.build_improved_prompt(question, schema_context, few_shot)
            response = self.llm.invoke(prompt)
            sql = response.content.strip()
            
            # Clean up markdown if present
            if sql.startswith("```"):
                sql = sql.split("```")[1]
                if sql.startswith("sql"):
                    sql = sql[3:]
            
            return sql.strip()
        except Exception as e:
            print(f"    ERROR: {str(e)[:80]}")
            return None
    
    def evaluate_validation_set(self):
        """Evaluate with improved prompting."""
        val_set = self.get_validation_set()
        train_set = self.get_train_set()
        
        print(f"\n{'=' * 80}")
        print(f"IMPROVED EVALUATION - VALIDATION SET ({len(val_set)} questions)")
        print(f"{'=' * 80}\n")
        
        # Use 4 best examples
        few_shot = self.format_few_shot_improved(train_set[:4])
        
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
            
            sim = self.sql_similarity(expected_sql, generated_sql)
            similarities.append(sim)
            
            status = "[GOOD]" if sim > 0.8 else "[OK]" if sim > 0.6 else "[POOR]"
            print(f"   {status} Similarity: {sim:.2f}")
            
            results.append({
                'question': nl,
                'similarity': sim,
                'expected': expected_sql[:150],
                'generated': generated_sql[:150]
            })
        
        # Summary
        print(f"\n{'=' * 80}")
        print(f"SUMMARY - IMPROVED PROMPT")
        print(f"{'=' * 80}")
        print(f"Total: {len(val_set)}")
        print(f"Evaluated: {len(similarities)}")
        
        if similarities:
            avg = sum(similarities) / len(similarities)
            print(f"Average Similarity: {avg:.2f}")
            print(f"Min: {min(similarities):.2f}")
            print(f"Max: {max(similarities):.2f}")
            
            good = len([s for s in similarities if s > 0.8])
            ok = len([s for s in similarities if 0.6 <= s <= 0.8])
            poor = len([s for s in similarities if s < 0.6])
            
            print(f"\nDistribution:")
            print(f"  Good (>0.8): {good}")
            print(f"  OK (0.6-0.8): {ok}")
            print(f"  Poor (<0.6): {poor}")
        
        # Show detailed results for first 2 questions
        print(f"\n{'=' * 80}")
        print("DETAILED RESULTS (First 2 Questions)")
        print(f"{'=' * 80}\n")
        
        for i, result in enumerate(results[:2], 1):
            print(f"Q{i}: {result['question'][:60]}...")
            print(f"Similarity: {result['similarity']:.2f}\n")
            print(f"Expected:\n{result['expected']}...\n")
            print(f"Generated:\n{result['generated']}...\n")
            print("-" * 80 + "\n")


def main():
    """Run improved evaluation."""
    try:
        evaluator = GroqSQLEvaluatorV2()
        evaluator.evaluate_validation_set()
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
