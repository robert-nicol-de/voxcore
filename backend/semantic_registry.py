import yaml

class SemanticRegistry:
    def __init__(self, path):
        with open(path, "r") as f:
            self.model = yaml.safe_load(f)

        self.metrics = {m["name"]: m for m in self.model["metrics"]}
        self.dimensions = {d["name"]: d for d in self.model["dimensions"]}
        self.relationships = self.model["relationships"]
        self.time = self.model["time"]

    # --- METRICS ---
    def get_metric(self, name):
        return self.metrics.get(name)

    # --- DIMENSIONS ---
    def get_dimension(self, name):
        return self.dimensions.get(name)

    # --- RELATIONSHIPS ---
    def get_relationships(self):
        return self.relationships

    # --- TIME ---
    def get_time_config(self):
        return self.time

    # --- VALIDATION ---
    def is_valid_metric(self, name):
        return name in self.metrics

    def is_valid_dimension(self, name):
        return name in self.dimensions

    # --- SEMANTIC-AWARE EXTRACTION ---
    def match_metric(self, text: str):
        text = text.lower()
        for name in self.metrics:
            if name in text:
                return name
        return None

    def match_dimension(self, text: str):
        text = text.lower()
        for name in self.dimensions:
            if name in text:
                return name
        return None

    def match_time(self, text: str):
        text = text.lower()
        for period in self.time.get("relativePeriods", []):
            if period.replace("_", " ") in text:
                return period
        return None

    # --- STATE EXTRACTION ---
    def extract_state_updates(self, message):
        updates = {}
        metric = self.match_metric(message)
        dimension = self.match_dimension(message)
        time_filter = self.match_time(message)
        if metric:
            updates["metric"] = metric
        if dimension:
            updates["dimension"] = dimension
        if time_filter:
            updates["time_filter"] = time_filter
        return updates

    # --- ANALYSIS PLAN DISCOVERY ---
    def discover_analysis_plan(self, schema):
        return {
            "metrics": list(self.metrics.keys()),
            "dimensions": list(self.dimensions.keys()),
            "time_columns": [self.time["defaultField"]],
            "relationships": self.get_relationships()
        }

    # --- VALIDATION LAYER ---
    def validate_query(self, metric, dimension):
        if metric not in self.metrics:
            raise ValueError("Invalid metric")
        if dimension not in self.dimensions:
            raise ValueError("Invalid dimension")
