"""
Character Encoding Validation Module

Validates character encoding and normalization.
"""

import json
import logging
import unicodedata
from pathlib import Path
from typing import Dict, List

logger = logging.getLogger(__name__)


class EncodingValidator:
    """Validates character encoding and Unicode normalization."""

    def __init__(self, locale: str, source_dir: str):
        self.locale = locale
        self.source_dir = Path(source_dir)
        self.results = {
            'locale': locale,
            'encoding_valid': True,
            'normalization_issues': [],
            'combining_characters': [],
            'surrogate_pairs': [],
        }

    def validate_encoding(self) -> bool:
        """Validate UTF-8 encoding of all files."""
        logger.info(f"Validating encoding for {self.locale}")
        valid = True

        for file_path in self.source_dir.glob('**/*'):
            if file_path.is_file() and file_path.suffix in ['.json', '.yml', '.yaml']:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    logger.debug(f"Valid UTF-8: {file_path.name}")
                except UnicodeDecodeError as e:
                    logger.error(f"Invalid UTF-8 in {file_path}: {e}")
                    self.results['encoding_valid'] = False
                    valid = False

        return valid

    def validate_normalization(self) -> bool:
        """Check Unicode normalization."""
        logger.debug("Validating Unicode normalization...")

        messages = self._load_messages()
        issues = []

        for key, value in messages.items():
            if not isinstance(value, str):
                continue

            # Check various normalization forms
            nfc = unicodedata.normalize('NFC', value)
            nfd = unicodedata.normalize('NFD', value)
            nfkc = unicodedata.normalize('NFKC', value)

            # Warn if value has multiple normalization forms
            if nfc != nfd:
                issues.append({
                    'key': key,
                    'message': 'Not in canonical composition',
                    'value': value,
                })

        self.results['normalization_issues'] = issues
        return len(issues) == 0

    def check_combining_characters(self) -> List[Dict]:
        """Check for combining characters that might cause issues."""
        logger.debug("Checking combining characters...")

        messages = self._load_messages()
        combining_chars = []

        for key, value in messages.items():
            if not isinstance(value, str):
                continue

            for i, char in enumerate(value):
                category = unicodedata.category(char)
                if category.startswith('M'):  # Mark characters (combining)
                    combining_chars.append({
                        'key': key,
                        'position': i,
                        'character': char,
                        'name': unicodedata.name(char, 'UNKNOWN'),
                    })

        self.results['combining_characters'] = combining_chars
        return combining_chars

    def check_surrogate_pairs(self) -> List[Dict]:
        """Check for emoji and surrogate pair handling."""
        logger.debug("Checking surrogate pairs...")

        messages = self._load_messages()
        surrogate_pairs = []

        for key, value in messages.items():
            if not isinstance(value, str):
                continue

            # Check for characters outside BMP
            for i, char in enumerate(value):
                code_point = ord(char)
                if code_point > 0xFFFF:
                    surrogate_pairs.append({
                        'key': key,
                        'position': i,
                        'character': char,
                        'code_point': hex(code_point),
                    })

        self.results['surrogate_pairs'] = surrogate_pairs
        return surrogate_pairs

    def _load_messages(self) -> Dict:
        """Load messages from locale."""
        messages_file = self.source_dir / 'messages.json'
        if not messages_file.exists():
            return {}

        try:
            with open(messages_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading messages: {e}")
            return {}
