from datetime import datetime
from .. import db
from ..models.workforce_models import WorkerEntry, Worker
from .material_models import MaterialEntry
from .equipment_models import EquipmentEntry
from .subcontractor_models import SubcontractorEntry
from .work_orders_models import WorkOrderEntry


class DailySummary(db.Model):
    __tablename__ = 'daily_summaries'
    
    # Core Fields
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)  # Links to Project
    task_id = db.Column(db.Integer, db.ForeignKey('project_tasks.id'), nullable=True)  # Links to Task
    activity_code_id = db.Column(db.Integer, db.ForeignKey('activity_codes.id'), nullable=True)  # Links to Activity Code
    date = db.Column(db.Date, nullable=False, index=True)  # Date of the summary

    # Cost Breakdown
    labor_cost = db.Column(db.Float, nullable=False, default=0.0)  # Labor costs
    material_cost = db.Column(db.Float, nullable=False, default=0.0)  # Material costs
    equipment_cost = db.Column(db.Float, nullable=False, default=0.0)  # Equipment costs
    subcontractor_cost = db.Column(db.Float, nullable=False, default=0.0)  # Subcontractor costs
    work_order_cost = db.Column(db.Float, nullable=False, default=0.0)  # Work order costs
    total_cost = db.Column(db.Float, nullable=False, default=0.0)  # Total cost

    # Resource-Level Metrics
    total_man_hours = db.Column(db.Float, nullable=True, default=0.0)  # Total hours worked by all workers
    total_equipment_hours = db.Column(db.Float, nullable=True, default=0.0)  # Total hours of equipment usage

    # Tags for Grouping
    phase = db.Column(db.String(100), nullable=True)  # Phase of construction (e.g., "Excavation")
    sector = db.Column(db.String(100), nullable=True)  # Sector or location (e.g., "North Wing")
    miscellaneous_tag = db.Column(db.String(100), nullable=True)  # Free-form tag for ad hoc grouping

    # Status and Metadata
    status = db.Column(
        db.Enum('pending', 'in_review', 'approved', name='daily_summary_status_enum'),
        default='pending'
    )  # Status of the summary
    created_by = db.Column(db.String(255), nullable=True)  # User who created the summary
    approved_by = db.Column(db.String(255), nullable=True)  # User who approved the summary

    # Relationships
    project = db.relationship('Project', backref='related_daily_summaries', lazy=True)  # Links to Project
    task = db.relationship('ProjectTask', backref='daily_summaries', lazy=True)  # Links to Task
    activity_code = db.relationship('ActivityCode', backref='daily_summaries', lazy=True)  # Links to Activity Code

    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Timestamp for creation
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)  # Timestamp for last update

    @staticmethod
    def calculate_daily_summary(project_id, date, task_id=None, activity_code_id=None):
        """
        Calculate the daily summary metrics at the task level and save to the database.
        """
        filters = [
            WorkerEntry.project_id == project_id,
            WorkerEntry.date == date
        ]
        if task_id:
            filters.append(WorkerEntry.task_id == task_id)
        if activity_code_id:
            filters.append(WorkerEntry.activity_code_id == activity_code_id)

        # Labor cost
        labor_cost = db.session.query(db.func.sum(WorkerEntry.labor_hours * Worker.taux_horaire)).filter(*filters).scalar() or 0.0

        # Material cost
        material_cost = db.session.query(db.func.sum(MaterialEntry.cost)).filter(
            MaterialEntry.project_id == project_id,
            MaterialEntry.date == date
        ).scalar() or 0.0

        # Equipment cost
        equipment_cost = db.session.query(db.func.sum(EquipmentEntry.cost)).filter(
            EquipmentEntry.project_id == project_id,
            EquipmentEntry.date == date
        ).scalar() or 0.0

        # Subcontractor cost
        subcontractor_cost = db.session.query(db.func.sum(SubcontractorEntry.cost)).filter(
            SubcontractorEntry.project_id == project_id,
            SubcontractorEntry.date == date
        ).scalar() or 0.0

        # Work order cost
        work_order_cost = db.session.query(db.func.sum(WorkOrderEntry.total_cost)).filter(
            WorkOrderEntry.project_id == project_id,
            WorkOrderEntry.date == date
        ).scalar() or 0.0

        # Total hours
        total_man_hours = db.session.query(db.func.sum(WorkerEntry.labor_hours)).filter(*filters).scalar() or 0.0
        total_equipment_hours = db.session.query(db.func.sum(EquipmentEntry.hours_used)).filter(
            EquipmentEntry.project_id == project_id,
            EquipmentEntry.date == date
        ).scalar() or 0.0

        # Total cost
        total_cost = labor_cost + material_cost + equipment_cost + subcontractor_cost + work_order_cost

        return DailySummary(
            project_id=project_id,
            task_id=task_id,
            activity_code_id=activity_code_id,
            date=date,
            labor_cost=labor_cost,
            material_cost=material_cost,
            equipment_cost=equipment_cost,
            subcontractor_cost=subcontractor_cost,
            work_order_cost=work_order_cost,
            total_man_hours=total_man_hours,
            total_equipment_hours=total_equipment_hours,
            total_cost=total_cost
        )