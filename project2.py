#Mayar Masalmeh || 1211246
#Lana Musaffer || 1210455

from datetime import datetime, timedelta
import statistics
import csv
import re

class MedicalTest:
    def __init__(self, name, test_range, unit, duration):
        self.name = name
        self.test_range = self.validate_range(test_range)
        self.unit = unit
        self.duration = duration
        self.start_time = datetime.now()
        self.end_time = self.start_time + self.parse_duration(duration)

    def parse_duration(self, duration):
        try:
            days, hours, minutes = map(int, duration.split('-'))
            return timedelta(days=days, hours=hours, minutes=minutes)
        except ValueError:
            raise ValueError("Invalid duration format! Ensure it's in DD-hh-mm format.")

    def validate_range(self, test_range):
        range_pattern = re.compile(
            r"(?:<|>|\d+(\.\d+)?)(?:\s*\d+(\.\d+)?)*(?:\s*,\s*(?:<|>|\d+(\.\d+)?)(?:\s*\d+(\.\d+)?))*")

        if not range_pattern.fullmatch(test_range):
            raise ValueError(
                "Invalid range format! Ensure it matches the format of '> 100', '< 120', or '13.8 < value < 17.2'.")

        parts = re.findall(r'(<|>|[\d\.]+(?:\s*<\s*[\d\.]+)?)', test_range)
        numeric_ranges = []
        for part in parts:
            if part in ['<', '>']:
                continue
            values = re.findall(r'[\d\.]+', part)
            numeric_ranges.extend(float(value) for value in values)

        if len(numeric_ranges) % 2 == 0:
            for i in range(0, len(numeric_ranges) - 1, 2):
                if numeric_ranges[i] > numeric_ranges[i + 1]:
                    raise ValueError(
                        f"Invalid range! Value {numeric_ranges[i]} is greater than {numeric_ranges[i + 1]}.")

        return test_range

    def get_turnaround_time(self):
        total_duration = self.end_time - self.start_time
        days = total_duration.days
        hours, remainder = divmod(total_duration.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        return f"{days:02d}-{hours:02d}-{minutes:02d}"

    def save_to_file(self, file):
        test_entry = f"Name: {self.name}; Range: {self.test_range}; Unit: {self.unit}, Turnaround Time: {self.get_turnaround_time()}\n"
        file.write(test_entry)

##########################################option 1###########################################
def get_test_input():
    name = input("Enter the test name: ").strip()
    unit = input("Enter the unit: ").strip()
    duration = input("Enter the nominal test duration (DD-hh-mm): ").strip()

    while not validate_duration(duration):
        print("Invalid duration format! Please enter in the format DD-hh-mm.")
        duration = input("Enter the nominal test duration (DD-hh-mm): ").strip()

    while True:
        test_range = input("Enter the test range: ").strip()
        try:
            return MedicalTest(name, test_range, unit, duration)
        except ValueError as e:
            print(f"Error: {e}")
            print("Please correct the test range and try again.")


def save_test():
    # Get test details from user
    user_test = get_test_input()

    # Save the test details to the file
    with open("medicalTest.txt", "a") as file:
        user_test.save_to_file(file)

    print("Medical test details and turnaround times saved successfully.")

##############################################option 2##############################################
def get_record_input(test_units):
    while True:
        patient_id = input("Enter patient ID (7 digits): ").strip()
        if patient_id.isdigit() and len(patient_id) == 7:
            break
        else:
            print("Invalid ID! Please enter a 7-digit numeric ID:")

    print("Available test names:")
    for name in test_units:
        print(name.capitalize())

    # Normalize test names to lowercase for comparison
    test_units_lower = {name.lower(): name for name in test_units}

    while True:
        test_name_input = input("Enter the test name from the list above: ").strip().lower()
        if test_name_input in test_units_lower:
            test_name = test_units_lower[test_name_input].capitalize()  # Capitalize for display purposes
            expected_unit = test_units[test_name_input]
            break
        else:
            print("Invalid test name! Please enter a valid test name from the list.")

    while True:
        test_datetime = input("Enter test date and time (YYYY-MM-DD hh:mm): ").strip()
        if validate_datetime(test_datetime):
            test_datetime_obj = datetime.strptime(test_datetime, "%Y-%m-%d %H:%M")
            break
        else:
            print("Invalid date and time format! Please enter in the format YYYY-MM-DD hh:mm.")

    while True:
        result_value = input("Enter numeric result value: ").strip()
        if validate_numeric(result_value):
            break
        else:
            print("Invalid result value! Please enter a numeric value.")

    while True:
        results_unit = input("Enter results unit: ").strip()
        if results_unit == expected_unit:
            break
        else:
            print(f"Invalid unit! The correct unit for {test_name} is {expected_unit}.")

    status = input("Enter status (Pending, Completed, or Reviewed): ").strip().capitalize()

    if status == "Completed":
        while True:
            results_datetime = input("Enter results date and time (YYYY-MM-DD hh:mm): ").strip()
            if validate_datetime(results_datetime):
                results_datetime_obj = datetime.strptime(results_datetime, "%Y-%m-%d %H:%M")
                if results_datetime_obj >= test_datetime_obj:
                    break
                else:
                    print("Error: Results date and time cannot be before the test date and time.")
            else:
                print("Invalid date and time format! Please enter in the format YYYY-MM-DD hh:mm.")
    else:
        results_datetime = ""

    return {
        "patient_id": patient_id,
        "test_name": test_name,
        "test_datetime": test_datetime,
        "result_value": result_value,
        "results_unit": results_unit,
        "status": status,
        "results_datetime": results_datetime
    }

def save_record(record, filename="medicalRecord.txt"):
    # Ensure the 'results_unit' is set to a default if not present
    results_unit = record.get('results_unit', 'N/A')

    with open(filename, "a") as file:
        if record["status"] == "Completed":
            file.write(
                f"{record['patient_id']}: {record['test_name']}, {record['test_datetime']}, {record['result_value']}, {results_unit}, {record['status']}, {record['results_datetime']}\n")
        else:
            file.write(
                f"{record['patient_id']}: {record['test_name']}, {record['test_datetime']}, {record['result_value']}, {results_unit}, {record['status']}\n")



def load_tests(filename="medicalTest.txt"):
    tests = {}
    try:
        with open(filename, "r") as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue

                # Split the line into parts based on semicolons
                parts = line.split(";")

                if len(parts) >= 3:
                    try:
                        # Extract and clean name part
                        name_part = parts[0].strip()
                        name = name_part.split("Name:")[1].strip().lower()  # Convert to lowercase

                        # Extract and clean unit part
                        unit_part = parts[2].strip()
                        if "Unit:" in unit_part:
                            unit = unit_part.split("Unit:")[1].strip().split(",")[0].strip()
                            tests[name] = unit
                        else:
                            print(f"Unit part not found in line: {line}")
                            continue
                    except IndexError as e:
                        print(f"Error processing line: {line} - {e}")
                else:
                    print(f"Invalid line format: {line} - Not enough parts. Skipping this entry.")
    except FileNotFoundError:
        print(f"File {filename} not found.")
    return tests

def save_record_info():
    test_units = load_tests()

    if not test_units:
        print("No test names available! Please add a medical test first.")
        return

    new_record = get_record_input(test_units)
    save_record(new_record)
    print("Medical record added successfully.")

############################################option 3#########################################################
def load_records(filename="medicalRecord.txt"):
    records = []
    try:
        with open(filename, "r") as file:
            for line in file:
                parts = line.strip().split(", ")
                if len(parts) < 5:
                    continue

                patient_id, test_name = parts[0].split(":")
                patient_id = patient_id.strip()
                test_name = test_name.strip()
                test_datetime = parts[1].strip()
                result_value = parts[2].strip()
                result_unit = parts[3].strip() if len(parts) > 3 else 'N/A'
                status = parts[4].strip().capitalize()

                # Handle results_datetime based on status
                results_datetime = parts[5].strip() if len(parts) > 5 and status == "Completed" else ""

                records.append({
                    "patient_id": patient_id,
                    "test_name": test_name,
                    "test_datetime": test_datetime,
                    "result_value": result_value,
                    "results_unit": result_unit,
                    "status": status,
                    "results_datetime": results_datetime
                })
    except FileNotFoundError:
        print(f"File {filename} not found.")
    return records


def display_records(records):
    for i, record in enumerate(records, 1):
        patient_id = record.get('patient_id', 'N/A')
        test_name = record.get('test_name', 'N/A')
        test_datetime = record.get('test_datetime', 'N/A')
        result_value = record.get('result_value', 'N/A')
        results_unit = record.get('results_unit', 'N/A')
        status = record.get('status', 'N/A')
        results_datetime = record.get('results_datetime', 'N/A')

        print(
            f"{i}. {patient_id}: {test_name}, {test_datetime}, {result_value}, {results_unit}, {status}, {results_datetime}")

def update_record(filename="medicalRecord.txt"):
    records = load_records(filename)
    if not records:
        print("No records available to update.")
        return

    print("Available records:")
    display_records(records)

    while True:
        record_index = int(input("Select the record number to update: ")) - 1
        if 0 <= record_index < len(records):
            record = records[record_index]
            break
        else:
            print("Invalid selection. Please choose a valid record number.")

    print(f"Updating record for Patient ID: {record['patient_id']} and Test: {record['test_name']}")

    # Load available test names
    test_units = load_tests()

    # Get updated test details
    updated_record = get_record_input(test_units)

    # Ensure the patient ID remains the same
    updated_record["patient_id"] = record["patient_id"]

    # Replace the record with the updated one
    records[record_index] = updated_record

    # Save all records back to the file
    with open(filename, "w") as file:
        for rec in records:
            save_record(rec, filename)

    print("Record updated successfully.")

#############################################option 4###############################################################
def update_test(filename="medicalTest.txt"):
    tests = load_tests(filename)
    if not tests:
        print("No tests available to update.")
        return

    print("Available tests:")
    display_tests(tests)

    while True:
        test_name = input("Enter the test name to update: ").strip().lower()
        if test_name in tests:
            break
        else:
            print("Invalid test name! Please enter a valid test name.")

    print(f"Updating test: {test_name.capitalize()}")

    # Get updated test details
    updated_test = get_test_input()

    # Save all tests back to the file
    with open(filename, "w") as file:
        for name, unit in tests.items():
            if name == test_name:
                updated_test.save_to_file(file)
            else:
                test_entry = f"Name: {name}; Range: {tests[name]}; Unit: {unit}, Turnaround Time: {updated_test.get_turnaround_time()}\n"
                file.write(test_entry)

    print("Test updated successfully.")
###########################################option 5###############################################################
# Display the filtered records
def display_records_filtered(records):
    if not records:
        print("No records to display.")
        return

    for idx, record in enumerate(records, start=1):
        patient_id = record.get('patient_id', 'N/A')
        test_name = record.get('test_name', 'N/A')
        test_datetime = record.get('test_datetime', 'N/A')
        result_value = record.get('result_value', 'N/A')
        result_unit = record.get('result_unit', '')
        status = record.get('status', 'N/A')
        results_datetime = record.get('results_datetime', '')

        result_date_str = f", Results Date: {results_datetime}" if status == "Completed" and results_datetime else ""
        unit_str = f" {result_unit}" if result_unit else ""

        print(f"{idx}. Patient ID: {patient_id}, Test Name: {test_name}, Test Date: {test_datetime}, Result: {result_value}{unit_str}, Status: {status}{result_date_str}")

def filter_tests(records):
    if not records:
        print("No records available for filtering.")
        return []

    print("Filter by:")
    print("1. Patient ID")
    print("2. Test Name")
    print("3. Abnormal Tests")
    print("4. Test Added Within a Specific Period")
    print("5. Test Status")
    print("6. Test Turnaround Time Within a Period")

    choice = input("Enter filter criteria number(s) separated by commas (e.g., 1,2): ").strip()
    criteria = [int(c.strip()) for c in choice.split(',')]

    filtered_records = records

    if 1 in criteria:
        patient_id = input("Enter Patient ID to filter: ").strip()
        filtered_records = [r for r in filtered_records if r['patient_id'] == patient_id]

    if 2 in criteria:
        test_name = input("Enter Test Name to filter: ").strip().capitalize()
        filtered_records = [r for r in filtered_records if r['test_name'] == test_name]

    if 3 in criteria:
        status = "Completed"
        filtered_records = [r for r in filtered_records if r['status'] == status]

    if 4 in criteria:
        start_date = get_valid_date("Enter start date (YYYY-MM-DD): ")
        end_date = get_valid_date("Enter end date (YYYY-MM-DD): ")

        while start_date > end_date:
            print("Start date cannot be after end date.")
            start_date = get_valid_date("Enter start date (YYYY-MM-DD): ")
            end_date = get_valid_date("Enter end date (YYYY-MM-DD): ")

        filtered_records = [
            r for r in filtered_records
            if start_date <= datetime.strptime(r['test_datetime'].split()[0], "%Y-%m-%d") <= end_date
        ]

    if 5 in criteria:
        status = input("Enter Test Status to filter (Pending, Completed, or Reviewed): ").strip().capitalize()
        print(f"Debug: Filtering by status: {status}")

        filtered_records = [r for r in filtered_records if r['status'] == status]

    if 6 in criteria:
        while True:
            try:
                min_time = float(input("Enter minimum turnaround time in minutes: ").strip())
                max_time = float(input("Enter maximum turnaround time in minutes: ").strip())
                if min_time > max_time:
                    print("Minimum turnaround time cannot be greater than maximum turnaround time. Please try again.")
                else:
                    break
            except ValueError:
                print("Invalid input. Please enter numeric values for turnaround times.")

        filtered_records = [
            r for r in filtered_records
            if min_time <= float(r['result_value']) <= max_time
        ]

    if not filtered_records:
        print("No records match the criteria.")
    else:
        display_records_filtered(filtered_records)

    return filtered_records  # Return filtered records


######################################option 6####################################################
def display_summary_report(statistics):
    print("\nSummary Report:")
    if statistics["min_value"] is not None:
        print(f"Minimum Test Value: {statistics['min_value']:.2f}")
        print(f"Maximum Test Value: {statistics['max_value']:.2f}")
        print(f"Average Test Value: {statistics['avg_value']:.2f}")
    else:
        print("No valid test values found for summary.")

    if statistics["min_turnaround"] is not None:
        print(f"Minimum Turnaround Time: {statistics['min_turnaround']:.2f} minutes")
        print(f"Maximum Turnaround Time: {statistics['max_turnaround']:.2f} minutes")
        print(f"Average Turnaround Time: {statistics['avg_turnaround']:.2f} minutes")
    else:
        print("No valid turnaround times found for summary.")

def compute_statistics(filtered_records):
    test_values = []
    turnaround_times = []

    for record in filtered_records:
        try:
            test_value = float(record["result_value"])
            test_values.append(test_value)
        except ValueError:
            continue

        if record["results_datetime"]:
            test_datetime = datetime.strptime(record["test_datetime"], "%Y-%m-%d %H:%M")
            results_datetime = datetime.strptime(record["results_datetime"], "%Y-%m-%d %H:%M")
            turnaround_time = (results_datetime - test_datetime).total_seconds() / 60
            turnaround_times.append(turnaround_time)

    # Compute statistics for test values
    if test_values:
        min_value = min(test_values)
        max_value = max(test_values)
        avg_value = statistics.mean(test_values)
    else:
        min_value = max_value = avg_value = None

    # Compute statistics for turnaround times
    if turnaround_times:
        min_turnaround = min(turnaround_times)
        max_turnaround = max(turnaround_times)
        avg_turnaround = statistics.mean(turnaround_times)
    else:
        min_turnaround = max_turnaround = avg_turnaround = None

    return {
        "min_value": min_value,
        "max_value": max_value,
        "avg_value": avg_value,
        "min_turnaround": min_turnaround,
        "max_turnaround": max_turnaround,
        "avg_turnaround": avg_turnaround
    }


filtered_records = []  # Declare filtered_records globally

def filter_and_generate_summary(records):
    global filtered_records  # Declare that we are using the global variable
    filtered_records = filter_tests(records)
    if filtered_records:
        stats = compute_statistics(filtered_records)
        display_summary_report(stats)
    else:
        print("No records matched the filtering criteria.")
#############################################option 7######################################################
def export_filtered_records():
    global filtered_records
    if filtered_records:
        filename = input(
            "Enter filename for export: ").strip() or "exported_records.csv"
        export_to_csv(filtered_records, filename)
    else:
        print("There is no filtered records available for export! Please generate a summary report first.")


def export_to_csv(records, filename="exported_records.csv"):
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Patient ID", "Test Name", "Test Date", "Result", "Unit", "Status", "Results Date"])

        for record in records:
            # Handle test datetime
            try:
                test_datetime = datetime.strptime(record["test_datetime"], "%Y-%m-%d %H:%M")
                test_datetime_str = test_datetime.strftime("%Y-%m-%d %H:%M")
            except ValueError:
                test_datetime_str = "Invalid Date"

            # Handle results datetime
            try:
                if record["results_datetime"]:
                    results_datetime = datetime.strptime(record["results_datetime"], "%Y-%m-%d %H:%M")
                    results_datetime_str = results_datetime.strftime("%Y-%m-%d %H:%M")
                else:
                    results_datetime_str = ""
            except ValueError:
                results_datetime_str = ""

            writer.writerow([
                record["patient_id"],
                record["test_name"],
                test_datetime_str,
                record["result_value"],
                record["results_unit"],
                record["status"],
                results_datetime_str
            ])

    print(f"Records successfully exported to {filename}")
#############################################option 8#########################################################
def import_records_from_csv(filename="imported_records.csv"):
    records = []
    try:
        with open(filename, mode='r') as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) < 6:
                    print(f"Skipping invalid row: {row}")
                    continue

                patient_id, test_name, test_datetime, result_value, results_unit, status, *results_datetime = row
                results_datetime = results_datetime[0] if results_datetime else ""

                record = {
                    "patient_id": patient_id.strip(),
                    "test_name": test_name.strip(),
                    "test_datetime": test_datetime.strip(),
                    "result_value": result_value.strip(),
                    "results_unit": results_unit.strip(),
                    "status": status.strip().capitalize(),
                    "results_datetime": results_datetime.strip()
                }
                records.append(record)
    except FileNotFoundError:
        print(f"File {filename} not found.")
    except csv.Error as e:
        print(f"CSV error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

    if records:
        try:
            # Save imported records to the main file
            with open("medicalRecord.txt", "a") as file:
                for record in records:
                    save_record(record, filename="medicalRecord.txt")
            print(f"Records successfully imported from {filename}.")
        except Exception as e:
            print(f"Failed to save records to 'medicalRecord.txt': {e}")

def import_records():
    import_filename = input(
        "Enter filename to import records from: ").strip() or "imported_records.csv"
    import_records_from_csv(import_filename)

###########################################################################################

def normalize_date_input(date_str):
    try:
        # Split into date and time components
        date_part, time_part = date_str.split()

        # Split date and time into components
        year, month, day = map(int, date_part.split('-'))
        hour, minute = map(int, time_part.split(':'))

        # Check for valid ranges
        if not (1 <= month <= 12):
            return None
        if not (1 <= day <= 31):  # Simplified check; more detailed checks below
            return None
        if not (0 <= hour <= 23) or not (0 <= minute <= 59):
            return None

        # Reformat date and time to ensure correct format
        normalized_date = f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}"
        return normalized_date
    except ValueError:
        return None


