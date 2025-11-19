"""
Concordance DAT Load File Generator

Generates Concordance DAT format load files for e-discovery productions.
Supports standard delimiters and metadata field mapping.

Usage:
    python 03_load_file_generator.py metadata.csv --output production.dat
"""

import csv
import argparse


# Standard Concordance delimiters
FIELD_DELIMITER = chr(20)  # ASCII 20 (¶)
QUOTE = chr(254)  # ASCII 254 (þ)
NEWLINE = chr(174)  # ASCII 174 («)


def read_metadata_csv(input_file: str) -> tuple:
    """Read metadata from CSV file."""
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        data = list(reader)
    return fieldnames, data


def generate_dat_file(data: list, fieldnames: list, output_file: str):
    """Generate Concordance DAT file."""
    with open(output_file, 'w', encoding='utf-8') as f:
        # Write header
        header = FIELD_DELIMITER.join(fieldnames)
        f.write(header + '\n')

        # Write data rows
        for row in data:
            values = []
            for field in fieldnames:
                value = row.get(field, '')
                # Replace problematic characters
                value = str(value).replace('\n', NEWLINE).replace('\r', '')
                values.append(value)

            line = FIELD_DELIMITER.join(values)
            f.write(line + '\n')


def validate_dat_file(dat_file: str) -> dict:
    """Validate DAT file structure."""
    with open(dat_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    header_fields = lines[0].strip().split(FIELD_DELIMITER)
    field_count = len(header_fields)

    errors = []
    for i, line in enumerate(lines[1:], start=2):
        fields = line.strip().split(FIELD_DELIMITER)
        if len(fields) != field_count:
            errors.append(f"Line {i}: Expected {field_count} fields, found {len(fields)}")

    return {
        'total_records': len(lines) - 1,
        'field_count': field_count,
        'fields': header_fields,
        'errors': errors,
        'valid': len(errors) == 0
    }


def main():
    parser = argparse.ArgumentParser(description='Generate Concordance DAT load file')
    parser.add_argument('input', help='Input CSV metadata file')
    parser.add_argument('--output', default='production.dat', help='Output DAT file')
    parser.add_argument('--validate', action='store_true', help='Validate output')

    args = parser.parse_args()

    # Read metadata
    fieldnames, data = read_metadata_csv(args.input)
    print(f"Read {len(data)} records with {len(fieldnames)} fields")

    # Generate DAT file
    generate_dat_file(data, fieldnames, args.output)
    print(f"Generated DAT file: {args.output}")

    # Validate if requested
    if args.validate:
        validation = validate_dat_file(args.output)
        print(f"\n=== Validation Results ===")
        print(f"Total Records: {validation['total_records']}")
        print(f"Field Count: {validation['field_count']}")
        print(f"Valid: {validation['valid']}")
        if validation['errors']:
            print("Errors:")
            for error in validation['errors'][:10]:  # Show first 10 errors
                print(f"  {error}")


if __name__ == '__main__':
    main()
