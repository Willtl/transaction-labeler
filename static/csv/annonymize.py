import csv
import re
import shutil


def anonymize_value(value):
    if value != "********":
        return "********"
    else:
        return value


def clean_description(description):
    cleaned_description = re.sub(r'[^a-zA-Z\s]', ' ', description)
    return cleaned_description.strip()  # Remove leading/trailing whitespace


def anonymize_csv(input_file):
    temp_file = input_file + ".tmp"
    with open(input_file, 'r') as csv_input, open(temp_file, 'w', newline='') as csv_output:
        reader = csv.reader(csv_input)
        writer = csv.writer(csv_output)

        for row in reader:
            anonymized_value = anonymize_value(row[-1])
            cleaned_description = clean_description(row[1])  # Assuming description is in the second column
            anonymized_row = [row[0], cleaned_description] + [anonymized_value]  # Assuming the description is in the second column
            writer.writerow(anonymized_row)

    shutil.move(temp_file, input_file)


if __name__ == "__main__":
    input_file = "transactions_anonymized.csv"
    anonymize_csv(input_file)
    print("Anonymization complete. Anonymized data saved to", input_file)
