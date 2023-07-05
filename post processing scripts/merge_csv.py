from decimal import Decimal
import os
import csv
from pathlib import Path

def AddMedians(current_row: list):
    #ganak pmc
    val1, val2, val3, median =  0, 0, 0, 0
    val1 = current_row[62]
    val2 = current_row[65]
    val3 = current_row[68]
    if(val1 == '9999'):
        median = '9999'
    elif(val1):
        median = sorted([Decimal(val1), Decimal(val2), Decimal(val3)])[1]
    else:
        median = ''
    current_row.insert(71, median)

    #dpmc pmc
    val1, val2, val3, median =  0, 0, 0, 0
    val1 = current_row[52]
    val2 = current_row[55]
    val3 = current_row[58]
    if(val1 == '9999'):
        median = '9999'
    elif(val1):
        median = sorted([Decimal(val1), Decimal(val2), Decimal(val3)])[1]
    else:
        median = ''
    current_row.insert(61, median)

    #d4 pmc
    val1, val2, val3, median =  0, 0, 0, 0
    val1 = current_row[42]
    val2 = current_row[45]
    val3 = current_row[48]
    if(val1 == '9999'):
        median = '9999'
    elif(val1):
        median = sorted([Decimal(val1), Decimal(val2), Decimal(val3)])[1]
    else:
        median = ''
    current_row.insert(51, median)

    #ganak mc
    val1, val2, val3, median =  0, 0, 0, 0
    val1 = current_row[31]
    val2 = current_row[34]
    val3 = current_row[37]
    if(val1 == '9999'):
        median = '9999'
    elif(val1):
        median = sorted([Decimal(val1), Decimal(val2), Decimal(val3)])[1]
    else:
        median = ''
    current_row.insert(40, median)

    #dpmc mc
    val1, val2, val3, median =  0, 0, 0, 0
    val1 = current_row[20]
    val2 = current_row[23]
    val3 = current_row[26]
    if(val1 == '9999'):
        median = '9999'
    elif(val1):
        median = sorted([Decimal(val1), Decimal(val2), Decimal(val3)])[1]
    else:
        median = ''
    current_row.insert(29, median)

    #d4 mc
    val1, val2, val3, median =  0, 0, 0, 0
    val1 = current_row[9]
    val2 = current_row[12]
    val3 = current_row[15]
    if(val1 == '9999'):
        median = '9999'
    elif(val1):
        median = sorted([Decimal(val1), Decimal(val2), Decimal(val3)])[1]
    else:
        median = ''
    current_row.insert(18, median)

    #slicer
    val1, val2, val3, median =  0, 0, 0, 0
    val1 = current_row[4]
    val2 = current_row[5]
    val3 = current_row[6]
    if(val1 == '9999'):
        median = '9999'
    elif(val1):
        median = sorted([Decimal(val1), Decimal(val2), Decimal(val3)])[1]
    else:
        median = ''
    current_row.insert(8, median)

    return current_row

def CalculateMedianTotal(current_row: list):
    slice_time = current_row[8]

    d4_time = current_row[19]
    if slice_time == '9999' or d4_time == '9999':
        current_row[20] = '9999'
    elif slice_time == '' or d4_time == '':
        current_row[20] = ''
    else:
        current_row[20] = Decimal(slice_time) + Decimal(d4_time)

    dpmc_time = current_row[31]
    if slice_time == '9999' or dpmc_time == '9999':
        current_row[32] = '9999'
    elif slice_time == '' or dpmc_time == '':
        current_row[32] = ''
    else:
        current_row[32] = Decimal(slice_time) + Decimal(dpmc_time)

    ganak_time = current_row[43]
    if slice_time == '9999' or ganak_time == '9999':
        current_row[44] = '9999'
    elif slice_time == '' or ganak_time == '':
        current_row[44] = ''
    else:
        current_row[44] = Decimal(slice_time) + Decimal(ganak_time)

    return current_row

# Path to directory containing CSV files
path = Path(r'<insert_path>')

# Get list of all CSV files in directory
csv_files = [f for f in os.listdir(path) if f.endswith('.csv')]

# Create a list to store data from all CSV files
data = []

# Loop through CSV files and read data into list
for csv_file in csv_files:
    with open(os.path.join(path, csv_file), 'r') as f:
        csv_reader = csv.reader(f)
        next(csv_reader)  # skip header row
        for row in csv_reader:
            # add median column
            new_row = AddMedians(row)
            new_row = CalculateMedianTotal(new_row)
            data.append(new_row)

# Sort data
data.sort(key=lambda x: x[0])
data.sort(key=lambda x: int(x[2]))

# Write data to new CSV file
with open(r'<insert_path>', 'w', encoding='UTF8', newline='') as f:
    csv_writer = csv.writer(f)
    csv_writer.writerow(['file', 'test instance', 'total variables', 'slicing variables', 'slicing time #1', 'slicing time #2', 'slicing time #3', 'slicing average time', 'slicing median time', 'd4 (mc) #1 internal', 'd4 (mc) #1 time', 'd4 (mc) #1 count', 'd4 (mc) #2 internal', 'd4 (mc) #2 time', 'd4 (mc) #2 count', 'd4 (mc) #3 internal', 'd4 (mc) #3 time', 'd4 (mc) #3 count', 'd4 (mc) average time', 'd4 (mc) median time', 'd4 (mc) total time', 'dpmc (mc) #1 internal', 'dpmc (mc) #1 time', 'dpmc (mc) #1 count', 'dpmc (mc) #2 internal', 'dpmc (mc) #2 time', 'dpmc (mc) #2 count', 'dpmc (mc) #3 internal', 'dpmc (mc) #3 time', 'dpmc (mc) #3 count', 'dpmc (mc) average time', 'dpmc (mc) median time', 'dpmc (mc) total time', 'ganak (mc) #1 internal', 'ganak (mc) #1 time', 'ganak (mc) #1 count', 'ganak (mc) #2 internal', 'ganak (mc) #2 time', 'ganak (mc) #2 count', 'ganak (mc) #3 internal', 'ganak (mc) #3 time', 'ganak (mc) #3 count', 'ganak (mc) average time', 'ganak (mc) median time', 'ganak (mc) total time', 'd4 (pmc) #1 internal', 'd4 (pmc) #1 time', 'd4 (pmc) #1 count', 'd4 (pmc) #2 internal', 'd4 (pmc) #2 time', 'd4 (pmc) #2 count', 'd4 (pmc) #3 internal', 'd4 (pmc) #3 time', 'd4 (pmc) #3 count', 'd4 (pmc) average time', 'd4 (pmc) median time', 'dpmc (pmc) #1 internal', 'dpmc (pmc) #1 time', 'dpmc (pmc) #1 count', 'dpmc (pmc) #2 internal', 'dpmc (pmc) #2 time', 'dpmc (pmc) #2 count', 'dpmc (pmc) #3 internal', 'dpmc (pmc) #3 time', 'dpmc (pmc) #3 count', 'dpmc (pmc) average time', 'dpmc (pmc) median time', 'ganak (pmc) #1 internal', 'ganak (pmc) #1 time', 'ganak (pmc) #1 count', 'ganak (pmc) #2 internal', 'ganak (pmc) #2 time', 'ganak (pmc) #2 count', 'ganak (pmc) #3 internal', 'ganak (pmc) #3 time', 'ganak (pmc) #3 count', 'ganak (pmc) average time', 'ganak (pmc) median time'])
    csv_writer.writerows(data)

print('Merged CSV file created!')