def get_valid_date(prompt):
    """Prompt the user for a valid date and return it as a datetime object."""
    while True:
        date_str = input(prompt).strip()
        if len(date_str) != 10 or not (date_str[4] == '-' and date_str[7] == '-'):
            print("Invalid date format. Please use YYYY-MM-DD.")
            continue
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            return date_obj
        except ValueError:
            print("Invalid date. Please ensure the date is valid and follows the format YYYY-MM-DD.")



def validate_duration(duration):
    pattern = r"^\d{2}-\d{2}-\d{2}$"
    return re.match(pattern, duration) is not None


def display_tests(tests):
    for i, (name, unit) in enumerate(tests.items(), 1):
        print(f"{i}. Name: {name.capitalize()}, Unit: {unit}")

def validate_datetime(date_str):
    # Define a regex pattern for valid datetime format YYYY-MM-DD hh:mm
    pattern = r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$"
    if re.match(pattern, date_str):
        try:
            # Attempt to parse the date to ensure it's a valid datetime
            datetime.strptime(date_str, "%Y-%m-%d %H:%M")
            return True
        except ValueError:
            return False
    return False

def validate_numeric(value):
    try:
        float(value)  # Convert to float to check if it's numeric
        return True
    except ValueError:
        return False


def menu():
    print(
        "Welcome to our medical system, please select an option:\n"
        "1. Add a Medical Test\n"
        "2. Add a Medical Record\n"
        "3. Update a Medical Record\n"
        "4. Update a Medical Test\n"
        "5. Filter Medical Tests\n"
        "6. Generate Summary Report\n"
        "7. Export Records to CSV\n"
        "8. Import Medical Records from CSV\n"
        "9. Exit. "
    )
    return input().strip().lower()


def main():
    actions = {
        '1': save_test,
        '2': save_record_info,
        '3': update_record,
        '4': update_test,
        '5': lambda: filter_tests(load_records()),
        '6': lambda: filter_and_generate_summary(load_records()),
        '7': export_filtered_records,
        '8': import_records,
        '9': exit
    }

    while True:
        choice = menu()

        action = actions.get(choice)
        if action:
            action()
        else:
            print("Invalid choice! Please try again:")



if __name__ == "__main__":
    main()