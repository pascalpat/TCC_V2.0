from datetime import datetime
from .. import db
from ..models.models import ProjectTask, CostEntry
from ..models.workforce_models import WorkerEntry

class ProjectProgress(db.Model):
    __tablename__ = 'project_progress'

    # Core Fields
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)  # Links to Project
    task_id = db.Column(db.Integer, db.ForeignKey('project_tasks.id'), nullable=True)  # Links to Task
    date = db.Column(db.Date, nullable=False, index=True)  # Date of the progress entry

    # Pre-Calculated Metrics
    earned_hours = db.Column(db.Float, nullable=False, default=0.0)  # Earned hours for the date
    actual_hours = db.Column(db.Float, nullable=False, default=0.0)  # Real hours performed for the date
    cumulative_earned_hours = db.Column(db.Float, nullable=False, default=0.0)  # Cumulative earned hours
    cumulative_actual_hours = db.Column(db.Float, nullable=False, default=0.0)  # Cumulative actual hours
    cumulative_cost = db.Column(db.Float, nullable=True, default=0.0)  # Cumulative actual cost
    cumulative_earned_value = db.Column(db.Float, nullable=True, default=0.0)  # Cumulative earned value

    # Progress and Metrics
    progress_percentage = db.Column(db.Float, nullable=True, default=0.0)  # Physical progress as a percentage
    cost_performance_index = db.Column(db.Float, nullable=True)  # Cost Performance Index (CPI)
    schedule_performance_index = db.Column(db.Float, nullable=True)  # Schedule Performance Index (SPI)

    # Tags for Grouping
    phase = db.Column(db.String(100), nullable=True)  # Phase of construction (e.g., "Excavation")
    sector = db.Column(db.String(100), nullable=True)  # Sector or location (e.g., "North Wing")
    category = db.Column(db.String(100), nullable=True)  # Custom category (e.g., "Civil", "Mechanical")

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    # Relationships
    project = db.relationship('Project', backref='progress_entries', lazy=True)
    task = db.relationship('ProjectTask', backref='progress_entries', lazy=True)

    @staticmethod
    def calculate_daily_metrics(project_id, date):
        """
        Calculate and store metrics for a given project and date.
        """
        # Earned hours
        earned_hours = db.session.query(db.func.sum(ProjectTask.standard_man_hours)).filter(
            ProjectTask.project_id == project_id,
            ProjectTask.end_date <= date
        ).scalar() or 0.0

        # Actual hours
        actual_hours = db.session.query(db.func.sum(WorkerEntry.labor_hours)).filter(
            WorkerEntry.project_id == project_id,
            WorkerEntry.date == date
        ).scalar() or 0.0

        # Earned value
        earned_value = db.session.query(db.func.sum(ProjectTask.EV)).filter(
            ProjectTask.project_id == project_id,
            ProjectTask.end_date <= date
        ).scalar() or 0.0

        # Actual cost
        actual_cost = db.session.query(db.func.sum(CostEntry.cost)).filter(
            CostEntry.project_id == project_id,
            CostEntry.entry_date <= date
        ).scalar() or 0.0

        # Cumulative earned and actual hours
        cumulative_earned_hours = db.session.query(db.func.sum(ProjectProgress.earned_hours)).filter(
            ProjectProgress.project_id == project_id,
            ProjectProgress.date <= date
        ).scalar() or 0.0

        cumulative_actual_hours = db.session.query(db.func.sum(ProjectProgress.actual_hours)).filter(
            ProjectProgress.project_id == project_id,
            ProjectProgress.date <= date
        ).scalar() or 0.0

        # Cost Performance Index (CPI)
        cost_performance_index = earned_value / actual_cost if actual_cost > 0 else None

        # Schedule Performance Index (SPI)
        planned_value = db.session.query(db.func.sum(ProjectTask.PV)).filter(
            ProjectTask.project_id == project_id,
            ProjectTask.end_date >= date
        ).scalar() or 0.0
        schedule_performance_index = earned_value / planned_value if planned_value > 0 else None

        return ProjectProgress(
            project_id=project_id,
            date=date,
            earned_hours=earned_hours,
            actual_hours=actual_hours,
            cumulative_earned_hours=cumulative_earned_hours + earned_hours,
            cumulative_actual_hours=cumulative_actual_hours + actual_hours,
            cumulative_cost=actual_cost,
            cumulative_earned_value=earned_value,
            cost_performance_index=cost_performance_index,
            schedule_performance_index=schedule_performance_index
        )