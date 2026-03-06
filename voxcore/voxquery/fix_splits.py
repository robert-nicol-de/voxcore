#!/usr/bin/env python3
"""Fix and reorganize train/validation/test splits for training dataset."""

import json
from collections import Counter

# Load data
with open('backend/training_questions.json', 'r') as f:
    data = json.load(f)

print("=" * 70)
print("FIXING SPLITS - BEFORE")
print("=" * 70)

# Count before
before_splits = Counter([q.get('split', 'MISSING') for q in data])
print(f"Before: {dict(before_splits)}")
print(f"Total questions: {len(data)}")

# Define the new split assignments based on question index
# Validation set (7 questions): indices 0, 1, 2, 3, 4, 5, 10
# Test set (6 questions): indices 6, 7, 8, 9, 11, 12
# Train set (37 questions): all others

validation_indices = [0, 1, 2, 3, 4, 5, 10]  # Questions 1-6, 11
test_indices = [6, 7, 8, 9, 11, 12]  # Questions 7-10, 12, 13
# Rest are train

# Apply new splits
for i, q in enumerate(data):
    if i in validation_indices:
        q['split'] = 'validation'
    elif i in test_indices:
        q['split'] = 'test'
    else:
        q['split'] = 'train'

# Count after
after_splits = Counter([q.get('split', 'MISSING') for q in data])
print("\n" + "=" * 70)
print("FIXING SPLITS - AFTER")
print("=" * 70)
print(f"After: {dict(after_splits)}")

# Check for missing splits
missing = [i for i, q in enumerate(data) if 'split' not in q]
print(f"Missing splits: {len(missing)}")

# Check SQL distribution
sql_by_split = {}
for split in ['validation', 'test', 'train']:
    count = len([q for q in data if q.get('split') == split and q.get('expected_sql')])
    total = len([q for q in data if q.get('split') == split])
    sql_by_split[split] = (count, total)
    print(f"  {split}: {count}/{total} with expected_sql")

# Show validation set questions
print("\n" + "=" * 70)
print("VALIDATION SET (7 questions)")
print("=" * 70)
for i, q in enumerate(data):
    if q.get('split') == 'validation':
        has_sql = "✓" if q.get('expected_sql') else "✗"
        print(f"  {has_sql} {q['natural_language_question'][:60]}...")

# Show test set questions
print("\n" + "=" * 70)
print("TEST SET (6 questions - HOLD-OUT)")
print("=" * 70)
for i, q in enumerate(data):
    if q.get('split') == 'test':
        has_sql = "✓" if q.get('expected_sql') else "✗"
        print(f"  {has_sql} {q['natural_language_question'][:60]}...")

# Save fixed version
with open('backend/training_questions.json', 'w') as f:
    json.dump(data, f, indent=2)

print("\n" + "=" * 70)
print("✅ SPLITS FIXED AND SAVED")
print("=" * 70)
print(f"Total: {len(data)} questions")
print(f"  Validation: {after_splits['validation']} (for prompt tuning)")
print(f"  Test: {after_splits['test']} (hold-out, never use in dev)")
print(f"  Train: {after_splits['train']} (few-shot examples)")
print("\nNext: Add expected_sql for validation set questions 3, 4, 6, 11")
