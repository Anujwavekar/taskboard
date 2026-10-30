import uuid
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

Priority = Literal["low", "medium", "high"]


def _clean_title(value: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError("Title is required")
    return value


def _clean_description(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    return value or None


class TaskCreate(BaseModel):
    title: str = Field(max_length=150)
    description: str | None = Field(default=None, max_length=2000)
    priority: Priority = "medium"
    due_date: date | None = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        return _clean_title(value)

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str | None) -> str | None:
        return _clean_description(value)


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=150)
    description: str | None = Field(default=None, max_length=2000)
    priority: Priority | None = None
    due_date: date | None = None
    is_completed: bool | None = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return _clean_title(value)

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str | None) -> str | None:
        return _clean_description(value)

    @model_validator(mode="after")
    def reject_null_required_fields(self):
        # Fields the client explicitly sent as null
        for name in ("title", "priority", "is_completed"):
            if name in self.model_fields_set and getattr(self, name) is None:
                raise ValueError(f"{name} cannot be null")
        return self


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    description: str | None
    priority: str
    due_date: date | None
    is_completed: bool
    created_at: datetime
    updated_at: datetime


class TaskCounts(BaseModel):
    total: int
    pending: int
    completed: int


class TaskListResponse(BaseModel):
    tasks: list[TaskResponse]
    counts: TaskCounts