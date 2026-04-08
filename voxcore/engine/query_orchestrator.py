from voxcore.engine.query_audit import create_audit, finalize_audit
"""
VoxCore Distributed Query Orchestrator (DQO)
Manages parallel execution of all analytics tasks with priority support.
"""
from concurrent.futures import ThreadPoolExecutor, Future
from queue import PriorityQueue
import threading
import enum

# --- Priority Levels ---
class QueryPriority(enum.IntEnum):
    HIGH = 0      # User queries
    MEDIUM = 1    # Exploration queries
    LOW = 2       # Proactive insights

# --- ThreadPool and Priority Queue ---
executor = ThreadPoolExecutor(max_workers=20)
_task_queue = PriorityQueue()

# --- Worker Thread to Pull from Priority Queue ---
def _worker():
    while True:
        priority, count, func, args, kwargs, future = _task_queue.get()
        if future.set_running_or_notify_cancel():
            try:
                result = func(*args, **kwargs)
                future.set_result(result)
            except Exception as e:
                future.set_exception(e)
        _task_queue.task_done()

_thread = threading.Thread(target=_worker, daemon=True)
_thread.start()

_task_counter = 0
_task_counter_lock = threading.Lock()

# --- Public API: Job Submission ---
def submit_query_task(func, *args, priority=QueryPriority.HIGH, **kwargs):
    """
    Submit a query task to be executed asynchronously.
    
    Returns a Future object that can be used to check status or get results.
    
    Args:
        func: Function to execute
        *args: Positional arguments to func
        priority: QueryPriority.HIGH (user), MEDIUM (exploration), LOW (insights)
        **kwargs: Keyword arguments to func
        
    Returns:
        Future object with .result() method
    """
    global _task_counter
    with _task_counter_lock:
        count = _task_counter
        _task_counter += 1
    future = Future()
    _task_queue.put((priority, count, func, args, kwargs, future))
    return future


def submit_query_job(question, sql, db_connection, user_id, session_id, workspace_id=None, priority=QueryPriority.HIGH):
    """
    Submit a query job to the orchestrator.
    
    This is the main entry point for async query execution.
    Returns immediately with a job_id.
    
    Args:
        question: User's natural language question
        sql: Generated SQL
        db_connection: Database connection
        user_id: User ID
        session_id: Session ID
        workspace_id: Workspace ID
        priority: QueryPriority
        
    Returns:
        job_id (str) - use to poll /api/jobs/{job_id}
    """
    from backend.services.query_job_queue import enqueue_query_job, mark_job_running
    
    # 1. Create job in queue
    payload = {
        "question": question,
        "sql": sql,
        "user_id": user_id,
        "session_id": session_id,
        "workspace_id": workspace_id,
        "platform": "postgres",  # TODO: make dynamic
    }
    
    job_id = enqueue_query_job(payload)
    
    # 2. Submit execution to thread pool
    def _execute_query_job():
        try:
            from voxcore.engine.core import get_voxcore
            from backend.services.query_job_queue import (
                mark_job_running,
                mark_job_completed,
                mark_job_failed,
                mark_job_blocked,
            )
            
            mark_job_running(job_id)
            
            engine = get_voxcore()
            result = engine.execute_query(
                question=question,
                generated_sql=sql,
                platform="postgres",
                user_id=user_id,
                connection=db_connection,
                session_id=session_id,
                workspace_id=workspace_id,
            )
            
            if result.success:
                mark_job_completed(job_id, {
                    "data": result.data,
                    "cost_score": result.cost_score,
                    "cost_level": result.cost_level,
                    "warnings": result.warnings or [],
                })
            else:
                # Policy blocked or cost exceeded
                mark_job_blocked(job_id, {
                    "error": result.error,
                    "cost_score": result.cost_score,
                    "cost_level": result.cost_level,
                })
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Query job {job_id} failed: {e}")
            
            from backend.services.query_job_queue import mark_job_failed
            mark_job_failed(job_id, str(e))
    
    # 3. Submit to thread pool
    submit_query_task(_execute_query_job, priority=priority)
    
    return job_id


# --- Internal: Legacy pipeline entry point ---
def run(message, schema, connection_id=None, schema_trust=None):

    # Step 1 — Learning: import and suggest tables
    from voxcore.learning.query_learning_engine import suggest_tables
    from voxcore.learning.query_learning_store import save_learning_entry
    suggested_tables = suggest_tables(message)

    # Step 2 — Initialize audit
    audit = create_audit(message)

    # Step 3 — Inject into pipeline (safe)
    try:
        from voxcore.engine.query_pipeline import QueryPipeline
        pipeline = QueryPipeline(db_path=connection_id or "")
        pipeline_result = pipeline.run(
            session_id=connection_id or "",
            message=message,
            audit=audit,
            schema=schema,
            schema_trust=schema_trust,
            suggested_tables=suggested_tables
        )
    except Exception as e:
        audit["warnings"].append(f"Pipeline error: {str(e)}")
        return {
            "message": "Failed to process query",
            "data": {},
            "audit": audit,
            "schema_trust": schema_trust
        }

    # Step 4 — Enforce minimum audit quality
    if not audit["reasoning"]:
        audit["warnings"].append("No reasoning generated")
    if not audit["selectedTables"]:
        audit["warnings"].append("No tables selected")

    # Step 5 — Anti-hallucination guard
    valid_tables = []
    if schema and "tables" in schema:
        tables = schema["tables"]
        if isinstance(tables, dict):
            valid_tables = list(tables.keys())
        elif isinstance(tables, list):
            valid_tables = [t["name"] for t in tables if isinstance(t, dict) and "name" in t]
    invalid_refs = [t for t in audit["selectedTables"] if t not in valid_tables]
    if invalid_refs:
        audit["warnings"].append(f"Invalid table references: {invalid_refs}")

    # Step 6 — Dynamic confidence
    confidence = min(
        1.0,
        (
            (len(audit["selectedTables"]) * 0.3) +
            (len(audit["reasoning"]) * 0.2) +
            (schema_trust["score"] * 0.5)
        )
    )
    audit = finalize_audit(audit, confidence=confidence)

    # Step 7 — Save learning entry
    save_learning_entry({
        "query": message,
        "selectedTables": audit["selectedTables"],
        "confidence": audit["confidence"],
        "schemaHash": str(hash(str(schema))),
        "success": len(audit["warnings"]) == 0
    })

    # Step 8 — Always return full contract
    return {
        "message": pipeline_result.get("message"),
        "data": pipeline_result.get("data"),
        "audit": audit,
        "schema_trust": schema_trust
    }
    """
    Submit a function to be executed in the background with a given priority.
    Returns a Future object.
    """
    global _task_counter
    with _task_counter_lock:
        count = _task_counter
        _task_counter += 1
    future = Future()
    _task_queue.put((priority, count, func, args, kwargs, future))
    return future

# Example usage:
# from voxcore.engine.query_orchestrator import submit_query_task, QueryPriority
# future = submit_query_task(execute_sql_pipeline, sql_query, metadata, db_connection, priority=QueryPriority.HIGH)
# result = future.result()
