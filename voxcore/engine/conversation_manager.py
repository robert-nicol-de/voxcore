"""
VoxCore Conversation Manager — Step 2: Curated Demo Scenarios
Handles intent detection, state extraction, and curated scenario routing
with structured response mapping to Playground contract.
"""

import logging
import re
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import random

logger = logging.getLogger(__name__)

# ============================================================================
# STEP 2: INTENT RECOGNITION (DETERMINISTIC)
# ============================================================================

class Intent:
    """Deterministic intent enum"""
    REVENUE_BY_REGION = "revenue_by_region"
    REVENUE_BY_PRODUCT = "revenue_by_product"
    TREND_OVER_TIME = "trend_over_time"
    ROOT_CAUSE = "root_cause"
    EXPLAIN_DATA = "explain_data"
    UNKNOWN = "unknown"

# ============================================================================
# STEP 2: STATE EXTRACTION (CLEAN)
# ============================================================================

@dataclass
class QueryState:
    """Extracted state - only useful fields, no silent defaults"""
    metric: Optional[str] = None  # revenue, orders, customers, etc.
    dimension: Optional[str] = None  # region, product, category, etc.
    time_filter: Optional[str] = None  # ytd, last_quarter, month_over_month, etc.
    entity_focus: Optional[str] = None  # specific region/product name if mentioned
    intent: str = Intent.UNKNOWN
    confidence: float = 0.0

    def is_complete(self) -> bool:
        """Check if state has enough info for meaningful response"""
        return self.metric is not None or self.intent in [
            Intent.EXPLAIN_DATA, Intent.ROOT_CAUSE
        ]

class StateExtractor:
    """Extract state from natural language - deterministic matching"""
    
    # Metric patterns
    METRIC_PATTERNS = {
        "revenue": [r"\brevenue\b", r"\bsales\b", r"\bincome\b", r"\btotal\b"],
        "orders": [r"\border", r"\btransaction", r"\bpurchase"],
        "customers": [r"\bcustomer", r"\buser", r"\bbuyer", r"\baccounts"],
        "growth": [r"\bgrowth\b", r"\bincrease", r"\brise"],
    }
    
    # Dimension patterns
    DIMENSION_PATTERNS = {
        "region": [r"\bregion\b", r"\barea\b", r"\bterritory\b", r"\bgeograph"],
        "product": [r"\bproduct\b", r"\bsku\b", r"\bitem\b", r"\bcategory\b"],
        "time": [r"\bmonth\b", r"\bquarter\b", r"\byear\b", r"\byearly\b"],
        "customer": [r"\bcustomer\b", r"\bsegment\b", r"\btype\b"],
    }
    
    # Time filter patterns
    TIME_PATTERNS = {
        "ytd": [r"\bytd\b", r"\byear to date\b", r"\bthis year\b"],
        "last_quarter": [r"\blast quarter\b", r"\bq\d\b", r"\bprevious quarter\b"],
        "month_over_month": [r"\bmonth over month\b", r"\bmom\b", r"\bmonthly change\b"],
        "trend": [r"\btrend\b", r"\bhistor", r"\bover time\b"],
    }
    
    @staticmethod
    def extract(message: str) -> QueryState:
        """Extract state from message with deterministic matching"""
        message_lower = message.lower()
        state = QueryState()
        
        # Extract metric
        for metric, patterns in StateExtractor.METRIC_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    state.metric = metric
                    state.confidence += 0.3
                    break
            if state.metric:
                break
        
        # Extract dimension
        for dimension, patterns in StateExtractor.DIMENSION_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    state.dimension = dimension
                    state.confidence += 0.3
                    break
            if state.dimension:
                break
        
        # Extract time filter
        for time_filter, patterns in StateExtractor.TIME_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    state.time_filter = time_filter
                    state.confidence += 0.2
                    break
            if state.time_filter:
                break
        
        # Extract entity focus (specific region/product)
        entity_match = re.search(r'\b(north|south|east|west|americas|emea|apac|us|europe|asia)\b', message_lower)
        if entity_match:
            state.entity_focus = entity_match.group(1)
            state.confidence += 0.2
        
        return state

