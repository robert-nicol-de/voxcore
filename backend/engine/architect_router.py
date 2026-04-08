from typing import Dict, Tuple

class ArchitectRouter:
    def __init__(self):
        self.domain_rules = {
            "Query Intelligence": ["query", "sql", "join", "aggregation", "slow"],
            "Governance & Safety": ["risk", "unsafe", "validation", "block"],
            "Insight Engine": ["insight", "trend", "anomaly", "why", "explain"],
            "Frontend UI/UX": ["ui", "button", "chart", "frontend", "react"],
            "Security & Permissions": ["auth", "permission", "token", "access"],
        }

    def route(self, text: str) -> Tuple[str, float]:
        text_lower = text.lower()
        scores = {}
        for domain, keywords in self.domain_rules.items():
            score = sum(1 for k in keywords if k in text_lower)
            if score > 0:
                scores[domain] = score
        if not scores:
            return "Unknown", 0.0
        best_domain = max(scores, key=scores.get)
        confidence = scores[best_domain] / len(self.domain_rules[best_domain])
        return best_domain, round(confidence, 2)

    def route_multi(self, text: str):
        text_lower = text.lower()
        results = []
        for domain, keywords in self.domain_rules.items():
            score = sum(1 for k in keywords if k in text_lower)
            if score > 0:
                confidence = score / len(keywords)
                results.append({
                    "domain": domain,
                    "confidence": round(confidence, 2)
                })
        results.sort(key=lambda x: x["confidence"], reverse=True)
        return results

    def build_context_bridge(self, pr: Dict, domain: str) -> Dict:
        return {
            "domain": domain,
            "input": pr.get("problem"),
            "expected_output": self._expected_output(domain),
            "pipeline_stage": self._pipeline_stage(domain),
            "constraints": [
                "Sandbox = production",
                "Must follow pipeline",
                "No cross-domain leakage",
            ],
        }

    def _expected_output(self, domain: str) -> str:
        mapping = {
            "Query Intelligence": "SQL + metadata",
            "Insight Engine": "Structured insights",
            "Frontend UI/UX": "React components",
            "Governance & Safety": "Validation result + risk score",
        }
        return mapping.get(domain, "System response")

    def _pipeline_stage(self, domain: str) -> str:
        mapping = {
            "Query Intelligence": "Query Generation",
            "Governance & Safety": "Validation",
            "Insight Engine": "Insight Generation",
            "Frontend UI/UX": "Presentation Layer",
        }
        return mapping.get(domain, "General")

PIPELINE_ORDER = [
    "Query Intelligence",
    "Governance & Safety",
    "Optimization",
    "Insight Engine",
    "Frontend UI/UX"
]

def sort_by_pipeline(domains):
    order_map = {d: i for i, d in enumerate(PIPELINE_ORDER)}
    return sorted(
        domains,
        key=lambda x: order_map.get(x["domain"], 999)
    )
