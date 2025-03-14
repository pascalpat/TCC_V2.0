from datetime import datetime
from .. import db
#from .daily_report_data import DailyReportData


class DailyReportStatus(db.Model):
    __tablename__ = 'daily_report_statuses'

    id = db.Column(db.Integer, primary_key=True)  # Unique ID for the status record
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)  # FK to the Projects table
    report_date = db.Column(db.Date, nullable=False)  # Date for which this status applies

    # Tab-Level Statuses
    workers_tab = db.Column(
        db.Enum('pending', 'in_progress', 'completed', name='tab_status'), default='pending'
    )
    materials_tab = db.Column(
        db.Enum('pending', 'in_progress', 'completed', name='tab_status'), default='pending'
    )
    equipment_tab = db.Column(
        db.Enum('pending', 'in_progress', 'completed', name='tab_status'), default='pending'
    )
    notes_tab = db.Column(
        db.Enum('pending', 'in_progress', 'completed', name='tab_status'), default='pending'
    )
    pictures_tab = db.Column(
        db.Enum('pending', 'in_progress', 'completed', name='tab_status'), default='pending'
    )
    subcontractors_tab = db.Column(
        db.Enum('pending', 'in_progress', 'completed', name='tab_status'), default='pending'
    )
    workorders_tab = db.Column(
        db.Enum('pending', 'in_progress', 'completed', name='tab_status'), default='pending'
    )

    # Overall Daily Report Status
    report_status = db.Column(
        db.Enum('pending', 'in_progress', 'completed', name='report_status_enum'), default='pending'
    )

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # When this record was created
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)  # When this record was last updated

    # Relationships
    project = db.relationship('Project', back_populates='daily_statuses', lazy=True)

    def update_report_status(self):
        """
        Update the overall report status based on the statuses of all tabs.
        """
        statuses = [
            self.workers_tab, self.materials_tab, self.equipment_tab,
            self.notes_tab, self.pictures_tab, self.subcontractors_tab,
            self.workorders_tab
        ]

        if all(status == 'completed' for status in statuses):
            self.report_status = 'completed'
        elif any(status == 'in_progress' for status in statuses):
            self.report_status = 'in_progress'
        else:
            self.report_status = 'pending'
        db.session.commit()

    def update_tab_status(self, tab_name):
        """
        Dynamically update a specific tab's status based on data in `daily_report_data`.
        """
        entity_type_mapping = {
            'workers_tab': 'worker',
            'materials_tab': 'material',
            'equipment_tab': 'equipment',
            'subcontractors_tab': 'subcontractor',
            'workorders_tab': 'workorder'
        }

        entity_type = entity_type_mapping.get(tab_name)
        if not entity_type:
            raise ValueError(f"Unknown tab name: {tab_name}")

        # Query related data in `daily_report_data`
        #entries = db.session.query(DailyReportData).filter_by(
            project_id=self.project_id,
            date=self.report_date,
            entity_type=entity_type
        #).all()

        #if not entries:
        #   setattr(self, tab_name, 'pending')
        #elif any(entry.status == 'in_progress' for entry in entries):
        #    setattr(self, tab_name, 'in_progress')
        #elif all(entry.status == 'completed' for entry in entries):
        #    setattr(self, tab_name, 'completed')
        #else:
        #    setattr(self, tab_name, 'in_progress')

        db.session.commit()