# ============================================================================
# STEP 2: INTENT DETECTION (DETERMINISTIC)
# ============================================================================

class IntentDetector:
    """Detect user intent from message and state - no ambiguity"""
    
    @staticmethod
    def detect(message: str, state: QueryState) -> str:
        """Detect intent based on message patterns and state"""
        message_lower = message.lower()
        
        # Priority 1: Explicit intent keywords
        if re.search(r"\b(explain|tell me about|describe|what is)\b", message_lower):
            return Intent.EXPLAIN_DATA
        
        if re.search(r"\b(why|root cause|dropped|declined|fell)\b", message_lower):
            return Intent.ROOT_CAUSE
        
        # Priority 2: State-based routing
        if state.metric and state.dimension:
            if state.dimension == "region":
                return Intent.REVENUE_BY_REGION
            elif state.dimension == "product":
                return Intent.REVENUE_BY_PRODUCT
        
        if state.time_filter == "trend" or re.search(r"\bover time\b", message_lower):
            return Intent.TREND_OVER_TIME
        
        if state.metric and "by" in message_lower:
            if "region" in message_lower:
                return Intent.REVENUE_BY_REGION
            elif "product" in message_lower:
                return Intent.REVENUE_BY_PRODUCT
        
        # Priority 3: Default to explain if we can't determine
        if state.is_complete():
            return Intent.TREND_OVER_TIME
        
        return Intent.UNKNOWN

# ============================================================================
# STEP 2: STRUCTURED SUGGESTIONS
# ============================================================================

@dataclass
class Suggestion:
    """Structured suggestion, not decorative strings"""
    label: str  # What to show user
    type: str  # "follow_up" | "drill_down" | "comparison" | "context"
    reason: str  # Why this is suggested
    safe: bool = True  # Is this safe under current policies
    priority: int = 1  # 1=high, 2=medium, 3=low

# ============================================================================
# STEP 2: CURATED SCENARIO HANDLERS
# ============================================================================

class ScenarioHandler:
    """Base class for scenario handlers"""
    
    def __init__(self):
        self.handler_name = self.__class__.__name__
    
    def execute(self, state: QueryState) -> Dict[str, Any]:
        """Execute scenario and return result"""
        raise NotImplementedError
    
    def build_suggestions(self, state: QueryState) -> List[Suggestion]:
        """Build structured suggestions for follow-up"""
        return []

class RevenueByRegionScenario(ScenarioHandler):
    """Revenue by region - curated demo scenario"""
    
    def execute(self, state: QueryState) -> Dict[str, Any]:
        """Return believable revenue by region data"""
        
        # Curated demo data - realistic regional splits
        regions = ["North America", "Europe", "Asia Pacific", "LATAM"]
        demo_data = []
        base_revenue = 850000
        
        for region in regions:
            # Realistic variation in revenue by region
            variance = random.uniform(0.8, 1.3)
            revenue = int(base_revenue * variance)
            pct_growth = random.uniform(-5, 25)
            
            demo_data.append({
                "region": region,
                "revenue": revenue,
                "orders": random.randint(80, 400),
                "growth_pct": round(pct_growth, 1),
                "avg_order_value": round(revenue / random.randint(80, 400), 2),
            })
        
        # Sort by revenue descending
        demo_data.sort(key=lambda x: x["revenue"], reverse=True)
        
        return {
            "data": demo_data,
            "narrative": "Revenue distribution shows strong North America performance (42% of total) with Europe second at 31%.",
            "chart_type": "bar",
            "chart_config": {
                "x_axis": "region",
                "y_axis": "revenue",
                "show_growth": True,
            },
            "governance_metadata": {
                "data_masked": False,
                "sensitivity": "internal",
            },
        }
    
    def build_suggestions(self, state: QueryState) -> List[Suggestion]:
        """Suggest logical follow-ups"""
        return [
            Suggestion(
                label="Compare to last quarter",
                type="comparison",
                reason="Understand seasonal patterns",
                priority=1,
            ),
            Suggestion(
                label="Drill into top region",
                type="drill_down",
                reason="Explore drivers of success",
                priority=1,
            ),
            Suggestion(
                label="Customer churn by region",
                type="follow_up",
                reason="Identify at-risk markets",
                priority=2,
            ),
        ]

