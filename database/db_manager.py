"""
Database Manager - Handles both in-memory and SQLite storage

Provides a unified interface for data persistence with automatic fallback to in-memory storage.
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
import logging

from .models import DBGig, DBUserProfile, DBApplication

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database operations with automatic SQLite/in-memory fallback"""

    def __init__(self, db_path: Optional[str] = None, use_sqlite: bool = False):
        """
        Initialize database manager

        Args:
            db_path: Path to SQLite database file (default: data/freelance.db)
            use_sqlite: Whether to use SQLite or in-memory storage
        """
        self.use_sqlite = use_sqlite
        self.db_path = db_path or "data/freelance.db"
        self.conn = None

        # In-memory storage (always available as fallback)
        self.memory_gigs: Dict[str, DBGig] = {}
        self.memory_profiles: Dict[str, DBUserProfile] = {}
        self.memory_applications: Dict[str, DBApplication] = {}

        if self.use_sqlite:
            self._init_sqlite()

    def _init_sqlite(self) -> None:
        """Initialize SQLite database with tables"""
        try:
            # Create data directory if it doesn't exist
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row

            # Create tables
            self._create_tables()
            logger.info(f"SQLite database initialized at {self.db_path}")

        except Exception as e:
            logger.warning(f"Failed to initialize SQLite: {e}. Falling back to in-memory storage.")
            self.use_sqlite = False
            self.conn = None

    def _create_tables(self) -> None:
        """Create database tables if they don't exist"""
        if not self.conn:
            return

        cursor = self.conn.cursor()

        # Gigs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gigs (
                id TEXT PRIMARY KEY,
                platform TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                budget_min REAL,
                budget_max REAL,
                hourly_rate REAL,
                project_type TEXT,
                skills_required TEXT,
                client_rating REAL,
                client_reviews INTEGER,
                posted_date TEXT,
                deadline TEXT,
                proposals_count INTEGER,
                url TEXT,
                remote_ok INTEGER,
                is_active INTEGER DEFAULT 1,
                created_at TEXT,
                updated_at TEXT
            )
        """)

        # User profiles table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_profiles (
                profile_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                title TEXT,
                hourly_rate_min REAL,
                hourly_rate_max REAL,
                location TEXT,
                bio TEXT,
                success_rate REAL DEFAULT 100.0,
                total_earnings REAL DEFAULT 0.0,
                total_jobs INTEGER DEFAULT 0,
                created_at TEXT,
                updated_at TEXT
            )
        """)

        # Applications table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS applications (
                application_id TEXT PRIMARY KEY,
                profile_id TEXT NOT NULL,
                gig_id TEXT NOT NULL,
                proposal_text TEXT,
                status TEXT DEFAULT 'pending',
                submitted_at TEXT,
                updated_at TEXT,
                response_date TEXT,
                match_score REAL,
                FOREIGN KEY (profile_id) REFERENCES user_profiles(profile_id),
                FOREIGN KEY (gig_id) REFERENCES gigs(id)
            )
        """)

        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_gigs_platform ON gigs(platform)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_gigs_active ON gigs(is_active)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_applications_profile ON applications(profile_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_applications_gig ON applications(gig_id)")

        self.conn.commit()

    # Gig operations
    def add_gig(self, gig: DBGig) -> bool:
        """Add a gig to the database"""
        if self.use_sqlite and self.conn:
            try:
                cursor = self.conn.cursor()
                cursor.execute("""
                    INSERT INTO gigs VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """, (
                    gig.id, gig.platform, gig.title, gig.description,
                    gig.budget_min, gig.budget_max, gig.hourly_rate,
                    gig.project_type, json.dumps(gig.skills_required),
                    gig.client_rating, gig.client_reviews,
                    gig.posted_date.isoformat(), gig.deadline.isoformat(),
                    gig.proposals_count, gig.url, int(gig.remote_ok),
                    int(gig.is_active), gig.created_at.isoformat(),
                    gig.updated_at.isoformat()
                ))
                self.conn.commit()
                return True
            except Exception as e:
                logger.error(f"Failed to add gig to SQLite: {e}")
                # Fallback to memory
                self.memory_gigs[gig.id] = gig
                return True
        else:
            self.memory_gigs[gig.id] = gig
            return True

    def get_gig(self, gig_id: str) -> Optional[DBGig]:
        """Get a gig by ID"""
        if self.use_sqlite and self.conn:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM gigs WHERE id = ?", (gig_id,))
            row = cursor.fetchone()
            if row:
                return self._row_to_gig(row)

        return self.memory_gigs.get(gig_id)

    def get_all_gigs(self, active_only: bool = True) -> List[DBGig]:
        """Get all gigs"""
        if self.use_sqlite and self.conn:
            cursor = self.conn.cursor()
            if active_only:
                cursor.execute("SELECT * FROM gigs WHERE is_active = 1")
            else:
                cursor.execute("SELECT * FROM gigs")
            return [self._row_to_gig(row) for row in cursor.fetchall()]

        gigs = list(self.memory_gigs.values())
        if active_only:
            gigs = [g for g in gigs if g.is_active]
        return gigs

    # Profile operations
    def add_profile(self, profile: DBUserProfile) -> bool:
        """Add a user profile"""
        if self.use_sqlite and self.conn:
            try:
                cursor = self.conn.cursor()
                cursor.execute("""
                    INSERT INTO user_profiles VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
                """, (
                    profile.profile_id, profile.name, profile.title,
                    profile.hourly_rate_min, profile.hourly_rate_max,
                    profile.location, profile.bio, profile.success_rate,
                    profile.total_earnings, profile.total_jobs,
                    profile.created_at.isoformat(), profile.updated_at.isoformat()
                ))
                self.conn.commit()
                return True
            except Exception as e:
                logger.error(f"Failed to add profile to SQLite: {e}")
                self.memory_profiles[profile.profile_id] = profile
                return True
        else:
            self.memory_profiles[profile.profile_id] = profile
            return True

    def get_profile(self, profile_id: str) -> Optional[DBUserProfile]:
        """Get a user profile by ID"""
        if self.use_sqlite and self.conn:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM user_profiles WHERE profile_id = ?", (profile_id,))
            row = cursor.fetchone()
            if row:
                return self._row_to_profile(row)

        return self.memory_profiles.get(profile_id)

    # Application operations
    def add_application(self, application: DBApplication) -> bool:
        """Add a job application"""
        if self.use_sqlite and self.conn:
            try:
                cursor = self.conn.cursor()
                cursor.execute("""
                    INSERT INTO applications VALUES (?,?,?,?,?,?,?,?,?)
                """, (
                    application.application_id, application.profile_id,
                    application.gig_id, application.proposal_text,
                    application.status, application.submitted_at.isoformat(),
                    application.updated_at.isoformat(),
                    application.response_date.isoformat() if application.response_date else None,
                    application.match_score
                ))
                self.conn.commit()
                return True
            except Exception as e:
                logger.error(f"Failed to add application to SQLite: {e}")
                self.memory_applications[application.application_id] = application
                return True
        else:
            self.memory_applications[application.application_id] = application
            return True

    def get_applications_by_profile(self, profile_id: str) -> List[DBApplication]:
        """Get all applications for a profile"""
        if self.use_sqlite and self.conn:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM applications WHERE profile_id = ?", (profile_id,))
            return [self._row_to_application(row) for row in cursor.fetchall()]

        return [app for app in self.memory_applications.values()
                if app.profile_id == profile_id]

    # Helper methods
    def _row_to_gig(self, row: sqlite3.Row) -> DBGig:
        """Convert database row to DBGig object"""
        return DBGig(
            id=row['id'],
            platform=row['platform'],
            title=row['title'],
            description=row['description'],
            budget_min=row['budget_min'],
            budget_max=row['budget_max'],
            hourly_rate=row['hourly_rate'],
            project_type=row['project_type'],
            skills_required=json.loads(row['skills_required']),
            client_rating=row['client_rating'],
            client_reviews=row['client_reviews'],
            posted_date=datetime.fromisoformat(row['posted_date']),
            deadline=datetime.fromisoformat(row['deadline']),
            proposals_count=row['proposals_count'],
            url=row['url'],
            remote_ok=bool(row['remote_ok']),
            is_active=bool(row['is_active']),
            created_at=datetime.fromisoformat(row['created_at']),
            updated_at=datetime.fromisoformat(row['updated_at'])
        )

    def _row_to_profile(self, row: sqlite3.Row) -> DBUserProfile:
        """Convert database row to DBUserProfile object"""
        return DBUserProfile(
            profile_id=row['profile_id'],
            name=row['name'],
            title=row['title'],
            hourly_rate_min=row['hourly_rate_min'],
            hourly_rate_max=row['hourly_rate_max'],
            location=row['location'],
            bio=row['bio'],
            success_rate=row['success_rate'],
            total_earnings=row['total_earnings'],
            total_jobs=row['total_jobs'],
            created_at=datetime.fromisoformat(row['created_at']),
            updated_at=datetime.fromisoformat(row['updated_at'])
        )

    def _row_to_application(self, row: sqlite3.Row) -> DBApplication:
        """Convert database row to DBApplication object"""
        return DBApplication(
            application_id=row['application_id'],
            profile_id=row['profile_id'],
            gig_id=row['gig_id'],
            proposal_text=row['proposal_text'],
            status=row['status'],
            submitted_at=datetime.fromisoformat(row['submitted_at']),
            updated_at=datetime.fromisoformat(row['updated_at']),
            response_date=datetime.fromisoformat(row['response_date']) if row['response_date'] else None,
            match_score=row['match_score']
        )

    def close(self) -> None:
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
