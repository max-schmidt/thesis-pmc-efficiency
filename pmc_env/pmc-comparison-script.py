import csv, datetime, gc, json, os, random, re, subprocess, time
from pathlib import Path
import signal
from subprocess import Popen, PIPE, TimeoutExpired
from decimal import *

class TestInstanceConfig:
    def __init__(self):
        self.testNumber = ""
        self.slicingVariableCount = 0
        self.slicingVariablesList = []
        self.pmcFilePath = ""
        self.slicedFilePath = ""

    def representJSON(self):
        return dict(testNumber = self.testNumber, slicingVariableCount = self.slicingVariableCount, slicingVariablesList = self.slicingVariablesList, pmcFilePath = self.pmcFilePath, slicedFilePath = self.slicedFilePath) 

class TestConfig:
    def __init__(self):
        self.originalFileName = ""
        self.originalFilePath = ""
        self.slicerPreparedFilePath = ""
        self.originalVariableCount = 0
        self.testInstances = []

    def representJSON(self):
        return dict(originalFileName = self.originalFileName, originalFilePath = self.originalFilePath, slicerPreparedFilePath = self.slicerPreparedFilePath, originalVariableCount = self.originalVariableCount, testInstances = self.testInstances)

class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj,'representJSON'):
            return obj.representJSON()
        else:
            return json.JSONEncoder.default(self, obj)

def get_files(folder_path: Path):
    filenames = os.listdir(folder_path)
    # create a list of file paths
    file_paths = [os.path.join(folder_path, filename) for filename in filenames if filename.endswith(".dimacs")]
    return file_paths

def create_testbatch_folders(folder_path: Path):
    now = datetime.datetime.now()
    # make a new folder name (e.g. batches_20230201_153000)
    folder_name = "test_batch_" + now.strftime("%Y%m%d_%H%M%S")
    batch_folder_path = Path(str(folder_path) + "/" + folder_name)
    # create the new folders at the given path
    pmc_path = Path(str(folder_path) + "/" + folder_name + "/pmc")
    if not os.path.exists(pmc_path):
        os.makedirs(pmc_path)
    sliced_path = Path(str(folder_path) + "/" + folder_name + "/sliced")
    if not os.path.exists(sliced_path):
        os.makedirs(sliced_path)
    slicer_prepared_path = Path(str(folder_path) + "/" + folder_name + "/slicer_prepared")
    if not os.path.exists(slicer_prepared_path):
        os.makedirs(slicer_prepared_path)
    return batch_folder_path, pmc_path, slicer_prepared_path

def read_first_line(filename: str):
    with open(filename, 'r') as file:
        return file.readline()

def get_variables_count(string: str):
    # search for a number
    match = re.search(r'\d+', string)
    # extract the first occurrence of a number
    number = int(match.group(0))
    return number

# Generate the number of variables that will be cut away.
# Make a selection in different value ranges. More precisely, 3 in each quarter of the value range.
def generate_random_batches(variable_count: int):
    random_list = []
    for i in range(4):
        lower_bound = int(max(variable_count * i * 0.25, 1))
        upper_bound = int((variable_count * (i+1) * 0.25)-1)
        for i in range(3):
            while(True):
                random_number = random.randint(lower_bound, upper_bound)
                if random_number not in random_list:
                    random_list.append(random_number)
                    break
    return random_list

def generate_random_numbers(total_number: int, range_number: int):
    random_list = []
    # get a specified quantity of random numbers between 1 and the total number
    for i in range(range_number):
        while(True):
                random_number = random.randint(1, total_number)
                if random_number not in random_list:
                    random_list.append(random_number)
                    break
    return random_list

def generate_third_line(variables_list: list):
    # add prefix
    third_line = "c p show"
    # add all variables
    for item in variables_list:
        third_line = third_line + " " + str(item)
    # add suffix
    third_line = third_line + " 0"
    return third_line