class RevenueByProductScenario(ScenarioHandler):
    """Revenue by product - curated demo scenario"""
    
    def execute(self, state: QueryState) -> Dict[str, Any]:
        """Return believable revenue by product data"""
        
        products = [
            "Premium Analytics",
            "Core Platform",
            "Integration Suite",
            "Compliance Module",
            "Developer Tools",
        ]
        demo_data = []
        
        for product in products:
            revenue = random.randint(200000, 800000)
            demo_data.append({
                "product": product,
                "revenue": revenue,
                "margin_pct": round(random.uniform(35, 75), 1),
                "customers": random.randint(20, 150),
                "satisfaction": round(random.uniform(3.5, 4.9), 1),
            })
        
        demo_data.sort(key=lambda x: x["revenue"], reverse=True)
        
        return {
            "data": demo_data,
            "narrative": "Premium Analytics leads revenue at $2.1M (36% mix) with strong customer satisfaction at 4.7/5.0.",
            "chart_type": "bar",
            "chart_config": {
                "x_axis": "product",
                "y_axis": "revenue",
                "show_margin": True,
            },
            "governance_metadata": {
                "data_masked": False,
                "sensitivity": "internal",
            },
        }
    
    def build_suggestions(self, state: QueryState) -> List[Suggestion]:
        """Suggest logical follow-ups"""
        return [
            Suggestion(
                label="Product-region heat map",
                type="follow_up",
                reason="Identify strongest combos",
                priority=1,
            ),
            Suggestion(
                label="Expansion opportunities",
                type="follow_up",
                reason="Find underserved segments",
                priority=2,
            ),
        ]

class TrendOverTimeScenario(ScenarioHandler):
    """Trend over time - curated demo scenario"""
    
    def execute(self, state: QueryState) -> Dict[str, Any]:
        """Return believable trend data over 12 months"""
        
        demo_data = []
        base_revenue = 650000
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        
        for i, month in enumerate(months):
            # Realistic growth trend with seasonality
            trend_growth = 1.0 + (i * 0.03)  # 3% monthly growth
            seasonality = 1.0 + (0.15 * (i % 3) / 3)  # Q-end seasonality
            revenue = int(base_revenue * trend_growth * seasonality)
            
            demo_data.append({
                "month": month,
                "revenue": revenue,
                "growth_pct": round(((revenue / base_revenue) - 1) * 100, 1),
            })
        
        return {
            "data": demo_data,
            "narrative": "Revenue shows steady 36% YTD growth with Q-end spikes. December projected to hit $1.2M.",
            "chart_type": "line",
            "chart_config": {
                "x_axis": "month",
                "y_axis": "revenue",
                "show_trend_line": True,
            },
            "governance_metadata": {
                "data_masked": False,
                "sensitivity": "internal",
            },
        }
    
    def build_suggestions(self, state: QueryState) -> List[Suggestion]:
        """Suggest logical follow-ups"""
        return [
            Suggestion(
                label="Forecast next quarter",
                type="follow_up",
                reason="Plan resource allocation",
                priority=1,
            ),
            Suggestion(
                label="Identify growth drivers",
                type="follow_up",
                reason="Replicate success",
                priority=1,
            ),
        ]

