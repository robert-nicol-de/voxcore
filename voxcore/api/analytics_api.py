from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, Query

from backend.services.session_singleton import session_service
from voxcore.models.ranked_analytics import (
    RevenueByCategoryResponse,
    RevenueByCustomerResponse,
    RevenueByProductResponse,
    RevenueByRegionResponse,
    RevenueCategoryDetailResponse,
    RevenueCustomerDetailResponse,
    RevenueProductDetailResponse,
    RevenueRegionDetailResponse,
)
from voxcore.models.revenue_anomalies import (
    RevenueAnomaliesResponse,
    RevenueAnomalyDetailResponse,
)
from voxcore.services.analytics_service import get_analytics_service


router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])


@router.get("/revenue-by-region", response_model=RevenueByRegionResponse)
async def revenue_by_region(session_id: Optional[str] = Query(default=None)) -> Dict[str, Any]:
    """
    Return governed revenue-by-region analytics for the active VoxCore session.
    """
    session = _resolve_session(session_id)
    db_connection = session.get("db")

    if not db_connection or not hasattr(db_connection, "cursor"):
        raise HTTPException(
            status_code=409,
            detail="No live database connection is available for this session.",
        )

    user_id = session.get("user_id") or "anonymous"
    workspace_id = session.get("workspace_id")
    resolved_session_id = session.get("session_id") or session_id or "live-session"

    result = get_analytics_service().get_revenue_by_region(
        db_connection=db_connection,
        session_id=resolved_session_id,
        user_id=user_id,
        workspace_id=workspace_id,
    )

    if not result.get("success"):
        raise HTTPException(
            status_code=400,
            detail=result.get("error", "Failed to load revenue by region analytics"),
        )

    return result


@router.get("/revenue-by-product", response_model=RevenueByProductResponse)
async def revenue_by_product(session_id: Optional[str] = Query(default=None)) -> Dict[str, Any]:
    """Return governed revenue-by-product analytics for the active VoxCore session."""
    session = _resolve_session(session_id)
    db_connection = session.get("db")

    if not db_connection or not hasattr(db_connection, "cursor"):
        raise HTTPException(
            status_code=409,
            detail="No live database connection is available for this session.",
        )

    user_id = session.get("user_id") or "anonymous"
    workspace_id = session.get("workspace_id")
    resolved_session_id = session.get("session_id") or session_id or "live-session"

    result = get_analytics_service().get_revenue_by_product(
        db_connection=db_connection,
        session_id=resolved_session_id,
        user_id=user_id,
        workspace_id=workspace_id,
    )

    if not result.get("success"):
        raise HTTPException(
            status_code=400,
            detail=result.get("error", "Failed to load revenue by product analytics"),
        )

    return result


@router.get("/revenue-by-category", response_model=RevenueByCategoryResponse)
async def revenue_by_category(session_id: Optional[str] = Query(default=None)) -> Dict[str, Any]:
    """Return governed revenue-by-category analytics for the active VoxCore session."""
    session = _resolve_session(session_id)
    db_connection = session.get("db")

    if not db_connection or not hasattr(db_connection, "cursor"):
        raise HTTPException(
            status_code=409,
            detail="No live database connection is available for this session.",
        )

    user_id = session.get("user_id") or "anonymous"
    workspace_id = session.get("workspace_id")
    resolved_session_id = session.get("session_id") or session_id or "live-session"

    result = get_analytics_service().get_revenue_by_category(
        db_connection=db_connection,
        session_id=resolved_session_id,
        user_id=user_id,
        workspace_id=workspace_id,
    )

    if not result.get("success"):
        raise HTTPException(
            status_code=400,
            detail=result.get("error", "Failed to load revenue by category analytics"),
        )

    return result


@router.get("/revenue-by-customer", response_model=RevenueByCustomerResponse)
async def revenue_by_customer(session_id: Optional[str] = Query(default=None)) -> Dict[str, Any]:
    """Return governed revenue-by-customer analytics for the active VoxCore session."""
    session = _resolve_session(session_id)
    db_connection = session.get("db")

    if not db_connection or not hasattr(db_connection, "cursor"):
        raise HTTPException(
            status_code=409,
            detail="No live database connection is available for this session.",
        )

    user_id = session.get("user_id") or "anonymous"
    workspace_id = session.get("workspace_id")
    resolved_session_id = session.get("session_id") or session_id or "live-session"

    result = get_analytics_service().get_revenue_by_customer(
        db_connection=db_connection,
        session_id=resolved_session_id,
        user_id=user_id,
        workspace_id=workspace_id,
    )

    if not result.get("success"):
        raise HTTPException(
            status_code=400,
            detail=result.get("error", "Failed to load revenue by customer analytics"),
        )

    return result


@router.get("/revenue-anomalies", response_model=RevenueAnomaliesResponse)
async def revenue_anomalies(session_id: Optional[str] = Query(default=None)) -> Dict[str, Any]:
    """Return governed revenue anomaly analytics for the active VoxCore session."""
    session = _resolve_session(session_id)
    db_connection = session.get("db")

    if not db_connection or not hasattr(db_connection, "cursor"):
        raise HTTPException(
            status_code=409,
            detail="No live database connection is available for this session.",
        )

    user_id = session.get("user_id") or "anonymous"
    workspace_id = session.get("workspace_id")
    resolved_session_id = session.get("session_id") or session_id or "live-session"

    result = get_analytics_service().get_revenue_anomalies(
        db_connection=db_connection,
        session_id=resolved_session_id,
        user_id=user_id,
        workspace_id=workspace_id,
    )

    if not result.get("success"):
        raise HTTPException(
            status_code=400,
            detail=result.get("error", "Failed to load revenue anomalies"),
        )

    return result


