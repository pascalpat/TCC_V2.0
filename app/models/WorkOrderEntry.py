from datetime import datetime
from app import db

class WorkOrderEntry(db.Model):
    __tablename__ = 'work_order_entries'

    # Primary Key
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Foreign Keys
    work_order_id = db.Column(db.Integer, db.ForeignKey('work_orders.id'), nullable=False)
    worker_id     = db.Column(db.Integer, db.ForeignKey('workers.id'),      nullable=True)
    #project_id    = db.Column(db.Integer, db.ForeignKey('projects.id'),     nullable=False)
    task_id       = db.Column(db.Integer, db.ForeignKey('project_tasks.id'), nullable=True)
    activity_code_id = db.Column(db.Integer, db.ForeignKey("activity_codes.id"), nullable=False)

    # Basic Fields
    hours_worked    = db.Column(db.Float, default=0.0)  # or nullable=True
    date            = db.Column(db.Date,  nullable=True)
    description     = db.Column(db.Text,  nullable=True)
    status = db.Column(db.Enum('pending', 'in_progress', 'completed', name='entry_progress_status'), default='pending', nullable=True)

    # Costs
    labor_cost          = db.Column(db.Float, nullable=True, default=0.0)
    equipement_cost     = db.Column(db.Float, nullable=True, default=0.0)
    subcontractor_cost  = db.Column(db.Float, nullable=True, default=0.0)
    service_cost        = db.Column(db.Float, nullable=True, default=0.0)
    total_cost          = db.Column(db.Float, nullable=True, default=0.0)
    progress_percentage = db.Column(db.Float, nullable=True, default=0.0)

    # Timestamps / Auditing
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = db.Column(db.String(50), nullable=True)

    ##########################################################
    # Relationships (optional if you want two-way navigation)
    ##########################################################
    # If you have back_populates on the other side (e.g. in WorkOrder, Worker, etc.):
    work_order = db.relationship('WorkOrder', back_populates='work_order_entries')
    #project    = db.relationship('Project',   back_populates='work_order_entries')
    task       = db.relationship('ProjectTask', back_populates='work_order_entries')
    # worker     = db.relationship('Worker',    back_populates='work_order_entries')
    activity_code = db.relationship("ActivityCode", back_populates="work_order_entries")
    attachments = db.relationship('WorkOrderEntryAttachment', back_populates='entry')

    def __repr__(self):
        return f"<WorkOrderEntry id={self.id}, work_order_id={self.work_order_id}, worker_id={self.worker_id}>"

    def to_dict(self):
        """
        Convert the WorkOrderEntry instance to a dictionary for JSON serialization.
        """
        return {
            'id': self.id,
            'work_order_id': self.work_order_id,
            'worker_id': self.worker_id,
            'hours_worked': self.hours_worked,
            'project_id': self.project_id,
            'task_id': self.task_id,
            'activity_code_id': self.activity_code_id,
            'date': self.date.isoformat() if self.date else None,
            'description': self.description,
            'labor_cost': self.labor_cost,
            'equipement_cost': self.equipement_cost,
            'subcontractor_cost': self.subcontractor_cost,
            'service_cost': self.service_cost,
            'total_cost': self.total_cost,
            'progress_percentage': self.progress_percentage,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'updated_by': self.updated_by,
        }
