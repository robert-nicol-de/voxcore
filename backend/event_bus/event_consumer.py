from __future__ import annotations

from collections import defaultdict
from typing import Any, Callable

from .event_types import EventType

EventHandler = Callable[[dict[str, Any]], None]


class EventConsumerRegistry:
    """In-process subscription registry for the Data Intelligence Bus."""

    def __init__(self) -> None:
        self._handlers: dict[str, list[EventHandler]] = defaultdict(list)

    def subscribe(self, event_type: EventType, handler: EventHandler) -> None:
        self._handlers[event_type].append(handler)

    def unsubscribe(self, event_type: EventType, handler: EventHandler) -> None:
        handlers = self._handlers.get(event_type, [])
        if handler in handlers:
            handlers.remove(handler)

    def dispatch(self, event: dict[str, Any]) -> None:
        event_type = str(event.get("event_type") or "")
        for handler in list(self._handlers.get(event_type, [])):
            try:
                handler(event)
            except Exception:
                # Consumers should never crash the publisher path.
                continue


registry = EventConsumerRegistry()