def generate_pmc_file(filename: str, test_number: int, new_third_line: str):
    with open(filename, "r") as file:
        lines = file.readlines()
    # insert the new second line
    lines.insert(1, "c t pmc\n")
    # insert the new third line
    lines.insert(2, new_third_line + "\n")
    # generate new file name
    new_filename = str(filename)[:-7] + "__test-" + str(test_number).zfill(2) + ".dimacs"
    # replace the folder path to the new one
    new_filename = (str(pmc_folder_path)).join((str(new_filename)).split(str(folder_path)))
    with open(new_filename, "w", newline='\n') as file:
        file.writelines(lines)
    return new_filename

def generate_slicer_file(filename: str):
    # replace the folder path to the new one
    new_filename = (str(slicer_prepared_path)).join((str(filename)).split(str(folder_path)))
    with open(filename, "r") as input_file:
        with open(new_filename, "w", newline="\n") as output_file:
            for line in input_file:
                # remove comment lines starting with "c "
                if not line.startswith("c "):
                    output_file.write(line)
    return new_filename

def prepare_tests():
    global original_files
    # loop through the feature models
    for file in original_files:
        print("\nPrepare tests for file: " + str(file) + "\n")
        test_config = TestConfig()
        test_config.originalFilePath = file
        test_config.originalFileName = Path(file).name
        slicer_filename = generate_slicer_file(file)
        test_config.slicerPreparedFilePath = slicer_filename
        problem_description = read_first_line(file)
        total_variables_count = get_variables_count(problem_description)
        test_config.originalVariableCount = total_variables_count
        slicing_number_list = generate_random_batches(total_variables_count)
        # Create the test instances
        for i in range(len(slicing_number_list)):
            test_instance_config = TestInstanceConfig()
            test_number = i+1
            test_instance_config.testNumber = str(test_number)
            slicing_number = slicing_number_list[i]
            test_instance_config.slicingVariableCount = slicing_number
            variables_list = generate_random_numbers(total_variables_count, slicing_number)
            test_instance_config.slicingVariablesList = variables_list
            third_line = generate_third_line(variables_list)
            new_file_name = generate_pmc_file(file, test_number, third_line)
            test_instance_config.pmcFilePath = new_file_name
            test_config.testInstances.append(test_instance_config)
        test_list.append(test_config)
    # prepare csv
    with open(csv_filename, 'w', encoding='UTF8', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['file', 'test instance', 'total variables', 'slicing variables', 'slicing time #1', 'slicing time #2', 'slicing time #3', 'slicing average time', 'd4 (mc) #1 internal', 'd4 (mc) #1 time', 'd4 (mc) #1 count', 'd4 (mc) #2 internal', 'd4 (mc) #2 time', 'd4 (mc) #2 count', 'd4 (mc) #3 internal', 'd4 (mc) #3 time', 'd4 (mc) #3 count', 'd4 (mc) average time', 'd4 (mc) total time', 'dpmc (mc) #1 internal', 'dpmc (mc) #1 time', 'dpmc (mc) #1 count', 'dpmc (mc) #2 internal', 'dpmc (mc) #2 time', 'dpmc (mc) #2 count', 'dpmc (mc) #3 internal', 'dpmc (mc) #3 time', 'dpmc (mc) #3 count', 'dpmc (mc) average time', 'dpmc (mc) total time', 'ganak (mc) #1 internal', 'ganak (mc) #1 time', 'ganak (mc) #1 count', 'ganak (mc) #2 internal', 'ganak (mc) #2 time', 'ganak (mc) #2 count', 'ganak (mc) #3 internal', 'ganak (mc) #3 time', 'ganak (mc) #3 count', 'ganak (mc) average time', 'ganak (mc) total time', 'd4 (pmc) #1 internal', 'd4 (pmc) #1 time', 'd4 (pmc) #1 count', 'd4 (pmc) #2 internal', 'd4 (pmc) #2 time', 'd4 (pmc) #2 count', 'd4 (pmc) #3 internal', 'd4 (pmc) #3 time', 'd4 (pmc) #3 count', 'd4 (pmc) average time', 'dpmc (pmc) #1 internal', 'dpmc (pmc) #1 time', 'dpmc (pmc) #1 count', 'dpmc (pmc) #2 internal', 'dpmc (pmc) #2 time', 'dpmc (pmc) #2 count', 'dpmc (pmc) #3 internal', 'dpmc (pmc) #3 time', 'dpmc (pmc) #3 count', 'dpmc (pmc) average time', 'ganak (pmc) #1 internal', 'ganak (pmc) #1 time', 'ganak (pmc) #1 count', 'ganak (pmc) #2 internal', 'ganak (pmc) #2 time', 'ganak (pmc) #2 count', 'ganak (pmc) #3 internal', 'ganak (pmc) #3 time', 'ganak (pmc) #3 count', 'ganak (pmc) average time'])
    # clean up memory
    gc.collect()