class RootCauseScenario(ScenarioHandler):
    """Root cause analysis - decline investigation"""
    
    def execute(self, state: QueryState) -> Dict[str, Any]:
        """Root cause analysis for metric decline"""
        
        # Hypothetical decline scenario
        analysis_points = [
            {
                "factor": "Customer churn",
                "impact_pct": 45,
                "detail": "Lost 12 enterprise customers in Q3",
            },
            {
                "factor": "Price competition",
                "impact_pct": 30,
                "detail": "3 competitors launched aggressive pricing",
            },
            {
                "factor": "Product issues",
                "impact_pct": 15,
                "detail": "API downtime in Aug reduced confidence",
            },
            {
                "factor": "Seasonality",
                "impact_pct": 10,
                "detail": "Q3 typically 8% below trend",
            },
        ]
        
        return {
            "data": analysis_points,
            "narrative": "Revenue decline analysis: Customer churn (45%) is primary driver. Recommend immediate retention program.",
            "chart_type": "waterfall",
            "chart_config": {
                "show_impact": True,
                "highlight_primary": True,
            },
            "governance_metadata": {
                "data_masked": False,
                "sensitivity": "confidential",
            },
        }
    
    def build_suggestions(self, state: QueryState) -> List[Suggestion]:
        """Suggest next actions"""
        return [
            Suggestion(
                label="Retention campaign analysis",
                type="follow_up",
                reason="Address top driver (churn)",
                priority=1,
            ),
            Suggestion(
                label="Win-back strategy",
                type="follow_up",
                reason="Recovery planning",
                priority=2,
            ),
        ]

class ExplainDatasetScenario(ScenarioHandler):
    """Explain dataset - data preview and context"""
    
    def execute(self, state: QueryState) -> Dict[str, Any]:
        """Return dataset context and preview"""
        
        dataset_overview = {
            "name": "Sales & Customer Analytics Warehouse",
            "tables": [
                {"name": "orders", "rows": 245000, "columns": 18},
                {"name": "customers", "rows": 12400, "columns": 22},
                {"name": "products", "rows": 540, "columns": 14},
                {"name": "regions", "rows": 48, "columns": 8},
            ],
            "data_freshness": "Updated daily at 2 AM UTC",
            "retention": "36 months rolling",
            "sample_metrics": [
                "Total Revenue: $38.2M YTD",
                "Active Customers: 2,340",
                "Order Volume: 245K transactions",
                "Average Order Value: $156",
            ],
        }
        
        return {
            "data": dataset_overview,
            "narrative": "This warehouse contains 3 years of transactional and customer data from 48 regions. Updates daily, covers $38.2M in revenue.",
            "chart_type": "info_panel",
            "governance_metadata": {
                "data_masked": False,
                "sensitivity": "public",
            },
        }
    
    def build_suggestions(self, state: QueryState) -> List[Suggestion]:
        """Suggest exploration starting points"""
        return [
            Suggestion(
                label="Revenue by region",
                type="follow_up",
                reason="Most popular analysis",
                priority=1,
            ),
            Suggestion(
                label="Customer segmentation",
                type="follow_up",
                reason="Unlock targeting insights",
                priority=2,
            ),
        ]

# ============================================================================
# STEP 2: SCENARIO FACTORY
# ============================================================================

class ScenarioFactory:
    """Map intent to scenario handler"""
    
    SCENARIOS = {
        Intent.REVENUE_BY_REGION: RevenueByRegionScenario(),
        Intent.REVENUE_BY_PRODUCT: RevenueByProductScenario(),
        Intent.TREND_OVER_TIME: TrendOverTimeScenario(),
        Intent.ROOT_CAUSE: RootCauseScenario(),
        Intent.EXPLAIN_DATA: ExplainDatasetScenario(),
    }
    
    @classmethod
    def get_handler(cls, intent: str) -> Optional[ScenarioHandler]:
        """Get scenario handler for intent"""
        return cls.SCENARIOS.get(intent)

