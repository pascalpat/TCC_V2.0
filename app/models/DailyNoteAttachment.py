from app import db
from datetime import datetime

class DailyNoteAttachment(db.Model):
    __tablename__ = 'daily_note_attachments'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    daily_note_id = db.Column(db.Integer, db.ForeignKey('entries_daily_notes.id'), nullable=False)
    # From DailyPicture:
    file_name   = db.Column(db.String(255), nullable=True)   # e.g. "photo1.jpg", "report.pdf"
    file_url    = db.Column(db.String(2083), nullable=False) # The actual path/URL
    description = db.Column(db.Text, nullable=True)          # Freed up for doc or pic desc
    doc_type    = db.Column(db.String(50), nullable=True)    # e.g. "jpg", "pdf", "doc", etc.
    taken_at    = db.Column(db.DateTime, nullable=True)      # If relevant for pictures
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)  # same as in DailyPicture
    # Additional optional fields if you want to keep them:
    coordinates = db.Column(db.JSON, nullable=True)  # If you want location data from pictures
    position    = db.Column(db.String(255), nullable=True)  # e.g. "North Wing"
    size        = db.Column(db.Float, nullable=True)  # maybe file size in MB
    tags        = db.Column(db.JSON, nullable=True)   # e.g., ["Safety", "Progress"]
    captured_by = db.Column(db.String(255), nullable=True)  # who took the pic

    # Relationship back to the note
    daily_note = db.relationship('DailyNoteEntry', back_populates='attachments')

    def __repr__(self):
        return f"<DailyNoteAttachment id={self.id}, file_url='{self.file_url}'>"