# Prevent from entering in the wrong column
def fillup_row(row_list: list, required_length: int):
    if len(row_list) != required_length:
        print("The length of the current row is not what it should be at this point. Filling up the row...")
        while(len(row_list) < required_length):
            row_list.append("")

# Calculate the average time of the runs
def calc_average(number1, number2, number3):
    var_count = 3
    sum = Decimal(0)
    for number in [number1, number2, number3]:
        if number == "" or number == "0" or number == "9999":
            number = "0"
            var_count -= 1
        sum += Decimal(str(number))
    if var_count != 0:
        average = Decimal(sum) / Decimal(var_count)
        print("average:", average)
        return str(average)
    else:
        return ""

def run_tests(test_list: list):
    # loop through all files and test instances
    for current_test_config in test_list:
        print("\n**************************************************\nCurrent Model: " + str(current_test_config.originalFileName) + "\n")
        for current_test_instance in current_test_config.testInstances:
            print("\n-------------------------\nCurrent Test Instance: " + str(current_test_instance.testNumber) + " of File: " + str(current_test_config.originalFileName) + "\n")
            csv_row = []
            csv_row.append(current_test_config.originalFileName)
            csv_row.append(current_test_instance.testNumber)
            csv_row.append(current_test_config.originalVariableCount)
            csv_row.append(current_test_instance.slicingVariableCount)
            fillup_row(csv_row, 4)

            # Part 1 - seperate slicing and model counting
            # FeatureIDE slicing
            print("Start slicing...")
            print("Run 1/3")
            slicer_duration_1, slicer_file = feature_ide_slicer(current_test_instance.testNumber, current_test_instance.slicingVariablesList, current_test_config.slicerPreparedFilePath)
            current_test_instance.slicedFilePath = slicer_file
            csv_row.append(slicer_duration_1)
            fillup_row(csv_row, 5)
            if slicer_file:
                print("Run 2/3")
                slicer_duration_2 = feature_ide_slicer((str(current_test_instance.testNumber)+"b"), current_test_instance.slicingVariablesList, current_test_config.slicerPreparedFilePath)[0]
                csv_row.append(slicer_duration_2)
                fillup_row(csv_row, 6)
                print("Run 3/3")
                slicer_duration_3 = feature_ide_slicer((str(current_test_instance.testNumber)+"c"), current_test_instance.slicingVariablesList, current_test_config.slicerPreparedFilePath)[0]
                csv_row.append(slicer_duration_3)
                fillup_row(csv_row, 7)
                slicer_average = calc_average(slicer_duration_1, slicer_duration_2, slicer_duration_3)
                csv_row.append(slicer_average)
                fillup_row(csv_row, 8)

                # d4 mc
                print('Start d4 model counting...')
                print("Run 1/3")
                d4_mc_internal_1, d4_mc_external_1, d4_mc_count_1 = d4_mc(slicer_file)
                csv_row.append(d4_mc_internal_1)
                csv_row.append(d4_mc_external_1)
                csv_row.append(d4_mc_count_1)
                fillup_row(csv_row, 11)
                if d4_mc_count_1:
                    print("Run 2/3")
                    d4_mc_internal_2, d4_mc_external_2, d4_mc_count_2 = d4_mc(slicer_file)
                    csv_row.append(d4_mc_internal_2)
                    csv_row.append(d4_mc_external_2)
                    csv_row.append(d4_mc_count_2)
                    fillup_row(csv_row, 14)
                    print("Run 3/3")
                    d4_mc_internal_3, d4_mc_external_3, d4_mc_count_3 = d4_mc(slicer_file)
                    csv_row.append(d4_mc_internal_3)
                    csv_row.append(d4_mc_external_3)
                    csv_row.append(d4_mc_count_3)
                    fillup_row(csv_row, 17)
                    print("Calculate average")
                    d4_mc_average = calc_average(d4_mc_external_1, d4_mc_external_2, d4_mc_external_3)
                    d4_mc_sum = Decimal(slicer_average) + Decimal(d4_mc_average)
                    csv_row.append(d4_mc_average)
                    csv_row.append(d4_mc_sum)
                    fillup_row(csv_row, 19)
                else:
                    print("> Skipping run 2 and 3.")
                    fillup_row(csv_row, 19)
                
                # dpmc mc
                print('Start dpmc model counting...')
                print("Run 1/3")
                dpmc_mc_internal_1, dpmc_mc_external_1, dpmc_mc_count_1 = dpmc_mc(slicer_file)
                csv_row.append(dpmc_mc_internal_1)
                csv_row.append(dpmc_mc_external_1)
                csv_row.append(dpmc_mc_count_1)
                fillup_row(csv_row, 22)
                if dpmc_mc_count_1:
                    print("Run 2/3")
                    dpmc_mc_internal_2, dpmc_mc_external_2, dpmc_mc_count_2 = dpmc_mc(slicer_file)
                    csv_row.append(dpmc_mc_internal_2)
                    csv_row.append(dpmc_mc_external_2)
                    csv_row.append(dpmc_mc_count_2)
                    fillup_row(csv_row, 25)
                    print("Run 3/3")
                    dpmc_mc_internal_3, dpmc_mc_external_3, dpmc_mc_count_3 = dpmc_mc(slicer_file)
                    csv_row.append(dpmc_mc_internal_3)
                    csv_row.append(dpmc_mc_external_3)
                    csv_row.append(dpmc_mc_count_3)
                    fillup_row(csv_row, 28)
                    print("Calculate average")
                    dpmc_mc_average = calc_average(dpmc_mc_external_1, dpmc_mc_external_2, dpmc_mc_external_3)
                    dpmc_mc_sum = Decimal(slicer_average) + Decimal(dpmc_mc_average)
                    csv_row.append(dpmc_mc_average)
                    csv_row.append(dpmc_mc_sum)
                    fillup_row(csv_row, 30)
                else:
                    print("> Skipping run 2 and 3.")
                    fillup_row(csv_row, 30)

                # ganak mc
                print('Start ganak model counting...')
                print("Run 1/3")
                ganak_mc_internal_1, ganak_mc_external_1, ganak_mc_count_1 = ganak_mc(slicer_file)
                csv_row.append(ganak_mc_internal_1)
                csv_row.append(ganak_mc_external_1)
                csv_row.append(ganak_mc_count_1)
                fillup_row(csv_row, 33)
                if ganak_mc_count_1:
                    print("Run 2/3")
                    ganak_mc_internal_2, ganak_mc_external_2, ganak_mc_count_2 = ganak_mc(slicer_file)
                    csv_row.append(ganak_mc_internal_2)
                    csv_row.append(ganak_mc_external_2)
                    csv_row.append(ganak_mc_count_2)
                    fillup_row(csv_row, 36)
                    print("Run 3/3")
                    ganak_mc_internal_3, ganak_mc_external_3, ganak_mc_count_3 = ganak_mc(slicer_file)
                    csv_row.append(ganak_mc_internal_3)
                    csv_row.append(ganak_mc_external_3)
                    csv_row.append(ganak_mc_count_3)
                    fillup_row(csv_row, 39)
                    print("Calculate average")
                    ganak_mc_average = calc_average(ganak_mc_external_1, ganak_mc_external_2, ganak_mc_external_3)
                    ganak_mc_sum = Decimal(slicer_average) + Decimal(ganak_mc_average)
                    csv_row.append(ganak_mc_average)
                    csv_row.append(ganak_mc_sum)
                    fillup_row(csv_row, 41)
                else:
                    print("> Skipping run 2 and 3.")
                    fillup_row(csv_row, 41)

            # If slicing fails the first time:
            else:
                print("> Do not make any further slicing attempts. Skipping the model counting (mc) steps for this test instance.")
                fillup_row(csv_row, 41)

            # Part 2 - projected model counting
            pmc_file = current_test_instance.pmcFilePath
            # d4 pmc
            print('Start d4 projected model counting...')
            print("Run 1/3")
            d4_pmc_internal_1, d4_pmc_external_1, d4_pmc_count_1 = d4_pmc(pmc_file)
            csv_row.append(d4_pmc_internal_1)
            csv_row.append(d4_pmc_external_1)
            csv_row.append(d4_pmc_count_1)
            fillup_row(csv_row, 44)
            if d4_pmc_count_1:
                print("Run 2/3")
                d4_pmc_internal_2, d4_pmc_external_2, d4_pmc_count_2 = d4_pmc(pmc_file)
                csv_row.append(d4_pmc_internal_2)
                csv_row.append(d4_pmc_external_2)
                csv_row.append(d4_pmc_count_2)
                fillup_row(csv_row, 47)
                print("Run 3/3")
                d4_pmc_internal_3, d4_pmc_external_3, d4_pmc_count_3 = d4_pmc(pmc_file)
                csv_row.append(d4_pmc_internal_3)
                csv_row.append(d4_pmc_external_3)
                csv_row.append(d4_pmc_count_3)
                fillup_row(csv_row, 50)
                print("Calculate average")
                d4_pmc_average = calc_average(d4_pmc_external_1, d4_pmc_external_2, d4_pmc_external_3)
                csv_row.append(d4_pmc_average)
                fillup_row(csv_row, 51)
            else:
                print("> Skipping run 2 and 3.")
                fillup_row(csv_row, 51)

            # dpmc pmc
            print('Start dpmc projected model counting...')
            print("Run 1/3")
            dpmc_pmc_internal_1, dpmc_pmc_external_1, dpmc_pmc_count_1 = dpmc_pmc(pmc_file)
            csv_row.append(dpmc_pmc_internal_1)
            csv_row.append(dpmc_pmc_external_1)
            csv_row.append(dpmc_pmc_count_1)
            fillup_row(csv_row, 54)
            if dpmc_pmc_count_1:
                print("Run 2/3")
                dpmc_pmc_internal_2, dpmc_pmc_external_2, dpmc_pmc_count_2 = dpmc_pmc(pmc_file)
                csv_row.append(dpmc_pmc_internal_2)
                csv_row.append(dpmc_pmc_external_2)
                csv_row.append(dpmc_pmc_count_2)
                fillup_row(csv_row, 57)
                print("Run 3/3")
                dpmc_pmc_internal_3, dpmc_pmc_external_3, dpmc_pmc_count_3 = dpmc_pmc(pmc_file)
                csv_row.append(dpmc_pmc_internal_3)
                csv_row.append(dpmc_pmc_external_3)
                csv_row.append(dpmc_pmc_count_3)
                fillup_row(csv_row, 60)
                print("Calculate average")
                dpmc_pmc_average = calc_average(dpmc_pmc_external_1, dpmc_pmc_external_2, dpmc_pmc_external_3)
                csv_row.append(dpmc_pmc_average)
                fillup_row(csv_row, 61)
            else:
                print("> Skipping run 2 and 3.")
                fillup_row(csv_row, 61)

            # ganak pmc
            print('Start ganak projected model counting...')
            print("Run 1/3")
            ganak_pmc_internal_1, ganak_pmc_external_1, ganak_pmc_count_1 = ganak_pmc(pmc_file)
            csv_row.append(ganak_pmc_internal_1)
            csv_row.append(ganak_pmc_external_1)
            csv_row.append(ganak_pmc_count_1)
            fillup_row(csv_row, 64)
            if ganak_pmc_count_1:
                print("Run 2/3")
                ganak_pmc_internal_2, ganak_pmc_external_2, ganak_pmc_count_2 = ganak_pmc(pmc_file)
                csv_row.append(ganak_pmc_internal_2)
                csv_row.append(ganak_pmc_external_2)
                csv_row.append(ganak_pmc_count_2)
                fillup_row(csv_row, 67)
                print("Run 3/3")
                ganak_pmc_internal_3, ganak_pmc_external_3, ganak_pmc_count_3 = ganak_pmc(pmc_file)
                csv_row.append(ganak_pmc_internal_3)
                csv_row.append(ganak_pmc_external_3)
                csv_row.append(ganak_pmc_count_3)
                fillup_row(csv_row, 70)
                print("Calculate average")
                ganak_pmc_average = calc_average(ganak_pmc_external_1, ganak_pmc_external_2, ganak_pmc_external_3)
                csv_row.append(ganak_pmc_average)
                fillup_row(csv_row, 71)
            else:
                print("> Skipping run 2 and 3.")
                fillup_row(csv_row, 71)
            
            # write results row to file
            with open(csv_filename, 'a', encoding='UTF8', newline='') as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(csv_row)