# ============================================================================
# STEP 2: RESPONSE BUILDER - CONTRACT MAPPING
# ============================================================================

class PlaygroundResponseBuilder:
    """Build response that maps cleanly to Playground contract"""
    
    @staticmethod
    def build_from_scenario(
        session_id: str,
        message: str,
        state: QueryState,
        intent: str,
        scenario_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Map scenario result to Playground response contract"""
        
        # Build hero insight from scenario
        hero_insights = {
            Intent.REVENUE_BY_REGION: "Regional revenue breakdown shows strong North America performance",
            Intent.REVENUE_BY_PRODUCT: "Premium Analytics drives 36% of revenue with highest margins",
            Intent.TREND_OVER_TIME: "Revenue trending +36% YTD with strong Q-end momentum",
            Intent.ROOT_CAUSE: "Customer churn is primary driver of revenue decline",
            Intent.EXPLAIN_DATA: "Sales warehouse contains 3-year transaction history",
        }
        
        hero_insight = hero_insights.get(intent, "Query analysis complete")
        
        return {
            # Internal structure (will be mapped to Playground contract)
            "_internal_result": {
                "session_id": session_id,
                "intent": intent,
                "state": state.__dict__,
                "hero_insight": hero_insight,
                "why_this_answer": scenario_result.get("narrative", ""),
                "result": scenario_result,
                "emd_preview": scenario_result.get("narrative", "")[:200],
                "suggestions": scenario_result.get("suggestions", []),
                "governance": {
                    "classification": "SAFE",
                    "risk_score": 0,
                    "sensitivity": scenario_result.get("governance_metadata", {}).get("sensitivity", "internal"),
                },
            },
        }

# ============================================================================
# STEP 2: CONVERSATION MANAGER - MAIN ORCHESTRATOR
# ============================================================================

class ConversationManager:
    """
    Main orchestrator for demo conversations.
    
    Pipeline:
    1. Extract state from message
    2. Detect intent (deterministic)
    3. Route to scenario handler
    4. Build response mapping to Playground contract
    """
    
    def __init__(self, demo_mode: bool = True):
        self.demo_mode = demo_mode
        self.state_extractor = StateExtractor()
        self.intent_detector = IntentDetector()
        self.scenario_factory = ScenarioFactory()
        self.response_builder = PlaygroundResponseBuilder()
        logger.info("ConversationManager initialized (Step 2: Curated scenarios)")
    
    def process_message(
        self,
        session_id: str,
        message: str,
    ) -> Dict[str, Any]:
        """Process user message through intent→scenario→response pipeline"""
        
        # Step 1: Extract state
        state = self.state_extractor.extract(message)
        logger.debug(f"State extracted: metric={state.metric}, dimension={state.dimension}")
        
        # Step 2: Detect intent
        intent = self.intent_detector.detect(message, state)
        logger.debug(f"Intent detected: {intent} (confidence={state.confidence:.2f})")
        
        # Step 3: Get scenario handler
        handler = self.scenario_factory.get_handler(intent)
        
        if not handler:
            # Fallback to explain dataset if intent unknown
            logger.warning(f"No handler for intent {intent}, falling back to EXPLAIN")
            handler = self.scenario_factory.get_handler(Intent.EXPLAIN_DATA)
            intent = Intent.EXPLAIN_DATA
        
        # Step 4: Execute scenario
        scenario_result = handler.execute(state)
        scenario_result["suggestions"] = handler.build_suggestions(state)
        logger.debug(f"Scenario executed: {handler.handler_name}")
        
        # Step 5: Build response
        response = self.response_builder.build_from_scenario(
            session_id=session_id,
            message=message,
            state=state,
            intent=intent,
            scenario_result=scenario_result,
        )
        
        return response
    
    def handle_message(self, session_id, message, **kwargs):
        """Legacy interface - delegates to process_message"""
        return self.process_message(session_id, message)
