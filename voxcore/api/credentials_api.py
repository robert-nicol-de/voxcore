from fastapi import APIRouter, Depends
from voxcore.services.credential_service import CredentialService
from voxcore.api.auth import get_current_user

router = APIRouter(prefix="/api/credentials", tags=["credentials"])
service = CredentialService()

@router.post("/")
def store_credentials(req: dict, user=Depends(get_current_user)):
    credential_id = service.store(
        db=req["db"],
        user_id=user["id"],
        connector_type=req["connector_type"],
        config=req["config"]
    )
    return {"credential_id": credential_id}
