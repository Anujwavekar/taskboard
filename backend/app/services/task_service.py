import uuid
from typing import Literal

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.models.task import Task
from app.schemas.task import TaskCounts, TaskCreate, TaskUpdate

StatusFilter = Literal["all", "pending", "completed"]
SortKey = Literal["due_date", "priority"]


class TaskNotFoundError(Exception):
    pass


def _get_owned_task(db: Session, user_id: uuid.UUID, task_id: uuid.UUID) -> Task:
    """The ownership check: match on task id AND owner."""
    task = db.scalar(
        select(Task).where(Task.id == task_id, Task.user_id == user_id)
    )
    if task is None:
        raise TaskNotFoundError()
    return task


def create_task(db: Session, user_id: uuid.UUID, data: TaskCreate) -> Task:
    task = Task(user_id=user_id, **data.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def get_counts(db: Session, user_id: uuid.UUID) -> TaskCounts:
    row = db.execute(
        select(
            func.count(Task.id),
            func.count(Task.id).filter(Task.is_completed.is_(False)),
            func.count(Task.id).filter(Task.is_completed.is_(True)),
        ).where(Task.user_id == user_id)
    ).one()
    return TaskCounts(total=row[0], pending=row[1], completed=row[2])


def list_tasks(
    db: Session,
    user_id: uuid.UUID,
    status: StatusFilter = "all",
    search: str | None = None,
    sort: SortKey = "due_date",
) -> tuple[list[Task], TaskCounts]:
    query = select(Task).where(Task.user_id == user_id)

    if status == "pending":
        query = query.where(Task.is_completed.is_(False))
    elif status == "completed":
        query = query.where(Task.is_completed.is_(True))

    if search and search.strip():
        # autoescape makes "%" and "_" typed by the user match literally
        query = query.where(Task.title.icontains(search.strip(), autoescape=True))

    due_soonest_first = Task.due_date.asc().nulls_last()
    if sort == "priority":
        priority_rank = case(
            {"high": 0, "medium": 1, "low": 2}, value=Task.priority, else_=3
        )
        query = query.order_by(priority_rank, due_soonest_first, Task.created_at.desc())
    else:
        query = query.order_by(due_soonest_first, Task.created_at.desc())

    tasks = list(db.scalars(query).all())
    return tasks, get_counts(db, user_id)


def update_task(
    db: Session, user_id: uuid.UUID, task_id: uuid.UUID, data: TaskUpdate
) -> Task:
    task = _get_owned_task(db, user_id, task_id)
    # Only the fields the client actually sent
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, user_id: uuid.UUID, task_id: uuid.UUID) -> None:
    task = _get_owned_task(db, user_id, task_id)
    db.delete(task)
    db.commit()