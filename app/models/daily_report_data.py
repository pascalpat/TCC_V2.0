from sqlalchemy import (
    Column, Integer, String, Float, Date, ForeignKey, Text, JSON
)
from sqlalchemy.orm import relationship
from datetime import datetime
from app import db


class DailyReportData(db.Model):
    __tablename__ = 'daily_report_data'

    # Core Fields
    id = Column(Integer, primary_key=True)  # Unique ID for the daily report entry
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)  # FK to Projects table
    activity_code_id = Column(Integer, ForeignKey('activity_codes.id'), nullable=True)
    payment_item_id = db.Column(db.Integer, db.ForeignKey('payment_items.id'), nullable=True)
    worker_id = db.Column(db.Integer, db.ForeignKey('workers.id'), nullable=True)
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable=True)
    po_id = db.Column(db.Integer, db.ForeignKey('purchase_orders.id'), nullable=True)
    quantity_used = db.Column(db.Float, default=0.0)  # Quantity consumed on the given date
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=True)
    subcontractor_id = db.Column(db.Integer, db.ForeignKey('subcontractors.id'), nullable=True)
    #daily_log_id = db.Column(db.Integer, db.ForeignKey('daily_report_data.id'), nullable=True)
    date = Column(Date, nullable=False)  # Date of the log entry
    hours = Column(Float, default=0.0)  # Hours worked or used
    cost = Column(Float, default=0.0)  # Associated cost
    quantity_used = db.Column(db.Float, default=0.0)  # Quantity of material used

    # Dynamic Entity Association
    entity_type = Column(String(50), nullable=False)  # Type of entity ('worker', 'equipment', 'material', etc.)
    entity_id = Column(Integer, nullable=True)  # ID of the specific entity (e.g., worker ID, equipment ID)

    # Granularity and Custom Fields
    task_id = Column(Integer, ForeignKey('project_tasks.id'), nullable=True)  # FK to Tasks table
    payment_item_id = Column(Integer, ForeignKey('payment_items.id'), nullable=True)  # FK to Payment Items table
    CWP = Column(String(100), nullable=True)  # Construction Work Package (optional)
    phase = Column(String(100), nullable=True)  # Construction phase (optional)
    location = Column(String(100), nullable=True)  # Optional location or sector

    # Flexible Data Storage
    tags = Column(JSON, nullable=True)  # Custom tags in a structured JSON format (e.g., {"priority": "High"})

    # Notes and Metadata
    notes = Column(Text, nullable=True)  # Additional notes or descriptions
    created_at = Column(Date, default=datetime.utcnow)  # Entry creation timestamp
    updated_at = Column(Date, default=datetime.utcnow, onupdate=datetime.utcnow)  # Last update timestamp

    # Relationships
    #project = relationship('Project', back_populates='daily_logs')  # Links to Projects
    task = relationship('Task', back_populates='')  # Links to Tasks
    #payment_item = relationship('PaymentItem', back_populates='daily_logs')  # Links to Payment Items
    #activity_code = db.relationship('ActivityCode', back_populates='daily_logs')
    #workers = db.relationship('Worker', back_populates='daily_report_data')
    #material = db.relationship('Material', back_populates='daily_logs')
    #equipment = db.relationship('Equipment', back_populates='daily_logs')
    #subcontractor = db.relationship('Subcontractor', back_populates='daily_logs')
    #documents = db.relationship('Document', back_populates='daily_log', lazy=True)
    #daily_log = db.relationship('DailyReportData', back_populates='entries_daily_notes')
    #entries_daily_notes = db.relationship('DailyNote', back_populates='daily_log', lazy=True)
    #pictures = db.relationship('DailyPicture', back_populates='daily_log', lazy=True)
    #weather_logs = db.relationship('WeatherLog', back_populates='daily_log', lazy=True)
    #purchase_order = db.relationship('PurchaseOrder', back_populates='daily_logs', lazy=True)
    #work_order = db.relationship('WorkOrder', back_populates='daily_logs', lazy=True)
    #tab_progress = db.relationship('TabProgress', back_populates='daily_log', lazy=True)
    #sustainability_metrics = db.relationship('SustainabilityMetric', back_populates='daily_log', lazy=True)
    #daily_report_data = db.relationship("DailyReportData", foreign_keys=[daily_report_id], back_populates="workers" )