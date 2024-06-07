import os
import glob

# Function to extract numeric data from a column in a dat file
def extract_numeric_data(file_path, start_keyword, column_index):
    all_data = []

    with open(file_path, 'r') as file:
        # Skip lines until the start_keyword is found
        for line in file:
            if start_keyword in line:
                break

        # Extract numeric data from the remaining lines
        for line in file:
            if line.strip():  # Check if the line is not empty
                try:
                    numeric_value = float(line.split()[column_index])  # Extract data from the specified column
                    all_data.append(numeric_value)
                except (ValueError, IndexError):
                    # If the line is not numeric or doesn't have enough columns, skip it
                    continue

    return all_data

# Specify the path of the file you want to test
# Find all instances of specimen.dat inside the working directory
cwd = os.getcwd()
search_pattern = os.path.join(cwd, "**", "specimen.dat")
dat_files = glob.glob(search_pattern, recursive=True)



for file_path in dat_files:
    cox1_data_con = []
    cox2_data_con = []

    # Extract data from specified columns
    cox1_data = extract_numeric_data(file_path, start_keyword="Axial LVDT1(COX1)", column_index=3)
    cox2_data = extract_numeric_data(file_path, start_keyword="Axial LVDT3(COX3)", column_index=5)

    if cox1_data and cox2_data:
        cox1_data_con.extend(cox1_data)
        cox2_data_con.extend(cox2_data)
        print(f"Extracted numeric data from file: {file_path}")
    else:
        print(f"No numeric data found in file: {file_path}")

    # Calculate averages if data lists are not empty
    if cox1_data_con:
        cox1_avg = sum(cox1_data_con) / len(cox1_data_con)
        print(f"Average value of LVDT1 data: {cox1_avg}")
    else:
        print("No numeric data found for LVDT1.")

    if cox2_data_con:
        cox2_avg = sum(cox2_data_con) / len(cox2_data_con)
        print(f"Average value of LVDT2 data: {cox2_avg}")
    else:
        print("No numeric data found for LVDT2.")
