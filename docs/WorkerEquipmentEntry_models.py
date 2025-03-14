from datetime import datetime
from .. import db  # Assuming `db` is your SQLAlchemy instance
from sqlalchemy.orm import validates  # For field validation (if needed)
from sqlalchemy import Enum  # For defining enumerations
from .workforce_models import Worker  # Replace with the correct path to Worker model
from .equipment_models import Equipment  # Replace with the correct path to Equipment model
from .core_models import Project  # Replace with the correct path to Project model
from .models import ProjectTask  # Replace with the correct path to ProjectTask model
from .core_models import ActivityCode  # Replace with the correct path to ActivityCode model


class WorkerEquipmentEntry(db.Model):
    __tablename__ = 'worker_equipment_entries'

    id = db.Column(db.Integer, primary_key=True)
    worker_id = db.Column(db.Integer, db.ForeignKey('workers.id', ondelete='CASCADE'), nullable=False)  # Links to Worker
    equipment_id = db.Column(db.String(100), db.ForeignKey('equipment.equipment_id', ondelete='SET NULL'), nullable=True)  # Links to Equipment
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False)  # Links to Project
    task_id = db.Column(db.Integer, db.ForeignKey('project_tasks.id', ondelete='SET NULL'), nullable=True)  # Links to Task
    activity_code_id = db.Column(db.Integer, db.ForeignKey('activity_codes.id', ondelete='SET NULL'), nullable=True)  # Links to Activity Code

    worker_hours = db.Column(db.Float, nullable=False)  # Hours worked by the worker
    equipment_hours = db.Column(db.Float, nullable=True, default=0.0)  # Hours the equipment was used
    payment_item = db.Column(db.String(100), nullable=True)  # Payment item ID (linked to ProjectTask)
    notes = db.Column(db.Text, nullable=True)  # Optional notes about the entry

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    # Relationships
    worker = db.relationship('Worker', back_populates='worker_equipment_entries', lazy=True)
    equipment = db.relationship('Equipment', back_populates='worker_equipment_entries', lazy=True)
    project = db.relationship('Project', back_populates='worker_equipment_entries', lazy=True)
    task = db.relationship('ProjectTask', back_populates='worker_equipment_entries', lazy=True)
    activity_code = db.relationship('ActivityCode', back_populates='worker_equipment_entries', lazy=True)

    @validates('worker_hours', 'equipment_hours')
    def validate_hours(self, key, value):
        if value < 0:
            raise ValueError(f"{key} cannot be negative.")
        if key == 'equipment_hours' and self.worker_hours and value > self.worker_hours:
            raise ValueError("Equipment hours cannot exceed worker hours.")
        return value