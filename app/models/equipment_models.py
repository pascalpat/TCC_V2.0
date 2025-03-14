from datetime import datetime
from .. import db
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Enum, JSON, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column, validates
from .core_models import Project  # Import the Project class
from .workforce_models import Worker  # Import the Worker class
from .workforce_models import equipment_assignments


class Equipment(db.Model):
    __tablename__ = 'equipment'

    id: Mapped[int] = mapped_column(primary_key=True)
    equipment_id: Mapped[str | None] = mapped_column(db.String(100), unique=True, nullable=True)  # Unique equipment ID
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)  # Equipment name
    serial_number: Mapped[str | None] = mapped_column(db.String(100), unique=True, nullable=True)  # Serial number
    assigned_to: Mapped[str | None] = mapped_column(db.String(100), nullable=True)  # Assigned to user
    assigned_project_id: Mapped[int | None] = mapped_column(db.ForeignKey('projects.id'), nullable=True)  # Assigned project
    maintenance_status = db.Column(db.Enum('operational', 'under_maintenance', 'out_of_service', name='equipment_status_enum'), default='operational')
    #maintenance_status: Mapped[str] = mapped_column(db.Enum('operational', 'under_maintenance', 'out_of_service', name='equipment_status_enum'), default='operational')
    hourly_rate: Mapped[float | None] = mapped_column(nullable=True)  # Hourly rate for usage
    last_maintenance_date: Mapped[datetime | None] = mapped_column(nullable=True)  # Last maintenance date
    next_maintenance_date: Mapped[datetime | None] = mapped_column(nullable=True)  # Next maintenance date

    # Geolocation Fields
    latitude: Mapped[float | None] = mapped_column(nullable=True)  # Geolocation latitude
    longitude: Mapped[float | None] = mapped_column(nullable=True)  # Geolocation longitude

    # IoT Integration Fields
    device_id: Mapped[str | None] = mapped_column(db.String(100), unique=True, nullable=True)  # IoT device ID
    telemetry_data: Mapped[dict | None] = mapped_column(db.JSON, nullable=True)  # Telemetry data in JSON format

    # Metadata
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime | None] = mapped_column(onupdate=datetime.utcnow)

    # Relationships
    project= db.relationship('Project', back_populates='equipment', lazy=True)
    #daily_logs = db.relationship('DailyReportData', back_populates='equipment')
    workers = relationship('Worker', secondary=equipment_assignments, back_populates='equipment', lazy='subquery')
    equipment_entries = db.relationship("EquipmentEntry", back_populates="equipment")
    @validates('hourly_rate')
    def validate_hourly_rate(self, key: str, value: float | None) -> float | None:
        if value is not None and value < 0:
            raise ValueError("Hourly rate cannot be negative.")
        return value



