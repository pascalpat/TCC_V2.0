from sqlalchemy.inspection import inspect
from app import db  # Adjust based on your app structure

def validate_models():
    for cls in db.Model._decl_class_registry.values():
        if hasattr(cls, '__tablename__'):
            inspector = inspect(cls)
            print(f"Validating table: {cls.__tablename__}")
            for column in inspector.columns:
                if column.foreign_keys:
                    for fk in column.foreign_keys:
                        print(f"  Foreign Key: {fk} -> {fk.target_fullname}")
                        assert fk.target_fullname in db.metadata.tables, "Invalid Foreign Key!"
            print("Relationships:")
            for rel in inspector.relationships:
                print(f"  Relationship: {rel.key} -> {rel.target}")
