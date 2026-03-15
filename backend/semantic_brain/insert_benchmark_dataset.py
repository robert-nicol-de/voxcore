# Script to insert benchmark questions and paraphrases into TrainingDataset

from benchmark_questions import BENCHMARK_QUESTIONS
from canonical_questions import CANONICAL_QUESTIONS
from training_dataset import TrainingDataset


def insert_benchmark_and_canonical_questions():
    dataset = TrainingDataset()
    # Insert 12 benchmark questions and paraphrases
    for q in BENCHMARK_QUESTIONS:
        dataset.record(
            question=q["question"],
            intent_type=q["intent"],
            metric=q["metric"],
            dimension=q["dimension"],
            sql="",
            confidence=1.0,
            difficulty_level=1
        )
        for phr in q.get("paraphrases", []):
            dataset.record(
                question=phr,
                intent_type=q["intent"],
                metric=q["metric"],
                dimension=q["dimension"],
                sql="",
                confidence=1.0,
                difficulty_level=1
            )
    # Insert 100 canonical questions (question text only)
    for q in CANONICAL_QUESTIONS:
        dataset.record(
            question=q["question"],
            intent_type=None,
            metric=None,
            dimension=None,
            sql="",
            confidence=1.0,
            difficulty_level=1
        )
    print("Inserted all benchmark, paraphrase, and canonical questions into TrainingDataset.")

if __name__ == "__main__":
    insert_benchmark_and_canonical_questions()
