import pandas as pd

class RootCauseEngine:
    def analyze(self, df: pd.DataFrame, metric: str, dimensions: list):
        """
        Finds biggest contributors to change in a metric
        """
        if df.empty or metric not in df.columns:
            return []
        total = df[metric].sum()
        results = []
        for dim in dimensions:
            if dim not in df.columns:
                continue
            grouped = df.groupby(dim)[metric].sum().reset_index()
            for _, row in grouped.iterrows():
                contribution = row[metric] / total if total else 0
                results.append({
                    "dimension": dim,
                    "value": row[dim],
                    "contribution": round(contribution * 100, 2),
                    "raw_value": float(row[metric])
                })
        # Sort by biggest impact
        results.sort(key=lambda x: abs(x["raw_value"]), reverse=True)
        return results[:5]
