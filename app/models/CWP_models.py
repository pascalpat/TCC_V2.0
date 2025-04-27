from . import db

class CWPackage(db.Model):
    __tablename__ = 'cw_packages'

    # e.g. "FWK01"
    code = db.Column(db.String(50), primary_key=True)

    # human-readable, e.g. "Formwork"
    name = db.Column(db.String(255), nullable=False)

    unit = db.Column('default_unit', db.String(20), nullable=True) # e.g. "m³", "hr", etc.
    project_id = db.Column(db.String(50), nullable=False)

