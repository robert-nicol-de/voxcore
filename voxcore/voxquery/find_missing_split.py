import json

data = json.load(open('backend/training_questions.json'))
no_split = [i for i, q in enumerate(data) if 'split' not in q]

if no_split:
    print(f"Found {len(no_split)} questions without split:")
    for i in no_split:
        q = data[i]
        print(f"  Index {i}: {q['natural_language_question'][:60]}")
else:
    print("All questions have split field assigned!")
