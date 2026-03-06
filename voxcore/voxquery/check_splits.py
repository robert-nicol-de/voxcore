#!/usr/bin/env python3
import json

data = json.load(open('backend/training_questions.json'))

val = [q for q in data if q.get('split') == 'validation']
test = [q for q in data if q.get('split') == 'test']
train = [q for q in data if q.get('split') == 'train']

print(f"Validation: {len(val)} total, {len([q for q in val if q.get('expected_sql')])} with SQL")
print(f"Test: {len(test)} total, {len([q for q in test if q.get('expected_sql')])} with SQL")
print(f"Train: {len(train)} total, {len([q for q in train if q.get('expected_sql')])} with SQL")

# Show test questions
print("\nTest set questions:")
for i, q in enumerate(test, 1):
    has_sql = "✓" if q.get('expected_sql') else "✗"
    print(f"  {i}. {has_sql} {q['natural_language_question'][:60]}...")
