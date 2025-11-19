#!/usr/bin/env python3
"""
FAIR Data Principles Validation Tool
Automated checking of Findable, Accessible, Interoperable, Reusable data
"""

import os
import json
import hashlib
from pathlib import Path
from datetime import datetime
import pandas as pd
import yaml

class FAIRDataValidator:
    """Validate research data against FAIR principles"""

    def __init__(self, dataset_path):
        """
        Initialize validator

        Parameters:
        -----------
        dataset_path : str or Path
            Path to dataset directory
        """
        self.dataset_path = Path(dataset_path)
        self.validation_report = {
            'dataset': str(self.dataset_path),
            'validation_date': datetime.now().isoformat(),
            'fair_scores': {},
            'issues': [],
            'recommendations': []
        }

    def validate_findable(self):
        """
        Validate F (Findable) principles:
        F1: Globally unique persistent identifier
        F2: Rich metadata
        F3: Metadata includes identifier
        F4: Indexed in searchable resource
        """
        score = 0
        max_score = 4

        # F1: Check for DOI or persistent identifier
        if self._has_persistent_id():
            score += 1
        else:
            self.validation_report['issues'].append(
                "F1: No persistent identifier (DOI) found"
            )
            self.validation_report['recommendations'].append(
                "F1: Register dataset with Zenodo, Dryad, or institutional repository to obtain DOI"
            )

        # F2: Check for metadata file
        if self._has_metadata():
            score += 1
        else:
            self.validation_report['issues'].append(
                "F2: No metadata file found (datacite.json, metadata.yml, or CITATION.cff)"
            )
            self.validation_report['recommendations'].append(
                "F2: Create metadata file with title, authors, description, keywords"
            )

        # F3: Check if metadata references identifier
        if self._metadata_has_identifier():
            score += 1
        else:
            self.validation_report['issues'].append(
                "F3: Metadata does not include dataset identifier"
            )

        # F4: Check for README (basic discoverability)
        if (self.dataset_path / "README.md").exists():
            score += 1
        else:
            self.validation_report['issues'].append(
                "F4: No README.md found"
            )
            self.validation_report['recommendations'].append(
                "F4: Create README.md describing dataset, usage, and provenance"
            )

        self.validation_report['fair_scores']['Findable'] = f"{score}/{max_score}"
        return score / max_score

    def validate_accessible(self):
        """
        Validate A (Accessible) principles:
        A1: Retrievable by identifier
        A1.1: Protocol open, free, universal
        A2: Metadata accessible even if data restricted
        """
        score = 0
        max_score = 3

        # A1: Check if data files exist and are readable
        data_files = list(self.dataset_path.glob("**/*.csv")) + \
                     list(self.dataset_path.glob("**/*.txt")) + \
                     list(self.dataset_path.glob("**/*.json"))

        if data_files and all(f.is_file() for f in data_files):
            score += 1
        else:
            self.validation_report['issues'].append(
                "A1: No accessible data files found (.csv, .txt, .json)"
            )

        # A1.1: Check for LICENSE file
        if (self.dataset_path / "LICENSE").exists() or (self.dataset_path / "LICENSE.txt").exists():
            score += 1
        else:
            self.validation_report['issues'].append(
                "A1.1: No LICENSE file found"
            )
            self.validation_report['recommendations'].append(
                "A1.1: Add LICENSE file (recommend CC0 or CC-BY for data)"
            )

        # A2: Metadata separate from data
        if self._has_metadata():
            score += 1

        self.validation_report['fair_scores']['Accessible'] = f"{score}/{max_score}"
        return score / max_score

    def validate_interoperable(self):
        """
        Validate I (Interoperable) principles:
        I1: Formal, accessible, shared language
        I2: FAIR vocabularies
        I3: Qualified references to other data
        """
        score = 0
        max_score = 3

        # I1: Check for standard file formats
        standard_formats = ['.csv', '.txt', '.json', '.xml', '.tsv']
        data_files = list(self.dataset_path.glob("**/*"))
        has_standard_format = any(f.suffix in standard_formats for f in data_files if f.is_file())

        if has_standard_format:
            score += 1
        else:
            self.validation_report['issues'].append(
                "I1: No standard open formats found (CSV, JSON, XML preferred)"
            )
            self.validation_report['recommendations'].append(
                "I1: Convert proprietary formats (Excel, SPSS) to open formats (CSV)"
            )

        # I2: Check for data dictionary
        if (self.dataset_path / "data_dictionary.md").exists() or \
           (self.dataset_path / "codebook.txt").exists():
            score += 1
        else:
            self.validation_report['issues'].append(
                "I2: No data dictionary or codebook found"
            )
            self.validation_report['recommendations'].append(
                "I2: Create data_dictionary.md defining all variables and codes"
            )

        # I3: Check for references to related datasets
        if self._has_related_references():
            score += 1
        else:
            self.validation_report['recommendations'].append(
                "I3: Add references to related datasets/publications in metadata"
            )

        self.validation_report['fair_scores']['Interoperable'] = f"{score}/{max_score}"
        return score / max_score

    def validate_reusable(self):
        """
        Validate R (Reusable) principles:
        R1: Rich metadata with provenance
        R1.1: Clear usage license
        R1.2: Provenance documented
        R1.3: Domain-relevant standards
        """
        score = 0
        max_score = 4

        # R1: Check metadata completeness
        metadata = self._get_metadata()
        if metadata and all(k in metadata for k in ['title', 'authors', 'description']):
            score += 1
        else:
            self.validation_report['issues'].append(
                "R1: Metadata incomplete (needs title, authors, description)"
            )

        # R1.1: License file
        if (self.dataset_path / "LICENSE").exists():
            score += 1

        # R1.2: Provenance/methods documented
        if (self.dataset_path / "METHODS.md").exists() or \
           (self.dataset_path / "protocols.md").exists():
            score += 1
        else:
            self.validation_report['issues'].append(
                "R1.2: No methods/provenance documentation found"
            )
            self.validation_report['recommendations'].append(
                "R1.2: Create METHODS.md documenting data collection and processing"
            )

        # R1.3: Check for standard metadata schema
        if (self.dataset_path / "datacite.json").exists() or \
           (self.dataset_path / "metadata.xml").exists():
            score += 1
        else:
            self.validation_report['recommendations'].append(
                "R1.3: Use standard metadata schema (DataCite, Dublin Core)"
            )

        self.validation_report['fair_scores']['Reusable'] = f"{score}/{max_score}"
        return score / max_score

    def _has_persistent_id(self):
        """Check if dataset has DOI or other persistent identifier"""
        metadata = self._get_metadata()
        if metadata:
            return 'doi' in metadata or 'identifier' in metadata
        return False

    def _has_metadata(self):
        """Check for metadata files"""
        metadata_files = [
            "metadata.json", "metadata.yml", "metadata.yaml",
            "datacite.json", "CITATION.cff"
        ]
        return any((self.dataset_path / f).exists() for f in metadata_files)

    def _metadata_has_identifier(self):
        """Check if metadata includes identifier"""
        metadata = self._get_metadata()
        return metadata and ('doi' in metadata or 'identifier' in metadata)

    def _has_related_references(self):
        """Check for references to related work"""
        metadata = self._get_metadata()
        if metadata:
            return 'related_publications' in metadata or 'related_datasets' in metadata
        return False

    def _get_metadata(self):
        """Load metadata from file"""
        metadata_files = {
            "metadata.json": lambda f: json.load(open(f)),
            "metadata.yml": lambda f: yaml.safe_load(open(f)),
            "metadata.yaml": lambda f: yaml.safe_load(open(f)),
            "datacite.json": lambda f: json.load(open(f))
        }

        for filename, loader in metadata_files.items():
            filepath = self.dataset_path / filename
            if filepath.exists():
                try:
                    return loader(filepath)
                except Exception as e:
                    print(f"Error loading {filename}: {e}")

        return None

    def generate_report(self):
        """Generate comprehensive FAIR validation report"""
        # Calculate scores
        f_score = self.validate_findable()
        a_score = self.validate_accessible()
        i_score = self.validate_interoperable()
        r_score = self.validate_reusable()

        overall_score = (f_score + a_score + i_score + r_score) / 4

        self.validation_report['overall_fair_score'] = f"{overall_score:.2%}"

        return self.validation_report

    def print_report(self):
        """Print formatted validation report"""
        report = self.generate_report()

        print("="*80)
        print("FAIR DATA PRINCIPLES VALIDATION REPORT")
        print("="*80)
        print(f"\nDataset: {report['dataset']}")
        print(f"Validation Date: {report['validation_date']}")
        print(f"\nOverall FAIR Score: {report['overall_fair_score']}")

        print("\nScores by Principle:")
        for principle, score in report['fair_scores'].items():
            print(f"  {principle}: {score}")

        if report['issues']:
            print("\n⚠ Issues Found:")
            for issue in report['issues']:
                print(f"  - {issue}")

        if report['recommendations']:
            print("\n💡 Recommendations:")
            for rec in report['recommendations']:
                print(f"  - {rec}")

        print("\n" + "="*80)

    def export_report(self, output_file):
        """Export report to JSON"""
        report = self.generate_report()
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\n✓ Report exported to {output_file}")

