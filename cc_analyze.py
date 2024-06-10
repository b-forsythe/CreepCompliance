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


def get_averages():
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
        cox1_data_con = []
        cox2_data_con = []

        for sample_dir in files:
            dat_file = os.path.join(sample_dir, "specimen.dat")
            if os.path.exists(dat_file):
                #print(f"Found file: {dat_file}")
                cox1_data = extract_numeric_data(dat_file, start_keyword="Axial LVDT1(COX1)", column_index=3)
                cox2_data = extract_numeric_data(dat_file, start_keyword="Axial LVDT2(COX2)", column_index=4)

                if cox1_data:
                    cox1_data_con.extend(cox1_data)
                if cox2_data:
                    cox2_data_con.extend(cox2_data)

        if cox1_data_con:
            cox1_avg = sum(cox1_data_con) / len(cox1_data_con)
            #print(f"Combined average value of LVDT1 data in {base_dir}: {cox1_avg}")
        else:
            print(f"No numeric data found for LVDT1 in {base_dir}.")

        if cox2_data_con:
            cox2_avg = sum(cox2_data_con) / len(cox2_data_con)
            #print(f"Combined average value of LVDT2 data in {base_dir}: {cox2_avg}")
        else:
            print(f"No numeric data found for LVDT2 in {base_dir}.")

    return cox1_avg, cox2_avg


cox1_avg, cox2_avg = get_averages()

print(f"cox1_avg: {cox1_avg}   ,    cox2_avg: {cox2_avg}   \n")


