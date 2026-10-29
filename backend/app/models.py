from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, ForeignKey, JSON, UniqueConstraint
)
from sqlalchemy.orm import relationship
from app.database import Base


def utcnow():
    return datetime.now(timezone.utc)


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, default="")
    created_at = Column(DateTime, default=utcnow)

    series_list = relationship(
        "DrawingSeries", back_populates="project", cascade="all, delete-orphan"
    )


class DrawingSeries(Base):
    __tablename__ = "drawing_series"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    drawing_number = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=utcnow)

    project = relationship("Project", back_populates="series_list")
    versions = relationship(
        "DrawingVersion", back_populates="series",
        order_by="DrawingVersion.version_number.desc()",
        cascade="all, delete-orphan",
    )


class DrawingVersion(Base):
    __tablename__ = "drawing_versions"
    __table_args__ = (
        UniqueConstraint("series_id", "file_hash", name="uq_series_hash"),
    )

    id = Column(Integer, primary_key=True, index=True)
    series_id = Column(Integer, ForeignKey("drawing_series.id"), nullable=False)
    version_number = Column(Integer, nullable=False)
    filename = Column(String(500), nullable=False)
    file_hash = Column(String(64), nullable=False)
    file_path = Column(String(1000), nullable=False)
    file_size = Column(Integer, nullable=False)
    thumbnail_path = Column(String(1000), nullable=True)
    metadata_json = Column(JSON, default=dict)
    change_note = Column(Text, default="")
    tags = Column(JSON, default=list)
    created_at = Column(DateTime, default=utcnow)

    series = relationship("DrawingSeries", back_populates="versions")


class DeletionLog(Base):
    __tablename__ = "deletion_logs"

    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String(50), nullable=False)  # "project" | "series" | "version"
    entity_id = Column(Integer, nullable=False)
    entity_name = Column(String(500), nullable=False)
    entity_data = Column(JSON, default=dict)
    deleted_at = Column(DateTime, default=utcnow)
