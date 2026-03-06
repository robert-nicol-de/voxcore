"""Example usage of VoxQuery"""

from voxquery.core.engine import VoxQueryEngine
from voxquery.formatting.formatter import ResultsFormatter
from voxquery.formatting.charts import ChartGenerator

# Example 1: Simple query with automatic execution
def example_basic_query():
    """Ask a simple question and get results"""
    engine = VoxQueryEngine(
        warehouse_type="snowflake",
        warehouse_host="xy12345.us-east-1.snowflakecomputing.com",
        warehouse_user="your_user",
        warehouse_password="your_password",
        warehouse_database="analytics",
    )
    
    result = engine.ask(
        question="Show top 10 clients by YTD revenue",
        execute=True,
        dry_run=True,
    )
    
    print("Generated SQL:")
    print(result["sql"])
    print(f"\nConfidence: {result['confidence']:.1%}")
    print(f"\nRow count: {result['row_count']}")
    print(f"Execution time: {result['execution_time_ms']:.1f}ms")
    print("\nFirst 5 rows:")
    for row in result["data"][:5]:
        print(row)
    
    engine.close()


# Example 2: Multi-turn conversation
def example_conversation():
    """Maintain context across follow-up questions"""
    engine = VoxQueryEngine()
    
    # First question
    result1 = engine.ask(
        question="Show top 10 clients by YTD revenue",
        execute=True,
    )
    print("Q1: Show top 10 clients by YTD revenue")
    print(f"SQL: {result1['sql']}\n")
    
    # Follow-up - will use conversation context
    result2 = engine.ask(
        question="Now filter to Western Cape only",
        execute=True,
    )
    print("Q2: Now filter to Western Cape only")
    print(f"SQL: {result2['sql']}\n")
    
    # Another follow-up
    result3 = engine.ask(
        question="And exclude cancelled orders",
        execute=True,
    )
    print("Q3: And exclude cancelled orders")
    print(f"SQL: {result3['sql']}\n")
    
    engine.close()


# Example 3: Custom formatting and export
def example_formatting():
    """Format results with type detection and export"""
    engine = VoxQueryEngine()
    
    result = engine.ask(
        question="Monthly revenue by region",
        execute=True,
    )
    
    # Format results
    formatter = ResultsFormatter(default_currency="ZAR")
    formatted = formatter.format_results(
        result["data"],
        format_type="table",
    )
    
    # Export to CSV
    csv = formatter.to_csv(result["data"])
    with open("results.csv", "w") as f:
        f.write(csv)
    print("Exported to results.csv")
    
    # Export to Excel
    excel = formatter.to_excel(result["data"], sheet_name="Monthly Revenue")
    with open("results.xlsx", "wb") as f:
        f.write(excel)
    print("Exported to results.xlsx")
    
    engine.close()


# Example 4: Auto-generated charts
def example_charts():
    """Generate charts from results"""
    engine = VoxQueryEngine()
    
    result = engine.ask(
        question="Top 10 products by sales",
        execute=True,
    )
    
    # Generate chart
    chart_gen = ChartGenerator()
    chart_type = chart_gen.suggest_chart_type(
        result["data"],
        {}  # Columns would be detected by formatter
    )
    
    if chart_type:
        vega_spec = chart_gen.generate_vega_lite(
            data=result["data"],
            title="Top 10 Products by Sales",
            x_axis="product_name",
            y_axis="sales_amount",
            chart_type=chart_type,
        )
        
        # Save spec to file for embedding in dashboard
        import json
        with open("chart.json", "w") as f:
            json.dump(vega_spec, f, indent=2)
        print("Chart spec saved to chart.json")
    
    engine.close()


# Example 5: Schema introspection
def example_schema():
    """Explore available tables and columns"""
    engine = VoxQueryEngine()
    
    schema = engine.get_schema()
    
    print("Available Tables:")
    for table_name, table_info in schema.items():
        print(f"\n{table_name}:")
        if "columns" in table_info:
            for col_name, col_info in table_info["columns"].items():
                print(f"  - {col_name}: {col_info.get('type', 'unknown')}")
    
    engine.close()


# Example 6: Complex financial query
def example_finance_query():
    """Complex financial reporting example"""
    engine = VoxQueryEngine()
    
    result = engine.ask(
        question="Compare Q4 actual vs budget for GL account group 4000, including variance %",
        execute=True,
    )
    
    print("Financial Analysis Query")
    print(f"SQL: {result['sql']}\n")
    
    # Format with auto-currency detection
    formatter = ResultsFormatter(default_currency="ZAR")
    formatted = formatter.format_results(result["data"])
    
    # Print formatted results
    print("Results:")
    for row in formatted["rows"][:10]:
        print(row)
    
    engine.close()


# Example 7: Using specific warehouse
def example_bigquery():
    """Query Google BigQuery"""
    engine = VoxQueryEngine(
        warehouse_type="bigquery",
        warehouse_database="my-project-id",
    )
    
    result = engine.ask(
        question="Show customer lifetime value by cohort",
        execute=True,
    )
    
    print(f"BigQuery Query: {result['sql']}")
    print(f"Execution time: {result['execution_time_ms']}ms")
    
    engine.close()


# Example 8: Error handling
def example_error_handling():
    """Handle errors gracefully"""
    try:
        engine = VoxQueryEngine()
        
        result = engine.ask(
            question="This question is ambiguous and has typos",
            execute=True,
        )
        
        if result.get("error"):
            print(f"Error: {result['error']}")
            print("Suggestions:")
            print("- Be more specific about which table")
            print("- Check spelling of column names")
        else:
            print(result["sql"])
    
    except Exception as e:
        print(f"Exception: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Run examples
    print("=" * 60)
    print("VoxQuery Examples")
    print("=" * 60)
    
    # Uncomment to run:
    # example_basic_query()
    # example_conversation()
    # example_formatting()
    # example_charts()
    # example_schema()
    # example_finance_query()
    # example_bigquery()
    # example_error_handling()
