from datetime import datetime
from app import db


class WorkerEntry(db.Model):
    """
    Represents a daily worker entry for tracking labor hours, project details, and activity codes.
    """
    __tablename__ = 'entries_workers'

    ################################## Core Fields ###############################################
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date_of_report = db.Column(db.Date, nullable=False, index=True)  # Date of the report
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)  # FK to Projects
    worker_id = db.Column(db.Integer, db.ForeignKey('workers.id'), nullable=True)  # FK to Workers
    worker_name = db.Column(db.Text, nullable=True) ## Worker name (optional, can be derived from worker_id)
    hours_worked = db.Column(db.Float, nullable=False, default=0.0)  # Hours worked
    status = db.Column(db.Enum('pending', 'in_progress', 'completed', name='entry_status'), default='pending', nullable=True)
    payment_item_id = db.Column(db.Integer, db.ForeignKey('payment_items.id'), nullable=True)  # FK to Payment Items
    
    ################################## Additional Fields ##########################################
    activity_id = db.Column(db.Integer, db.ForeignKey('activity_codes.id'), nullable=True)  # FK to Activity Codes
    cwp = db.Column(db.String(50), nullable=True)  # Construction Work Package
    phase = db.Column(db.String(50), nullable=True)  # Construction phase
    metier = db.Column(db.String(100), nullable=True)
    taux_horaire = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Timestamp for creation
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Last updated timestamp

    ################################## Relationships #############################################
    project = db.relationship('Project', back_populates='worker_entries')  # Relates to Project model
    worker = db.relationship('Worker', back_populates='worker_entries')  # Relates to Worker model
    activity = db.relationship('ActivityCode', back_populates='worker_entries')  # Relates to ActivityCode model
    related_project = db.relationship("Project", back_populates="associated_worker_entries")  # match the other side’s property name
    
    
    def __repr__(self):
        return f"<WorkerEntry id={self.id}, worker_id={self.worker_id}, date={self.date_of_report}>"

    def to_dict(self):
        """
        Convert the WorkerEntry instance to a dictionary for JSON serialization.
        """
        return {
            'id': self.id,
            'date_of_report': self.date_of_report.isoformat(),
            'project_id': self.project_id,
            'worker_id': self.worker_id,
            'hours_worked': self.hours_worked,
            'activity_id': self.activity_id,
            'cwp': self.cwp,
            'phase': self.phase,
            'metier': self.metier,
            'taux_horaire': self.taux_horaire,
            'payment_item_id': self.payment_item_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
