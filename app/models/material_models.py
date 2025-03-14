from datetime import datetime
from .. import db
from .purchase_order_models import PurchaseOrder  # Adjust the import path as necessary
from .core_models import Project  # Adjust the import path as necessary
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from sqlalchemy import Column, String, Integer, ForeignKey, Float


class Material(db.Model):
    __tablename__ = 'materials'

    id = db.Column(db.Integer, primary_key=True)
    material_id = db.Column(db.String(100), unique=True, nullable=True)
    name = db.Column(db.String(255), nullable=False)
    unit = db.Column(db.String(50), nullable=True)
    cost_per_unit = db.Column(db.Float, nullable=True)
    description = db.Column(db.Text, nullable=True)
    
    # Link to Project
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id', ondelete='CASCADE'), nullable=True)
    # Link to PurchaseOrder
    purchase_order_id = db.Column(db.Integer, db.ForeignKey('purchase_orders.id'), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    # Relationships
    # The "back_populates" below must match Project.materials on the other side.
    project = db.relationship('Project', back_populates='materials', lazy=True)
    # The "back_populates" below must match PurchaseOrder.materials on the other side.
    purchase_order = db.relationship('PurchaseOrder', back_populates='materials', lazy=True)
    # If you have a MaterialEntry table linking daily usage, e.g.:
    material_entries = db.relationship('MaterialEntry', back_populates='material', lazy=True)

    @validates('cost_per_unit')
    def validate_cost_per_unit(self, key: str, value: float) -> float:
        if value < 0:
            raise ValueError("Cost per unit cannot be negative.")
        return value
    
