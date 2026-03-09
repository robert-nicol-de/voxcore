#!/usr/bin/env python3
"""
Add a god-level user account directly to VoxCore SQLite database.
Standalone script without VoxQuery imports to avoid pydantic/langchain conflicts.

Usage:
    python add_god_user_standalone.py
"""

import os
import sys
from datetime import datetime
import bcrypt
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Database setup
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "voxcore_users.db")
DB_URL = f"sqlite:///{os.path.abspath(DB_PATH)}"
engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models
class Company(Base):
    """Companies / tenants table."""
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True, autoincrement=True)
    company_name = Column(String(255), nullable=False, unique=True)
    status = Column(String(50), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    users = relationship("User", back_populates="company")

class User(Base):
    """Users table — each user belongs to a company."""
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), nullable=False, unique=True)
    name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    role = Column(String(50), nullable=False, default="user")
    status = Column(String(50), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    company = relationship("Company", back_populates="users")

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
            return True
        
        # Get or create VoxCore company
        company = db.query(Company).filter(Company.company_name == COMPANY_NAME).first()
        if not company:
            print(f"Creating company: {COMPANY_NAME}")
            company = Company(company_name=COMPANY_NAME, status="active")
            db.add(company)
            db.flush()
        
        # Hash password using bcrypt.hashpw directly
        print(f"Hashing password for {EMAIL}...")
        password_bytes = PASSWORD.encode("utf-8")
        salt = bcrypt.gensalt(rounds=12)
        password_hash_bytes = bcrypt.hashpw(password_bytes, salt)
        password_hash = password_hash_bytes.decode("utf-8")
        
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
        print(f"\n📍 Database: {DB_PATH}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    success = add_god_user()
    sys.exit(0 if success else 1)
