import yaml
import random

def load_yaml(path):
    with open(path) as f:
        return yaml.safe_load(f)

metrics = load_yaml("voxcore/training/libraries/metrics.yaml")['metrics']
entities = load_yaml("voxcore/training/libraries/entities.yaml")['entities']
times = load_yaml("voxcore/training/libraries/time_ranges.yaml")['time_ranges']

templates = [
    "Which {entity} had declining {metric} trends over the {time_range}?",
    "Which {entity} grew the fastest in {metric} over the {time_range}?",
    "Which {entity} had unusual spikes in {metric} over the {time_range}?",
    "Who are the top 10 {entity} by {metric} in the {time_range}?"
]

def generate_questions(n=5000):
    questions = []
    for i in range(n):
        template = random.choice(templates)
        q = template.format(
            entity=random.choice(entities),
            metric=random.choice(metrics),
            time_range=random.choice(times)
        )
        questions.append({
            "id": i + 1,
            "question": q
        })
    return questions

dataset = generate_questions(5000)

with open("voxcore/training/sql_reasoning_generated.yaml", "w") as f:
    yaml.dump({"examples": dataset}, f)
