"""
Repository for organizations, users, and policies.

Handles multi-tenant data access with proper isolation.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from backend.db.models import Organization, User, Policy
from backend.db.connection_manager import SessionLocal
from backend.middleware import logger

class OrganizationRepository:
	"""Repository for organization operations"""
	
	@staticmethod
	def create_organization(org_id: str, name: str) -> bool:
		"""Create a new organization"""
		try:
			db = SessionLocal()
			org = Organization(id=org_id, name=name)
			db.add(org)
			db.commit()
			db.close()
			return True
		except Exception as e:
			logger.error({"event": "org_create_failed", "org_id": org_id, "error": str(e)})
			return False
	
	@staticmethod
	def get_organization(org_id: str) -> Optional[Dict]:
		"""Get organization by ID"""
		try:
			db = SessionLocal()
			org = db.query(Organization).filter(Organization.id == org_id).first()
			db.close()
			return org.to_dict() if org else None
		except Exception as e:
			logger.error({"event": "org_get_failed", "org_id": org_id, "error": str(e)})
			return None

class UserRepository:
	"""Repository for user operations"""
	
	@staticmethod
	def create_user(user_id: str, org_id: str, email: str, role: str) -> bool:
		"""Create a new user in an organization"""
		try:
			db = SessionLocal()
			user = User(id=user_id, org_id=org_id, email=email, role=role)
			db.add(user)
			db.commit()
			db.close()
			logger.info({"event": "user_created", "user_id": user_id, "org_id": org_id, "role": role})
			return True
		except Exception as e:
			logger.error({"event": "user_create_failed", "user_id": user_id, "error": str(e)})
			return False
	
	@staticmethod
	def get_user(user_id: str) -> Optional[Dict]:
		"""Get user by ID"""
		try:
			db = SessionLocal()
			user = db.query(User).filter(User.id == user_id).first()
			db.close()
			return user.to_dict() if user else None
		except Exception as e:
			logger.error({"event": "user_get_failed", "user_id": user_id, "error": str(e)})
			return None
	
	@staticmethod
	def get_user_by_email(org_id: str, email: str) -> Optional[Dict]:
		"""Get user by org and email"""
		try:
			db = SessionLocal()
			user = db.query(User).filter(
				User.org_id == org_id,
				User.email == email
			).first()
			db.close()
			return user.to_dict() if user else None
		except Exception as e:
			logger.error({"event": "user_email_lookup_failed", "email": email, "error": str(e)})
			return None
	
	@staticmethod
	def get_org_users(org_id: str) -> List[Dict]:
		"""Get all users in an organization"""
		try:
			db = SessionLocal()
			users = db.query(User).filter(User.org_id == org_id).all()
			db.close()
			return [u.to_dict() for u in users]
		except Exception as e:
			logger.error({"event": "org_users_failed", "org_id": org_id, "error": str(e)})
			return []
	
	@staticmethod
	def update_user_role(user_id: str, new_role: str) -> bool:
		"""Update user role"""
		try:
			db = SessionLocal()
			user = db.query(User).filter(User.id == user_id).first()
			if user:
				user.role = new_role
				db.commit()
				logger.info({"event": "user_role_updated", "user_id": user_id, "new_role": new_role})
				db.close()
				return True
			db.close()
			return False
		except Exception as e:
			logger.error({"event": "user_role_update_failed", "user_id": user_id, "error": str(e)})
			return False

class PolicyRepository:
	"""Repository for query execution policies"""
	
	@staticmethod
	def create_policy(
		policy_id: str,
		org_id: str,
		name: str,
		rule_type: str,
		condition: Dict,
		action: str,
		description: str = None
	) -> bool:
		"""Create a new policy for an organization"""
		try:
			db = SessionLocal()
			policy = Policy(
				id=policy_id,
				org_id=org_id,
				name=name,
				description=description,
				rule_type=rule_type,
				condition=condition,
				action=action
			)
			db.add(policy)
			db.commit()
			db.close()
			logger.info({
				"event": "policy_created",
				"policy_id": policy_id,
				"org_id": org_id,
				"rule_type": rule_type,
				"action": action
			})
			return True
		except Exception as e:
			logger.error({"event": "policy_create_failed", "policy_id": policy_id, "error": str(e)})
			return False
	
	@staticmethod
	def get_org_policies(org_id: str, enabled_only: bool = True) -> List[Dict]:
		"""Get all policies for an organization"""
		try:
			db = SessionLocal()
			query = db.query(Policy).filter(Policy.org_id == org_id)
			
			if enabled_only:
				query = query.filter(Policy.enabled == True)
			
			policies = query.all()
			db.close()
			return [p.to_dict() for p in policies]
		except Exception as e:
			logger.error({"event": "org_policies_failed", "org_id": org_id, "error": str(e)})
			return []
	
	@staticmethod
	def get_policy(policy_id: str) -> Optional[Dict]:
		"""Get a specific policy"""
		try:
			db = SessionLocal()
			policy = db.query(Policy).filter(Policy.id == policy_id).first()
			db.close()
			return policy.to_dict() if policy else None
		except Exception as e:
			logger.error({"event": "policy_get_failed", "policy_id": policy_id, "error": str(e)})
			return None
	
	@staticmethod
	def update_policy(policy_id: str, updates: Dict) -> bool:
		"""Update a policy"""
		try:
			db = SessionLocal()
			policy = db.query(Policy).filter(Policy.id == policy_id).first()
			
			if not policy:
				return False
			
			for key, value in updates.items():
				if hasattr(policy, key):
					setattr(policy, key, value)
			
			policy.updated_at = datetime.utcnow()
			db.commit()
			db.close()
			
			logger.info({"event": "policy_updated", "policy_id": policy_id, "updates": list(updates.keys())})
			return True
		except Exception as e:
			logger.error({"event": "policy_update_failed", "policy_id": policy_id, "error": str(e)})
			return False
	
	@staticmethod
	def delete_policy(policy_id: str) -> bool:
		"""Delete a policy"""
		try:
			db = SessionLocal()
			policy = db.query(Policy).filter(Policy.id == policy_id).first()
			
			if policy:
				db.delete(policy)
				db.commit()
				logger.info({"event": "policy_deleted", "policy_id": policy_id})
				db.close()
				return True
			
			db.close()
			return False
		except Exception as e:
			logger.error({"event": "policy_delete_failed", "policy_id": policy_id, "error": str(e)})
			return False
