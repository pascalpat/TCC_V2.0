from datetime import datetime
from .. import db


class Subcontractor(db.Model):
    __tablename__ = 'subcontractors'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True)
    name = db.Column(db.String(255), nullable=False)  # Subcontractor name
    task = db.Column(db.String(255), nullable=True)  # Task or scope of work
    contract_type = db.Column(
        db.Enum('fixed_amount', 'cost_plus_expenses', 'time_and_materials', name='contract_type_enum'),
        nullable=True
    )
    total_contract_value = db.Column(db.Float, nullable=True)  # Fixed contract value
    progress_percentage = db.Column(db.Float, default=0.0)  # Progress for fixed contracts
    payment_status = db.Column(
        db.Enum('pending', 'partial', 'paid', 'overdue', name='subcontractor_payment_status'),
        default='pending'
    )
    payment_terms = db.Column(db.String(255), nullable=True)  # Payment terms or conditions
    last_payment_date = db.Column(db.Date, nullable=True)  # Date of the last payment
    cost_plus_total = db.Column(db.Float, nullable=True, default=0.0)  # Total costs for cost-plus contracts

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    # Relationships
    # project = db.relationship('Project', backref='subcontractors', lazy=True)
    project = db.relationship('Project', back_populates='subcontractors', lazy=True)
    # bill_of_work_entries = db.relationship('BillOfWorkEntry', backref='subcontractor', lazy=True)  # Links to daily tracking
    work_orders = db.relationship('WorkOrder', back_populates='subcontractor', lazy=True)
    # daily_logs = db.relationship('DailyReportData', back_populates='subcontractor')
    subcontractor_entries = db.relationship("SubcontractorEntry", back_populates="subcontractor")

    def __repr__(self):
        return f"<Subcontractor id={self.id} name={self.name}>"

    def to_dict(self):
        """Serialize the Subcontractor instance for JSON responses."""
        return {
            'id': self.id,
            'project_id': self.project_id,
            'name': self.name,
            'task': self.task,
            'contract_type': self.contract_type,
            'total_contract_value': self.total_contract_value,
            'progress_percentage': self.progress_percentage,
            'payment_status': self.payment_status,
            'payment_terms': self.payment_terms,
            'last_payment_date': self.last_payment_date.isoformat() if self.last_payment_date else None,
            'cost_plus_total': self.cost_plus_total,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
