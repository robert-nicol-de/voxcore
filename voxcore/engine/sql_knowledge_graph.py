import yaml

class SQLKnowledgeGraph:
    def __init__(self, path):
        with open(path, 'r', encoding='utf-8') as f:
            self.graph = yaml.safe_load(f)

    def get_entity(self, name):
        return self.graph["entities"].get(name)

    def get_relationships(self):
        return self.graph["relationships"]

    def find_join_path(self, from_entity, to_entity):
        # Simple BFS for join path (expand as needed)
        from collections import deque
        graph = {}
        for rel in self.graph["relationships"]:
            src = rel["from"].split('.')[0]
            tgt = rel["to"].split('.')[0]
            graph.setdefault(src, []).append(tgt)
        queue = deque([(from_entity, [from_entity])])
        visited = set()
        while queue:
            current, path = queue.popleft()
            if current == to_entity:
                return path
            visited.add(current)
            for neighbor in graph.get(current, []):
                if neighbor not in visited:
                    queue.append((neighbor, path + [neighbor]))
        return None
