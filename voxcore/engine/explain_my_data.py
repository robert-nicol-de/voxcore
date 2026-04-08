from voxcore.engine.root_cause_engine import RootCauseEngine

def build_emd_output(insight_text, root_causes):
    primary = root_causes[0] if root_causes else None
    narrative = insight_text
    if primary:
        narrative += (
            f" driven primarily by {primary['value']} "
            f"in {primary['dimension']} "
            f"({primary['contribution']}% contribution)."
        )
    impact = sum(rc["raw_value"] for rc in root_causes[:2])
    recommendations = []
    for rc in root_causes[:2]:
        recommendations.append(
            f"Investigate {rc['value']} in {rc['dimension']}"
        )
    return {
        "insight": insight_text,
        "root_causes": root_causes,
        "impact": round(impact, 2),
        "narrative": narrative,
        "recommendations": recommendations
    }
"""
VoxCore Explain My Data (EMD) Mode
Automated insight discovery engine for datasets.
All queries governed through VoxCoreEngine (cost limits, RBAC, policies).
"""
import numpy as np
## run_reasoning_query import removed: not implemented in sql_reasoning_engine
from voxcore.engine.insight_engine import generate_insights
# from voxcore.engine.query_cost_analyzer import check_query_cost  # Removed: function does not exist
from voxcore.engine.adaptive_query_optimizer import optimize_query
from voxcore.engine.semantic_cache import get_cached_result, cache_result

# --- Insight Discovery Engine ---
def explain_dataset(schema, db, max_insights=10, user_id=None, session_id=None):
    """
    Main entry point for Explain My Data mode.
    Scans schema, plans analysis, runs insight algorithms, returns ranked insights.
    
    All queries are governed through VoxCoreEngine.
    """
    analysis_plan = discover_analysis_plan(schema)
    insights = []
    used_queries = {}
    used_signatures = set()

    # 1. Top Performers
    insights += run_top_performers(analysis_plan, db, used_queries, used_signatures, user_id, session_id)
    # 2. Growth Trends
    insights += run_growth_analysis(analysis_plan, db, used_queries, used_signatures, user_id, session_id)
    # 3. Declining Trends
    insights += run_decline_analysis(analysis_plan, db, used_queries, used_signatures, user_id, session_id)
    # 4. Regional Comparisons
    insights += run_regional_comparison(analysis_plan, db, used_queries, used_signatures, user_id, session_id)
    # 5. Product Rankings
    insights += run_product_rankings(analysis_plan, db, used_queries, used_signatures, user_id, session_id)
    # 6. Anomaly Detection
    insights += run_anomaly_detection(analysis_plan, db, used_queries, used_signatures, user_id, session_id)
    # 7. Customer Churn Risk
    insights += run_churn_detection(analysis_plan, db, used_queries, used_signatures, user_id, session_id)
    # 8. Seasonality Detection
    insights += run_seasonality_detection(analysis_plan, db, used_queries, used_signatures, user_id, session_id)
    # 9. Revenue Distribution
    insights += run_revenue_distribution(analysis_plan, db, used_queries, used_signatures, user_id, session_id)
    # 10. Emerging Growth Segments
    insights += run_emerging_segments(analysis_plan, db, used_queries, used_signatures, user_id, session_id)

    # Rank by score and return top N
    insights = sorted(insights, key=lambda x: x.get("score", 0), reverse=True)
    return insights[:max_insights]

# --- Schema Analysis ---
def discover_analysis_plan(schema):
    """
    Scans schema to identify metrics, dimensions, time columns, relationships.
    Returns a plan dict.
    """
    # Example: schema = {tables: {sales: {...}, customers: {...}}, ...}
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

# --- Insight Algorithms ---
def build_query_signature(metric, dimension=None, time=None):
    return f"{metric}:{dimension or ''}:{time or ''}"

def run_top_performers(plan, db, used_queries, used_signatures, user_id=None, session_id=None):
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
                    insights += generate_insights('top_performers', result, dim, metric)
    return insights

def run_growth_analysis(plan, db, used_queries, used_signatures, user_id=None, session_id=None):
    # Example: Revenue growth over time
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
                    insights += generate_insights('growth_trend', result, time, metric)
    return insights

def run_decline_analysis(plan, db, used_queries, used_signatures, user_id=None, session_id=None):
    # Example: Declining sales, profit, etc.
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
                    insights += generate_insights('decline_trend', result, time, metric)
    return insights

def run_regional_comparison(plan, db, used_queries, used_signatures, user_id=None, session_id=None):
    # Example: Compare regions by revenue
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
                        insights += generate_insights('regional_comparison', result, dim, metric)
    return insights

def run_product_rankings(plan, db, used_queries, used_signatures, user_id=None, session_id=None):
    # Example: Product rankings by sales
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
                        insights += generate_insights('product_ranking', result, dim, metric)
    return insights

def run_anomaly_detection(plan, db, used_queries, used_signatures, user_id=None, session_id=None):
    # Example: Detect spikes/outliers in metrics over time
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
                    insights += generate_insights('anomaly_detection', result, time, metric)
    return insights

def run_churn_detection(plan, db, used_queries, used_signatures, user_id=None, session_id=None):
    # Example: Customers not active in last N days
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
                        insights += generate_insights('churn_risk', result, dim, time)
    return insights

def run_seasonality_detection(plan, db, used_queries, used_signatures, user_id=None, session_id=None):
    # Example: Detect seasonality in metrics
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
                    insights += generate_insights('seasonality', result, time, metric)
    return insights

def run_revenue_distribution(plan, db, used_queries, used_signatures, user_id=None, session_id=None):
    # Example: Revenue distribution across segments
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
                    insights += generate_insights('revenue_distribution', result, dim, metric)
    return insights

def run_emerging_segments(plan, db, used_queries, used_signatures, user_id=None, session_id=None):
    # Example: Find segments with fastest recent growth
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
                        insights += generate_insights('emerging_segment', result, dim, metric, time)
    return insights

# --- Query Execution with Caching, Cost, and Governance ---
def run_query_with_cache(sql, db, used_queries, user_id=None, session_id=None):
    """
    Execute a query with caching and governance checks.
    
    All EMD queries go through VoxCoreEngine to enforce:
    - RBAC checks
    - Cost limits (70+ blocked)
    - Policy evaluation
    - Audit logging
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
