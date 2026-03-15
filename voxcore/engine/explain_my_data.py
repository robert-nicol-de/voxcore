"""
VoxCore Explain My Data (EMD) Mode
Automated insight discovery engine for datasets.
"""
import numpy as np
from voxcore.engine.sql_reasoning_engine import run_reasoning_query
from voxcore.engine.insight_engine import generate_insights
from voxcore.engine.query_cost_analyzer import check_query_cost
from voxcore.engine.adaptive_query_optimizer import optimize_query
from voxcore.engine.semantic_cache import get_cached_result, cache_result

# --- Insight Discovery Engine ---
def explain_dataset(schema, db, max_insights=10):
    """
    Main entry point for Explain My Data mode.
    Scans schema, plans analysis, runs insight algorithms, returns ranked insights.
    """
    analysis_plan = discover_analysis_plan(schema)
    insights = []
    used_queries = {}
    used_signatures = set()

    # 1. Top Performers
    insights += run_top_performers(analysis_plan, db, used_queries, used_signatures)
    # 2. Growth Trends
    insights += run_growth_analysis(analysis_plan, db, used_queries, used_signatures)
    # 3. Declining Trends
    insights += run_decline_analysis(analysis_plan, db, used_queries, used_signatures)
    # 4. Regional Comparisons
    insights += run_regional_comparison(analysis_plan, db, used_queries, used_signatures)
    # 5. Product Rankings
    insights += run_product_rankings(analysis_plan, db, used_queries, used_signatures)
    # 6. Anomaly Detection
    insights += run_anomaly_detection(analysis_plan, db, used_queries, used_signatures)
    # 7. Customer Churn Risk
    insights += run_churn_detection(analysis_plan, db, used_queries, used_signatures)
    # 8. Seasonality Detection
    insights += run_seasonality_detection(analysis_plan, db, used_queries, used_signatures)
    # 9. Revenue Distribution
    insights += run_revenue_distribution(analysis_plan, db, used_queries, used_signatures)
    # 10. Emerging Growth Segments
    insights += run_emerging_segments(analysis_plan, db, used_queries, used_signatures)

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

def run_top_performers(plan, db, used_queries, used_signatures):
    insights = []
    for dim in plan['dimensions']:
        for metric in plan['metrics']:
            if dim['table'] == metric['table']:
                signature = build_query_signature(metric['column'], dim['column'])
                if signature in used_signatures:
                    continue
                used_signatures.add(signature)
                sql = f"SELECT {dim['column']}, SUM({metric['column']}) as value FROM {dim['table']} GROUP BY {dim['column']} ORDER BY value DESC LIMIT 5"
                result = run_query_with_cache(sql, db, used_queries)
                if result is not None:
                    insights += generate_insights('top_performers', result, dim, metric)
    return insights

def run_growth_analysis(plan, db, used_queries, used_signatures):
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
                result = run_query_with_cache(sql, db, used_queries)
                if result is not None:
                    insights += generate_insights('growth_trend', result, time, metric)
    return insights

def run_decline_analysis(plan, db, used_queries, used_signatures):
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
                result = run_query_with_cache(sql, db, used_queries)
                if result is not None:
                    insights += generate_insights('decline_trend', result, time, metric)
    return insights

def run_regional_comparison(plan, db, used_queries, used_signatures):
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
                    result = run_query_with_cache(sql, db, used_queries)
                    if result is not None:
                        insights += generate_insights('regional_comparison', result, dim, metric)
    return insights

def run_product_rankings(plan, db, used_queries, used_signatures):
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
                    result = run_query_with_cache(sql, db, used_queries)
                    if result is not None:
                        insights += generate_insights('product_ranking', result, dim, metric)
    return insights

def run_anomaly_detection(plan, db, used_queries, used_signatures):
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
                result = run_query_with_cache(sql, db, used_queries)
                if result is not None:
                    insights += generate_insights('anomaly_detection', result, time, metric)
    return insights

def run_churn_detection(plan, db, used_queries, used_signatures):
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
                    result = run_query_with_cache(sql, db, used_queries)
                    if result is not None:
                        insights += generate_insights('churn_risk', result, dim, time)
    return insights

def run_seasonality_detection(plan, db, used_queries, used_signatures):
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
                result = run_query_with_cache(sql, db, used_queries)
                if result is not None:
                    insights += generate_insights('seasonality', result, time, metric)
    return insights

def run_revenue_distribution(plan, db, used_queries, used_signatures):
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
                result = run_query_with_cache(sql, db, used_queries)
                if result is not None:
                    insights += generate_insights('revenue_distribution', result, dim, metric)
    return insights

def run_emerging_segments(plan, db, used_queries, used_signatures):
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
                    result = run_query_with_cache(sql, db, used_queries)
                    if result is not None:
                        insights += generate_insights('emerging_segment', result, dim, metric, time)
    return insights

# --- Query Execution with Caching, Cost, and Optimization ---
def run_query_with_cache(sql, db, used_queries):
    if sql in used_queries:
        return used_queries[sql]
    cached = get_cached_result(sql)
    if cached is not None:
        used_queries[sql] = cached
        return cached
    if not check_query_cost(sql):
        return None
    optimized_sql = optimize_query(sql)
    result = run_reasoning_query(optimized_sql, db)
    if result is not None:
        cache_result(sql, result)
        used_queries[sql] = result
    return result
