class JoinResolver:
    def find_join(self, graph, from_table, to_table):
        """
        Returns best join path and confidence score. If ambiguous, returns all candidates.
        """
        if from_table == to_table:
            return {"path": [], "confidence": 1.0, "ambiguous": False, "candidates": []}

        # DFS to find all paths up to max_depth
        max_depth = 4
        paths = []
        def dfs(current, target, visited, path):
            if len(path) > max_depth:
                return
            if current == target:
                paths.append(list(path))
                return
            visited.add(current)
            for edge in graph.get(current, []):
                if edge["table"] not in visited:
                    path.append(edge)
                    dfs(edge["table"], target, visited, path)
                    path.pop()
            visited.remove(current)

        dfs(from_table, to_table, set(), [])

        if not paths:
            return {"path": [], "confidence": 0.0, "ambiguous": False, "candidates": []}

        # Score each path: shorter is better, direct FK is best
        def score_path(path):
            score = 1.0
            if not path:
                return 1.0
            score -= 0.15 * (len(path) - 1)
            # Prefer inferred_fk over name_match
            for edge in path:
                if edge.get("type") == "inferred_fk":
                    score += 0.05
                elif edge.get("type") == "name_match":
                    score -= 0.05
            return max(0.0, min(1.0, score))

        scored = [(score_path(p), p) for p in paths]
        scored.sort(reverse=True)
        best_score, best_path = scored[0]

        ambiguous = len(scored) > 1 and (scored[0][0] - scored[1][0] < 0.15)
        candidates = [dict(path=p, confidence=s) for s, p in scored[:3]] if ambiguous else []

        return {
            "path": best_path,
            "confidence": round(best_score, 2),
            "ambiguous": ambiguous,
            "candidates": candidates,
        }
