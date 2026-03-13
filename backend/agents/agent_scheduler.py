"""
backend/agents/agent_scheduler.py

AI Agent Scheduler — runs each agent on its own periodic interval
using a non-blocking asyncio background loop.

Schedules:
  • Risk agent:    every 30 minutes  (security alerting needs to be fast)
  • Insight agent: every 60 minutes
  • Anomaly agent: every 60 minutes
  • Schema agent:  every 6 hours

The scheduler starts 15 seconds after app boot to avoid competing
with server startup I/O, then runs every 5 minutes and dispatches
whichever agents are due.
"""
import asyncio
import logging
import time

from . import insight_agent, anomaly_agent, risk_agent, schema_agent

logger = logging.getLogger(__name__)

# Interval in seconds for each agent
_AGENT_INTERVALS: dict[str, int] = {
    "risk":    1800,    # 30 minutes
    "insight": 3600,    # 1 hour
    "anomaly": 3600,    # 1 hour
    "schema":  21600,   # 6 hours
}

_AGENT_MODULES = {
    "insight": insight_agent,
    "anomaly": anomaly_agent,
    "risk":    risk_agent,
    "schema":  schema_agent,
}

_last_run: dict[str, float] = {}
_scheduler_task: asyncio.Task | None = None


async def _dispatch_due_agents() -> None:
    """Run any agents whose interval has elapsed."""
    now = time.monotonic()
    for name, interval in _AGENT_INTERVALS.items():
        if now - _last_run.get(name, 0.0) >= interval:
            try:
                module = _AGENT_MODULES[name]
                alerts = await asyncio.get_event_loop().run_in_executor(
                    None, module.run
                )
                if alerts:
                    logger.info(
                        f"[AgentScheduler] {name.capitalize()}Agent created "
                        f"{len(alerts)} new alert(s)"
                    )
                _last_run[name] = now
            except Exception as exc:
                logger.warning(f"[AgentScheduler] {name} agent error: {exc}")


async def _scheduler_loop() -> None:
    """Main background loop. Checks for due agents every 5 minutes."""
    logger.info("[AgentScheduler] AI Data Agents starting — waiting for warm-up…")
    await asyncio.sleep(15)  # let the server fully boot first
    logger.info("[AgentScheduler] Running initial agent pass")

    while True:
        await _dispatch_due_agents()
        await asyncio.sleep(300)  # check every 5 minutes


def start() -> None:
    """
    Attach the scheduler loop as an asyncio background task.
    Must be called from inside a running event loop (e.g. FastAPI startup).
    """
    global _scheduler_task
    try:
        loop = asyncio.get_event_loop()
        _scheduler_task = loop.create_task(_scheduler_loop())
        logger.info("[AgentScheduler] Background scheduler task registered")
    except RuntimeError as exc:
        logger.warning(f"[AgentScheduler] Could not start — no event loop: {exc}")


def stop() -> None:
    """Cancel the scheduler task cleanly on shutdown."""
    global _scheduler_task
    if _scheduler_task and not _scheduler_task.done():
        _scheduler_task.cancel()
        logger.info("[AgentScheduler] Scheduler stopped")
