"""
API endpoints for multi-tenant organization and policy management.

Provides REST endpoints for:
- Organization management
- User management with RBAC
- Policy creation and management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uuid
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from backend.middleware import verify_api_key, logger
from backend.db.org_repository import OrganizationRepository, UserRepository, PolicyRepository

# Create router
router = APIRouter(prefix="/api", tags=["Organizations & Policies"])

# ==================
# Request/Response Models
# ==================

class CreateOrganizationRequest(BaseModel):
	org_id: str
	name: str

class OrganizationResponse(BaseModel):
	id: str
	name: str
	created_at: Optional[str]

class CreateUserRequest(BaseModel):
	email: str
	role: str = "analyst"  # admin, analyst, viewer

class UserResponse(BaseModel):
	id: str
	org_id: str
	email: str
	role: str
	created_at: Optional[str]

class UpdateUserRoleRequest(BaseModel):
	user_id: str
	new_role: str

class CreatePolicyRequest(BaseModel):
	name: str
	description: Optional[str]
	rule_type: str  # no_full_scan, max_joins, max_rows, destructive_check
	condition: Dict[str, Any]
	action: str  # block, allow, require_approval

class PolicyResponse(BaseModel):
	id: str
	org_id: str
	name: str
	description: Optional[str]
	rule_type: str
	condition: Dict
	action: str
	enabled: bool
	created_at: Optional[str]

class UpdatePolicyRequest(BaseModel):
	name: Optional[str] = None
	description: Optional[str] = None
	condition: Optional[Dict] = None
	action: Optional[str] = None
	enabled: Optional[bool] = None

# ==================
# Organization Endpoints
# ==================

@router.post("/orgs", response_model=OrganizationResponse)
async def create_organization(
	request: CreateOrganizationRequest,
	x_api_key: str = Depends(verify_api_key)
):
	"""Create a new organization (multi-tenant)"""
	success = OrganizationRepository.create_organization(request.org_id, request.name)
	
	if not success:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="Failed to create organization"
		)
	
	org = OrganizationRepository.get_organization(request.org_id)
	return org

@router.get("/orgs/{org_id}", response_model=OrganizationResponse)
async def get_organization(
	org_id: str,
	x_api_key: str = Depends(verify_api_key)
):
	"""Get organization details"""
	org = OrganizationRepository.get_organization(org_id)
	
	if not org:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail="Organization not found"
		)
	
	return org

# ==================
# User Management Endpoints
# ==================

@router.post("/orgs/{org_id}/users", response_model=UserResponse)
async def create_user(
	org_id: str,
	request: CreateUserRequest,
	x_api_key: str = Depends(verify_api_key)
):
	"""Create a user in an organization"""
	
	# Verify org exists
	org = OrganizationRepository.get_organization(org_id)
	if not org:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail="Organization not found"
		)
	
	# Check role is valid
	if request.role not in ["admin", "analyst", "viewer"]:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="Invalid role. Must be admin, analyst, or viewer"
		)
	
	# Generate user ID
	user_id = f"user_{uuid.uuid4().hex[:12]}"
	
	# Create user
	success = UserRepository.create_user(user_id, org_id, request.email, request.role)
	
	if not success:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="Failed to create user"
		)
	
	user = UserRepository.get_user(user_id)
	logger.info({
		"event": "user_created_via_api",
		"user_id": user_id,
		"org_id": org_id,
		"email": request.email
	})
	
	return user

@router.get("/orgs/{org_id}/users", response_model=List[UserResponse])
async def list_org_users(
	org_id: str,
	x_api_key: str = Depends(verify_api_key)
):
	"""List all users in an organization"""
	
	# Verify org exists
	org = OrganizationRepository.get_organization(org_id)
	if not org:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail="Organization not found"
		)
	
	users = UserRepository.get_org_users(org_id)
	return users

@router.put("/orgs/{org_id}/users/{user_id}/role")
async def update_user_role(
	org_id: str,
	user_id: str,
	request: UpdateUserRoleRequest,
	x_api_key: str = Depends(verify_api_key)
):
	"""Update user role"""
	
	user = UserRepository.get_user(user_id)
	if not user or user["org_id"] != org_id:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail="User not found"
		)
	
	if request.new_role not in ["admin", "analyst", "viewer"]:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="Invalid role"
		)
	
	success = UserRepository.update_user_role(user_id, request.new_role)
	
	if not success:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail="Failed to update role"
		)
	
	logger.info({
		"event": "user_role_updated_via_api",
		"user_id": user_id,
		"new_role": request.new_role
	})
	
	return {"success": True, "message": f"User role updated to {request.new_role}"}

# ==================
# Policy Management Endpoints
# ==================

@router.post("/orgs/{org_id}/policies", response_model=PolicyResponse)
async def create_policy(
	org_id: str,
	request: CreatePolicyRequest,
	x_api_key: str = Depends(verify_api_key)
):
	"""Create a query policy for an organization"""
	
	# Verify org exists
	org = OrganizationRepository.get_organization(org_id)
	if not org:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail="Organization not found"
		)
	
	# Validate policy
	if request.rule_type not in ["no_full_scan", "max_joins", "max_rows", "destructive_check", "no_cross_join"]:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="Invalid rule_type"
		)
	
	if request.action not in ["block", "allow", "require_approval"]:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="Invalid action"
		)
	
	# Generate policy ID
	policy_id = f"pol_{uuid.uuid4().hex[:12]}"
	
	# Create policy
	success = PolicyRepository.create_policy(
		policy_id=policy_id,
		org_id=org_id,
		name=request.name,
		rule_type=request.rule_type,
		condition=request.condition,
		action=request.action,
		description=request.description
	)
	
	if not success:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="Failed to create policy"
		)
	
	policy = PolicyRepository.get_policy(policy_id)
	return policy

@router.get("/orgs/{org_id}/policies", response_model=List[PolicyResponse])
async def list_org_policies(
	org_id: str,
	enabled_only: bool = True,
	x_api_key: str = Depends(verify_api_key)
):
	"""List policies for an organization"""
	
	# Verify org exists
	org = OrganizationRepository.get_organization(org_id)
	if not org:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail="Organization not found"
		)
	
	policies = PolicyRepository.get_org_policies(org_id, enabled_only=enabled_only)
	return policies

@router.get("/orgs/{org_id}/policies/{policy_id}", response_model=PolicyResponse)
async def get_policy(
	org_id: str,
	policy_id: str,
	x_api_key: str = Depends(verify_api_key)
):
	"""Get a specific policy"""
	
	policy = PolicyRepository.get_policy(policy_id)
	
	if not policy or policy["org_id"] != org_id:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail="Policy not found"
		)
	
	return policy

@router.put("/orgs/{org_id}/policies/{policy_id}", response_model=PolicyResponse)
async def update_policy(
	org_id: str,
	policy_id: str,
	request: UpdatePolicyRequest,
	x_api_key: str = Depends(verify_api_key)
):
	"""Update a policy"""
	
	policy = PolicyRepository.get_policy(policy_id)
	if not policy or policy["org_id"] != org_id:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail="Policy not found"
		)
	
	# Build updates
	updates = {}
	if request.name:
		updates["name"] = request.name
	if request.description:
		updates["description"] = request.description
	if request.condition:
		updates["condition"] = request.condition
	if request.action:
		updates["action"] = request.action
	if request.enabled is not None:
		updates["enabled"] = request.enabled
	
	success = PolicyRepository.update_policy(policy_id, updates)
	
	if not success:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail="Failed to update policy"
		)
	
	updated = PolicyRepository.get_policy(policy_id)
	return updated

@router.delete("/orgs/{org_id}/policies/{policy_id}")
async def delete_policy(
	org_id: str,
	policy_id: str,
	x_api_key: str = Depends(verify_api_key)
):
	"""Delete a policy"""
	
	policy = PolicyRepository.get_policy(policy_id)
	if not policy or policy["org_id"] != org_id:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail="Policy not found"
		)
	
	success = PolicyRepository.delete_policy(policy_id)
	
	if not success:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail="Failed to delete policy"
		)
	
	logger.info({
		"event": "policy_deleted_via_api",
		"policy_id": policy_id,
		"org_id": org_id
	})
	
	return {"success": True, "message": "Policy deleted"}
