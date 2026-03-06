#!/usr/bin/env python3
"""
Baseline evaluation of Groq SQL generation without database connection.
Tests SQL generation quality using similarity metrics only.
"""

import json
import os
from difflib import SequenceMatcher
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Import Groq directly
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

class GroqSQLEvaluator:
    """Evaluate Groq SQL generation without database."""
    
    def __init__(self):
        """Initialize Groq LLM."""
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            raise ValueError("GROQ_API_KEY not set in .env")
        
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            groq_api_key=groq_api_key,
            temperature=0.0,
            max_tokens=1024,
        )
        
        # Load training dataset
        with open('backend/training_questions.json', 'r') as f:
            self.data = json.load(f)
        
        print("✓ Groq initialized (llama-3.3-70b-versatile)")
        print(f"✓ Dataset loaded: {len(self.data)} questions")
    
    def get_validation_set(self) -> List[Dict]:
        """Get validation set."""
        return [q for q in self.data if q.get('split') == 'validation' and q.get('expected_sql')]
    
    def get_train_set(self) -> List[Dict]:
        """Get training set for few-shot examples."""
        return [q for q in self.data if q.get('split') == 'train' and q.get('expected_sql')]
    
    def build_prompt(self, question: str, schema_context: str, few_shot: str) -> str:
        """Build prompt for Groq."""
        return f"""You are a Snowflake SQL expert. Generate clean, production-ready SQL.

SCHEMA CONTEXT:
{schema_context}

FEW-SHOT EXAMPLES:
{few_shot}

QUESTION:
{question}

Generate ONLY valid Snowflake SQL. No explanations, no markdown code blocks.
- Use QUALIFY for window functions
- Use DATE_TRUNC for date operations
- Use DATEADD for date arithmetic
- No TOP keyword (use LIMIT instead)
- Return complete, executable SQL only"""
    
    def format_schema_context(self, question_dict: Dict) -> str:
        """Format schema context."""
        tables = question_dict.get('relevant_tables', [])
        columns = question_dict.get('key_columns', [])
        
        context = "TABLES:\n"
        for table in tables:
            context += f"  - {table}\n"
        
        context += "\nKEY COLUMNS:\n"
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
                sql_short = sql[:150] + "..." if len(sql) > 150 else sql
                formatted += f"Example {i}:\nQ: {nl}\nSQL: {sql_short}\n\n"
        
        return formatted
    
    def sql_similarity(self, sql1: str, sql2: str) -> float:
        """Calculate SQL similarity."""
        sql1_norm = ' '.join(sql1.split()).lower()
        sql2_norm = ' '.join(sql2.split()).lower()
        return SequenceMatcher(None, sql1_norm, sql2_norm).ratio()
    
    def generate_sql(self, question: str, schema_context: str, few_shot: str) -> Optional[str]:
        """Generate SQL using Groq."""
        try:
            prompt = self.build_prompt(question, schema_context, few_shot)
            
            # Call Groq
            response = self.llm.invoke(prompt)
            
            # Extract SQL
            sql = response.content.strip()
            
            # Remove markdown if present
            if sql.startswith("```"):
                sql = sql.split("```")[1]
                if sql.startswith("sql"):
                    sql = sql[3:]
            
            return sql.strip()
        except Exception as e:
            print(f"    ERROR: {str(e)[:100]}")
            return None
    
    def evaluate_validation_set(self):
        """Evaluate validation set."""
        val_set = self.get_validation_set()
        train_set = self.get_train_set()
        
        print(f"\n{'=' * 80}")
        print(f"BASELINE EVALUATION - VALIDATION SET ({len(val_set)} questions)")
        print(f"{'=' * 80}\n")
        
        # Format few-shot examples
        few_shot = self.format_few_shot(train_set[:3])
        
        similarities = []
        
        for i, q in enumerate(val_set, 1):
            nl = q['natural_language_question']
            expected_sql = q['expected_sql']
            schema_context = self.format_schema_context(q)
            
            print(f"{i}. {nl[:65]}...")
            
            # Generate SQL
            generated_sql = self.generate_sql(nl, schema_context, few_shot)
            
            if not generated_sql:
                print(f"   [FAIL] Could not generate SQL")
                continue
            
            # Calculate similarity
            sim = self.sql_similarity(expected_sql, generated_sql)
            similarities.append(sim)
            
            status = "[GOOD]" if sim > 0.8 else "[OK]" if sim > 0.6 else "[POOR]"
            print(f"   {status} Similarity: {sim:.2f}")
            
            # Show first generated SQL for inspection
            if i == 1:
                print(f"\n   EXPECTED SQL (first 200 chars):\n   {expected_sql[:200]}...")
                print(f"\n   GENERATED SQL (first 200 chars):\n   {generated_sql[:200]}...")
        
        # Summary
        print(f"\n{'=' * 80}")
        print(f"SUMMARY")
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
        
        print(f"\n{'=' * 80}")
        print("NEXT STEPS:")
        print("1. Review generated vs expected SQL above")
        print("2. Identify common failure patterns")
        print("3. Refine prompt with better examples")
        print("4. Re-run evaluation")
        print(f"{'=' * 80}\n")


def main():
    """Run baseline evaluation."""
    try:
        evaluator = GroqSQLEvaluator()
        evaluator.evaluate_validation_set()
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
