#
# cc_analyze.py
# Created by Brandon Forsythe 06/10/24
# Computes creep compliance in the file the executable is placed in
#


import os
import re
from collections import defaultdict

# function extract_numeric_data:
#   given a file path, keyword, and column index, pulls all consecutive data points from the rows below
#   example: Axial LVDT1(COX1) Column in specimen.dat will return all points in that column.

def extract_numeric_data(file_path, start_keyword, column_index):
    all_data = []

    with open(file_path, 'r') as file:
        for line in file:
            if start_keyword in line:
                break

        for line in file:
            if line.strip():
                try:
                    numeric_value = float(line.split()[column_index])
                    all_data.append(numeric_value)
                except (ValueError, IndexError):
                    continue

    return all_data

def calculate_average(data_list):
    if data_list:
        return sum(data_list) / len(data_list)
    else:
        return None



cwd = os.getcwd()
print(cwd)

rap_pattern = re.compile(r"52-40\s*\d+%RAP\s*-?\d*")

matched_dirs = defaultdict(list)

for root, dirs, files in os.walk(cwd):
    for dir_name in dirs:
        if rap_pattern.match(dir_name):
            for sample_dir in ["Sample 1", "Sample 2", "Sample 3"]:
                sample_path = os.path.join(root, dir_name, sample_dir)
                if os.path.exists(sample_path):
                    matched_dirs[os.path.join(root, dir_name)].append(sample_path)

dat_files = []
for base_dir, sample_dirs in matched_dirs.items():
    for dir_path in sample_dirs:
        dat_file = os.path.join(dir_path, "specimen.dat")
        if os.path.exists(dat_file):
            dat_files.append((base_dir, dat_file))

#print(f"PER RAP HERE: {matched_dirs}\n")

for base_dir, files in matched_dirs.items():
    lvdt1_data_con = []
    lvdt2_data_con = []
    lvdt3_data_con = []
    lvdt4_data_con = []
    axial_load_con = []

    for sample_dir in files:
        dat_file = os.path.join(sample_dir, "specimen.dat")
        if os.path.exists(dat_file):
            #print(f"Found file: {dat_file}")

        #Get horizontal lvdt data
            lvdt1_data = extract_numeric_data(dat_file, start_keyword="Axial LVDT1(COX1)", column_index=3)
            lvdt2_data = extract_numeric_data(dat_file, start_keyword="Axial LVDT2(COX2)", column_index=5)
        #Get vertical lvdt data
            lvdt3_data = extract_numeric_data(dat_file, start_keyword="Axial LVDT3(COX3)", column_index=4)
            lvdt4_data = extract_numeric_data(dat_file, start_keyword="Axial LVDT4(COX4)", column_index=6)

        #Grab axial load data
            axial_load = extract_numeric_data(dat_file, start_keyword="Axial Load", column_index=2)
            

            if lvdt1_data:
                lvdt1_data_con.extend(lvdt1_data)
            if lvdt2_data:
                lvdt2_data_con.extend(lvdt2_data)
            if lvdt3_data:
                lvdt3_data_con.extend(lvdt3_data)
            if lvdt4_data:
                lvdt4_data_con.extend(lvdt4_data)
            if axial_load:
                axial_load_con.extend(axial_load)


            size_difference = len(lvdt1_data_con) - (len(lvdt1_data_con) - len(lvdt2_data_con))         # THIS IS IMPORTANT, AND REALLY BAD.
            lvdt1_data_con = lvdt1_data_con[:size_difference]


    if lvdt1_data_con:
        lvdt1_avg = sum(lvdt1_data_con) / len(lvdt1_data_con)
        #print(f"Combined average value of LVDT1 data in {base_dir}: {lvdt1_avg}")
    else:
        print(f"No numeric data found for LVDT1 in {base_dir}.")

    if lvdt2_data_con:
        lvdt2_avg = sum(lvdt2_data_con) / len(lvdt2_data_con)
        #print(f"Combined average value of LVDT2 data in {base_dir}: {lvdt2_avg}")
    else:
        print(f"No numeric data found for LVDT2 in {base_dir}.")

    if lvdt3_data_con:
        lvdt3_avg = sum(lvdt3_data_con) / len(lvdt3_data_con)
        #print(f"Combined average value of LVDT3 data in {base_dir}: {lvdt3_avg}")
    else:
        print(f"No numeric data found for LVDT3 in {base_dir}.")

    if lvdt4_data_con:
        lvdt4_avg = sum(lvdt4_data_con) / len(lvdt4_data_con)
        #print(f"Combined average value of LVDT4 data in {base_dir}: {lvdt4_avg}")
    else:
        print(f"No numeric data found for LVDT4 in {base_dir}.")

    # Compute sums of averages over the 3 specimens

    if lvdt1_avg is not None and lvdt3_avg is not None:
        horizontal_avg = lvdt1_avg + lvdt3_avg
        print(f"Combined average value of LVDT1 and LVDT3 in {base_dir}: {horizontal_avg}")
    else:
        print(f"Not enough data to compute combined average for LVDT1 and LVDT3 in {base_dir}.")

    if lvdt2_avg is not None and lvdt4_avg is not None:
        vertical_avg = lvdt2_avg + lvdt4_avg
        print(f"Combined average value of LVDT2 and LVDT4 in {base_dir}: {vertical_avg}")
    else:
        print(f"Not enough data to compute combined average for LVDT2 and LVDT4 in {base_dir}.")

    #Compute normalized horizontal and vertical deformation arrays
    # assuming "measured deformation for face == column 'Axial Displacement'

    b_avg = calculate_average(lvdt1_data_con + lvdt3_data_con)
    d_avg = calculate_average(lvdt2_data_con + lvdt4_data_con)
    p_avg = calculate_average(axial_load_con)

    horiz_def_arr = []
    vert_def_arr = []
    for i in range(len(lvdt1_data_con)):
        if i < len(lvdt2_data_con):  # Check if i is within bounds of lvdt2_data_con
            deltaX_n_i = lvdt1_data_con[i] * (lvdt1_data_con[i] / b_avg ) * (lvdt2_data_con[i] / d_avg) * (p_avg / axial_load_con[i])
            # Store deltaX_n_i in your horizontal deformation array
            horiz_def_arr.append(deltaX_n_i)
        else:
            print(f"Index {i} is out of range for lvdt2_data_con.")

    for j in range(len(lvdt2_data_con)):
        if j < len(lvdt1_data_con):  # Check if j is within bounds of lvdt1_data_con
            deltaY_n_j = lvdt3_data_con[j] * (lvdt3_data_con[j] / b_avg ) * (lvdt4_data_con[j] / d_avg) * (p_avg / axial_load_con[j])
            # Store deltaY_n_j in your vertical deformation array
            vert_def_arr.append(deltaY_n_j)
        else:
            print(f"Index {j} is out of range for lvdt1_data_con.")

print(horiz_def_arr)
print(vert_def_arr)
# Obtain average horizontal and vert deformations at 1/2 creep test time



