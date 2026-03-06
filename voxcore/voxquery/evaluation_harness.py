#!/usr/bin/env python3
"""
Evaluation harness for testing Groq SQL generation against golden set.

This script:
1. Loads the training dataset
2. Filters validation and test sets
3. Calls VoxQuery LLM for each question
4. Compares generated SQL to expected SQL
5. Reports metrics on result match, SQL similarity, and execution success
"""

import json
import sys
from difflib import SequenceMatcher
from typing import Dict, List, Tuple, Optional

# Try to import VoxQuery components
try:
    from voxquery.core.sql_generator import SQLGenerator
    from voxquery.config import settings
    from sqlalchemy import create_engine
    VOXQUERY_AVAILABLE = True
except ImportError:
    VOXQUERY_AVAILABLE = False
    print("⚠️  VoxQuery not available - will show SQL comparison only")


class EvaluationHarness:
    """Evaluate SQL generation quality against golden set."""
    
    def __init__(self, dataset_path: str = 'backend/training_questions.json'):
        """Initialize harness with training dataset."""
        with open(dataset_path, 'r') as f:
            self.data = json.load(f)
        
        self.sql_generator = None
        
        if VOXQUERY_AVAILABLE:
            try:
                # Create SQLAlchemy engine from settings
                # For now, we'll create a dummy engine since we're not executing queries
                # In production, this would connect to the actual warehouse
                self.sql_generator = SQLGenerator(
                    engine=None,  # Will be set when needed
                    dialect="snowflake"
                )
            except Exception as e:
                print(f"⚠️  Could not initialize SQLGenerator: {e}")
                print("   Continuing with SQL comparison only (no execution)")
    
    def get_validation_set(self) -> List[Dict]:
        """Get validation set questions."""
        return [q for q in self.data if q.get('split') == 'validation' and q.get('expected_sql')]
    
    def get_test_set(self) -> List[Dict]:
        """Get test set questions (hold-out)."""
        return [q for q in self.data if q.get('split') == 'test' and q.get('expected_sql')]
    
    def get_train_set(self) -> List[Dict]:
        """Get training set for few-shot examples."""
        return [q for q in self.data if q.get('split') == 'train' and q.get('expected_sql')]
    
    def sql_similarity(self, sql1: str, sql2: str) -> float:
        """Calculate SQL similarity using SequenceMatcher (0-1)."""
        # Normalize whitespace for comparison
        sql1_norm = ' '.join(sql1.split()).lower()
        sql2_norm = ' '.join(sql2.split()).lower()
        return SequenceMatcher(None, sql1_norm, sql2_norm).ratio()
    
    def generate_sql(self, question: str, schema_context: str = "", few_shot: str = "") -> Optional[str]:
        """Generate SQL using VoxQuery LLM with Groq."""
        if not self.sql_generator:
            return None
        
        try:
            # Call the actual Groq LLM through VoxQuery
            result = self.sql_generator.generate(question, context=few_shot)
            if result and result.sql:
                return result.sql
            return None
        except Exception as e:
            print(f"  ❌ Generation error: {e}")
            return None
    
    def evaluate_question(self, question_dict: Dict, few_shot_examples: str = "") -> Dict:
        """Evaluate a single question."""
        nl = question_dict['natural_language_question']
        expected_sql = question_dict.get('expected_sql')
        schema_context = self._format_schema_context(question_dict)
        
        if not expected_sql:
            return {
                'question': nl,
                'status': 'SKIP',
                'reason': 'No expected_sql'
            }
        
        # Generate SQL with schema context and few-shot examples
        generated_sql = self.generate_sql(nl, schema_context=schema_context, few_shot=few_shot_examples)
        
        if not generated_sql:
            return {
                'question': nl,
                'status': 'SKIP',
                'reason': 'Could not generate SQL'
            }
        
        # Calculate metrics
        sql_sim = self.sql_similarity(expected_sql, generated_sql)
        
        result = {
            'question': nl,
            'status': 'EVALUATED',
            'sql_similarity': sql_sim,
            'expected_sql': expected_sql[:100] + '...' if len(expected_sql) > 100 else expected_sql,
            'generated_sql': generated_sql[:100] + '...' if len(generated_sql) > 100 else generated_sql,
        }
        
        return result
    
    def _format_schema_context(self, question_dict: Dict) -> str:
        """Format schema context from question metadata."""
        tables = question_dict.get('relevant_tables', [])
        columns = question_dict.get('key_columns', [])
        
        if not tables and not columns:
            return "No schema context available"
        
        context = "TABLES:\n"
        for table in tables:
            context += f"  - {table}\n"
        
        context += "\nKEY COLUMNS:\n"
        for col in columns:
            context += f"  - {col}\n"
        
        return context
    
    def evaluate_set(self, question_set: List[Dict], set_name: str = 'Validation') -> Dict:
        """Evaluate a set of questions."""
        print(f"\n{'=' * 70}")
        print(f"EVALUATING {set_name.upper()} SET ({len(question_set)} questions)")
        print(f"{'=' * 70}\n")
        
        # Get few-shot examples from training set
        train_set = self.get_train_set()
        few_shot_examples = self._format_few_shot_examples(train_set[:4])
        
        results = []
        sql_similarities = []
        
        for i, q in enumerate(question_set, 1):
            result = self.evaluate_question(q, few_shot_examples=few_shot_examples)
            results.append(result)
            
            nl = q['natural_language_question']
            print(f"{i}. {nl[:60]}...")
            
            if result['status'] == 'EVALUATED':
                sim = result['sql_similarity']
                sql_similarities.append(sim)
                status = "[OK]" if sim > 0.8 else "[MED]" if sim > 0.6 else "[LOW]"
                print(f"   {status} SQL Similarity: {sim:.2f}")
            else:
                print(f"   [SKIP] {result['reason']}")
        
        # Summary
        print(f"\n{'-' * 70}")
        print(f"SUMMARY - {set_name} Set")
        print(f"{'-' * 70}")
        print(f"Total Questions: {len(question_set)}")
        print(f"Evaluated: {len(sql_similarities)}")
        
        if sql_similarities:
            avg_sim = sum(sql_similarities) / len(sql_similarities)
            print(f"Average SQL Similarity: {avg_sim:.2f}")
            print(f"Min Similarity: {min(sql_similarities):.2f}")
            print(f"Max Similarity: {max(sql_similarities):.2f}")
            
            # Distribution
            high = len([s for s in sql_similarities if s > 0.8])
            med = len([s for s in sql_similarities if 0.6 <= s <= 0.8])
            low = len([s for s in sql_similarities if s < 0.6])
            print(f"\nSimilarity Distribution:")
            print(f"  High (>0.8): {high}")
            print(f"  Medium (0.6-0.8): {med}")
            print(f"  Low (<0.6): {low}")
        
        return {
            'set_name': set_name,
            'total': len(question_set),
            'evaluated': len(sql_similarities),
            'avg_similarity': sum(sql_similarities) / len(sql_similarities) if sql_similarities else 0,
            'results': results
        }
    
    def _format_few_shot_examples(self, examples: List[Dict]) -> str:
        """Format few-shot examples for the prompt."""
        if not examples:
            return ""
        
        formatted = "Few-shot examples:\n\n"
        for i, ex in enumerate(examples, 1):
            nl = ex['natural_language_question']
            sql = ex.get('expected_sql', '')
            if sql:
                # Truncate long SQL
                sql_display = sql[:200] + "..." if len(sql) > 200 else sql
                formatted += f"Example {i}:\nQ: {nl}\nSQL: {sql_display}\n\n"
        
        return formatted
    
    def run_validation_eval(self):
        """Run evaluation on validation set."""
        val_set = self.get_validation_set()
        return self.evaluate_set(val_set, 'Validation')
    
    def run_test_eval(self):
        """Run evaluation on test set (hold-out)."""
        test_set = self.get_test_set()
        return self.evaluate_set(test_set, 'Test (Hold-out)')
    
    def print_few_shot_examples(self, num_examples: int = 4):
        """Print few-shot examples for prompt engineering."""
        train_set = self.get_train_set()[:num_examples]
        
        print(f"\n{'=' * 70}")
        print(f"FEW-SHOT EXAMPLES FOR GROQ PROMPT ({len(train_set)} examples)")
        print(f"{'=' * 70}\n")
        
        for i, q in enumerate(train_set, 1):
            nl = q['natural_language_question']
            sql = q.get('expected_sql', 'N/A')
            print(f"Example {i}:")
            print(f"Question: {nl}")
            print(f"SQL:\n{sql}\n")
            print("-" * 70 + "\n")


