from . import db

class CWPackage(db.Model):
    __tablename__ = 'cw_packages'

    # e.g. "FWK01"
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), primary_key=True)
    code = db.Column(db.String(50), primary_key=True)

    name = db.Column(db.String(255), nullable=False)
    unit = db.Column('default_unit', db.String(20), nullable=True)

    project = db.relationship('Project', backref='cwp_packages', lazy=True)

    def __repr__(self):
        return f"<CWPackage project_id={self.project_id} code={self.code}>"

    def to_dict(self):
        return {
            'project_id': self.project_id,
            'code': self.code,
            'name': self.name,
            'unit': self.unit,
        }

