"""
Seed test users for E2E testing (Playwright/Cypress).
This script creates test users that E2E tests can use for authentication.

Usage:
    python scripts/seed_test_users.py
"""

import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.core.security import hash_password
from app.models.user import User


def seed_test_users():
    """Create test users for E2E testing."""
    db: Session = SessionLocal()

    try:
        # Create tables if they don't exist
        Base.metadata.create_all(bind=engine)

        test_users = [
            {
                "email": "test@e2etest.example.com",
                "name": "Test User",
                "password": "TestPassword123!",
                "is_active": True,
            },
            {
                "email": "admin@e2etest.example.com",
                "name": "Admin User",
                "password": "AdminPassword123!",
                "is_active": True,
            },
        ]

        for user_data in test_users:
            # Check if user already exists
            existing_user = db.query(User).filter(User.email == user_data["email"]).first()

            if existing_user:
                print(f"✓ User {user_data['email']} already exists")
                # Update password in case it changed
                existing_user.password = hash_password(user_data["password"])
                existing_user.is_active = True
                db.commit()
                print(f"  → Password updated for {user_data['email']}")
            else:
                # Create new user
                new_user = User(
                    email=user_data["email"],
                    name=user_data["name"],
                    password=hash_password(user_data["password"]),
                    is_active=user_data["is_active"],
                )
                db.add(new_user)
                db.commit()
                print(f"✓ Created user {user_data['email']}")

        print("\n✅ Test users seeded successfully!")
        print("\nTest credentials:")
        print("  Email: test@e2etest.example.com")
        print("  Password: TestPassword123!")
        print("\n  Email: admin@e2etest.example.com")
        print("  Password: AdminPassword123!")

    except Exception as e:
        print(f"❌ Error seeding test users: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_test_users()
