from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base
from app import db  # Replace with your actual database instance

def generate_model_schema_report(output_file):
    """
    Generate a schema report from the SQLAlchemy models before migration.
    
    Args:
        output_file (str): Path to save the schema report as a text file.
    """
    Base = declarative_base()  # Use SQLAlchemy's declarative base
    metadata = Base.metadata  # Retrieve metadata from models

    with open(output_file, 'w') as f:
        for table in metadata.sorted_tables:
            f.write(f"Table: {table.name}\n")
            f.write("=" * 40 + "\n")

            # Columns
            for column in table.columns:
                column_details = f"  - {column.name} ({column.type})"
                if column.primary_key:
                    column_details += " [PK]"
                if not column.nullable:
                    column_details += " [NOT NULL]"
                if column.default is not None:
                    column_details += f" [Default: {column.default}]"
                f.write(column_details + "\n")

            # Foreign Keys
            foreign_keys = [fk for fk in column.foreign_keys for column in table.columns]
            if foreign_keys:
                f.write("  Foreign Keys:\n")
                for fk in foreign_keys:
                    f.write(f"    - {fk.column.name} -> {fk.column.table.name}.{fk.column.name}\n")

            # Indexes
            if table.indexes:
                f.write("  Indexes:\n")
                for index in table.indexes:
                    f.write(f"    - {index.name}: {', '.join(c.name for c in index.columns)}\n")

            f.write("\n")

# Example Usage
if __name__ == "__main__":
    output_path = "model_schema_report.txt"  # Path to save the report
    generate_model_schema_report(output_path)
    print(f"Model schema report generated at {output_path}")
