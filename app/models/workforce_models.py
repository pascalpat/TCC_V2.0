from datetime import datetime
from .. import db
from sqlalchemy import String, Column, Integer, ForeignKey, Float, Table
from sqlalchemy.orm import validates

equipment_assignments = db.Table(
    'equipment_assignments', 
    db.Column('worker_id', db.Integer, db.ForeignKey('workers.id'), primary_key=True),
    db.Column('equipment_id', db.Integer, db.ForeignKey('equipment.id'), primary_key=True),
    db.Column('project_id', db.Integer, db.ForeignKey('projects.id'), nullable=False),  # Links the assignment to a project
    db.Column('start_date', db.Date, nullable=True),  # Assignment start date
    db.Column('end_date', db.Date, nullable=True),  # Assignment end date
    db.Column('role', db.String(50), nullable=True),  # Role of the worker (e.g., "Operator", "Supervisor")
    db.Column('notes', db.String(255), nullable=True)  # Additional notes
)

VALID_ROLES = {"admin", "manager", "superintendent", "foreman", "worker"}

class Worker(db.Model):
    __tablename__ = 'workers'

    ################################## Core Fields ###############################################
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(String(255), nullable=False)  # Full name of the worker
    genre = db.Column(db.Enum('male', 'female', 'other', name='worker_genre'), nullable=True)  # Gender
    worker_id = db.Column(db.String(50), unique=True, nullable=False)  # Unique worker company identifier (e.g., Employee ID)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id', name='fk_worker_project'), nullable=True)
    #daily_report_id = db.Column(db.Integer, db.ForeignKey('daily_report_data.id'))

    ################################## Contact Information #######################################
    code_postal = db.Column(db.String(10), nullable=True)  # Postal code
    num_cell = db.Column(db.String(15), nullable=True)  # Cellphone number
    courriel = db.Column(db.String(255), nullable=True, unique=True)  # Email address
    certifications = db.Column(db.JSON, nullable=True)  # JSON to store worker certifications
    experience_years = db.Column(db.Integer, nullable=True)  # Number of years of experience

    ################################## Authentification ##########################################
    password_hash = db.Column(db.String(255), nullable=True)  # Hashed password for user authentication
    last_login = db.Column(db.DateTime, nullable=True)  # Last login timestamp
    login_attempts = db.Column(db.Integer, default=0)  # Count of failed login attempts

    ################################## Compensation and Benefits ##################################
    metier = db.Column(db.String(100), nullable=True)  # Occupation or trade
    convention = db.Column(db.String(100), nullable=True)  # Collective agreement
    taux_horaire = db.Column(db.Float, nullable=True)  # Hourly rate
    taux_over = db.Column(db.Float, nullable=True)  # Overtime rate
    Gite_couvert = db.Column(db.Float, nullable=True)  # Room and board daily cost
    transp_1 = db.Column(db.Float, nullable=True, default=0.0)  # Transportation type 1 daily cost
    transp_2 = db.Column(db.Float, nullable=True, default=0.0)  # Transportation type 2 daily cost

    ################################## Work Details ###############################################
    equip_asso = db.Column(db.String(255), nullable=True)  # Associated equipment
    departement = db.Column(db.String(100), nullable=True)  # Department or team

    ################################## User Account Fields #######################################
    role = db.Column(db.Enum('admin', 'manager', 'superintendent', 'foreman', 'worker', name='user_roles'), default='worker')  # System role
    is_active = db.Column(db.Boolean, nullable=False, default=True)  # Status for account activation

    ################################## Metadata ##################################################
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    updated_by = db.Column(db.String(255), nullable=True)  # User who last updated the worker

    ################################## Relationships #############################################
    equipment = db.relationship('Equipment', secondary=equipment_assignments, back_populates='workers', lazy='subquery')
    project = db.relationship('Project', back_populates='workers')  # Links to Project table
    #entries = db.relationship('WorkerEntry', back_populates='workers')
    #daily_report_data = db.relationship("DailyReportData", back_populates="workers")
    worker_entries = db.relationship("WorkerEntry", back_populates="worker")

    @validates('role')
    def validate_role(self, key, role_value):
        """Ensures only valid roles are saved to the database."""
        if role_value not in VALID_ROLES:
            raise ValueError(f"Invalid role: {role_value}. Allowed roles: {VALID_ROLES}")
        return role_value