from datetime import datetime
from .. import db


class DailyNoteEntry(db.Model):
    __tablename__ = 'entries_daily_notes'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    note_datetime = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    date_of_report = db.Column(db.Date, nullable=False, index=True)
    status = db.Column(db.Enum('pending','committed','rejected', name='entry_status'), default='pending')
    author = db.Column(db.String(255), nullable=True)
    category = db.Column(db.String(50), nullable=True)
    tags = db.Column(db.JSON, nullable=True)
    content = db.Column(db.Text, nullable=False)
    priority = db.Column(db.Enum('low', 'medium', 'high', name='note_priority_enum'), default='low')
    activity_code_id = db.Column(db.Integer, db.ForeignKey('activity_codes.id'), nullable=True)
    payment_item_id = db.Column(db.Integer, db.ForeignKey('payment_items.id'), nullable=True)
    work_order_id = db.Column(db.Integer, db.ForeignKey('work_orders.id'), nullable=True)
    cwp = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    # Permissions
    editable_by = db.Column(db.String(255), nullable=True)  # User or role allowed to edit

    # Relationships
    project = db.relationship('Project', back_populates='daily_note_entries')
    activity_code = db.relationship('ActivityCode', back_populates='daily_note_entries')
    attachments = db.relationship('DailyNoteAttachment', back_populates='daily_note', lazy=True)
    documents = db.relationship('Document', back_populates='daily_note', lazy=True)
    work_order = db.relationship('WorkOrder', backref='entries_daily_notes', lazy=True)

    def __repr__(self):
        return f"<DailyNoteEntry id={self.id} project_id={self.project_id}>"

    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'note_datetime': self.note_datetime.isoformat() if self.note_datetime else None,
            'date_of_report': self.date_of_report.isoformat() if self.date_of_report else None,
            'author': self.author,
            'category': self.category,
            'tags': self.tags,
            'content': self.content,
            'priority': self.priority,
            'status': self.status,
            'activity_code_id': self.activity_code_id,
            'payment_item_id': self.payment_item_id,
            'work_order_id': self.work_order_id,
            'cwp': self.cwp,
            'editable_by': self.editable_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

class DailyPicture(db.Model):
    __tablename__ = 'daily_pictures'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)  # Links to a project
    #daily_log_id = db.Column(db.Integer, db.ForeignKey('daily_report_data.id'), nullable=True)  # Links to a daily log
    file_name = db.Column(db.String(255), nullable=False)  # Picture file name
    file_url = db.Column(db.String(2083), nullable=False)  # Path or URL to the picture
    description = db.Column(db.Text, nullable=True)  # Description or notes about the picture
    taken_at = db.Column(db.DateTime, nullable=True)  # Timestamp when the picture was taken
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)  # Timestamp of upload
    status = db.Column(db.Enum('pending', 'committed', name='record_status'),default='pending')

    # Relationships to Activity Codes, Work Orders, and Notes
    activity_code = db.Column(db.String(50), db.ForeignKey('activity_codes.id'), nullable=True)  # Links to an activity code
    work_order_id = db.Column(db.Integer, db.ForeignKey('work_orders.id'), nullable=True)  # Links to a work order
    daily_note_id = db.Column(db.Integer, db.ForeignKey('entries_daily_notes.id'), nullable=True)

    # Advanced Parsing Fields
    coordinates = db.Column(db.JSON, nullable=True)  # JSON storing GPS coordinates (latitude, longitude)
    position = db.Column(db.String(255), nullable=True)  # Position or location in relation to site (e.g., "North Wing")
    size = db.Column(db.Float, nullable=True)  # File size or resolution (e.g., MB or pixels)

    # Tags for Categorization
    tags = db.Column(db.JSON, nullable=True)  # JSON array for tags (e.g., ["Safety", "Progress"])
    captured_by = db.Column(db.String(255), nullable=True)  # User who captured the picture
    # Relationships
    project = db.relationship('Project', backref='daily_pictures', lazy=True)
    work_order = db.relationship('WorkOrder', backref='pictures', lazy=True)
    daily_note = db.relationship('DailyNoteEntry', backref='pictures', lazy=True)


class WeatherLog(db.Model):
    __tablename__ = 'weather_logs'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)  # Links to a project
    #daily_log_id = db.Column(db.Integer, db.ForeignKey('daily_report_data.id'), nullable=True)
    date = db.Column(db.Date, nullable=False)  # Date of the weather observation
    temperature = db.Column(db.Float, nullable=True)  # Temperature in Celsius
    humidity = db.Column(db.Float, nullable=True)  # Humidity percentage
    wind_speed = db.Column(db.Float, nullable=True)  # Wind speed in km/h
    description = db.Column(db.String(255), nullable=True)  # Weather description (e.g., "Sunny", "Rainy")

    # Impact Fields
    severity = db.Column(db.Enum('low', 'medium', 'high', name='weather_severity_enum'), default='low')  # Impact severity
    work_impact = db.Column(db.Enum('none', 'partial_delay', 'full_stop', name='weather_impact_enum'), default='none')  # Impact on work
    delay_reason = db.Column(db.Text, nullable=True)  # Description of the reason for the delay
    hours_lost = db.Column(db.Float, nullable=True)  # Total hours lost due to weather impact   
    impacted_activity_codes = db.Column(db.JSON, nullable=True)  # List of impacted activity codes

    # Metadata
    api_data = db.Column(db.JSON, nullable=True)  # Raw API response for future reference
    trend = db.Column(db.String(50), nullable=True)  # Weather trend (optional)
    predicted_hours_lost = db.Column(db.Float, nullable=True)  # Predicted hours lost (optional)

    #################################################  relationships #################################################
    #daily_log = db.relationship('DailyReportData', back_populates='weather_logs')
    project = db.relationship('Project', backref='weather_logs', lazy=True)
