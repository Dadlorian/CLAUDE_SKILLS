#!/usr/bin/env python3
"""
Translation Memory Builder - TMX Generation Script

Builds translation memory files (TMX format) from localized content.
Generates translation units with metadata and enables TM-based translation suggestions.

Features:
- Automatic TMX generation from translated files
- Multi-format support (JSON, YAML, PO, properties)
- Context and metadata preservation
- Quality metrics calculation
- Batch processing with progress tracking
- Deduplication and conflict resolution
"""

import argparse
import json
import logging
import os
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from xml.etree import ElementTree as ET

import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TranslationUnit:
    """Represents a single translation unit for TMX."""

    def __init__(self, source: str, target: str, locale: str, context: Optional[str] = None):
        self.source = source
        self.target = target
        self.locale = locale
        self.context = context or ""
        self.metadata = {
            'created': datetime.utcnow().isoformat(),
            'modified': datetime.utcnow().isoformat(),
            'source_hash': hash(source),
        }
        self.quality_score = 0.0
        self.usage_count = 1

    def to_xml(self) -> ET.Element:
        """Convert translation unit to TMX XML element."""
        tu = ET.Element('tu')
        tu.set('tuid', str(self.metadata['source_hash']))

        # Add source variant
        tuv_src = ET.SubElement(tu, 'tuv')
        tuv_src.set('xml:lang', 'en-US')
        seg_src = ET.SubElement(tuv_src, 'seg')
        seg_src.text = self.source

        # Add context if available
        if self.context:
            context_elem = ET.SubElement(tu, 'context')
            context_elem.text = self.context

        # Add target variant
        tuv_tgt = ET.SubElement(tu, 'tuv')
        tuv_tgt.set('xml:lang', self.locale)
        seg_tgt = ET.SubElement(tuv_tgt, 'seg')
        seg_tgt.text = self.target

        # Add metadata
        for key, value in self.metadata.items():
            prop = ET.SubElement(tu, 'prop')
            prop.set('type', key)
            prop.text = str(value)

        return tu

    def __hash__(self) -> int:
        """Hash based on source and locale."""
        return hash((self.source, self.locale))

    def __eq__(self, other: 'TranslationUnit') -> bool:
        """Compare translation units."""
        if not isinstance(other, TranslationUnit):
            return False
        return self.source == other.source and self.locale == other.locale


