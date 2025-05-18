from datetime import datetime
from .. import db
from .core_models import Project

class TabProgress(db.Model):
    __tablename__ = 'tab_progress'
    
    # Core Fields
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)  # Links to Project
    #daily_log_id = db.Column(db.Integer, db.ForeignKey('daily_report_data.id'), nullable=True)  # Links to daily logs
    date = db.Column(db.Date, nullable=False)  # Date of the progress entry
    tab_name = db.Column(db.String(50), nullable=False)  # Name of the tab (e.g., "Workers", "Materials")
    status = db.Column(
        db.Enum('incomplete', 'in_review', 'completed', 'approved', 'rejected', name='tab_status'),
        default='incomplete'
    )  # Status of the tab
    progress_percentage = db.Column(db.Float, default=0.0)  # Fine-grained progress tracking
    is_locked = db.Column(db.Boolean, default=False)  # Prevent further edits
    status_history = db.Column(db.JSON, nullable=True)  # Tracks historical status changes

    # Notes and Metadata
    tab_notes = db.Column(db.Text, nullable=True)  # Notes or comments about the tab
    last_updated_by = db.Column(db.String(255), nullable=True)  # User who last updated the tab
    reviewed_by = db.Column(db.String(255), nullable=True)  # User who reviewed the tab

    # Relationships
    project = db.relationship('Project', backref='tab_progress_entries', lazy=True)  # Links to Project
    #daily_log = db.relationship('DailyReportData', back_populates='tab_progress', lazy=True)

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Timestamp for creation
    last_updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)  # Timestamp for the last update

    @staticmethod
    def initialize_tabs_for_report(project_id, date, tab_names):
        """
        Initialize TabProgress entries for all tabs in a new daily report.
        """
        entries = []
        for tab_name in tab_names:
            entry = TabProgress(
                project_id=project_id,
                date=date,
                tab_name=tab_name,
                status="incomplete"
            )
            db.session.add(entry)
            entries.append(entry)
        db.session.commit()
        return entries

    @staticmethod
    def aggregate_report_status(project_id, date):
        """
        Aggregate the overall status of a daily report based on TabProgress entries.
        """
        tabs = TabProgress.query.filter_by(project_id=project_id, date=date).all()
        statuses = [tab.status for tab in tabs]

        if all(status == "completed" for status in statuses):
            return "completed"
        elif any(status in ["in_review", "in_progress"] for status in statuses):
            return "in_progress"
        else:
            return "incomplete"

class SustainabilityMetric(db.Model):
    __tablename__ = 'sustainability_metrics'
    
    # Core Fields
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))  # Links to Project
    task_id = db.Column(db.Integer, db.ForeignKey('project_tasks.id'), nullable=True)  # Links to Task
    #daily_log_id = db.Column(db.Integer, db.ForeignKey('daily_report_data.id'), nullable=True)
    metric_name = db.Column(db.String(255), nullable=False)  # Name of the metric (e.g., "Carbon Emissions")
    category = db.Column(
        db.Enum('energy', 'emissions', 'water', 'waste', 'materials', name='sustainability_category'),
        nullable=True
    )  # Metric category
    value = db.Column(db.Float, nullable=False)  # Value of the metric
    unit = db.Column(db.String(50), nullable=False)  # Unit of the metric (e.g., "kg", "liters")
    threshold = db.Column(db.Float, nullable=True)  # Threshold for triggering alerts
    target_value = db.Column(db.Float, nullable=True)  # Target value for the metric
    deviation = db.Column(db.Float, nullable=True)  # Deviation from the target value
    triggered_alert = db.Column(db.Boolean, default=False)  # Whether the threshold was exceeded

    # Metadata
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)  # Timestamp of metric recording
    recorded_by = db.Column(db.String(255), nullable=True)  # User who recorded the metric
    notes = db.Column(db.Text, nullable=True)  # Additional notes or context

    # Relationships
    project = db.relationship('Project', backref='sustainability_metrics', lazy=True)  # Links to Project
    task = db.relationship('ProjectTask', backref='sustainability_metrics', lazy=True)  # Links to Task
    #daily_log = db.relationship('DailyReportData', back_populates='sustainability_metrics')
    

class Document(db.Model):
    __tablename__ = 'documents'
    
    # Core Fields
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)  # Links to Project
    #daily_log_id = db.Column(db.Integer, db.ForeignKey('daily_report_data.id'), nullable=True)  # Links to Daily Log
    file_name = db.Column(db.String(255), nullable=False)  # Name of the uploaded file
    file_url = db.Column(db.String(2083), nullable=False)  # Path or URL to the file
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)  # Timestamp of upload

    # Document Type and Category
    document_type = db.Column(
        db.Enum(
            'h_s', 'environment', 'field_inspection', 'maintenance', 'general',
            name='document_type_enum'
        ),
        nullable=False
    )  # Type of document
    category = db.Column(db.String(50), nullable=True)  # Free-form category for additional grouping

    # Related Daily Notes and Pictures
    daily_note_id = db.Column(db.Integer, db.ForeignKey('entries_daily_notes.id'), nullable=True)
    picture_repository_url = db.Column(db.String(2083), nullable=True)  # Link to related pictures repository

    # Approval Workflow
    is_approved = db.Column(db.Boolean, default=False)  # Approval status
    approved_by = db.Column(db.String(255), nullable=True)  # User who approved the document
    approval_date = db.Column(db.DateTime, nullable=True)  # Date of approval

    # Tags and Metadata
    tags = db.Column(db.JSON, nullable=True)  # JSON array for tags (e.g., ["Safety", "Urgent"])
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Timestamp for creation
    last_modified_at = db.Column(db.DateTime, nullable=True)  # Timestamp of the last modification

    # Relationships
    project = db.relationship('Project', backref='documents', lazy=True)  # Links to Project
    daily_note = db.relationship('DailyNoteEntry', back_populates='documents', lazy=True)
    #daily_log = db.relationship('DailyReportData', back_populates='documents')

