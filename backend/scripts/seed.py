from datetime import date, timedelta

from sqlalchemy import delete, select

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.task import Task
from app.models.user import User

DEMO_NAME = "Demo User"
DEMO_EMAIL = "demo@taskboard.com"
DEMO_PASSWORD = "Demo@123"


def build_tasks(today: date) -> list[dict]:
    return [
        {
            "title": "Prepare client demo slides",
            "description": "Include the Q3 numbers and the product roadmap.",
            "priority": "high",
            "due_date": today + timedelta(days=3),
            "is_completed": False,
        },
        {
            "title": "Pay electricity bill",
            "priority": "medium",
            "due_date": today - timedelta(days=5),  # overdue
            "is_completed": False,
        },
        {
            "title": "Book dentist appointment",
            "priority": "low",
            "due_date": today + timedelta(days=7),
            "is_completed": False,
        },
        {
            "title": "Send weekly report",
            "priority": "medium",
            "due_date": today - timedelta(days=2),  # past date, but completed
            "is_completed": True,
        },
        {
            "title": "Buy groceries",
            "priority": "low",
            "due_date": None,
            "is_completed": False,
        },
        {
            "title": "Plan weekend trip",
            "priority": "medium",
            "due_date": None,
            "is_completed": False,
        },
    ]


def main() -> None:
    db = SessionLocal()
    try:
        user = db.scalar(select(User).where(User.email == DEMO_EMAIL))
        if user is None:
            user = User(
                name=DEMO_NAME,
                email=DEMO_EMAIL,
                password_hash=hash_password(DEMO_PASSWORD),
            )
            db.add(user)
            db.flush()  # assigns user.id
            print("Created demo user")
        else:
            user.name = DEMO_NAME
            user.password_hash = hash_password(DEMO_PASSWORD)
            db.execute(delete(Task).where(Task.user_id == user.id))
            print("Demo user exists: password reset, old tasks removed")

        for data in build_tasks(date.today()):
            db.add(Task(user_id=user.id, **data))

        db.commit()
        print(f"Seeded 6 tasks for {DEMO_EMAIL}")
    finally:
        db.close()


if __name__ == "__main__":
    main()