# slicing (FeatureIDE slicer)
def feature_ide_slicer(current_test_number: str, feature_list: list, current_file: str):
    cmd_prefix = 'java -jar ./slicer/slicer.jar '
    # prepare the arguments
    testIdentifier = "test-" + str(current_test_number)
    cleaned_feature_list = " ".join(str(x) for x in feature_list)
    cmd = str(cmd_prefix) + str(current_file) + " " + str(testIdentifier) + " " + str(cleaned_feature_list)
    # advanced subprocess handling to be sure that the subprocesses are killed
    with Popen(cmd, shell=True, stdout=PIPE, preexec_fn=os.setsid) as process:
        try:
            # START TIMING
            start_time = time.time()
            cmd_output = process.communicate(timeout=subprocess_timeout)[0].decode(cmd_encoding)
            end_time = time.time()
            # END TIMING
            match_filename = re.search(r'Filepath:\s(.+)', cmd_output)
            if match_filename:
                sliced_filename = match_filename.group(1)
                duration = end_time - start_time
                print('time ' + str(duration))
                return duration, sliced_filename
        except TimeoutExpired:
            os.killpg(process.pid, signal.SIGINT) # send signal to the process group
            process.communicate()
            print('Timeout')
            return "9999", ""
        except:
            print('Error')
            return "", ""

