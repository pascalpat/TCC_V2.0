from datetime import datetime
from app import db

class SubcontractorEntry(db.Model):
    __tablename__ = 'subcontractor_entries'

    ################################## Core Fields ###############################################
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Foreign Keys
    subcontractor_id = db.Column(db.Integer, db.ForeignKey('subcontractors.id'), nullable=False)
    project_id       = db.Column(db.Integer, db.ForeignKey('projects.id'),       nullable=False)
    task_id          = db.Column(db.Integer, db.ForeignKey('project_tasks.id'),  nullable=True)
    work_order_id    = db.Column(db.Integer, db.ForeignKey('work_orders.id'),    nullable=True)
    activity_code_id = db.Column(db.Integer, db.ForeignKey('activity_codes.id'), nullable=True)
    status = db.Column(db.Enum('pending', 'in_progress', 'completed', name='entry_progress_status'), default='pending', nullable=True)

    ################################## Additional Fields #########################################
    date               = db.Column(db.Date, nullable=True)
    description        = db.Column(db.Text, nullable=True)
    equipment_hours    = db.Column(db.Float, default=0.0)
    material_cost      = db.Column(db.Float, default=0.0)
    labor_hours        = db.Column(db.Float, default=0.0)
    total_cost         = db.Column(db.Float, default=0.0)
    progress_percentage = db.Column(db.Float, default=0.0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    ################################## Relationships (Optional) ###################################
    activity_code = db.relationship('ActivityCode', back_populates='subcontractor_entries',  foreign_keys='[SubcontractorEntry.activity_code_id]')  # Relates to ActivityCode mo
    subcontractor = db.relationship('Subcontractor', back_populates='subcontractor_entries')
    project       = db.relationship('Project', back_populates='subcontractor_entries')
    #subcontractor_entries = db.relationship('SubcontractorEntry', back_populates='project')
    
    def __repr__(self):
        return f"<SubcontractorEntry id={self.id}, subcontractor_id={self.subcontractor_id}, date={self.date}>"

    def to_dict(self):
        """Convert the SubcontractorEntry instance to a dictionary for JSON serialization."""
        return {
            'id': self.id,
            'date': self.date.isoformat() if self.date else None,
            'subcontractor_name': self.subcontractor.name if self.subcontractor else None,
            'project_id': self.project_id,
            'description': self.description,
            'equipment_hours': self.equipment_hours,
            'material_cost': self.material_cost,
            'labor_hours': self.labor_hours,
            'total_cost': self.total_cost,
            'progress_percentage': self.progress_percentage,
            'activity_code_id': self.activity_code_id,
            'activity_code': self.activity_code.code if self.activity_code else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
