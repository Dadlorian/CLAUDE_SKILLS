"""
E-Discovery File Hash Calculation and Deduplication

This script calculates MD5 and SHA-256 hashes for files and identifies duplicates
based on hash values. Essential for e-discovery processing and data reduction.

Usage:
    python 01_hash_deduplication.py /path/to/data --output duplicates_report.csv
"""

import hashlib
import os
import csv
import argparse
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple


def calculate_hash(file_path: str, algorithm: str = 'md5') -> str:
    """
    Calculate hash of file using specified algorithm.

    Args:
        file_path: Path to file
        algorithm: 'md5' or 'sha256'

    Returns:
        Hexadecimal hash string
    """
    hash_func = hashlib.md5() if algorithm == 'md5' else hashlib.sha256()

    try:
        with open(file_path, 'rb') as f:
            # Read file in chunks to handle large files
            for chunk in iter(lambda: f.read(8192), b''):
                hash_func.update(chunk)
        return hash_func.hexdigest()
    except Exception as e:
        print(f"Error hashing {file_path}: {e}")
        return None


def process_directory(root_path: str, algorithms: List[str] = ['md5', 'sha256']) -> List[Dict]:
    """
    Process all files in directory and calculate hashes.

    Args:
        root_path: Root directory to process
        algorithms: List of hash algorithms to use

    Returns:
        List of file information dictionaries
    """
    file_data = []

    for dirpath, _, filenames in os.walk(root_path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            file_info = {
                'file_path': file_path,
                'file_name': filename,
                'file_size': os.path.getsize(file_path),
                'file_extension': Path(filename).suffix,
            }

            # Calculate hashes
            for algo in algorithms:
                hash_value = calculate_hash(file_path, algo)
                file_info[f'{algo}_hash'] = hash_value

            file_data.append(file_info)

    return file_data


def identify_duplicates(file_data: List[Dict], hash_field: str = 'md5_hash') -> Dict[str, List[Dict]]:
    """
    Identify duplicate files based on hash values.

    Args:
        file_data: List of file information dictionaries
        hash_field: Hash field to use for deduplication

    Returns:
        Dictionary mapping hash values to lists of duplicate files
    """
    hash_groups = defaultdict(list)

    for file_info in file_data:
        hash_value = file_info.get(hash_field)
        if hash_value:
            hash_groups[hash_value].append(file_info)

    # Filter to only groups with duplicates
    duplicates = {h: files for h, files in hash_groups.items() if len(files) > 1}

    return duplicates


def generate_deduplication_report(duplicates: Dict[str, List[Dict]], output_file: str):
    """
    Generate CSV report of duplicate files.

    Args:
        duplicates: Dictionary of duplicate file groups
        output_file: Output CSV file path
    """
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Hash', 'Duplicate_Group', 'File_Path', 'File_Size', 'Status'])

        for hash_value, files in duplicates.items():
            # First file is master, others are duplicates
            for idx, file_info in enumerate(files):
                status = 'MASTER' if idx == 0 else 'DUPLICATE'
                writer.writerow([
                    hash_value,
                    f"DUP_{list(duplicates.keys()).index(hash_value) + 1}",
                    file_info['file_path'],
                    file_info['file_size'],
                    status
                ])


def calculate_deduplication_stats(file_data: List[Dict], duplicates: Dict[str, List[Dict]]) -> Dict:
    """
    Calculate deduplication statistics.

    Args:
        file_data: All file information
        duplicates: Duplicate file groups

    Returns:
        Statistics dictionary
    """
    total_files = len(file_data)
    duplicate_files = sum(len(files) - 1 for files in duplicates.values())  # Exclude masters
    unique_files = total_files - duplicate_files

    total_size = sum(f['file_size'] for f in file_data)
    duplicate_size = sum(
        sum(f['file_size'] for f in files[1:])  # Exclude master
        for files in duplicates.values()
    )

    dedup_percentage = (duplicate_files / total_files * 100) if total_files > 0 else 0
    size_reduction = (duplicate_size / total_size * 100) if total_size > 0 else 0

    return {
        'total_files': total_files,
        'unique_files': unique_files,
        'duplicate_files': duplicate_files,
        'deduplication_percentage': dedup_percentage,
        'total_size_bytes': total_size,
        'duplicate_size_bytes': duplicate_size,
        'size_reduction_percentage': size_reduction,
        'total_size_gb': total_size / (1024**3),
        'savings_gb': duplicate_size / (1024**3)
    }


def main():
    parser = argparse.ArgumentParser(description='E-Discovery File Deduplication')
    parser.add_argument('path', help='Directory to process')
    parser.add_argument('--output', default='duplicates_report.csv', help='Output CSV file')
    parser.add_argument('--hash', default='md5', choices=['md5', 'sha256'], help='Hash algorithm')
    parser.add_argument('--stats', action='store_true', help='Print deduplication statistics')

    args = parser.parse_args()

    print(f"Processing directory: {args.path}")
    print(f"Hash algorithm: {args.hash}")

    # Process files and calculate hashes
    file_data = process_directory(args.path, [args.hash])
    print(f"Processed {len(file_data)} files")

    # Identify duplicates
    duplicates = identify_duplicates(file_data, f'{args.hash}_hash')
    print(f"Found {len(duplicates)} duplicate groups")

    # Generate report
    generate_deduplication_report(duplicates, args.output)
    print(f"Report saved to: {args.output}")

    # Print statistics if requested
    if args.stats:
        stats = calculate_deduplication_stats(file_data, duplicates)
        print("\n=== Deduplication Statistics ===")
        print(f"Total Files: {stats['total_files']:,}")
        print(f"Unique Files: {stats['unique_files']:,}")
        print(f"Duplicate Files: {stats['duplicate_files']:,}")
        print(f"Deduplication Rate: {stats['deduplication_percentage']:.1f}%")
        print(f"Total Size: {stats['total_size_gb']:.2f} GB")
        print(f"Duplicate Size: {stats['savings_gb']:.2f} GB")
        print(f"Size Reduction: {stats['size_reduction_percentage']:.1f}%")


if __name__ == '__main__':
    main()
