import numpy as np

class SemanticMemory:
    def __init__(self):
        self.memory = []

    def embed(self, text: str):
        # 🔥 TEMP: simple vector (replace with real embeddings later)
        return np.array([ord(c) for c in text[:50]])

    def similarity(self, v1, v2):
        if len(v1) == 0 or len(v2) == 0:
            return 0
        return np.dot(v1, v2) / (
            np.linalg.norm(v1) * np.linalg.norm(v2)
        )

    def store(self, question: str, refined: str):
        vector = self.embed(question)
        self.memory.append({
            "question": question,
            "refined": refined,
            "vector": vector
        })

    def find_best_match(self, question: str, threshold=0.8):
        query_vec = self.embed(question)
        best = None
        best_score = 0
        for m in self.memory:
            score = self.similarity(query_vec, m["vector"])
            if score > best_score:
                best_score = score
                best = m
        if best_score >= threshold:
            return best, round(best_score, 2)
        return None, best_score

semantic_memory = SemanticMemory()
