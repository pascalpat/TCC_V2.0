# app/models/purchase_order_models.py

from .. import db
from datetime import datetime
from sqlalchemy.orm import validates



class PurchaseOrder(db.Model):
    __tablename__ = 'purchase_orders'

    id                     = db.Column(db.Integer, primary_key=True)
    po_id                  = db.Column(db.Integer, db.ForeignKey('purchase_orders.id'), nullable=True)
    linked_po_id           = db.Column(db.Integer, db.ForeignKey('purchase_orders.id'), nullable=True)
    order_number           = db.Column(db.String(50), unique=True, nullable=False)
    vendor                 = db.Column(db.String(255), nullable=False)
    vendor_address         = db.Column(db.String(255), nullable=True)
    vendor_phone           = db.Column(db.String(50), nullable=True)
    vendor_general_email   = db.Column(db.String(255), nullable=True)
    vendor_accounting_email= db.Column(db.String(255), nullable=True)
    vendor_contact_name    = db.Column(db.String(255), nullable=True)
    vendor_contact_phone   = db.Column(db.String(50), nullable=True)
    vendor_contact_email   = db.Column(db.String(255), nullable=True)
    project_id             = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True)
    equipment_id           = db.Column(db.String(100), db.ForeignKey('equipment.equipment_id'), nullable=True)
    worker_id              = db.Column(db.Integer, db.ForeignKey('workers.id'), nullable=True)
    subcontractor_id       = db.Column(db.Integer, db.ForeignKey('subcontractors.id'), nullable=True)
    service_name           = db.Column(db.String(255), nullable=True)
    activity_code_id       = db.Column(db.Integer, db.ForeignKey('activity_codes.id'), nullable=True)
    task_id                = db.Column(db.Integer, db.ForeignKey('project_tasks.id'), nullable=True)
    quantity_purchased     = db.Column(db.Float, nullable=True)
    unit_price             = db.Column(db.Float, nullable=True)
    total_cost             = db.Column(db.Float, nullable=True, default=0.0)
    procurement_group      = db.Column(
                               db.Enum('direct','bulk','rental',name='procurement_group_enum'),
                               default='direct', nullable=True
                             )
    procurement_type       = db.Column(
                               db.Enum(
                                 'material','equipment','worker','subcontractor','service',
                                 name='procurement_type_enum'
                               ),
                               nullable=True
                             )
    delivery_date          = db.Column(db.Date, nullable=True)
    delivery_location      = db.Column(db.String(255), nullable=True)
    link_to_supplier_quote = db.Column(db.String(2083), nullable=True)
    quantity_consumed      = db.Column(db.Float, nullable=True, default=0.0)
    delivery_compliance    = db.Column(
                               db.Enum(
                                 'on_time','late','partial','not_delivered',
                                 name='delivery_compliance_enum'
                               ),
                               nullable=True
                             )
    attachments            = db.Column(db.JSON, nullable=True)
    is_change_order        = db.Column(db.Boolean, default=False, nullable=True)
    on_site_status         = db.Column(
                               db.Enum(
                                 'pending','received','inspected','rejected',
                                 name='on_site_status_enum'
                               ),
                               default='pending', nullable=True
                             )
    created_at             = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at             = db.Column(db.DateTime, onupdate=datetime.utcnow)

    # Relationships
    materials        = db.relationship('Material', back_populates='purchase_order', lazy=True)
    parent_po        = db.relationship(
                          'PurchaseOrder', foreign_keys=[po_id],
                          remote_side=[id], backref='child_pos', lazy=True
                       )
    linked_po        = db.relationship(
                          'PurchaseOrder', foreign_keys=[linked_po_id],
                          remote_side=[id], backref='change_orders', lazy=True
                       )
    project          = db.relationship('Project', back_populates='purchase_orders', lazy=True)
    equipment        = db.relationship('Equipment', backref='purchase_orders', lazy=True)
    worker           = db.relationship('Worker', backref='purchase_orders', lazy=True)
    subcontractor    = db.relationship('Subcontractor', backref='purchase_orders', lazy=True)
    activity_code    = db.relationship('ActivityCode', backref='purchase_orders', lazy=True)
    task             = db.relationship('ProjectTask', backref='purchase_orders', lazy=True)

    @validates('material_id','equipment_id','worker_id','subcontractor_id','service_name')
    def validate_procurement_reference(self, key, value):
        setattr(self, key, value)
        if not any([
            getattr(self, 'material_id', None),
            self.equipment_id,
            self.worker_id,
            self.subcontractor_id,
            self.service_name
        ]):
            raise ValueError("At least one procurement reference is required.")
        return value


class PurchaseOrderAttachment(db.Model):
    __tablename__ = 'purchase_order_attachments'

    id          = db.Column(db.Integer, primary_key=True)
    po_id       = db.Column(db.Integer, db.ForeignKey('purchase_orders.id'), nullable=False)
    file_name   = db.Column(db.String(255), nullable=False)
    file_url    = db.Column(db.String(2083), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
