class JoinGraph:
    def build(self, relationships):
        graph = {}
        for rel in relationships:
            t1 = rel["from_table"]
            t2 = rel["to_table"]
            graph.setdefault(t1, []).append({
                "table": t2,
                "join": f"{t1}.{rel['from_column']} = {t2}.{rel['to_column']}"
            })
        return graph
