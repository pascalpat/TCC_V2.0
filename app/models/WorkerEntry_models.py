# app/models/WorkerEntry_models.py

from datetime import datetime
from app import db
from app.models.core_models import PaymentItem  # <- import your model here

class WorkerEntry(db.Model):
    """
    Represents a daily worker entry for tracking labor hours, project details, and activity codes.
    """
    __tablename__ = 'entries_workers'

    # ─────────────────────────────────────────────────────────────────────────────
    # Core Fields
    # ─────────────────────────────────────────────────────────────────────────────
    id              = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date_of_report  = db.Column(db.Date,     nullable=False, index=True)
    project_id      = db.Column(db.Integer,  db.ForeignKey('projects.id'),  nullable=False)
    worker_id       = db.Column(db.Integer,  db.ForeignKey('workers.id'),   nullable=True)
    worker_name     = db.Column(db.Text,     nullable=True)
    hours_worked    = db.Column(db.Float,    nullable=False, default=0.0)
    status          = db.Column(
                        db.Enum('pending', 'in_progress', 'completed', name='entry_status'),
                        default='pending',
                        nullable=True
                     )
    payment_item_id = db.Column(db.Integer,  db.ForeignKey('payment_items.id'), nullable=True)

    # ─────────────────────────────────────────────────────────────────────────────
    # Additional Fields
    # ─────────────────────────────────────────────────────────────────────────────
    activity_id     = db.Column(db.Integer,  db.ForeignKey('activity_codes.id'), nullable=True)
    cwp             = db.Column(db.String(50), nullable=True)
    phase           = db.Column(db.String(50), nullable=True)
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at      = db.Column(
                        db.DateTime,
                        default=datetime.utcnow,
                        onupdate=datetime.utcnow
                     )

    # ─────────────────────────────────────────────────────────────────────────────
    # Relationships
    # ─────────────────────────────────────────────────────────────────────────────
    project        = db.relationship('Project',       back_populates='worker_entries')
    worker         = db.relationship('Worker',        back_populates='worker_entries')
    activity       = db.relationship('ActivityCode',  back_populates='worker_entries')

    # New relationship for payment_item via the FK column
    payment_item   = db.relationship('PaymentItem',   back_populates='worker_entries',foreign_keys=[payment_item_id],lazy=True)

    def __repr__(self):
        return f"<WorkerEntry id={self.id}, worker_id={self.worker_id}, date={self.date_of_report}>"

    def to_dict(self):
        """
        Convert the WorkerEntry instance to a dictionary for JSON serialization.
        """
        return {
            'id':                 self.id,
            'date_of_report':     self.date_of_report.isoformat(),
            'project_id':         self.project_id,
            'worker_id':          self.worker_id,
            'hours_worked':       self.hours_worked,
            'status':             self.status,
            'activity_id':        self.activity_id,
            'cwp':                self.cwp,
            'phase':              self.phase,
            'payment_item_id':    self.payment_item_id,
            'created_at':         self.created_at.isoformat(),
            'updated_at':         self.updated_at.isoformat() if self.updated_at else None,
        }
