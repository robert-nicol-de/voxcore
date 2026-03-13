import asyncio
import logging
import os
from typing import Optional

import backend.db.org_store as org_store


logger = logging.getLogger(__name__)
_cleanup_task: Optional[asyncio.Task] = None


def _cleanup_interval_seconds() -> int:
    raw = os.getenv("VOXCORE_PLAYGROUND_CLEANUP_INTERVAL_SECONDS", "600")
    try:
        value = int(raw)
    except ValueError:
        value = 600
    return max(60, min(value, 3600))


async def _cleanup_loop() -> None:
    interval = _cleanup_interval_seconds()
    while True:
        removed_sessions = org_store.cleanup_expired_playground_sessions()
        removed_shares = org_store.cleanup_expired_share_insights()
        if removed_sessions or removed_shares:
            logger.info(
                "Playground cleanup removed sessions=%s shares=%s",
                removed_sessions,
                removed_shares,
            )
        await asyncio.sleep(interval)


def start_cleanup_task() -> None:
    global _cleanup_task
    if _cleanup_task and not _cleanup_task.done():
        return
    _cleanup_task = asyncio.create_task(_cleanup_loop())


async def stop_cleanup_task() -> None:
    global _cleanup_task
    if not _cleanup_task:
        return
    _cleanup_task.cancel()
    try:
        await _cleanup_task
    except asyncio.CancelledError:
        pass
    _cleanup_task = None
