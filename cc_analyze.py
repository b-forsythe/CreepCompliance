# cc_analyze.py
# Created by Brandon Forsythe 06/10/24
#
# cc_analyze will compute creep compliance for all sample sets inside the folder the executable is placed.
# The results are saved within the results.txt text file, including data that was unable to run.

import os
import re
from collections import defaultdict

# Function to extract numeric data from .dat files
def extract_numeric_data(file_path, start_keyword, column_indices, displacement_threshold=-0.010, tolerance=0.001):
    all_data = defaultdict(list)
    start_collecting = False

    with open(file_path, 'r') as file:
        for line in file:
            if start_keyword in line:
                break

        for line in file:
            if line.strip():
                try:
                    columns = line.split()
                    axial_displacement = float(columns[1])  # Assuming the "Axial Displacement" is in column 1
                    if not start_collecting:
                        if abs(axial_displacement - displacement_threshold) <= tolerance:
                            start_collecting = True
                    if start_collecting:
                        for idx in column_indices:
                            all_data[idx].append(float(columns[idx]))
                except (ValueError, IndexError):
                    continue

    return all_data

# Function to calculate average of a data list
def calculate_average(data_list):
    return sum(data_list) / len(data_list) if data_list else None

# Function to compute Poisson's ratio
def calculate_poissons_ratio(horizontal_avg, vertical_avg):
    if vertical_avg == 0:
        return None
    ratio = horizontal_avg / vertical_avg
    poisson = 0.10 + 1.480 * (ratio ** 2) - 0.778 * ratio
    return poisson

# Function to calculate creep compliance
def calculate_creep_compliance(horizontal_avg, thickness_avg, load_avg, gauge_length=0.038):
    if load_avg == 0:
        return None
    creep_compliance = (horizontal_avg * thickness_avg) / (load_avg * gauge_length)
    return creep_compliance

# Function to write results to a file (clears the file first)
def clear_and_write_to_file(file_name, content):
    with open(file_name, 'w') as file:
        file.write(content + '\n')

# Start processing directories and files
cwd = os.getcwd()
output_file = os.path.join(cwd, 'results.txt')
clear_and_write_to_file(output_file, "Results of Creep Compliance and Poisson's Ratio Calculations")

rap_pattern = re.compile(r"52-40\s*\d+%RAP\s*-?\d*")
matched_dirs = defaultdict(list)

# Walk through the file structure and find directories that match the pattern
for root, dirs, files in os.walk(cwd):
    for dir_name in dirs:
        if rap_pattern.match(dir_name):
            for sample_dir in ["Sample 1", "Sample 2", "Sample 3"]:
                sample_path = os.path.join(root, dir_name, sample_dir)
                if os.path.exists(sample_path):
                    matched_dirs[os.path.join(root, dir_name)].append(sample_path)

results_content = ""

# Iterate over the matched directories
for base_dir, sample_dirs in matched_dirs.items():
    x, y = [], []
    thickness_values, load_values = [], []  # Lists to collect thickness and load

    for sample_dir in sample_dirs:
        dat_file = os.path.join(sample_dir, "specimen.dat")
        if os.path.exists(dat_file):
            data = extract_numeric_data(dat_file, start_keyword="Axial LVDT1(COX1)", column_indices=[3, 4, 5, 6])
            
            # Horizontal (1, 3) and Vertical (2, 4)
            lvdt1_data, lvdt3_data = data[3], data[4]  #bAvg
            lvdt2_data, lvdt4_data = data[5], data[6]  #pAvg

            # Validate LVDT1 data
            if lvdt1_data:
                first_lvdt = lvdt1_data[0]
                if not (0.0000492 <= first_lvdt <= 0.000748):
                    results_content += f"Reject file {base_dir}: LVDT1 out of range ({first_lvdt})\n\n"
                    continue
            
            lvdt1_avg, lvdt3_avg = calculate_average(lvdt1_data), calculate_average(lvdt3_data)
            lvdt2_avg, lvdt4_avg = calculate_average(lvdt2_data), calculate_average(lvdt4_data)

            if lvdt1_avg and lvdt3_avg:
                thickness_avg = lvdt1_avg + lvdt3_avg
                thickness_values.append(thickness_avg)
            else:
                results_content += f"Insufficient data for thickness average in {sample_dir}\n\n"

            if lvdt2_avg and lvdt4_avg:
                load_avg = lvdt2_avg + lvdt4_avg
                load_values.append(load_avg)
            else:
                results_content += f"Insufficient data for load average in {sample_dir}\n\n"

    # Sort and select middle values
    all_averages = thickness_values + load_values
    all_averages.sort()

    middle_values = all_averages[1:-1] if len(all_averages) >= 6 else all_averages

    if middle_values:
        avg_horizontal_deformation = calculate_average(middle_values)

        # Calculate creep compliance
        avg_thickness = calculate_average(thickness_values)
        avg_load = calculate_average(load_values)

        creep_compliance = calculate_creep_compliance(avg_horizontal_deformation, avg_thickness, avg_load)
        results_content += f"Creep Compliance for {base_dir}: {creep_compliance}\n"

    # Compute Poisson's ratio
    if thickness_values and load_values:
        poisson_ratio = calculate_poissons_ratio(calculate_average(thickness_values), calculate_average(load_values))
        if poisson_ratio is not None:
            results_content += f"Poisson's Ratio for {base_dir}: {poisson_ratio}\n\n"
        else:
            results_content += f"Cannot calculate Poisson's ratio for {base_dir}\n"

# Write all results to the file (overwrites)
clear_and_write_to_file(output_file, results_content)
print(f"Results written to {output_file}")
