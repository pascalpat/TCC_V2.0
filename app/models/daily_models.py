from datetime import datetime
from .. import db


class DailyNote(db.Model):
    __tablename__ = 'daily_notes'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)  # Links to a project
    #daily_log_id = db.Column(db.Integer, db.ForeignKey('daily_report_data.id'), nullable=True)  # Links to daily logs
    note = db.Column(db.Text, nullable=False)  # Daily note or observation
    created_by = db.Column(db.String(255), nullable=True)  # User who created the note
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Timestamp of creation

    # Categorization
    category = db.Column(db.String(50), nullable=True)  # Category of the note (e.g., "Progress", "Issues")
    priority = db.Column(db.Enum('low', 'medium', 'high', name='note_priority_enum'), default='low')  # Priority level

    # Linking
    linked_activity_code = db.Column(db.Integer, db.ForeignKey('activity_codes.id'), nullable=True)  # Links to an activity code

    # Attachments
    attachment_url = db.Column(db.String(2083), nullable=True)  # Optional link to an attached file or picture

    # Permissions
    editable_by = db.Column(db.String(255), nullable=True)  # User or role allowed to edit

    # Relationships
    project = db.relationship('Project', backref='daily_notes', lazy=True)
    #daily_log = db.relationship('DailyReportData', back_populates='daily_notes', lazy=True)
    activity_code = db.relationship('ActivityCode', backref='daily_notes', lazy=True)

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

    # Relationships to Activity Codes, Work Orders, and Notes
    activity_code = db.Column(db.String(50), db.ForeignKey('activity_codes.id'), nullable=True)  # Links to an activity code
    work_order_id = db.Column(db.Integer, db.ForeignKey('work_orders.id'), nullable=True)  # Links to a work order
    daily_note_id = db.Column(db.Integer, db.ForeignKey('daily_notes.id'), nullable=True)  # Links to a daily note

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
    daily_note = db.relationship('DailyNote', backref='pictures', lazy=True)
    #daily_log = db.relationship('DailyReportData', back_populates='pictures', lazy=True)


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