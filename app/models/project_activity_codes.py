# app/models/ProjectActivityCode.py

from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Enum,
    DateTime,
    ForeignKey,
    Index,
)
from sqlalchemy.orm import relationship, validates
from .. import db

class ProjectActivityCode(db.Model):
    __tablename__ = 'project_activity_codes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(
        Integer,
        ForeignKey('projects.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    global_id = Column(
        Integer,
        ForeignKey('activity_codes.id', ondelete='SET NULL'),
        nullable=True,
        index=True
    )
    code = Column(String(20), nullable=False, index=True)
    description = Column(Text, nullable=True)
    status = Column(
        Enum('active', 'pending', 'rejected', name='project_activity_code_status'),
        default='pending',
        nullable=False,
        index=True
    )
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # — Relationships —
    project = relationship(
        'Project',
        back_populates='project_activity_codes',
        lazy=True
    )
    global_ref = relationship(
        'ActivityCode',
        back_populates='project_activity_codes',
        lazy=True
    )

    # — Validations —
    @validates('code')
    def validate_code(self, key, value):
        if not value or not value.strip():
            raise ValueError("`code` must not be empty")
        if len(value) > 20:
            raise ValueError("`code` must be at most 20 characters")
        return value.strip()

    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'global_id': self.global_id,
            'code': self.code,
            'description': self.description,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return (
            f"<ProjectActivityCode "
            f"id={self.id} project_id={self.project_id} "
            f"code={self.code!r} status={self.status}>"
        )
