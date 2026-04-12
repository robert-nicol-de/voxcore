"""
VoxCore Explain My Data (EMD) Mode
Automated insight discovery engine for datasets.

PLAYGROUND SCOPE: Only runs 4 stable insight types.
- growth_trend
- decline_trend
- top_performers
- anomaly_detection

All queries governed through VoxCoreEngine (cost limits, RBAC, policies).
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import numpy as np

# Import stable insight generation
from voxcore.engine.insight_engine import generate_emd_preview, generate_insights, EMDCard
from voxcore.engine.semantic_cache import get_cached_result, cache_result
from voxcore.engine.adaptive_query_optimizer import optimize_query

# --- Main Entrypoints ---

def playground_emd_preview(
    schema: Dict[str, Any],
    db: Any,
    max_cards: int = 4,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None
) -> List[EMDCard]:
    """
    Playground EMD Preview entrypoint.
    
    Runs ONLY the 4 stable insight types:
    - growth_trend
    - decline_trend
    - top_performers
    - anomaly_detection
    
    Bounded for safe demo mode:
    - Max 4 cards returned (capped)
    - Query signature deduplication (no redundant queries)
    - All queries governed by VoxCoreEngine
    - Cost limits enforced
    
    Args:
        schema: Database schema dict with metric/dimension definitions
        db: Database connection
        max_cards: Maximum cards to return (default 4)
        user_id: User ID for governance checks
        session_id: Session ID for audit logging
    
    Returns:
        List[EMDCard]: 0-4 lightweight preview cards ready for Playground
    """
    analysis_plan = discover_analysis_plan(schema)
    insights = []
    used_queries = {}
    used_signatures = set()
    
    # Run ONLY stable insight types (4 total)
    insights += run_top_performers(analysis_plan, db, used_queries, used_signatures, user_id, session_id)
    insights += run_growth_analysis(analysis_plan, db, used_queries, used_signatures, user_id, session_id)
    insights += run_decline_analysis(analysis_plan, db, used_queries, used_signatures, user_id, session_id)
    insights += run_anomaly_detection(analysis_plan, db, used_queries, used_signatures, user_id, session_id)
    
    # Sort by score and cap at max_cards
    insights = sorted(insights, key=lambda x: x.get("score", 0), reverse=True)[:max_cards]
    
    # Convert to EMDCard objects (lightweight, clean)
    cards = []
    for insight in insights:
        card = EMDCard(
            title=_generate_card_title(insight),
            insight=insight.get("insight", ""),
            score=insight.get("score", 0),
            confidence=insight.get("confidence", 0),
            chart=insight.get("chart", {})
        )
        cards.append(card)
    
    return cards


def explain_dataset(
    schema: Dict[str, Any],
    db: Any,
    max_insights: int = 10,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Full Explain My Data mode (INTERNAL/ADVANCED USE ONLY).
    
    ⚠️  WARNING: This runs all 10 insight types and may be expensive.
    For Playground, use playground_emd_preview() instead.
    
    Runs all insight algorithms:
    - Top Performers, Growth, Decline (stable)
    - Anomaly Detection (stable)
    - Regional Comparison, Product Rankings (unstable)
    - Churn Risk, Seasonality (unstable)
    - Revenue Distribution, Emerging Segments (unstable)
    
    All queries are governed through VoxCoreEngine.
    """
    analysis_plan = discover_analysis_plan(schema)
    insights = []
    used_queries = {}
    used_signatures = set()

    # Stable types (same as Playground)
    insights += run_top_performers(analysis_plan, db, used_queries, used_signatures, user_id, session_id)
    insights += run_growth_analysis(analysis_plan, db, used_queries, used_signatures, user_id, session_id)
    insights += run_decline_analysis(analysis_plan, db, used_queries, used_signatures, user_id, session_id)
    insights += run_anomaly_detection(analysis_plan, db, used_queries, used_signatures, user_id, session_id)
    
    # Unstable types (internal use only)
    insights += run_regional_comparison(analysis_plan, db, used_queries, used_signatures, user_id, session_id)
    insights += run_product_rankings(analysis_plan, db, used_queries, used_signatures, user_id, session_id)
    insights += run_churn_detection(analysis_plan, db, used_queries, used_signatures, user_id, session_id)
    insights += run_seasonality_detection(analysis_plan, db, used_queries, used_signatures, user_id, session_id)
    insights += run_revenue_distribution(analysis_plan, db, used_queries, used_signatures, user_id, session_id)
    insights += run_emerging_segments(analysis_plan, db, used_queries, used_signatures, user_id, session_id)

    # Rank by score and return top N
    insights = sorted(insights, key=lambda x: x.get("score", 0), reverse=True)
    return insights[:max_insights]

# --- Utility Functions ---

