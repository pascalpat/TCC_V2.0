import os
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from app import create_app, db  # Adjust import paths based on your project structure
from app import db  # Import your SQLAlchemy db object
import pandas as pd

# Function to generate a report for all tables in the models directory
def generate_table_reports(output_file):
    """
    Generates an Excel file with metadata for all tables in the SQLAlchemy database.
    
    Args:
        output_file (str): Path to the output Excel file.
    """
    # Initialize database inspector
    engine = db.engine()
    inspector = inspect(engine)
    
    # Placeholder for table metadata
    table_reports = {}

    # Loop through all tables
    for table_name in inspector.get_table_names():
        columns = inspector.get_columns(table_name)
        constraints = inspector.get_pk_constraint(table_name)
        indexes = inspector.get_indexes(table_name)
        
        # Collect column information
        table_data = []
        for column in columns:
            field_name = column['name']
            data_type = str(column['type'])
            is_pk = '✅' if field_name in constraints.get('constrained_columns', []) else ''
            is_indexed = '✅' if any(index['column_names'] and field_name in index['column_names'] for index in indexes) else ''
            nullable = '' if column['nullable'] else 'NOT NULL'
            default = column.get('default', '')

            table_data.append({
                'Field Name': field_name,
                'Data Type': data_type,
                'Primary Key': is_pk,
                'Indexed': is_indexed,
                'Constraints': nullable,
                'Field Description': '',  # Add descriptions manually if desired
                'Notes': ''  # Add additional notes manually
            })
        
        # Convert to DataFrame
        table_reports[table_name] = pd.DataFrame(table_data)

    # Save each table's details into a new sheet in an Excel file
    with pd.ExcelWriter(output_file) as writer:
        for table_name, df in table_reports.items():
            df.to_excel(writer, sheet_name=table_name, index=False)

    print(f"Table reports saved to {output_file}")

# Example usage
if __name__ == '__main__':
    # Create the Flask app and push the application context
    app = create_app()  # Replace with your app factory function if applicable
    with app.app_context():
        output_excel_path = r'C:\Users\patri\OneDrive\Bureau\TCC_V2.0\docs\data_model.md\table_reports.xlsx'  # Specify the output file path
        generate_table_reports(output_excel_path)