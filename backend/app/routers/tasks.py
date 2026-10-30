import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.task import (
    TaskCreate,
    TaskListResponse,
    TaskResponse,
    TaskUpdate,
)
from app.services import task_service
from app.services.task_service import SortKey, StatusFilter

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

NOT_FOUND = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
)


@router.get("", response_model=TaskListResponse)
def list_tasks(
    status: StatusFilter = Query("all"),
    search: str | None = Query(None, max_length=100),
    sort: SortKey = Query("due_date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tasks, counts = task_service.list_tasks(
        db, current_user.id, status=status, search=search, sort=sort
    )
    return TaskListResponse(tasks=tasks, counts=counts)


@router.post("", response_model=TaskResponse, status_code=201)
def create_task(
    data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return task_service.create_task(db, current_user.id, data)


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: uuid.UUID,
    data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return task_service.update_task(db, current_user.id, task_id, data)
    except task_service.TaskNotFoundError:
        raise HTTPException(status_code=404, detail="Task not found")


@router.delete("/{task_id}", status_code=204)
def delete_task(
    task_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        task_service.delete_task(db, current_user.id, task_id)
    except task_service.TaskNotFoundError:
        raise HTTPException(status_code=404, detail="Task not found")
    return Response(status_code=204)