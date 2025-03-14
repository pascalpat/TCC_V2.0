from app import create_app, db

def validate_models():
    """
    Validate SQLAlchemy models for correct relationships and foreign keys using metadata.
    """
    validation_errors = []

    # Iterate over all tables in metadata
    for table_name, table in db.metadata.tables.items():
        print(f"Validating table: {table_name}")
        try:
            # Validate columns
            for column in table.columns:
                if column.foreign_keys:
                    for fk in column.foreign_keys:
                        target_table = fk.target_fullname.split('.')[0]
                        if target_table not in db.metadata.tables:
                            validation_errors.append(f"Invalid Foreign Key: {fk} in table {table_name}")

            # Validate relationships (if applicable)
            if hasattr(table, 'relationships'):
                for rel in table.relationships:
                    if rel.target not in db.metadata.tables.values():
                        validation_errors.append(f"Invalid Relationship: {rel} in table {table_name}")

        except Exception as e:
            validation_errors.append(f"Error validating table {table_name}: {e}")

    # Output results
    if validation_errors:
        print("\nValidation Errors:")
        for error in validation_errors:
            print(f"- {error}")
    else:
        print("All tables validated successfully!")

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        validate_models()
