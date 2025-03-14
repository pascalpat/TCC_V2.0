import os

def print_directory_tree(start_path, prefix='', file=None):
    """
    Recursively print the directory structure starting from the given path,
    and save it to a file.
    """
    for item in sorted(os.listdir(start_path)):
        path = os.path.join(start_path, item)
        # Format the current item
        line = f"{prefix}|-- {item}\n"
        # Print to console
        print(line, end='')
        # Write to file if specified
        if file:
            file.write(line)
        # Recurse into directories
        if os.path.isdir(path):
            print_directory_tree(path, prefix + '    ', file)

# Set the starting path to the project root
project_root = "C:/Users/patri/OneDrive/Bureau/TCC_V2.0"
output_file_path = "project_tree.txt"

# Generate the directory tree and save to a text file
with open(output_file_path, 'w') as file:
    print_directory_tree(project_root, file=file)

print(f"\nDirectory tree saved to {output_file_path}")
