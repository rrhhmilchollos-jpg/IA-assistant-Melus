"""
MelusAI Database Schemas
SQLAlchemy models for PostgreSQL
"""
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, 
    Text, JSON, ForeignKey, Index, Enum as SQLEnum
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from enum import Enum
import uuid

from .config import Base


def generate_uuid() -> str:
    """Generate a unique ID"""
    return str(uuid.uuid4())[:12]


def utc_now() -> datetime:
    """Get current UTC time"""
    return datetime.now(timezone.utc)


class SubscriptionTier(str, Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class AuthProvider(str, Enum):
    EMAIL = "email"
    GOOGLE = "google"
    GITHUB = "github"
    FACEBOOK = "facebook"


class ProjectStatus(str, Enum):
    PENDING = "pending"
    PLANNING = "planning"
    GENERATING = "generating"
    COMPLETED = "completed"
    ERROR = "error"


class TransactionStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


# ================== USER MODELS ==================

class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(50), unique=True, default=lambda: f"user_{generate_uuid()}")
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    picture: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    password_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Credits
    credits: Mapped[int] = mapped_column(Integer, default=500)
    credits_used: Mapped[int] = mapped_column(Integer, default=0)
    unlimited_credits: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Role & Subscription
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    is_owner: Mapped[bool] = mapped_column(Boolean, default=False)
    subscription_tier: Mapped[str] = mapped_column(String(50), default=SubscriptionTier.FREE.value)
    
    # Auth
    auth_provider: Mapped[str] = mapped_column(String(50), default=AuthProvider.EMAIL.value)
    session_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    
    # Stripe
    stripe_customer_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            "user_id": self.user_id,
            "email": self.email,
            "name": self.name,
            "picture": self.picture,
            "credits": self.credits,
            "credits_used": self.credits_used,
            "is_admin": self.is_admin,
            "subscription_tier": self.subscription_tier,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class UserSession(Base):
    """User session model"""
    __tablename__ = "user_sessions"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(50), unique=True, default=lambda: f"sess_{generate_uuid()}")
    user_id: Mapped[str] = mapped_column(String(50), ForeignKey("users.user_id", ondelete="CASCADE"))
    session_token: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    
    # Relationships
    user = relationship("User", back_populates="sessions")


class OAuthState(Base):
    """OAuth state for CSRF protection"""
    __tablename__ = "oauth_states"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    state: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    provider: Mapped[str] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


# ================== PROJECT MODELS ==================

class Project(Base):
    """Project model"""
    __tablename__ = "projects"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    project_id: Mapped[str] = mapped_column(String(50), unique=True, default=lambda: f"proj_{generate_uuid()}")
    user_id: Mapped[str] = mapped_column(String(50), ForeignKey("users.user_id", ondelete="CASCADE"), index=True)
    
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    prompt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Generation metadata
    status: Mapped[str] = mapped_column(String(50), default=ProjectStatus.PENDING.value)
    intent_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    template_used: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    complexity: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Files and data
    files: Mapped[Optional[dict]] = mapped_column(JSON, default=list)
    metadata: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)
    agent_results: Mapped[Optional[dict]] = mapped_column(JSON, default=list)
    
    # Credits
    credits_used: Mapped[int] = mapped_column(Integer, default=0)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="projects")
    files_list = relationship("ProjectFile", back_populates="project", cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            "project_id": self.project_id,
            "user_id": self.user_id,
            "name": self.name,
            "description": self.description,
            "prompt": self.prompt,
            "status": self.status,
            "intent_type": self.intent_type,
            "template_used": self.template_used,
            "files_count": len(self.files) if self.files else 0,
            "credits_used": self.credits_used,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class ProjectFile(Base):
    """Project file model"""
    __tablename__ = "project_files"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    file_id: Mapped[str] = mapped_column(String(50), unique=True, default=lambda: f"file_{generate_uuid()}")
    project_id: Mapped[str] = mapped_column(String(50), ForeignKey("projects.project_id", ondelete="CASCADE"), index=True)
    
    path: Mapped[str] = mapped_column(String(500))
    content: Mapped[str] = mapped_column(Text)
    file_type: Mapped[str] = mapped_column(String(50))  # component, page, style, util, etc.
    
    version: Mapped[int] = mapped_column(Integer, default=1)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
    
    # Relationships
    project = relationship("Project", back_populates="files_list")


# ================== BILLING MODELS ==================

class Transaction(Base):
    """Payment transaction model"""
    __tablename__ = "transactions"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    transaction_id: Mapped[str] = mapped_column(String(50), unique=True, default=lambda: f"txn_{generate_uuid()}")
    user_id: Mapped[str] = mapped_column(String(50), ForeignKey("users.user_id", ondelete="CASCADE"), index=True)
    
    # Stripe
    stripe_session_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    stripe_payment_intent: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Transaction details
    amount: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(10), default="usd")
    credits: Mapped[int] = mapped_column(Integer)
    
    package_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    promo_code: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    discount: Mapped[float] = mapped_column(Float, default=0)
    
    # Status
    status: Mapped[str] = mapped_column(String(50), default=TransactionStatus.PENDING.value)
    payment_status: Mapped[str] = mapped_column(String(50), default="unpaid")
    processed: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
    
    # Relationships
    user = relationship("User", back_populates="transactions")


class Subscription(Base):
    """User subscription model"""
    __tablename__ = "subscriptions"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    subscription_id: Mapped[str] = mapped_column(String(50), unique=True, default=lambda: f"sub_{generate_uuid()}")
    user_id: Mapped[str] = mapped_column(String(50), ForeignKey("users.user_id", ondelete="CASCADE"), index=True)
    
    # Stripe
    stripe_subscription_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    stripe_price_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Plan details
    plan_id: Mapped[str] = mapped_column(String(50))
    tier: Mapped[str] = mapped_column(String(50))
    credits_per_month: Mapped[int] = mapped_column(Integer, default=0)
    
    # Status
    status: Mapped[str] = mapped_column(String(50), default="active")
    
    # Timestamps
    current_period_start: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    current_period_end: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    canceled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)


# ================== TEMPLATE MODELS ==================

class Template(Base):
    """Project template model"""
    __tablename__ = "templates"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    template_id: Mapped[str] = mapped_column(String(50), unique=True, default=lambda: f"tpl_{generate_uuid()}")
    
    name: Mapped[str] = mapped_column(String(255))
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Classification
    intent_type: Mapped[str] = mapped_column(String(50), index=True)
    complexity: Mapped[str] = mapped_column(String(50))
    builder: Mapped[str] = mapped_column(String(50))
    
    # Template content
    files: Mapped[dict] = mapped_column(JSON, default=list)
    config: Mapped[dict] = mapped_column(JSON, default=dict)
    
    # Metadata
    tech_stack: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    features: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    preview_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Stats
    usage_count: Mapped[int] = mapped_column(Integer, default=0)
    rating: Mapped[float] = mapped_column(Float, default=0)
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_premium: Mapped[bool] = mapped_column(Boolean, default=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)


# ================== INDEXES ==================

# User indexes
Index("idx_users_email_provider", User.email, User.auth_provider)

# Project indexes
Index("idx_projects_user_status", Project.user_id, Project.status)
Index("idx_projects_intent", Project.intent_type)

# Template indexes
Index("idx_templates_intent_complexity", Template.intent_type, Template.complexity)