@router.get("/revenue-by-region/{region}", response_model=RevenueRegionDetailResponse)
async def revenue_by_region_detail(
    region: str,
    session_id: Optional[str] = Query(default=None),
) -> Dict[str, Any]:
    """Return governed, aggregate-first region detail for a selected region."""
    session = _resolve_session(session_id)
    db_connection = session.get("db")

    if not db_connection or not hasattr(db_connection, "cursor"):
        raise HTTPException(
            status_code=409,
            detail="No live database connection is available for this session.",
        )

    user_id = session.get("user_id") or "anonymous"
    workspace_id = session.get("workspace_id")
    resolved_session_id = session.get("session_id") or session_id or "live-session"

    result = get_analytics_service().get_revenue_region_detail(
        region=region,
        db_connection=db_connection,
        session_id=resolved_session_id,
        user_id=user_id,
        workspace_id=workspace_id,
    )

    if not result.get("success"):
        raise HTTPException(
            status_code=400,
            detail=result.get("error", "Failed to load region detail analytics"),
        )

    return result


@router.get("/revenue-by-product/{product}", response_model=RevenueProductDetailResponse)
async def revenue_by_product_detail(
    product: str,
    session_id: Optional[str] = Query(default=None),
) -> Dict[str, Any]:
    """Return governed, aggregate-first product detail for a selected product."""
    session = _resolve_session(session_id)
    db_connection = session.get("db")

    if not db_connection or not hasattr(db_connection, "cursor"):
        raise HTTPException(
            status_code=409,
            detail="No live database connection is available for this session.",
        )

    user_id = session.get("user_id") or "anonymous"
    workspace_id = session.get("workspace_id")
    resolved_session_id = session.get("session_id") or session_id or "live-session"

    result = get_analytics_service().get_revenue_product_detail(
        product=product,
        db_connection=db_connection,
        session_id=resolved_session_id,
        user_id=user_id,
        workspace_id=workspace_id,
    )

    if not result.get("success"):
        raise HTTPException(
            status_code=400,
            detail=result.get("error", "Failed to load product detail analytics"),
        )

    return result


@router.get("/revenue-by-category/{category}", response_model=RevenueCategoryDetailResponse)
async def revenue_by_category_detail(
    category: str,
    session_id: Optional[str] = Query(default=None),
) -> Dict[str, Any]:
    """Return governed, aggregate-first category detail for a selected category."""
    session = _resolve_session(session_id)
    db_connection = session.get("db")

    if not db_connection or not hasattr(db_connection, "cursor"):
        raise HTTPException(
            status_code=409,
            detail="No live database connection is available for this session.",
        )

    user_id = session.get("user_id") or "anonymous"
    workspace_id = session.get("workspace_id")
    resolved_session_id = session.get("session_id") or session_id or "live-session"

    result = get_analytics_service().get_revenue_category_detail(
        category=category,
        db_connection=db_connection,
        session_id=resolved_session_id,
        user_id=user_id,
        workspace_id=workspace_id,
    )

    if not result.get("success"):
        raise HTTPException(
            status_code=400,
            detail=result.get("error", "Failed to load category detail analytics"),
        )

    return result


@router.get("/revenue-by-customer/{customer}", response_model=RevenueCustomerDetailResponse)
async def revenue_by_customer_detail(
    customer: str,
    session_id: Optional[str] = Query(default=None),
) -> Dict[str, Any]:
    """Return governed, aggregate-first customer detail for a selected customer."""
    session = _resolve_session(session_id)
    db_connection = session.get("db")

    if not db_connection or not hasattr(db_connection, "cursor"):
        raise HTTPException(
            status_code=409,
            detail="No live database connection is available for this session.",
        )

    user_id = session.get("user_id") or "anonymous"
    workspace_id = session.get("workspace_id")
    resolved_session_id = session.get("session_id") or session_id or "live-session"

    result = get_analytics_service().get_revenue_customer_detail(
        customer=customer,
        db_connection=db_connection,
        session_id=resolved_session_id,
        user_id=user_id,
        workspace_id=workspace_id,
    )

    if not result.get("success"):
        raise HTTPException(
            status_code=400,
            detail=result.get("error", "Failed to load customer detail analytics"),
        )

    return result


@router.get("/revenue-anomalies/{entity}", response_model=RevenueAnomalyDetailResponse)
async def revenue_anomaly_detail(
    entity: str,
    session_id: Optional[str] = Query(default=None),
) -> Dict[str, Any]:
    """Return governed, aggregate-first anomaly detail for a selected entity."""
    session = _resolve_session(session_id)
    db_connection = session.get("db")

    if not db_connection or not hasattr(db_connection, "cursor"):
        raise HTTPException(
            status_code=409,
            detail="No live database connection is available for this session.",
        )

    user_id = session.get("user_id") or "anonymous"
    workspace_id = session.get("workspace_id")
    resolved_session_id = session.get("session_id") or session_id or "live-session"

    result = get_analytics_service().get_revenue_anomaly_detail(
        entity=entity,
        db_connection=db_connection,
        session_id=resolved_session_id,
        user_id=user_id,
        workspace_id=workspace_id,
    )

    if not result.get("success"):
        raise HTTPException(
            status_code=400,
            detail=result.get("error", "Failed to load anomaly detail analytics"),
        )

    return result


def _resolve_session(session_id: Optional[str]) -> Dict[str, Any]:
    if session_id:
        session = session_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found or expired.")
        session["session_id"] = session_id
        return session

    created_session_id, session = session_service.get_or_create_session(mode="live")
    session["session_id"] = created_session_id
    return session
