"""Database models for multi-tenant user management."""

import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# SQLite database for user/company management (separate from data warehouses)
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "voxcore_users.db")
DB_URL = f"sqlite:///{os.path.abspath(DB_PATH)}"

engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Company(Base):
    """Companies / tenants table."""
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_name = Column(String(255), nullable=False, unique=True)
    status = Column(String(50), default="active")  # active, suspended, trial
    created_at = Column(DateTime, default=datetime.utcnow)

    users = relationship("User", back_populates="company")

    def to_dict(self):
        return {
            "id": self.id,
            "company_name": self.company_name,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class User(Base):
    """Users table — each user belongs to a company."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), nullable=False, unique=True)
    name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    role = Column(String(50), nullable=False, default="user")  # god, admin, developer, user, viewer
    status = Column(String(50), default="active")  # active, disabled, invited
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    company = relationship("Company", back_populates="users")

    # Role hierarchy for permission checks
    ROLE_HIERARCHY = {
        "god": 100,
        "admin": 80,
        "developer": 60,
        "user": 40,
        "viewer": 20,
    }

    ROLE_LABELS = {
        "god": "God Admin",
        "admin": "Company Admin",
        "developer": "Developer",
        "user": "User",
        "viewer": "Viewer",
    }

    def has_permission(self, required_role: str) -> bool:
        """Check if user has at least the required role level."""
        user_level = self.ROLE_HIERARCHY.get(self.role, 0)
        required_level = self.ROLE_HIERARCHY.get(required_role, 0)
        return user_level >= required_level

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "company_id": self.company_id,
            "company_name": self.company.company_name if self.company else None,
            "role": self.role,
            "role_label": self.ROLE_LABELS.get(self.role, self.role),
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
        }


def init_db():
    """Create tables and seed default data if empty."""
    from passlib.hash import bcrypt

    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Only seed if no companies exist yet
        if db.query(Company).count() == 0:
            # Create default companies
            voxcore = Company(company_name="VoxCore", status="active")
            astutetech = Company(company_name="AstuteTech", status="active")
            democorp = Company(company_name="DemoCorp", status="active")
            db.add_all([voxcore, astutetech, democorp])
            db.flush()  # Get IDs

            # Create default users (password: VoxCore!@#$)
            pw_hash = bcrypt.hash("VoxCore!@#$")
            users = [
                User(
                    email="ico@astutetech.co.za",
                    name="Ico",
                    password_hash=pw_hash,
                    company_id=astutetech.id,
                    role="god",
                ),
                User(
                    email="drikus.dewet@astutetech.co.za",
                    name="Drikus de Wet",
                    password_hash=pw_hash,
                    company_id=astutetech.id,
                    role="god",
                ),
                User(
                    email="admin@voxcore.org",
                    name="VoxCore Admin",
                    password_hash=pw_hash,
                    company_id=voxcore.id,
                    role="admin",
                ),
            ]
            db.add_all(users)
            db.commit()
            print("[MODELS] ✅ Database seeded with default companies and users")
        else:
            print("[MODELS] ✅ User database already initialized")
    except Exception as e:
        db.rollback()
        print(f"[MODELS] ⚠️  Error seeding database: {e}")
    finally:
        db.close()


def get_db():
    """Dependency to get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
