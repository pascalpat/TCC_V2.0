import os
import re
import pandas as pd
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship

Base = declarative_base()

# Target folder for saving Excel files
OUTPUT_DIR = r"C:\Users\patri\OneDrive\Bureau\TCC_V2.0\docs\models"

def extract_model_details(file_path):
    """
    Extracts model details (columns and relationships) from a given SQLAlchemy model file.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    models = re.findall(r'class (\w+)\(db.Model\):', content)
    tables = []

    for model in models:
        # Extract columns
        columns = re.findall(rf'{model}.*?= db.Column\((.*?)\)', content, re.DOTALL)
        columns_data = []
        for col in columns:
            details = re.findall(r'(\w+)\((.*?)\)', col)
            data = {
                "Column Name": details[0][1] if details else "N/A",
                "Data Type": details[1][1] if len(details) > 1 else "N/A",
                "Nullable": "Yes" if 'nullable=True' in col else "No",
                "Default": re.search(r'default=(\w+)', col).group(1) if 'default=' in col else "None",
                "Description": ""
            }
            columns_data.append(data)

        # Extract relationships
        relationships = re.findall(rf'{model}.*?= db.relationship\((.*?)\)', content, re.DOTALL)
        relationships_data = []
        for rel in relationships:
            related_model = re.search(r"'(\w+)'", rel).group(1)
            direction = "Back_populates" if "back_populates" in rel else "Backref"
            relationships_data.append({
                "Relationship": "",
                "Related Model": related_model,
                "Type": "One-to-Many",  # Guessing based on relationship patterns
                "Direction": direction,
                "Description": ""
            })

        tables.append((model, columns_data, relationships_data))

    return tables

def generate_excel_for_models(tables):
    """
    Generates Excel files for each table extracted from the models.
    """
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    for table, columns, relationships in tables:
        file_path = os.path.join(OUTPUT_DIR, f"{table}_table_layout.xlsx")

        # Create DataFrames
        columns_df = pd.DataFrame(columns, columns=["Column Name", "Primary/Foreign Key", "Data Type", "Nullable", "Default", "Description"])
        relationships_df = pd.DataFrame(relationships, columns=["Relationship", "Related Model", "Type", "Direction", "Description"])

        # Write to Excel
        with pd.ExcelWriter(file_path) as writer:
            columns_df.to_excel(writer, index=False, sheet_name="Columns")
            relationships_df.to_excel(writer, index=False, sheet_name="Relationships")

def process_models_folder(folder_path):
    """
    Processes all model files in the given folder.
    """
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.py') and not file.startswith('__'):
                file_path = os.path.join(root, file)
                tables = extract_model_details(file_path)
                generate_excel_for_models(tables)

# Run the script for the models folder
process_models_folder(r'C:\Users\patri\OneDrive\Bureau\TCC_V2.0\app\models')
