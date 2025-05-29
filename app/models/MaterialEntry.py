from datetime import datetime
from app import db

class MaterialEntry(db.Model):
    __tablename__ = 'entries_material'

    ############################## Core Fields ##############################
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Foreign Keys
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    purchase_order_id = db.Column(db.Integer, db.ForeignKey('purchase_orders.id'), nullable=True)
    activity_code_id = db.Column(db.Integer, db.ForeignKey('activity_codes.id'), nullable=True)
    task_id = db.Column(db.Integer, db.ForeignKey('project_tasks.id'), nullable=True)
    date_of_report = db.Column(db.Date, nullable=False)
    work_order_id = db.Column(db.Integer, db.ForeignKey('work_orders.id'), nullable=True)
    status = db.Column(db.Enum('pending', 'in_progress', 'completed', name='entry_progress_status'), default='pending', nullable=True)
    payment_item_id = db.Column(db.Integer, db.ForeignKey('payment_items.id'), nullable=True)
    cwp = db.Column(db.String(50), nullable=True)
    

    ############################## Additional Fields ########################
    material_name = db.Column(db.String(255), nullable=True)
    unit = db.Column(db.String(50), nullable=True)
    unit_price = db.Column(db.Float, nullable=True)
    quantity_used = db.Column(db.Float, nullable=True)
    supplier_name = db.Column(db.String(255), nullable=True)
    cost = db.Column(db.Float, nullable=True)
    procurement_status = db.Column(db.String(50), nullable=True)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    ############################## Relationships ############################
    # These lines assume you have matching back_populates in those models.
    project       = db.relationship('Project', back_populates='material_entries', lazy=True)
    activity_code = db.relationship('ActivityCode', back_populates='material_entries')
    material      = db.relationship('Material', back_populates='material_entries')
    #project = db.relationship("Project", back_populates="material_entries", lazy=True)
    # If you want two-way relationships to purchase_orders, tasks, or work_orders, 
    # define the back_populates in those models as well.

    def __repr__(self):
        return f"<MaterialEntry id={self.id}, material_id={self.material_id}>"

    def to_dict(self):
        """
        Convert the MaterialEntry instance to a dictionary for JSON serialization.
        """
        return {
            'id': self.id,
            'material_id':          self.material_id,
            'project_id':           self.project_id,
            'purchase_order_id':    self.purchase_order_id,
            'activity_code_id':     self.activity_code_id,
            'task_id':              self.task_id,
            'work_order_id':        self.work_order_id,
            'material_name':        self.material_name,
            'unit':                 self.unit,
            'unit_price':           self.unit_price,
            'quantity_used':        self.quantity_used,
            'supplier_name':        self.supplier_name,
            'cost':                 self.cost,
            'procurement_status':   self.procurement_status,
            'payment_item_id':      self.payment_item_id,
            'cwp':                  self.cwp,
            'created_at':           self.created_at.isoformat() if self.created_at else None,
            'updated_at':           self.updated_at.isoformat() if self.updated_at else None,
        }
