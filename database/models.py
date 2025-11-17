"""
Database models for persistent storage

Supports both in-memory (demo) and SQLite (production) modes.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from enum import Enum


@dataclass
class DBGig:
    """Database model for gig listings"""
    id: str
    platform: str
    title: str
    description: str
    budget_min: Optional[float]
    budget_max: Optional[float]
    hourly_rate: Optional[float]
    project_type: str
    skills_required: List[str]
    client_rating: float
    client_reviews: int
    posted_date: datetime
    deadline: datetime
    proposals_count: int
    url: str
    remote_ok: bool
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class DBUserProfile:
    """Database model for user profiles"""
    profile_id: str
    name: str
    title: str
    hourly_rate_min: float
    hourly_rate_max: float
    location: str = "Remote"
    bio: str = ""
    success_rate: float = 100.0
    total_earnings: float = 0.0
    total_jobs: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class DBApplication:
    """Database model for job applications"""
    application_id: str
    profile_id: str
    gig_id: str
    proposal_text: str
    status: str  # pending, accepted, rejected, withdrawn
    submitted_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    response_date: Optional[datetime] = None
    match_score: float = 0.0