def _generate_card_title(insight: Dict[str, Any]) -> str:
    """Generate a clean title for EMD card based on insight type and metric"""
    insight_type = insight.get("type", "insight")
    metric = insight.get("metric", "Metric")
    entity = insight.get("entity")
    
    if insight_type == "growth_trend":
        return f"{metric} Growth"
    elif insight_type == "decline_trend":
        return f"{metric} Decline"
    elif insight_type == "top_performers":
        return f"Leader: {entity}" if entity else "Top Performer"
    elif insight_type == "anomaly_detection":
        return f"Anomaly: {entity}" if entity else "Anomaly Detected"
    else:
        return f"{metric}"
def discover_analysis_plan(schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    Scans schema to identify metrics, dimensions, time columns, relationships.
    
    Args:
        schema: Dict with 'tables' key containing column definitions
        
    Returns:
        plan: Dict with 'metrics', 'dimensions', 'time_columns', 'tables', 'relationships'
    """
    plan = {
        'metrics': [],
        'dimensions': [],
        'time_columns': [],
        'tables': list(schema.get('tables', {}).keys()),
        'relationships': schema.get('relationships', [])
    }
    for table, tdef in schema.get('tables', {}).items():
        for col, cdef in tdef.get('columns', {}).items():
            if cdef.get('is_metric'):
                plan['metrics'].append({'table': table, 'column': col})
            if cdef.get('is_dimension'):
                plan['dimensions'].append({'table': table, 'column': col})
            if cdef.get('is_time'):
                plan['time_columns'].append({'table': table, 'column': col})
    return plan

def build_query_signature(metric: str, dimension: Optional[str] = None, time: Optional[str] = None) -> str:
    """Generate a unique signature for a query to prevent duplicates"""
    return f"{metric}:{dimension or ''}:{time or ''}"


def run_top_performers(
    plan: Dict[str, Any],
    db: Any,
    used_queries: Dict[str, Any],
    used_signatures: set,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Detect top performers: entities with highest metric values.
    
    Uses insight_engine.generate_emd_preview() for reliable structured output.
    """
    insights = []
    for dim in plan['dimensions']:
        for metric in plan['metrics']:
            if dim['table'] == metric['table']:
                signature = build_query_signature(metric['column'], dim['column'])
                if signature in used_signatures:
                    continue
                used_signatures.add(signature)
                
                sql = f"SELECT {dim['column']}, SUM({metric['column']}) as value FROM {dim['table']} GROUP BY {dim['column']} ORDER BY value DESC LIMIT 5"
                result = run_query_with_cache(sql, db, used_queries, user_id, session_id)
                
                if result is not None:
                    # Use stable insight engine for EMD cards
                    cards = generate_emd_preview(
                        insight_type="top_performers",
                        data=result,
                        value_key="value",
                        label_key=dim['column'],
                        period_label="entity"
                    )
                    # Convert EMDCard back to insight dict for ranking
                    for card in cards:
                        insights.append({
                            "type": "top_performers",
                            "insight": card.insight,
                            "score": card.score,
                            "confidence": card.confidence,
                            "chart": card.chart,
                            "metric": metric['column'],
                            "entity": dim['column']
                        })
    return insights


def run_growth_analysis(
    plan: Dict[str, Any],
    db: Any,
    used_queries: Dict[str, Any],
    used_signatures: set,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Detect growth trends: monotonic increase over time.
    
    Uses insight_engine.generate_emd_preview() for reliable structured output.
    """
    insights = []
    for metric in plan['metrics']:
        for time in plan['time_columns']:
            if metric['table'] == time['table']:
                signature = build_query_signature(metric['column'], None, time['column'])
                if signature in used_signatures:
                    continue
                used_signatures.add(signature)
                
                sql = f"SELECT {time['column']}, SUM({metric['column']}) as value FROM {metric['table']} GROUP BY {time['column']} ORDER BY {time['column']}"
                result = run_query_with_cache(sql, db, used_queries, user_id, session_id)
                
                if result is not None:
                    cards = generate_emd_preview(
                        insight_type="growth_trend",
                        data=result,
                        value_key="value",
                        label_key=time['column'],
                        period_label="period"
                    )
                    for card in cards:
                        insights.append({
                            "type": "growth_trend",
                            "insight": card.insight,
                            "score": card.score,
                            "confidence": card.confidence,
                            "chart": card.chart,
                            "metric": metric['column'],
                            "entity": None
                        })
    return insights


def run_decline_analysis(
    plan: Dict[str, Any],
    db: Any,
    used_queries: Dict[str, Any],
    used_signatures: set,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Detect decline trends: monotonic decrease over time.
    
    Uses insight_engine.generate_emd_preview() for reliable structured output.
    """
    insights = []
    for metric in plan['metrics']:
        for time in plan['time_columns']:
            if metric['table'] == time['table']:
                signature = build_query_signature(metric['column'], None, time['column'])
                if signature in used_signatures:
                    continue
                used_signatures.add(signature)
                
                sql = f"SELECT {time['column']}, SUM({metric['column']}) as value FROM {metric['table']} GROUP BY {time['column']} ORDER BY {time['column']}"
                result = run_query_with_cache(sql, db, used_queries, user_id, session_id)
                
                if result is not None:
                    cards = generate_emd_preview(
                        insight_type="decline_trend",
                        data=result,
                        value_key="value",
                        label_key=time['column'],
                        period_label="period"
                    )
                    for card in cards:
                        insights.append({
                            "type": "decline_trend",
                            "insight": card.insight,
                            "score": card.score,
                            "confidence": card.confidence,
                            "chart": card.chart,
                            "metric": metric['column'],
                            "entity": None
                        })
    return insights

def run_anomaly_detection(
    plan: Dict[str, Any],
    db: Any,
    used_queries: Dict[str, Any],
    used_signatures: set,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Detect anomalies: statistical spikes or outliers.
    
    Uses insight_engine.generate_emd_preview() for reliable structured output.
    """
    insights = []
    for metric in plan['metrics']:
        for time in plan['time_columns']:
            if metric['table'] == time['table']:
                signature = build_query_signature(metric['column'], None, time['column'])
                if signature in used_signatures:
                    continue
                used_signatures.add(signature)
                
                sql = f"SELECT {time['column']}, SUM({metric['column']}) as value FROM {metric['table']} GROUP BY {time['column']} ORDER BY {time['column']}"
                result = run_query_with_cache(sql, db, used_queries, user_id, session_id)
                
                if result is not None:
                    cards = generate_emd_preview(
                        insight_type="anomaly_detection",
                        data=result,
                        value_key="value",
                        label_key=time['column'],
                        period_label="period"
                    )
                    for card in cards:
                        insights.append({
                            "type": "anomaly_detection",
                            "insight": card.insight,
                            "score": card.score,
                            "confidence": card.confidence,
                            "chart": card.chart,
                            "metric": metric['column'],
                            "entity": None
                        })
    return insights


# --- UNSTABLE INSIGHT TYPES (Internal Use Only) ---

def run_regional_comparison(
    plan: Dict[str, Any],
    db: Any,
    used_queries: Dict[str, Any],
    used_signatures: set,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """NOT FOR PLAYGROUND: Regional comparison analysis (unstable)"""
    insights = []
    for dim in plan['dimensions']:
        if 'region' in dim['column'].lower():
            for metric in plan['metrics']:
                if dim['table'] == metric['table']:
                    signature = build_query_signature(metric['column'], dim['column'])
                    if signature in used_signatures:
                        continue
                    used_signatures.add(signature)
                    sql = f"SELECT {dim['column']}, SUM({metric['column']}) as value FROM {dim['table']} GROUP BY {dim['column']} ORDER BY value DESC"
                    result = run_query_with_cache(sql, db, used_queries, user_id, session_id)
                    if result is not None:
                        insights += generate_insights('top_performers', result, value_key='value', label_key=dim['column'])
    return insights


def run_product_rankings(
    plan: Dict[str, Any],
    db: Any,
    used_queries: Dict[str, Any],
    used_signatures: set,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """NOT FOR PLAYGROUND: Product ranking analysis (unstable)"""
    insights = []
    for dim in plan['dimensions']:
        if 'product' in dim['column'].lower():
            for metric in plan['metrics']:
                if dim['table'] == metric['table']:
                    signature = build_query_signature(metric['column'], dim['column'])
                    if signature in used_signatures:
                        continue
                    used_signatures.add(signature)
                    sql = f"SELECT {dim['column']}, SUM({metric['column']}) as value FROM {dim['table']} GROUP BY {dim['column']} ORDER BY value DESC LIMIT 5"
                    result = run_query_with_cache(sql, db, used_queries, user_id, session_id)
                    if result is not None:
                        insights += generate_insights('top_performers', result, value_key='value', label_key=dim['column'])
    return insights


def run_churn_detection(
    plan: Dict[str, Any],
    db: Any,
    used_queries: Dict[str, Any],
    used_signatures: set,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """NOT FOR PLAYGROUND: Customer churn risk detection (unstable)"""
    insights = []
    for dim in plan['dimensions']:
        if 'customer' in dim['column'].lower():
            for time in plan['time_columns']:
                if dim['table'] == time['table']:
                    signature = build_query_signature('churn', dim['column'], time['column'])
                    if signature in used_signatures:
                        continue
                    used_signatures.add(signature)
                    sql = f"SELECT {dim['column']}, MAX({time['column']}) as last_active FROM {dim['table']} GROUP BY {dim['column']}"
                    result = run_query_with_cache(sql, db, used_queries, user_id, session_id)
                    if result is not None:
                        insights += generate_insights('top_performers', result, value_key='last_active', label_key=dim['column'])
    return insights


def run_seasonality_detection(
    plan: Dict[str, Any],
    db: Any,
    used_queries: Dict[str, Any],
    used_signatures: set,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """NOT FOR PLAYGROUND: Seasonality pattern detection (unstable)"""
    insights = []
    for metric in plan['metrics']:
        for time in plan['time_columns']:
            if metric['table'] == time['table']:
                signature = build_query_signature(metric['column'], None, time['column'])
                if signature in used_signatures:
                    continue
                used_signatures.add(signature)
                sql = f"SELECT {time['column']}, SUM({metric['column']}) as value FROM {metric['table']} GROUP BY {time['column']} ORDER BY {time['column']}"
                result = run_query_with_cache(sql, db, used_queries, user_id, session_id)
                if result is not None:
                    insights += generate_insights('growth_trend', result, value_key='value', label_key=time['column'])
    return insights


def run_revenue_distribution(
    plan: Dict[str, Any],
    db: Any,
    used_queries: Dict[str, Any],
    used_signatures: set,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """NOT FOR PLAYGROUND: Revenue distribution analysis (unstable)"""
    insights = []
    for metric in plan['metrics']:
        for dim in plan['dimensions']:
            if metric['table'] == dim['table']:
                signature = build_query_signature(metric['column'], dim['column'])
                if signature in used_signatures:
                    continue
                used_signatures.add(signature)
                sql = f"SELECT {dim['column']}, SUM({metric['column']}) as value FROM {dim['table']} GROUP BY {dim['column']}"
                result = run_query_with_cache(sql, db, used_queries, user_id, session_id)
                if result is not None:
                    insights += generate_insights('top_performers', result, value_key='value', label_key=dim['column'])
    return insights


def run_emerging_segments(
    plan: Dict[str, Any],
    db: Any,
    used_queries: Dict[str, Any],
    used_signatures: set,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """NOT FOR PLAYGROUND: Emerging segment growth detection (unstable)"""
    insights = []
    for dim in plan['dimensions']:
        for metric in plan['metrics']:
            for time in plan['time_columns']:
                if dim['table'] == metric['table'] == time['table']:
                    signature = build_query_signature(metric['column'], dim['column'], time['column'])
                    if signature in used_signatures:
                        continue
                    used_signatures.add(signature)
                    sql = f"SELECT {dim['column']}, {time['column']}, SUM({metric['column']}) as value FROM {dim['table']} GROUP BY {dim['column']}, {time['column']}"
                    result = run_query_with_cache(sql, db, used_queries, user_id, session_id)
                    if result is not None:
                        insights += generate_insights('growth_trend', result, value_key='value', label_key=dim['column'])
    return insights


# --- Query Execution with Caching, Cost, and Governance ---

def run_query_with_cache(
    sql: str,
    db: Any,
    used_queries: Dict[str, Any],
    user_id: Optional[str] = None,
    session_id: Optional[str] = None
) -> Optional[List[Dict[str, Any]]]:
    """
    Execute a query with caching and governance checks.
    
    All EMD queries go through VoxCoreEngine to enforce:
    - RBAC checks
    - Cost limits (70+ blocked)
    - Policy evaluation
    - Audit logging
    
    Args:
        sql: SQL query string
        db: Database connection
        used_queries: Cache of already-executed queries
        user_id: User ID (optional, for governance)
        session_id: Session ID (optional, for audit logging)
    
    Returns:
        List of result dicts, or None if query failed/was blocked
    """
    if sql in used_queries:
        return used_queries[sql]
    
    cached = get_cached_result(sql)
    if cached is not None:
        used_queries[sql] = cached
        return cached
    
    # 🔒 GOVERNANCE CHECK via VoxCoreEngine
    if user_id and db:
        try:
            from voxcore.engine.core import get_voxcore
            engine = get_voxcore()
            result = engine.execute_query(
                question="Explain My Data generative query",
                generated_sql=sql,
                platform="postgres",
                user_id=user_id or "system",
                connection=db,
                session_id=session_id,
            )
            if result.success and result.data:
                cache_result(sql, result.data)
                used_queries[sql] = result.data
                return result.data
            elif not result.success:
                # Cost limit exceeded or policy blocked
                print(f"⚠️ EMD query blocked: {result.error}")
                return None
        except Exception as e:
            print(f"Governance check failed: {e}")
            return None
    
    # Fallback: try to execute without governance
    optimized_sql = optimize_query(sql)
    result = None  # Placeholder
    if result is not None:
        cache_result(sql, result)
        used_queries[sql] = result
    return result