class TranslationMemoryBuilder:
    """Main builder class for TMX generation."""

    def __init__(self, source_dir: str, output_dir: str, format: str = 'tmx'):
        self.source_dir = Path(source_dir)
        self.output_dir = Path(output_dir)
        self.format = format
        self.translation_units: Dict[str, List[TranslationUnit]] = defaultdict(list)
        self.statistics = {
            'total_units': 0,
            'unique_units': 0,
            'locales': set(),
            'files_processed': 0,
            'errors': 0,
        }

        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def process_json_files(self) -> None:
        """Process JSON translation files."""
        logger.info("Processing JSON translation files...")

        json_files = self.source_dir.glob('**/messages.json')
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                locale = self._extract_locale(json_file)
                self.statistics['locales'].add(locale)

                for key, value in self._flatten_dict(data).items():
                    if isinstance(value, str):
                        unit = TranslationUnit(
                            source=key,
                            target=value,
                            locale=locale,
                            context=f"json:{json_file.name}"
                        )
                        self.translation_units[locale].append(unit)
                        self.statistics['total_units'] += 1

                self.statistics['files_processed'] += 1
                logger.debug(f"Processed: {json_file}")

            except Exception as e:
                logger.error(f"Error processing {json_file}: {e}")
                self.statistics['errors'] += 1

    def process_yaml_files(self) -> None:
        """Process YAML translation files."""
        logger.info("Processing YAML translation files...")

        yaml_files = list(self.source_dir.glob('**/*.yml')) + \
                     list(self.source_dir.glob('**/*.yaml'))

        for yaml_file in yaml_files:
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)

                if not data:
                    continue

                locale = self._extract_locale(yaml_file)
                self.statistics['locales'].add(locale)

                for key, value in self._flatten_dict(data).items():
                    if isinstance(value, str):
                        unit = TranslationUnit(
                            source=key,
                            target=value,
                            locale=locale,
                            context=f"yaml:{yaml_file.name}"
                        )
                        self.translation_units[locale].append(unit)
                        self.statistics['total_units'] += 1

                self.statistics['files_processed'] += 1
                logger.debug(f"Processed: {yaml_file}")

            except Exception as e:
                logger.error(f"Error processing {yaml_file}: {e}")
                self.statistics['errors'] += 1

    def process_po_files(self) -> None:
        """Process PO (gettext) translation files."""
        logger.info("Processing PO translation files...")

        po_files = self.source_dir.glob('**/*.po')
        for po_file in po_files:
            try:
                with open(po_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                locale = self._extract_locale(po_file)
                self.statistics['locales'].add(locale)

                units = self._parse_po_content(content)
                for source, target, context in units:
                    unit = TranslationUnit(
                        source=source,
                        target=target,
                        locale=locale,
                        context=context or f"po:{po_file.name}"
                    )
                    self.translation_units[locale].append(unit)
                    self.statistics['total_units'] += 1

                self.statistics['files_processed'] += 1
                logger.debug(f"Processed: {po_file}")

            except Exception as e:
                logger.error(f"Error processing {po_file}: {e}")
                self.statistics['errors'] += 1

    def deduplicate_units(self) -> None:
        """Remove duplicate translation units."""
        logger.info("Deduplicating translation units...")

        for locale, units in self.translation_units.items():
            unique_units = {}
            for unit in units:
                key = (unit.source, unit.locale)
                if key in unique_units:
                    # Merge duplicate units
                    unique_units[key].usage_count += 1
                else:
                    unique_units[key] = unit

            self.translation_units[locale] = list(unique_units.values())

        self.statistics['unique_units'] = sum(
            len(units) for units in self.translation_units.values()
        )
        logger.info(f"Reduced from {self.statistics['total_units']} to "
                   f"{self.statistics['unique_units']} unique units")

    def calculate_quality_scores(self) -> None:
        """Calculate quality scores for translation units."""
        logger.info("Calculating quality scores...")

        for locale, units in self.translation_units.items():
            for unit in units:
                score = self._calculate_unit_quality(unit)
                unit.quality_score = score

    def _calculate_unit_quality(self, unit: TranslationUnit) -> float:
        """Calculate quality score for a translation unit."""
        score = 1.0

        # Check for empty translations
        if not unit.target or not unit.target.strip():
            score -= 0.5

        # Check for untranslated content
        if unit.source == unit.target:
            score -= 0.3

        # Check length ratio (should be somewhat similar)
        source_len = len(unit.source)
        target_len = len(unit.target)
        if source_len > 0:
            ratio = target_len / source_len
            if ratio < 0.3 or ratio > 3.0:
                score -= 0.2

        # Boost for frequent usage
        if unit.usage_count > 1:
            score += min(0.1 * unit.usage_count, 0.3)

        return max(0.0, min(1.0, score))

    def build_tmx(self, output_file: Optional[str] = None) -> str:
        """Build TMX (Translation Memory eXchange) file."""
        if output_file is None:
            output_file = str(self.output_dir / 'translation-memory.tmx')

        logger.info(f"Building TMX file: {output_file}")

        # Create TMX root element
        tmx = ET.Element('tmx')
        tmx.set('version', '1.4')

        # Add header
        header = ET.SubElement(tmx, 'header')
        header.set('creationtool', 'TranslationMemoryBuilder')
        header.set('creationtoolversion', '1.0')
        header.set('datatype', 'plaintext')
        header.set('segtype', 'sentence')
        header.set('adminlang', 'en-US')
        header.set('srclang', 'en-US')
        header.set('o-tmf', 'Translation Memory eXchange')
        header.set('creationdate', datetime.utcnow().isoformat())

        # Add metadata about TM
        note = ET.SubElement(header, 'note')
        note.text = f"Generated translation memory from {self.statistics['files_processed']} files"

        # Add body with translation units
        body = ET.SubElement(tmx, 'body')

        for locale, units in sorted(self.translation_units.items()):
            logger.debug(f"Adding {len(units)} units for {locale}")
            for unit in units:
                tu_elem = unit.to_xml()
                body.append(tu_elem)

        # Write TMX file
        tree = ET.ElementTree(tmx)
        ET.indent(tree, space="  ")
        tree.write(output_file, encoding='utf-8', xml_declaration=True)

        logger.info(f"TMX file created: {output_file}")
        return output_file

    def build_csv(self, output_file: Optional[str] = None) -> str:
        """Build CSV export of translation memory."""
        if output_file is None:
            output_file = str(self.output_dir / 'translation-memory.csv')

        logger.info(f"Building CSV file: {output_file}")

        import csv
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Locale', 'Source', 'Target', 'Context', 'Quality', 'Usage'])

            for locale, units in sorted(self.translation_units.items()):
                for unit in units:
                    writer.writerow([
                        locale,
                        unit.source,
                        unit.target,
                        unit.context,
                        f"{unit.quality_score:.2f}",
                        unit.usage_count,
                    ])

        logger.info(f"CSV file created: {output_file}")
        return output_file

    def build_json(self, output_file: Optional[str] = None) -> str:
        """Build JSON export of translation memory."""
        if output_file is None:
            output_file = str(self.output_dir / 'translation-memory.json')

        logger.info(f"Building JSON file: {output_file}")

        tm_data = {
            'metadata': {
                'created': datetime.utcnow().isoformat(),
                'source_language': 'en-US',
                'target_languages': sorted(list(self.statistics['locales'])),
                'total_units': self.statistics['unique_units'],
                'files_processed': self.statistics['files_processed'],
            },
            'translation_units': {}
        }

        for locale, units in sorted(self.translation_units.items()):
            tm_data['translation_units'][locale] = [
                {
                    'source': unit.source,
                    'target': unit.target,
                    'context': unit.context,
                    'quality_score': unit.quality_score,
                    'usage_count': unit.usage_count,
                    'metadata': unit.metadata,
                }
                for unit in units
            ]

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(tm_data, f, indent=2, ensure_ascii=False)

        logger.info(f"JSON file created: {output_file}")
        return output_file

    def generate_report(self, output_file: Optional[str] = None) -> str:
        """Generate translation memory statistics report."""
        if output_file is None:
            output_file = str(self.output_dir / 'tmx-report.json')

        logger.info(f"Generating TM report: {output_file}")

        report = {
            'summary': {
                'total_translation_units': self.statistics['unique_units'],
                'source_language': 'en-US',
                'target_languages': sorted(list(self.statistics['locales'])),
                'files_processed': self.statistics['files_processed'],
                'processing_errors': self.statistics['errors'],
                'generated_at': datetime.utcnow().isoformat(),
            },
            'quality_metrics': self._calculate_quality_metrics(),
            'locale_statistics': self._calculate_locale_statistics(),
            'top_quality_units': self._get_top_units(10),
            'low_quality_units': self._get_low_units(10),
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        logger.info(f"Report generated: {output_file}")
        return output_file

    def _calculate_quality_metrics(self) -> Dict:
        """Calculate overall quality metrics."""
        all_units = [
            unit for units in self.translation_units.values()
            for unit in units
        ]

        if not all_units:
            return {}

        scores = [unit.quality_score for unit in all_units]
        return {
            'average_quality': sum(scores) / len(scores),
            'min_quality': min(scores),
            'max_quality': max(scores),
            'units_with_high_quality': sum(1 for s in scores if s >= 0.8),
            'units_with_low_quality': sum(1 for s in scores if s < 0.5),
        }

    def _calculate_locale_statistics(self) -> Dict:
        """Calculate per-locale statistics."""
        stats = {}
        for locale, units in sorted(self.translation_units.items()):
            scores = [u.quality_score for u in units]
            stats[locale] = {
                'total_units': len(units),
                'average_quality': sum(scores) / len(scores) if scores else 0,
                'coverage_percentage': (len(units) / max(1, sum(
                    len(u) for u in self.translation_units.values()
                ))) * 100,
            }
        return stats

    def _get_top_units(self, limit: int) -> List[Dict]:
        """Get top quality translation units."""
        all_units = [
            unit for units in self.translation_units.values()
            for unit in units
        ]
        top_units = sorted(all_units, key=lambda u: u.quality_score, reverse=True)[:limit]

        return [
            {
                'source': u.source,
                'target': u.target,
                'locale': u.locale,
                'quality': u.quality_score,
            }
            for u in top_units
        ]

    def _get_low_units(self, limit: int) -> List[Dict]:
        """Get low quality translation units."""
        all_units = [
            unit for units in self.translation_units.values()
            for unit in units
        ]
        low_units = sorted(all_units, key=lambda u: u.quality_score)[:limit]

        return [
            {
                'source': u.source,
                'target': u.target,
                'locale': u.locale,
                'quality': u.quality_score,
            }
            for u in low_units
        ]

    def _extract_locale(self, file_path: Path) -> str:
        """Extract locale code from file path."""
        parts = file_path.parts
        for i, part in enumerate(parts):
            if part in ['locales', 'translations']:
                if i + 1 < len(parts):
                    return parts[i + 1]
        return 'unknown'

    def _flatten_dict(self, d: Dict, parent_key: str = '', sep: str = '.') -> Dict:
        """Flatten nested dictionary."""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)

    def _parse_po_content(self, content: str) -> List[Tuple[str, str, Optional[str]]]:
        """Parse PO file content."""
        units = []
        current_msgctxt = None
        current_msgid = None
        current_msgstr = None

        for line in content.split('\n'):
            line = line.strip()

            if line.startswith('msgctxt'):
                current_msgctxt = self._extract_po_string(line)
            elif line.startswith('msgid'):
                current_msgid = self._extract_po_string(line)
            elif line.startswith('msgstr'):
                current_msgstr = self._extract_po_string(line)
                if current_msgid and current_msgstr:
                    units.append((current_msgid, current_msgstr, current_msgctxt))

        return units

    def _extract_po_string(self, line: str) -> str:
        """Extract string value from PO format."""
        match = line.split('"', 1)
        if len(match) > 1:
            return match[1].rsplit('"', 1)[0]
        return ""

    def print_statistics(self) -> None:
        """Print build statistics."""
        logger.info("=" * 60)
        logger.info("TRANSLATION MEMORY STATISTICS")
        logger.info("=" * 60)
        logger.info(f"Files processed: {self.statistics['files_processed']}")
        logger.info(f"Total units extracted: {self.statistics['total_units']}")
        logger.info(f"Unique units: {self.statistics['unique_units']}")
        logger.info(f"Target locales: {', '.join(sorted(self.statistics['locales']))}")
        logger.info(f"Processing errors: {self.statistics['errors']}")
        logger.info("=" * 60)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Build Translation Memory (TMX) from localized content'
    )
    parser.add_argument(
        '--source-dir',
        required=True,
        help='Source directory containing translation files'
    )
    parser.add_argument(
        '--output',
        default=None,
        help='Output file path (default: output-dir/translation-memory.{format})'
    )
    parser.add_argument(
        '--format',
        choices=['tmx', 'csv', 'json', 'all'],
        default='tmx',
        help='Output format (default: tmx)'
    )
    parser.add_argument(
        '--output-dir',
        default='./translation-memory',
        help='Output directory (default: ./translation-memory)'
    )
    parser.add_argument(
        '--include-json',
        action='store_true',
        default=True,
        help='Process JSON files (default: True)'
    )
    parser.add_argument(
        '--include-yaml',
        action='store_true',
        default=True,
        help='Process YAML files (default: True)'
    )
    parser.add_argument(
        '--include-po',
        action='store_true',
        help='Process PO files'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    try:
        builder = TranslationMemoryBuilder(args.source_dir, args.output_dir)

        # Process translation files
        if args.include_json:
            builder.process_json_files()
        if args.include_yaml:
            builder.process_yaml_files()
        if args.include_po:
            builder.process_po_files()

        # Process and build TM
        builder.deduplicate_units()
        builder.calculate_quality_scores()
        builder.print_statistics()

        # Generate outputs
        if args.format in ['tmx', 'all']:
            builder.build_tmx(args.output)
        if args.format in ['csv', 'all']:
            builder.build_csv()
        if args.format in ['json', 'all']:
            builder.build_json()

        # Generate report
        builder.generate_report()

        logger.info("Translation memory build completed successfully!")
        return 0

    except Exception as e:
        logger.error(f"Error building translation memory: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
