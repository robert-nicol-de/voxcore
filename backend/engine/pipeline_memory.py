class PipelineMemory:
    def __init__(self):
        self.memory = []

    def store(self, record: dict):
        self.memory.append(record)

    def find_similar(self, question: str):
        for m in self.memory:
            if m["question"] in question or question in m["question"]:
                return m
        return None

# global instance
pipeline_memory = PipelineMemory()
