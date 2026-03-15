"""
VoxCore Query Cost Analyzer (QCA)
Estimates the cost and risk of executing a SQL query before it runs.
"""

def estimate_query_cost(join_count, has_filter, estimated_rows, result_rows):
    """
    Estimate the cost score for a query.
    Args:
        join_count (int): Number of joins in the query
        has_filter (bool): True if query has a WHERE filter on a fact table
        estimated_rows (int): Estimated number of rows scanned
        result_rows (int): Estimated number of rows returned
    Returns:
        int: Cost score (0-100, lower is safer)
    """
    score = 0
    # Join complexity
    score += join_count * 10  # Each join adds 10 points
    # Filter presence
    if not has_filter:
        score += 30  # No filter is high risk
    # Estimated rows scanned
    if estimated_rows > 1000000:
        score += 20  # Large scan
    elif estimated_rows > 100000:
        score += 10  # Moderate scan
    # Estimated result size
    if result_rows > 100000:
        score += 20  # Large result set
    elif result_rows > 10000:
        score += 10  # Moderate result set
    return min(score, 100)

if __name__ == "__main__":
    # Example usage
    cost = estimate_query_cost(
        join_count=3,
        has_filter=False,
        estimated_rows=5000000,
        result_rows=200000
    )
    print("Query Cost Score:", cost)
