# app/models/daily_models.py

from uuid import uuid4
from datetime import datetime

from sqlalchemy.dialects.postgresql import UUID
from .. import db


class DailyNote(db.Model):
    __tablename__ = 'daily_notes'

    id              = db.Column(
                         UUID(as_uuid=True),
                         primary_key=True,
                         default=uuid4
                      )
    project_id      = db.Column(
                         db.Integer,
                         db.ForeignKey('projects.id'),
                         nullable=False
                      )
    content         = db.Column(
                         db.Text,
                         nullable=False
                      )
    created_by      = db.Column(
                         db.String(255),
                         nullable=True
                      )
    created_at      = db.Column(
                         db.DateTime,
                         default=datetime.utcnow,
                         nullable=False
                      )

    # Categorization
    category        = db.Column(
                         db.String(50),
                         nullable=True
                      )  # e.g. "Progress", "Issue", "Note générale"
    priority        = db.Column(
                         db.Enum('low', 'medium', 'high', name='note_priority_enum'),
                         default='low',
                         nullable=False
                      )

    # Linking
    linked_activity_code = db.Column(
                              db.Integer,
                              db.ForeignKey('activity_codes.id'),
                              nullable=True
                           )
    work_order_id        = db.Column(
                              db.Integer,
                              db.ForeignKey('work_orders.id'),
                              nullable=True
                           )

    # Attachments
    attachment_url = db.Column(
                         db.String(2083),
                         nullable=True
                      )

    # Permissions
    editable_by    = db.Column(
                         db.String(255),
                         nullable=True
                      )

    # Relationships
    project         = db.relationship('Project', backref='daily_notes', lazy=True)
    activity_code   = db.relationship('ActivityCode', backref='daily_notes', lazy=True)
    work_order      = db.relationship('WorkOrder',   backref='daily_notes', lazy=True)


class DailyPicture(db.Model):
    __tablename__ = 'daily_pictures'

    id             = db.Column(db.Integer, primary_key=True)
    project_id     = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    file_name      = db.Column(db.String(255), nullable=False)
    file_url       = db.Column(db.String(2083), nullable=False)
    description    = db.Column(db.Text, nullable=True)
    taken_at       = db.Column(db.DateTime, nullable=True)
    uploaded_at    = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    activity_code  = db.Column(db.Integer, db.ForeignKey('activity_codes.id'), nullable=True)
    work_order_id  = db.Column(db.Integer, db.ForeignKey('work_orders.id'), nullable=True)
    daily_note_id  = db.Column(db.Integer, db.ForeignKey('daily_notes.id'),   nullable=True)

    coordinates    = db.Column(db.JSON,   nullable=True)
    position       = db.Column(db.String(255), nullable=True)
    size           = db.Column(db.Float, nullable=True)

    tags           = db.Column(db.JSON, nullable=True)  # e.g. ["Safety", "Progress"]
    captured_by    = db.Column(db.String(255), nullable=True)

    project        = db.relationship('Project',       backref='daily_pictures', lazy=True)
    work_order     = db.relationship('WorkOrder',     backref='pictures',       lazy=True)
    daily_note     = db.relationship('DailyNote',     backref='pictures',       lazy=True)
    activity_code_rel = db.relationship('ActivityCode', backref='pictures',      lazy=True)


class WeatherLog(db.Model):
    __tablename__ = 'weather_logs'

    id            = db.Column(db.Integer, primary_key=True)
    project_id    = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    date          = db.Column(db.Date, nullable=False)
    temperature   = db.Column(db.Float, nullable=True)
    humidity      = db.Column(db.Float, nullable=True)
    wind_speed    = db.Column(db.Float, nullable=True)
    description   = db.Column(db.String(255), nullable=True)

    severity              = db.Column(
                               db.Enum('low','medium','high', name='weather_severity_enum'),
                               default='low',
                               nullable=False
                            )
    work_impact           = db.Column(
                               db.Enum('none','partial_delay','full_stop', name='weather_impact_enum'),
                               default='none',
                               nullable=False
                            )
    delay_reason          = db.Column(db.Text, nullable=True)
    hours_lost            = db.Column(db.Float, nullable=True)
    impacted_activity_codes = db.Column(db.JSON, nullable=True)

    api_data             = db.Column(db.JSON, nullable=True)
    trend                = db.Column(db.String(50), nullable=True)
    predicted_hours_lost = db.Column(db.Float, nullable=True)

    project              = db.relationship('Project', backref='weather_logs', lazy=True)
