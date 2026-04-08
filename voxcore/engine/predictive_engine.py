import pandas as pd

class PredictiveEngine:
    def forecast_trend(self, df, metric, time_col):
        """
        Simple trend-based forecast (fast + explainable)
        """
        df = df.sort_values(time_col)
        values = df[metric].values
        if len(values) < 3:
            return None
        # Simple slope
        trend = (values[-1] - values[0]) / len(values)
        next_value = values[-1] + trend
        change_pct = ((next_value - values[-1]) / values[-1]) * 100 if values[-1] else 0
        return {
            "predicted_value": float(next_value),
            "trend": float(trend),
            "change_pct": round(change_pct, 2)
        }

    def evaluate_risk(self, forecast):
        if not forecast:
            return None
        if forecast["change_pct"] < -10:
            return "HIGH"
        if forecast["change_pct"] < -5:
            return "MEDIUM"
        return "LOW"