# model counting
# d4
def d4_mc(current_file: str):
    cmd_prefix = './d4/bin/d4_static -i '
    cmd_suffix = ' -m counting'
    cmd = str(cmd_prefix) + str(current_file) + str(cmd_suffix)
    with Popen(cmd, shell=True, stdout=PIPE, preexec_fn=os.setsid) as process:
        try:
            # START TIMING
            start_time = time.time()
            cmd_output = process.communicate(timeout=subprocess_timeout)[0].decode(cmd_encoding)
            end_time = time.time()
            # END TIMING
            match_count = re.search(r's\s(\d+)', cmd_output)
            match_time = re.search(r'c\sFinal\stime\:\s((\d|\.)+)', cmd_output)
            if match_count and match_time:
                count = match_count.group(1)
                own_time = match_time.group(1)
                print('internal ' + str(own_time))
                duration = end_time - start_time
                print('external ' + str(duration))
                return own_time, duration, count
            else:
                print('Invalid Output')
                return "", "", ""
        except TimeoutExpired:
            os.killpg(process.pid, signal.SIGINT) # send signal to the process group
            process.communicate()
            print('Timeout')
            return "9999", "9999", ""
        except:
            print('Error')
            return "", "", ""

# dpmc
def dpmc_mc(current_file: str):
    cmd_prefix = './dpmc/bin/driver.py --cluster=tu --maxrss=4 --tmpdir=./dpmc/tmp --task=mc --mp=1 '
    cmd = str(cmd_prefix) + str(current_file)
    with Popen(cmd, shell=True, stdout=PIPE, preexec_fn=os.setsid) as process:
        try:
            # START TIMING
            start_time = time.time()
            cmd_output = process.communicate(timeout=subprocess_timeout)[0].decode(cmd_encoding)
            end_time = time.time()
            # END TIMING
            match_count = re.search(r'c\ss\sexact\sarb\sint\s(\d+)', cmd_output)
            match_time = re.search(r'c\s(preprocessor\s)?seconds(\:)?(\s)*(?P<time>(\d|\.)+)', cmd_output)
            if match_count and match_time:
                count = match_count.group(1)
                own_time = match_time.group('time')
                print('internal ' + str(own_time))
                duration = end_time - start_time
                print('external ' + str(duration))
                return own_time, duration, count
            else:
                print('Invalid Output')
                return "", "", ""
        except TimeoutExpired:
            os.killpg(process.pid, signal.SIGINT) # send kill signal to the process group
            process.communicate()
            try:
                kill_dpmc_cmd = r"kill $(ps aux | grep '[/]dpmc/bin/pmc' | awk '{print $2}')"
                subprocess.call(kill_dpmc_cmd, shell=True, timeout=subprocess_timeout)
            except:
                print('Could not kill process')
            print('Timeout')
            return "9999", "9999", ""
        except:
            print('Error')
            return "", "", ""

