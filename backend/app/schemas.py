from datetime import datetime
from pydantic import BaseModel, Field


# ── Project ──

class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str = ""


class ProjectOut(BaseModel):
    id: int
    name: str
    description: str
    created_at: datetime
    series_count: int = 0

    model_config = {"from_attributes": True}


# ── DrawingSeries ──

class DrawingSeriesOut(BaseModel):
    id: int
    project_id: int
    drawing_number: str
    created_at: datetime
    latest_version: "DrawingVersionOut | None" = None
    version_count: int = 0

    model_config = {"from_attributes": True}


# ── DrawingVersion ──

class DrawingVersionOut(BaseModel):
    id: int
    series_id: int
    version_number: int
    filename: str
    file_hash: str
    file_size: int
    thumbnail_path: str | None = None
    metadata_json: dict = {}
    change_note: str = ""
    created_at: datetime

    model_config = {"from_attributes": True}


class ChangeNoteUpdate(BaseModel):
    change_note: str


# ── Upload response ──

class UploadResult(BaseModel):
    series_id: int
    version_id: int
    version_number: int
    drawing_number: str
    is_new_series: bool
    filename: str
    file_size: int


# ── Compare ──

class FieldDiff(BaseModel):
    field: str
    label: str
    old_value: str
    new_value: str
    changed: bool


class CompareResult(BaseModel):
    version_new: DrawingVersionOut
    version_old: DrawingVersionOut
    hash_match: bool
    size_diff_percent: float
    diffs: list[FieldDiff]
