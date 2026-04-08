
from fastapi import APIRouter, Depends
from backend.db import get_db

from voxcore.security.approval_service import ApprovalService
from voxcore.security.approval_executor import ApprovalExecutor
from voxcore.core import VoxCoreEngine, get_voxcore

router = APIRouter(prefix="/api/approvals", tags=["approvals"])

@router.get("/pending")
def get_pending(conn=Depends(get_db)):
    service = ApprovalService(conn)
    return {"requests": service.list_pending()}


@router.post("/{request_id}/approve")
def approve(request_id: int, conn=Depends(get_db)):
    service = ApprovalService(conn)
    # 1. mark approved
    service.review(request_id, "approved", "admin")
    # 2. fetch request
    request = service.get_by_id(request_id)
    if not request:
        return {"status": "error", "message": "Approval request not found"}
    # 3. execute
    executor = ApprovalExecutor(get_voxcore() if 'get_voxcore' in globals() else VoxCoreEngine())
    result = executor.execute_from_approval(request)
    return {
        "status": "approved",
        "result": result
    }

@router.post("/{request_id}/reject")
def reject(request_id: int, conn=Depends(get_db)):
    service = ApprovalService(conn)
    service.review(request_id, "rejected", "admin")
    return {"status": "rejected"}
