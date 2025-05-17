from datetime import datetime
from .. import db
from sqlalchemy import Column, String, Integer, ForeignKey, Enum, Float, Date, DateTime
from sqlalchemy.orm import relationship, validates


class Project(db.Model):
    __tablename__ = 'projects'
    ################################## Core fields ##################################
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)  # Project name
    description = Column(String(500), nullable=True)
    project_number = db.Column(db.String(50), nullable=False, unique=True, index=True)  # Unique project number
    category = db.Column(db.String(100), nullable=False, index=True)  # Project category (e.g., Residential, Commercial)
    status = db.Column(db.Enum('planned', 'in_progress', 'completed', 'on_hold', 'canceled', name='project_status'), default='planned', index=True)
    client_name = db.Column(db.String(255), nullable=True)  # Name of the client
    project_manager = db.Column(db.String(255), nullable=True)  # Name of the project manager
    address = db.Column(db.String(255), nullable=True)
    
    ################################## Budget and risk fields ##################################
    budget = db.Column(db.Float, nullable=True)  # Budget for the project
    original_budget = db.Column(db.Float, nullable=True)
    revised_budget = db.Column(db.Float, nullable=True)
    contingency_fund = db.Column(db.Float, nullable=True)
    risk_level = db.Column(db.Enum('low', 'medium', 'high', name='project_risk_level'), nullable=True, default='low')
    risk_notes = db.Column(db.Text, nullable=True)
    
    ################################## Picture and Map fields ##################################
    map_url = db.Column(db.String(2083), nullable=True)  # URL for an online map (e.g., Google Maps link)
    latitude = db.Column(db.Float, nullable=True)  # Latitude coordinate
    longitude = db.Column(db.Float, nullable=True)  # Longitude coordinate
    picture_url = db.Column(db.String(2083), nullable=True)  # URL for the project picture
    video_capture_url = db.Column(db.String(2083), nullable=True)  # Link to video capture or real-time stream 

    ################################## Additional fields for future-proofing ##################################
    
    start_date = db.Column(db.Date, nullable=True, index=True)
    end_date = db.Column(db.Date, nullable=True, index=True)
    notes = db.Column(db.Text, nullable=True)  # Additional notes or description
    plan_repository_url = db.Column(db.String(2083), nullable=True)  # Link to plans or Bluebeam repository
    sustainability_rating = db.Column(db.Enum('basic', 'silver', 'gold', 'platinum', name='sustainability_rating'), nullable=True)
    sustainability_goals = db.Column(db.Text, nullable=True)
    collaboration_url = db.Column(db.String(2083), nullable=True)
    integration_status = db.Column(db.Boolean, default=False)
    audit_due_date = db.Column(db.Date, nullable=True)
    compliance_status = db.Column(db.Enum('pending', 'approved', 'non_compliant', name='compliance_status'), default='pending')
    local_hires = db.Column(db.Integer, nullable=True)
    community_engagement_notes = db.Column(db.Text, nullable=True)
    previous_project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True)
    benchmark_cost_per_unit = db.Column(db.Float, nullable=True)
    tags = db.Column(db.JSON, nullable=True)
    critical_path_duration = db.Column(db.Integer, nullable=True)
    key_milestones = db.Column(db.JSON, nullable=True)
    safety_incidents = db.Column(db.Integer, nullable=True, default=0)
    incident_notes = db.Column(db.Text, nullable=True)

    #################################  BIM360 fields #################################
    bim_file_url = db.Column(db.String(2083), nullable=True)  # URL to the BIM file
    bim_model_id = db.Column(db.String(255), nullable=True)  # BIM platform-specific ID

    ################################# Metadata #################################
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    updated_by = db.Column(db.String(255), nullable=True)  # User who last updated the project

    ################################# Static methods #################################
    @staticmethod
    def validate_coordinates(latitude, longitude):
        if latitude is not None and (latitude < -90 or latitude > 90):
            raise ValueError("Latitude must be between -90 and 90.")
        if longitude is not None and (longitude < -180 or longitude > 180):
            raise ValueError("Longitude must be between -180 and 180.")
    ################################# Relationships ##################################
    tasks                   = db.relationship('ProjectTask',        back_populates='project', lazy=True)
    payment_items           = db.relationship('PaymentItem',        back_populates='project', lazy=True)
    daily_statuses          = db.relationship('DailyReportStatus',  back_populates='project', lazy=True)
    work_orders             = db.relationship('WorkOrder',          back_populates='project', lazy=True)
    activity_codes          = db.relationship('ActivityCode',       back_populates='project', cascade="all, delete-orphan", lazy=True)
    worker_entries          = db.relationship('WorkerEntry',        back_populates='project', lazy=True)
    equipment               = db.relationship("Equipment",          back_populates="project", lazy=True)
    equipment_entries       = db.relationship('EquipmentEntry',     back_populates='project', lazy=True)  # New relationship
    workers                 = db.relationship("Worker",             back_populates="project")
    subcontractors          = db.relationship("Subcontractor",      back_populates="project")
    subcontractor_entries   = db.relationship("SubcontractorEntry", back_populates="project")
    materials               = relationship('Material',              back_populates='project', lazy=True)
    material_entries        = db.relationship("MaterialEntry",      back_populates="project", lazy=True)
    purchase_orders         = db.relationship('PurchaseOrder',      back_populates='project', lazy=True)

    def __repr__(self):
        return f"<Project id={self.id} name={self.name}>"

