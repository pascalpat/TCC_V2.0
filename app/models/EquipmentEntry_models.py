from datetime import datetime
from app import db

class EquipmentEntry(db.Model):
    __tablename__ = 'entries_equipment'  # Make sure this is set!

    ############################## Core Fields ###############################
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date_of_report = db.Column(db.Date, nullable=False, index=True)  # Date of the report
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=True)
    equipment_name = db.Column(db.Text, nullable=True)  # Equipment name (optional, can be derived from equipment_id)
    hours_used = db.Column(db.Float, nullable=False, default=0.0)
    status = db.Column(db.Enum('pending', 'in_progress', 'completed', name='entry_progress_status'),default='pending',nullable=True)

    ############################## Additional Fields #########################
    activity_id = db.Column(db.Integer, db.ForeignKey('activity_codes.id'), nullable=True)
    cwp = db.Column(db.String(50), nullable=True)
    payment_item_id = db.Column(db.Integer, db.ForeignKey('payment_items.id'), nullable=True)
    phase = db.Column(db.String(50), nullable=True)
    usage_description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    ############################## Relationships #############################
    project = db.relationship('Project', back_populates='equipment_entries')
    equipment = db.relationship('Equipment', back_populates='equipment_entries')
    activity = db.relationship('ActivityCode', back_populates='equipment_entries')

    def __repr__(self):
        return f"<EquipmentEntry id={self.id}, equipment_id={self.equipment_id}, date={self.date_of_report}>"

    def to_dict(self):
        return {
            'id': self.id,
            'date_of_report': self.date_of_report.isoformat(),
            'project_id': self.project_id,
            'equipment_id': self.equipment_id,
            'hours_used': self.hours_used,
            'activity_id': self.activity_id,
            'cwp': self.cwp,
            'phase': self.phase,
            'payment_item_id': self.payment_item_id,
            'usage_description': self.usage_description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