class DatasetInventory:
    """Create inventory of dataset files with checksums"""

    def __init__(self, dataset_path):
        self.dataset_path = Path(dataset_path)

    def generate_manifest(self):
        """Generate manifest with file checksums"""
        manifest = []

        for filepath in self.dataset_path.rglob('*'):
            if filepath.is_file():
                # Calculate MD5 checksum
                md5_hash = hashlib.md5()
                with open(filepath, 'rb') as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        md5_hash.update(chunk)

                file_info = {
                    'path': str(filepath.relative_to(self.dataset_path)),
                    'size_bytes': filepath.stat().st_size,
                    'modified': datetime.fromtimestamp(filepath.stat().st_mtime).isoformat(),
                    'md5': md5_hash.hexdigest()
                }
                manifest.append(file_info)

        return pd.DataFrame(manifest)

    def save_manifest(self, output_file="MANIFEST.csv"):
        """Save manifest to CSV"""
        manifest = self.generate_manifest()
        output_path = self.dataset_path / output_file
        manifest.to_csv(output_path, index=False)
        print(f"✓ Manifest saved to {output_path}")
        return manifest

# Example usage
if __name__ == "__main__":
    # Example: Validate a dataset
    dataset_path = "."  # Current directory

    print("Validating dataset against FAIR principles...")
    print()

    validator = FAIRDataValidator(dataset_path)
    validator.print_report()

    # Export detailed report
    validator.export_report("fair_validation_report.json")

    # Generate file manifest
    print("\nGenerating file manifest...")
    inventory = DatasetInventory(dataset_path)
    manifest = inventory.save_manifest()
    print(f"  Total files: {len(manifest)}")
    print(f"  Total size: {manifest['size_bytes'].sum() / 1024 / 1024:.2f} MB")