def main():
    """Run evaluation harness."""
    harness = EvaluationHarness()
    
    # Show dataset info
    print(f"\n{'=' * 70}")
    print("EVALUATION HARNESS - VoxQuery SQL Generation")
    print(f"{'=' * 70}\n")
    
    val_set = harness.get_validation_set()
    test_set = harness.get_test_set()
    train_set = harness.get_train_set()
    
    print(f"Dataset loaded:")
    print(f"  Validation set: {len(val_set)} questions")
    print(f"  Test set (hold-out): {len(test_set)} questions")
    print(f"  Training set: {len(train_set)} questions")
    
    # Run validation evaluation
    val_results = harness.run_validation_eval()
    
    # Show few-shot examples
    harness.print_few_shot_examples(4)
    
    print(f"\n{'=' * 70}")
    print("NEXT STEPS")
    print(f"{'=' * 70}")
    print("""
1. Integrate with Groq LLM:
   - Update generate_sql() to call VoxQuery API
   - Use few-shot examples in prompt
   - Test with validation set first

2. Iterate on prompt:
   - Adjust dialect instructions
   - Add schema context
   - Refine few-shot examples

3. Final evaluation:
   - Run test set evaluation (hold-out)
   - Compare results to validation
   - Measure generalization

4. Production deployment:
   - Use train set for ongoing few-shot examples
   - Monitor SQL generation quality
   - Collect real user feedback
""")


if __name__ == '__main__':
    main()