# ganak
def ganak_mc(current_file: str):
    cmd_prefix = './ganak/bin/starexec_run_track3_conf2_mod.sh '
    cmd = str(cmd_prefix) + str(current_file)
    with Popen(cmd, shell=True, stdout=PIPE, preexec_fn=os.setsid) as process:
        try:
            # START TIMING
            start_time = time.time()
            cmd_output = process.communicate(timeout=subprocess_timeout)[0].decode(cmd_encoding)
            end_time = time.time()
            # END TIMING
            match_count = re.search(r'c\ss\sexact\sarb\sint\s(\d+)', cmd_output)
            match_time = re.search(r'c\so\sc\stime\:\s((\d|\.)+)', cmd_output)
            if match_count and match_time:
                count = match_count.group(1)
                own_time = match_time.group(1)
                print('internal ' + str(own_time))
                duration = end_time - start_time
                print('external ' + str(duration))
                return own_time, duration, count
            else:
                print('Invalid Output')
                return "", "", ""
        except TimeoutExpired:
            os.killpg(process.pid, signal.SIGINT) # send signal to the process group
            process.communicate()
            print('Timeout')
            return "9999", "9999", ""
        except:
            print('Error')
            return "", "", ""

# projected model counting
# d4
def d4_pmc(current_file: str):
    cmd_prefix = './d4/bin/d4_static -i '
    cmd_suffix = ' -m projMC'
    cmd = str(cmd_prefix) + str(current_file) + str(cmd_suffix)
    with Popen(cmd, shell=True, stdout=PIPE, preexec_fn=os.setsid) as process:
        try:
            # START TIMING
            start_time = time.time()
            cmd_output = process.communicate(timeout=subprocess_timeout)[0].decode(cmd_encoding)
            end_time = time.time()
            # END TIMING
            match_count = re.search(r's\s(\d+)', cmd_output)
            match_time = re.search(r'c\s\[PROJMC\]\sFinal\stime\:\s((\d|\.)+)', cmd_output)
            if match_count and match_time:
                count = match_count.group(1)
                own_time = match_time.group(1)
                print('internal ' + str(own_time))
                duration = end_time - start_time
                print('external ' + str(duration))
                return own_time, duration, count
            else:
                print('Invalid Output')
                return "", "", ""
        except TimeoutExpired:
            os.killpg(process.pid, signal.SIGINT) # send signal to the process group
            process.communicate()
            print('Timeout')
            return "9999", "9999", ""
        except:
            print('Error')
            return "", "", ""

