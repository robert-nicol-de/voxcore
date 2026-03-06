#!/usr/bin/env python3
"""Verification script for VoxQuery training dataset and system setup."""

import json
import sys

def verify_training_dataset():
    """Verify training_questions.json is properly configured."""
    try:
        with open('backend/training_questions.json', 'r') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Failed to load training_questions.json: {e}")
        return False
    
    print("=" * 70)
    print("VOXQUERY SYSTEM VERIFICATION")
    print("=" * 70)
    
    # Basic counts
    total = len(data)
    golden = len([q for q in data if q.get('priority_golden_set')])
    sql = len([q for q in data if q.get('expected_sql')])
    tables = len([q for q in data if q.get('relevant_tables')])
    
    print(f"\n📊 TRAINING DATASET")
    print(f"   Total Questions: {total}")
    print(f"   Priority Golden Set: {golden}")
    print(f"   With Expected SQL: {sql}")
    print(f"   With Schema Context: {tables}")
    
    # Split distribution
    splits = {}
    for q in data:
        s = q.get('split', 'MISSING')
        splits[s] = splits.get(s, 0) + 1
    
    print(f"\n📋 SPLIT DISTRIBUTION")
    print(f"   Validation Set (val): {splits.get('val', 0)}")
    print(f"   Test Set (test): {splits.get('test', 0)}")
    print(f"   Training Set (train): {splits.get('train', 0)}")
    if splits.get('MISSING'):
        print(f"   ⚠️  Missing split: {splits.get('MISSING', 0)}")
    
    # Golden set details
    val_set = [q for q in data if q.get('split') == 'validation']
    test_set = [q for q in data if q.get('split') == 'test']
    
    print(f"\n🎯 GOLDEN SET DETAILS")
    print(f"   Validation Questions: {len(val_set)}")
    for i, q in enumerate(val_set, 1):
        has_sql = "✓" if q.get('expected_sql') else "✗"
        print(f"      {i}. {has_sql} {q['natural_language_question'][:55]}...")
    
    print(f"\n   Test Questions (Hold-out): {len(test_set)}")
    for i, q in enumerate(test_set, 1):
        has_sql = "✓" if q.get('expected_sql') else "✗"
        print(f"      {i}. {has_sql} {q['natural_language_question'][:55]}...")
    
    # Validation
    print(f"\n✅ VALIDATION CHECKS")
    checks = [
        ("JSON Valid", True),
        ("All questions have split", splits.get('MISSING', 0) == 0),
        ("Golden set marked", golden >= 12),
        ("Expected SQL added", sql >= 3),
        ("Schema context added", tables >= 3),
    ]
    
    all_pass = True
    for check_name, result in checks:
        status = "✅" if result else "❌"
        print(f"   {status} {check_name}")
        if not result:
            all_pass = False
    
    print(f"\n{'=' * 70}")
    if all_pass:
        print("✅ SYSTEM READY - All checks passed!")
        print("   Next: Build evaluation harness & add remaining SQL")
    else:
        print("⚠️  ISSUES FOUND - Review above")
    print(f"{'=' * 70}\n")
    
    return all_pass

if __name__ == '__main__':
    success = verify_training_dataset()
    sys.exit(0 if success else 1)
