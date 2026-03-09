#!/usr/bin/env python3
"""
Add a god-level user account to the VoxCore database.

Usage:
    python add_god_user.py
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from passlib.hash import bcrypt
from voxquery.api.models import Base, User, Company, SessionLocal, engine

# User details
EMAIL = "robert.nicol@voxcore.org"
PASSWORD = "6%=ANA[)E%IlwEv"
NAME = "Robert Nicol"
COMPANY_NAME = "VoxCore"
ROLE = "god"


def add_god_user():
    """Add or update god user in database."""
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == EMAIL).first()
        if existing_user:
            print(f"✓ User {EMAIL} already exists (ID: {existing_user.id})")
            print(f"  Role: {existing_user.role}")
            print(f"  Status: {existing_user.status}")
            return
        
        # Get or create VoxCore company
        company = db.query(Company).filter(Company.company_name == COMPANY_NAME).first()
        if not company:
            print(f"Creating company: {COMPANY_NAME}")
            company = Company(company_name=COMPANY_NAME, status="active")
            db.add(company)
            db.flush()
        
        # Hash password
        password_hash = bcrypt.hash(PASSWORD)
        
        # Create user
        user = User(
            email=EMAIL,
            name=NAME,
            password_hash=password_hash,
            company_id=company.id,
            role=ROLE,
            status="active",
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        print(f"\n✅ God user created successfully!")
        print(f"   Email: {user.email}")
        print(f"   Name: {user.name}")
        print(f"   Role: {user.role}")
        print(f"   Company: {company.company_name}")
        print(f"   Status: {user.status}")
        print(f"   User ID: {user.id}")
        
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        db.rollback()
        return False
    finally:
        db.close()
    
    return True


if __name__ == "__main__":
    success = add_god_user()
    sys.exit(0 if success else 1)
