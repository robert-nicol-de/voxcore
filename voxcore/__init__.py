"""VoxCore - SQL Governance & Validation Engine
Unified platform for SQL governance, validation, and multi-platform support
"""

from voxcore.core import (
    VoxCoreEngine,
    ExecutionLog,
    ExecutionStatus,
    ValidationResult,
    get_voxcore,
)

__version__ = "1.0.0"
__all__ = [
    "VoxCoreEngine",
    "ExecutionLog",
    "ExecutionStatus",
    "ValidationResult",
    "get_voxcore",
]
