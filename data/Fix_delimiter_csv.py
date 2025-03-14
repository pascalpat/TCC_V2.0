import pandas as pd

# Load the CSV file with the current delimiter
input_file = 'workers.csv'  # Replace with your file path
output_file = 'workers_new.csv'  # Output file with the new delimiter
current_delimiter = ';'  # Replace with the current delimiter
new_delimiter = ','  # Replace with the desired delimiter

# Read the CSV file
df = pd.read_csv(input_file, delimiter=current_delimiter)

# Save the file with the new delimiter
df.to_csv(output_file, sep=new_delimiter, index=False)

print(f"Delimiter changed from '{current_delimiter}' to '{new_delimiter}'. Saved as {output_file}.")
