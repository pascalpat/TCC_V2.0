from datetime import datetime
from .. import db



class WorkOrder(db.Model):
    __tablename__ = 'work_orders'

    # Core Fields
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)  # Links to a Project
    sequential_number = db.Column(db.String(10), nullable=False, unique=True)  # Temporary sequential number
    work_order_number = db.Column(db.Integer, db.ForeignKey('work_orders.id'), nullable=True)
    description = db.Column(db.String(255), nullable=False)  # Description of the work order
    subcontractor_id = db.Column(db.Integer, db.ForeignKey('subcontractors.id'), nullable=True)  # Add ForeignKey
    type = db.Column(db.Enum('change_order', 'additional_scope', 'emergency', name='work_order_type_enum'), nullable=False)  # Type of work order
    status = db.Column(db.Enum('open', 'in_progress', 'completed', 'canceled', 'deferred', name='work_order_status_enum'), default='open')  # Status of the work order
    reason = db.Column(db.String(255), nullable=True)  # Reason for the work order
    estimated_cost = db.Column(db.Float, nullable=True)  # Estimated cost
    cumulative_actual_cost = db.Column(db.Float, nullable=True, default=0.0)  # Cumulative actual costs
    progress_percentage = db.Column(db.Float, nullable=True, default=0.0)  # Overall progress
     # new numeric reference
    activity_code_id = db.Column(db.Integer, db.ForeignKey('activity_codes.id'), nullable=True)

    #@property
    #def progress_percentage(self):
    #    total_progress = sum(log.progress_percentage for log in self.daily_logs)
    #    return total_progress / len(self.daily_logs) if self.daily_logs else 0
    
    # Timeline Fields
    start_date = db.Column(db.Date, nullable=True)  # Start date of the work order
    expected_completion_date = db.Column(db.Date, nullable=True)  # Expected completion date

    # Dates for Status Transitions
    requested_date = db.Column(db.Date, nullable=True)  # Date the work order was requested
    approved_date = db.Column(db.Date, nullable=True)  # Date the work order was approved
    completed_date = db.Column(db.Date, nullable=True)  # Date the work order was completed

    # Activity Code Integration
    activity_code = db.Column(db.String(50), nullable=True, unique=True)  # Activity code generated for this work order

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    # Relationships
    project = db.relationship('Project', back_populates='work_orders', lazy=True)
    subcontractor = db.relationship('Subcontractor', back_populates='work_orders', lazy=True)  # Links to Subcontractor
    #work_order = db.relationship('WorkOrder', back_populates='daily_logs')
    #daily_logs = db.relationship('DailyReportData', back_populates='work_order', lazy=True)
    activity_code_rel = db.relationship('ActivityCode', backref='work_orders')
    work_order_entries = db.relationship('WorkOrderEntry', back_populates="work_order")

    def to_dict(self):
        """Serialize the WorkOrder for JSON responses."""
        return {
            'id': self.id,
            'project_id': self.project_id,
            'sequential_number': self.sequential_number,
            'work_order_number': self.work_order_number,
            'description': self.description,
            'subcontractor_id': self.subcontractor_id,
            'type': self.type,
            'status': self.status,
            'reason': self.reason,
            'estimated_cost': self.estimated_cost,
            'cumulative_actual_cost': self.cumulative_actual_cost,
            'activity_code_id': self.activity_code_id,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'expected_completion_date': self.expected_completion_date.isoformat() if self.expected_completion_date else None,
            'requested_date': self.requested_date.isoformat() if self.requested_date else None,
            'approved_date': self.approved_date.isoformat() if self.approved_date else None,
            'completed_date': self.completed_date.isoformat() if self.completed_date else None,
            'activity_code': self.activity_code,
            'progress_percentage': self.progress_percentage,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }