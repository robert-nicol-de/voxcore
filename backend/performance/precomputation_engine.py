"""
Precomputation Engine — Run Expensive Queries Before Users Ask

Strategy:
1. Define "common queries" (revenue by region, top products, etc.)
2. Run them every 5-15 minutes
3. Cache results
4. When user asks, results are instant (cache hit)

This is how BI dashboards feel so fast = precomputed aggregations.
"""

from typing import Dict, List, Any, Callable, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import asyncio
import json


@dataclass
class PrecomputeJob:
    """Definition of a query to precompute."""
    job_id: str
    name: str
    description: str
    
    # Query definition
    metric: str  # "revenue", "count", etc.
    aggregation: str  # "sum", "count", "avg"
    dimensions: List[str]  # Group by these
    
    # Scheduling
    interval_minutes: int = 15  # Run every 15 min
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    
    # State
    enabled: bool = True
    is_running: bool = False
    last_error: Optional[str] = None
    
    def should_run(self) -> bool:
        """Check if this job should run now."""
        if not self.enabled:
            return False
        
        if self.is_running:
            return False  # Already running
        
        if self.next_run is None:
            return True  # Never run
        
        return datetime.now() >= self.next_run


class PrecomputationEngine:
    """
    Run expensive queries in the background.
    
    Usage:
    ------
    engine = get_precomputation_engine()
    
    # Define a job
    job = PrecomputeJob(
        job_id="revenue_by_region",
        name="Revenue by Region",
        metric="revenue",
        aggregation="sum",
        dimensions=["region"],
        interval_minutes=15
    )
    engine.register_job(job, query_executor)
    
    # Start background scheduler
    await engine.start()
    
    # Results are cached and served instantly
    """
    
    def __init__(self):
        self.jobs: Dict[str, PrecomputeJob] = {}
        self.executor: Optional[Callable] = None
        self.is_running = False
        self.scheduler_task = None
        self.stats = {
            "total_runs": 0,
            "successful_runs": 0,
            "failed_runs": 0,
            "avg_duration_ms": 0,
        }
    
    def register_job(
        self,
        job: PrecomputeJob,
        executor: Callable,
    ) -> None:
        """
        Register a precomputation job.
        
        Args:
            job: PrecomputeJob definition
            executor: Function to execute query (will be called)
        """
        self.jobs[job.job_id] = job
        self.executor = executor
        
        # Schedule first run
        job.next_run = datetime.now()
    
    async def start(self) -> None:
        """Start the background scheduler."""
        self.is_running = True
        self.scheduler_task = asyncio.create_task(self._scheduler_loop())
    
    async def stop(self) -> None:
        """Stop the background scheduler."""
        self.is_running = False
        if self.scheduler_task:
            self.scheduler_task.cancel()
    
    async def _scheduler_loop(self) -> None:
        """Background task that runs precomputation jobs."""
        while self.is_running:
            try:
                for job in self.jobs.values():
                    if job.should_run():
                        await self._run_job(job)
                
                # Check every 10 seconds
                await asyncio.sleep(10)
            
            except Exception as e:
                print(f"Scheduler error: {e}")
                await asyncio.sleep(10)
    
    async def _run_job(self, job: PrecomputeJob) -> None:
        """Execute a single precomputation job."""
        job.is_running = True
        start_time = datetime.now()
        
        try:
            # Build query
            query = {
                "metric": job.metric,
                "aggregation": job.aggregation,
                "dimensions": job.dimensions,
            }
            
            # Execute
            result = await self.executor(query)
            
            # Calculate timing
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            # Schedule next run
            job.next_run = datetime.now() + timedelta(minutes=job.interval_minutes)
            job.last_run = datetime.now()
            job.last_error = None
            
            # Update stats
            self.stats["total_runs"] += 1
            self.stats["successful_runs"] += 1
            self.stats["avg_duration_ms"] = (
                (self.stats["avg_duration_ms"] * (self.stats["successful_runs"] - 1) + duration_ms)
                / self.stats["successful_runs"]
            )
            
            print(
                f"✅ Precompute job '{job.name}' completed in {duration_ms:.0f}ms"
            )
        
        except Exception as e:
            job.last_error = str(e)
            self.stats["failed_runs"] += 1
            
            print(f"❌ Precompute job '{job.name}' failed: {e}")
        
        finally:
            job.is_running = False
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a precomputation job."""
        job = self.jobs.get(job_id)
        
        if not job:
            return None
        
        return {
            "job_id": job.job_id,
            "name": job.name,
            "enabled": job.enabled,
            "is_running": job.is_running,
            "last_run": job.last_run.isoformat() if job.last_run else None,
            "next_run": job.next_run.isoformat() if job.next_run else None,
            "last_error": job.last_error,
            "interval_minutes": job.interval_minutes,
        }
    
    def list_jobs(self) -> List[Dict[str, Any]]:
        """Get status of all precomputation jobs."""
        return [
            self.get_job_status(job_id)
            for job_id in self.jobs.keys()
        ]
    
    def disable_job(self, job_id: str) -> None:
        """Temporarily disable a job."""
        if job_id in self.jobs:
            self.jobs[job_id].enabled = False
    
    def enable_job(self, job_id: str) -> None:
        """Re-enable a disabled job."""
        if job_id in self.jobs:
            self.jobs[job_id].enabled = True
            self.jobs[job_id].next_run = datetime.now()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get scheduler statistics."""
        return {
            "total_jobs": len(self.jobs),
            "enabled_jobs": sum(1 for j in self.jobs.values() if j.enabled),
            "total_runs": self.stats["total_runs"],
            "successful_runs": self.stats["successful_runs"],
            "failed_runs": self.stats["failed_runs"],
            "avg_duration_ms": round(self.stats["avg_duration_ms"], 2),
        }


# Global instance
_precomputation_engine = None


def get_precomputation_engine() -> PrecomputationEngine:
    """Get or create the global precomputation engine."""
    global _precomputation_engine
    if _precomputation_engine is None:
        _precomputation_engine = PrecomputationEngine()
    return _precomputation_engine


# ============================================================================
# EXAMPLE PRECOMPUTATION JOBS
# ============================================================================
# These are common queries most data analytics users would want precomputed

COMMON_PRECOMPUTE_JOBS = [
    PrecomputeJob(
        job_id="revenue_by_region",
        name="Revenue by Region",
        description="Total revenue grouped by region",
        metric="revenue",
        aggregation="sum",
        dimensions=["region"],
        interval_minutes=15,
    ),
    PrecomputeJob(
        job_id="revenue_by_product",
        name="Revenue by Product",
        description="Total revenue grouped by product",
        metric="revenue",
        aggregation="sum",
        dimensions=["product"],
        interval_minutes=15,
    ),
    PrecomputeJob(
        job_id="top_10_products",
        name="Top 10 Products by Revenue",
        description="Highest-revenue products",
        metric="revenue",
        aggregation="sum",
        dimensions=["product"],
        interval_minutes=30,
    ),
    PrecomputeJob(
        job_id="regional_breakdown",
        name="Regional Breakdown",
        description="Revenue by region and product",
        metric="revenue",
        aggregation="sum",
        dimensions=["region", "product"],
        interval_minutes=30,
    ),
    PrecomputeJob(
        job_id="daily_revenue_trend",
        name="Daily Revenue Trend",
        description="Revenue over time",
        metric="revenue",
        aggregation="sum",
        dimensions=["date"],
        interval_minutes=60,
    ),
]
