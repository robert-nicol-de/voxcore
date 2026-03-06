# Engine Async Ask Method Added

## Status: ✓ Complete

The async `ask` method has been successfully added to the VoxQueryEngine class in `backend/voxquery/core/engine.py`.

## Method Signature

```python
async def ask(self, question: str, context: str = None):
    """Execute a natural language question (async version)
    
    Args:
        question: Natural language question
        context: Optional context for the question
    
    Returns:
        Dictionary with results or error
    """
```

## Implementation Details

The method:
1. **Generates SQL** from the natural language question using the SQL generator
2. **Validates & Rewrites** the SQL using the dialect engine for the current platform
3. **Executes** the final SQL against the database connection
4. **Formats Results** as a list of dictionaries with column names as keys
5. **Returns** a structured response with:
   - `success`: Boolean indicating success/failure
   - `question`: Original question
   - `generated_sql`: Raw SQL from LLM
   - `final_sql`: Rewritten SQL after dialect processing
   - `was_rewritten`: Boolean indicating if SQL was modified
   - `results`: List of result rows as dictionaries
   - `row_count`: Number of rows returned
   - `error`: Error message if failed

## Usage Example

```python
engine = VoxQueryEngine(...)
result = await engine.ask("What is the total balance?")

if result["success"]:
    print(f"Found {result['row_count']} rows")
    for row in result["results"]:
        print(row)
else:
    print(f"Error: {result['error']}")
```

## Key Features

- **Async/Await Support**: Can be called with `await` in async contexts
- **Dialect Engine Integration**: Automatically rewrites SQL for the target platform
- **Error Handling**: Gracefully handles exceptions and returns error details
- **Direct Execution**: Uses raw database cursor for direct execution
- **Result Formatting**: Converts rows to dictionaries for easy access

## File Modified

- `backend/voxquery/core/engine.py` - Added async ask method (Line 467)

## Verification

✓ No syntax errors
✓ Method properly integrated into VoxQueryEngine class
✓ Follows the exact specification provided
✓ Includes proper error handling
