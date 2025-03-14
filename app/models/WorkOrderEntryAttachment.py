from datetime import datetime
from app import db

class WorkOrderEntryAttachment(db.Model):
    """
    Represents a document or file attached to a specific WorkOrderEntry record.
    """
    __tablename__ = 'work_order_entry_attachments'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # FK referencing the primary key in 'work_order_entries' table
    entry_id = db.Column(db.Integer, db.ForeignKey('work_order_entries.id'), nullable=False)

    # Path (or URL) to the physical file location (e.g., local disk or cloud)
    file_path = db.Column(db.String(255), nullable=False)

    # Optional descriptive info
    description = db.Column(db.String(255), nullable=True)
    doc_type = db.Column(db.String(50), nullable=True)

    # Tracks when the file was uploaded
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship back to the parent WorkOrderEntry
    entry = db.relationship('WorkOrderEntry', back_populates='attachments')

    def __repr__(self):
        return f"<WorkOrderEntryAttachment id={self.id}, file_path='{self.file_path}'>"
