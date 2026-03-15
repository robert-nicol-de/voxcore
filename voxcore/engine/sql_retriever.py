import yaml
import numpy as np
from sentence_transformers import SentenceTransformer

class SQLRetriever:
    def __init__(self, example_file, embedding_model_name="all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(embedding_model_name)
        with open(example_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        self.examples = data["examples"]
        self.embeddings = [
            self.model.encode(e["question"]) for e in self.examples
        ]

    def retrieve(self, question, k=3):
        query_vec = self.model.encode(question)
        similarities = [
            np.dot(query_vec, e) for e in self.embeddings
        ]
        top_k = np.argsort(similarities)[-k:][::-1]
        return [self.examples[i] for i in top_k]
            return []
        embedding = self.embed_question(question)
        D, I = self.index.search(embedding, k)
        return [self.examples[i] for i in I[0]]

if __name__ == "__main__":
    retriever = SQLRetriever()
    q = "Which regions generated the highest revenue last quarter?"
    results = retriever.retrieve_similar(q, k=3)
    for i, ex in enumerate(results, 1):
        print(f"{i}. {ex['question']}")
        print(ex['sql'])
        print()