class ActivityCode(db.Model):
    __tablename__ = 'activity_codes'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False, index=True)  # e.g., "32172"
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id', ondelete='CASCADE'), nullable=True)
    cwp = db.Column(db.String(50), nullable=True)  # Construction Work Package
    description = db.Column(db.String(255), nullable=False)  # Activity description
    unit = db.Column(db.String(50), nullable=True)  # e.g., "m²", "hrs"
    std_man_hours_per_unit = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # ------------------- RELATIONSHIPS -------------------
    # Ties to a ProjectTask
    project_tasks       = db.relationship('ProjectTask',        back_populates='activity_code', lazy='select')
    # Ties to PaymentItem (one FK: activity_code_id)
    payment_items       = db.relationship('PaymentItem',        back_populates='activity_code', lazy=True)
    # Worker / Equipment / Material references
    entries             = db.relationship('WorkerEntry',        back_populates='activity')
    equipment_entries   = db.relationship('EquipmentEntry',     back_populates='activity')
    material_entries    = db.relationship('MaterialEntry',      back_populates='activity_code')
    # Subcontractor references
    subcontractor_entries = db.relationship('SubcontractorEntry', back_populates='activity_code', lazy=True)
    # Parent project
    project             = db.relationship('Project',            back_populates='activity_codes', lazy=True)
        # Additional worker / order logs
    worker_entries      = db.relationship('WorkerEntry',        back_populates='activity')
    work_order_entries  = db.relationship('WorkOrderEntry',     back_populates='activity_code')


class ProjectTask(db.Model):
    __tablename__ = 'project_tasks'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)  # Task name
    activity_code_id = db.Column(db.Integer, db.ForeignKey('activity_codes.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.Enum('not_started', 'in_progress', 'completed', name='task_status'), default='not_started')
    progress = db.Column(db.Float, default=0.0)  # Progress percentage

    # Cost and EVM Fields
    man_hour_budget = db.Column(db.Float, nullable=True, default=0.0)  # Initial planned man-hours
    man_hours = db.Column(db.Float, nullable=True, default=0.0)  # Actual man-hours
    #payment_item_id = db.Column(db.Integer, db.ForeignKey('payment_items.id'), nullable=True)
    unit = db.Column(db.String(50), nullable=True)  # Unit of measurement
    qte = db.Column(db.Float, nullable=True)  # Quantity of work completed

    PV = db.Column(db.Float, nullable=True, default=0.0)  # Planned Value
    EV = db.Column(db.Float, nullable=True, default=0.0)  # Earned Value
    AC = db.Column(db.Float, nullable=True, default=0.0)  # Actual Cost
    CV = db.Column(db.Float, nullable=True, default=0.0)  # Cost Variance
    SV = db.Column(db.Float, nullable=True, default=0.0)  # Schedule Variance
    VAC = db.Column(db.Float, nullable=True, default=0.0)  # Variance at Completion
    CPI = db.Column(db.Float, nullable=True, default=0.0)  # Cost Performance Index
    SPI = db.Column(db.Float, nullable=True, default=0.0)  # Schedule Performance Index
    EAC = db.Column(db.Float, nullable=True, default=0.0)  # Estimate at Completion
    ETC = db.Column(db.Float, nullable=True, default=0.0)  # Estimate to Complete
    TCPI = db.Column(db.Float, nullable=True, default=0.0)  # To-Complete Performance Index

    # Work Package and Specialty        
    CWP = db.Column(db.String(100), nullable=True)  # Construction Work Package
    specialty = db.Column(db.String(100), nullable=True)  # Specialty

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    # Relationships
    project             = db.relationship('Project',        back_populates='tasks', lazy=True)
    payment_items       = db.relationship("PaymentItem",    back_populates='project_task', lazy=True)
    activity_code       = db.relationship('ActivityCode',   back_populates='project_tasks')
    work_order_entries  = db.relationship("WorkOrderEntry", back_populates="task")

class PaymentItem(db.Model):
    __tablename__ = 'payment_items'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    payment_code = db.Column(db.String(50), unique=True, nullable=False, index=True)  
    activity_code_id = db.Column(db.Integer, db.ForeignKey('activity_codes.id'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey("project_tasks.id"), nullable=True)
    item_name = db.Column(db.String(255), nullable=False, index=True)  
    unit = db.Column(db.String(50), nullable=True)  
    rate_per_unit = db.Column(db.Float, nullable=True) 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # ------------------- RELATIONSHIPS -------------------
    activity_code       = db.relationship("ActivityCode",   back_populates="payment_items", lazy=True)
    project_task        = db.relationship('ProjectTask',    back_populates='payment_items', lazy=True)
    project             = db.relationship('Project',        back_populates='payment_items', lazy=True)
    worker_entries      = db.relationship('WorkerEntry',    back_populates='payment_item', foreign_keys='WorkerEntry.payment_item_id',lazy=True)
    equipment_entries   = db.relationship('EquipmentEntry', back_populates='payment_item', foreign_keys='EquipmentEntry.payment_item_id', lazy=True)
    
    @validates('rate_per_unit')
    def validate_rate(self, key, value):
        if value is not None and value < 0:
            raise ValueError("Rate per unit cannot be negative.")
        return value

class CWPackage(db.Model):
    __tablename__ = 'cw_packages'

    project_id = db.Column(
        db.Integer,
        db.ForeignKey('projects.id'),
        primary_key=True
    )
    code       = db.Column(db.String(50), primary_key=True)
    name       = db.Column(db.String(255), nullable=False)
    unit       = db.Column(db.String(20), nullable=True)
    project_id = db.Column(db.String(50), nullable=False, index=True)