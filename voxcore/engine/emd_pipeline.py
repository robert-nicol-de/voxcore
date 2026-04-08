from voxcore.engine.explain_my_data import explain_dataset
from voxcore.engine.root_cause_engine import RootCauseEngine
from voxcore.engine.predictive_engine import PredictiveEngine
from voxcore.engine.cross_dataset_engine import CrossDatasetEngine
from voxcore.engine.learning_engine import LearningEngine
from voxcore.engine.insight_memory import InsightMemory

class EMDPipeline:
    def __init__(self):
        self.rca = RootCauseEngine()
        self.predictor = PredictiveEngine()
        self.cross = CrossDatasetEngine()
        self.learning = LearningEngine()
        self.memory = InsightMemory()

    def run(self, schema, connection, datasets=None):
        """
        Full EMD intelligence pipeline
        """
        # 🔹 Step 1 — Base insights
        insights = explain_dataset(schema, connection)
        results = []
        for insight in insights:
            df = insight.get("dataframe")
            metric = insight.get("metric", "value")
            # 🔍 Step 2 — Root Cause
            root_causes = self.rca.analyze(
                df=df,
                metric=metric,
                dimensions=["region", "product", "category"]
            )
            # 🔮 Step 3 — Prediction
            forecast = self.predictor.forecast_trend(
                df=df,
                metric=metric,
                time_col="date"
            )
            risk = self._evaluate_risk(forecast)
            # 🧠 Step 4 — Learning
            self.memory.store_insight(insight)
            patterns = self.learning.detect_patterns(self.memory)
            # 🔗 Step 5 — Cross Dataset
            cross_insights = []
            if datasets:
                cross_insights = self.cross.correlate(datasets)
            # 🧠 Step 6 — Build final output
            enriched = self._build_output(
                insight,
                root_causes,
                forecast,
                risk,
                patterns,
                cross_insights
            )
            results.append(enriched)
        return results

    def _evaluate_risk(self, forecast):
        if not forecast:
            return None
        if forecast["change_pct"] < -10:
            return "HIGH"
        if forecast["change_pct"] < -5:
            return "MEDIUM"
        return "LOW"

    def _build_output(self, insight, root_causes, forecast, risk, patterns, cross):
        primary = root_causes[0] if root_causes else None
        narrative = insight["insight"]
        if primary:
            narrative += f" driven by {primary['value']} in {primary['dimension']}."
        if forecast:
            narrative += f" Forecast shows {forecast['change_pct']}% change next period."
        return {
            "insight": insight["insight"],
            "narrative": narrative,
            "root_causes": root_causes,
            "prediction": forecast,
            "risk": risk,
            "patterns": patterns,
            "cross_dataset": cross,
            "recommendations": self._generate_recommendations(root_causes, risk)
        }

    def _generate_recommendations(self, root_causes, risk):
        recs = []
        for rc in root_causes[:2]:
            recs.append(f"Investigate {rc['value']} in {rc['dimension']}")
        if risk == "HIGH":
            recs.append("Take immediate corrective action")
        return recs