# dpmc
def dpmc_pmc(current_file: str):
    cmd_prefix = './dpmc/bin/driver.py --cluster=tu --maxrss=4 --tmpdir=./dpmc/tmp --task=pmc --mp=1 '
    cmd = str(cmd_prefix) + str(current_file)
    with Popen(cmd, shell=True, stdout=PIPE, preexec_fn=os.setsid) as process:
        try:
            # START TIMING
            start_time = time.time()
            cmd_output = process.communicate(timeout=subprocess_timeout)[0].decode(cmd_encoding)
            end_time = time.time()
            # END TIMING
            match_count = re.search(r'c\ss\sexact\sarb\sint\s(\d+)', cmd_output)
            match_time = re.search(r'c\s(preprocessor\s)?seconds(\:)?(\s)*(?P<time>(\d|\.)+)', cmd_output)
            if match_count and match_time:
                count = match_count.group(1)
                own_time = match_time.group('time')
                print('internal ' + str(own_time))
                duration = end_time - start_time
                print('external ' + str(duration))
                return own_time, duration, count
            else:
                print('Invalid Output')
                return "", "", ""
        except TimeoutExpired:
            os.killpg(process.pid, signal.SIGINT) # send signal to the process group
            process.communicate()
            try:
                kill_dpmc_cmd = r"kill $(ps aux | grep '[/]dpmc/bin/pmc' | awk '{print $2}')"
                subprocess.call(kill_dpmc_cmd, shell=True, timeout=subprocess_timeout)
            except:
                print('Could not kill process')
            print('Timeout')
            return "9999", "9999", ""
        except:
            print('Error')
            return "", "", ""

# ganak
def ganak_pmc(current_file: str):
    cmd_prefix = './ganak/bin/starexec_run_track3_conf2_mod.sh '
    cmd = str(cmd_prefix) + str(current_file)
    with Popen(cmd, shell=True, stdout=PIPE, preexec_fn=os.setsid) as process:
        try:
            # START TIMING
            start_time = time.time()
            cmd_output = process.communicate(timeout=subprocess_timeout)[0].decode(cmd_encoding)
            end_time = time.time()
            # END TIMING
            match_count = re.search(r'c\ss\sexact\sarb\sint\s(\d+)', cmd_output)
            match_time = re.search(r'c\so\sc\stime\:\s((\d|\.)+)', cmd_output)
            if match_count and match_time:
                count = match_count.group(1)
                own_time = match_time.group(1)
                print('internal ' + str(own_time))
                duration = end_time - start_time
                print('external ' + str(duration))
                return own_time, duration, count
            else:
                print('Invalid Output')
                return "", "", ""
        except TimeoutExpired:
            os.killpg(process.pid, signal.SIGINT) # send signal to the process group
            process.communicate()
            print('Timeout')
            return "9999", "9999", ""
        except:
            print('Error')
            return "", "", ""


# MAIN
# prepare
cmd_encoding = os.device_encoding(0)
subprocess_timeout = 1500
folder_path = Path(str(os.getcwd()) + '/models')
original_files = get_files(folder_path)
batch_folder_path, pmc_folder_path, slicer_prepared_path = create_testbatch_folders(folder_path)
csv_filename = os.path.join(batch_folder_path, 'results.csv')
test_list = []
prepare_tests()
# run
run_tests(test_list)
print("Done.")
