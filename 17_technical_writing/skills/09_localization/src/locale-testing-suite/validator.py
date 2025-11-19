"""
Core Locale Validation Module

Validates localized content for completeness, consistency, and quality.
"""

import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple

logger = logging.getLogger(__name__)


class LocaleValidator:
    """Main locale validation orchestrator."""

    # CLDR Language codes and properties
    PLURAL_FORMS = {
        'es': 2, 'fr': 2, 'de': 2, 'it': 2, 'ja': 1, 'zh': 1,
        'pt': 2, 'ru': 3, 'ar': 6, 'ko': 1, 'tr': 1, 'pl': 3,
        'nl': 2, 'en': 2,
    }

    def __init__(self, locale: str, source_dir: str, strict: bool = False):
        self.locale = locale
        self.source_dir = Path(source_dir)
        self.strict = strict
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.results = {
            'locale': locale,
            'valid': True,
            'errors': [],
            'warnings': [],
            'metrics': {},
        }

    def validate_all(self) -> bool:
        """Run all validation checks."""
        logger.info(f"Starting validation for locale: {self.locale}")

        # Run all validation methods
        self.validate_file_existence()
        self.validate_encoding()
        self.validate_placeholders()
        self.validate_length_constraints()
        self.validate_markup()
        self.validate_consistency()
        self.validate_special_characters()
        self.validate_punctuation()

        # Compile results
        self.results['valid'] = len(self.errors) == 0
        self.results['errors'] = self.errors
        self.results['warnings'] = self.warnings

        return self.results['valid']

    def validate_file_existence(self) -> bool:
        """Check that all required locale files exist."""
        logger.debug("Validating file existence...")
        required_files = ['messages.json', 'metadata.json']

        if not self.source_dir.exists():
            self.errors.append(f"Source directory not found: {self.source_dir}")
            return False

        for required_file in required_files:
            file_path = self.source_dir / required_file
            if not file_path.exists():
                self.warnings.append(f"Expected file not found: {required_file}")

        return len(self.errors) == 0

    def validate_encoding(self) -> bool:
        """Validate UTF-8 encoding of all locale files."""
        logger.debug("Validating encoding...")
        valid = True

        for file_path in self.source_dir.glob('**/*.json'):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    f.read()
            except UnicodeDecodeError as e:
                self.errors.append(f"Invalid UTF-8 encoding in {file_path.name}: {e}")
                valid = False

        return valid

    def validate_placeholders(self) -> bool:
        """Validate translation placeholders are present and correctly formatted."""
        logger.debug("Validating placeholders...")
        valid = True

        messages = self._load_messages()
        pattern = re.compile(r'\{[^}]+\}')

        for key, value in messages.items():
            if not isinstance(value, str):
                continue

            # Extract placeholders
            placeholders = set(pattern.findall(value))

            # Check for unescaped braces
            unescaped = re.findall(r'(?<![\\])\{[^}]*$|^[^}]*\}', value)
            if unescaped:
                self.errors.append(
                    f"Unescaped braces in '{key}': {value}"
                )
                valid = False

        return valid

    def validate_length_constraints(self) -> bool:
        """Validate translations meet reasonable length constraints."""
        logger.debug("Validating length constraints...")
        valid = True

        messages_en = self._load_messages_from_locale('en')
        messages_target = self._load_messages()

        for key in messages_en:
            if key not in messages_target:
                continue

            source_text = messages_en.get(key, '')
            target_text = messages_target.get(key, '')

            if not isinstance(source_text, str) or not isinstance(target_text, str):
                continue

            source_len = len(source_text)
            target_len = len(target_text)

            # Check ratio (target should be 30-300% of source)
            if source_len > 10:
                ratio = target_len / source_len if source_len > 0 else 1
                if ratio < 0.3 or ratio > 3.0:
                    self.warnings.append(
                        f"Unusual length ratio for '{key}': "
                        f"{source_len} -> {target_len} chars (ratio: {ratio:.2f})"
                    )

        return valid

    def validate_markup(self) -> bool:
        """Validate HTML/Markdown markup consistency."""
        logger.debug("Validating markup...")
        valid = True

        messages = self._load_messages()
        html_pattern = re.compile(r'<[^>]+>')

        for key, value in messages.items():
            if not isinstance(value, str):
                continue

            # Extract HTML tags
            tags = html_pattern.findall(value)
            opening_tags = [t for t in tags if not t.startswith('</')]
            closing_tags = [t for t in tags if t.startswith('</')]

            # Basic tag balance check
            if len(opening_tags) != len(closing_tags):
                self.warnings.append(
                    f"Possible tag mismatch in '{key}': {len(opening_tags)} opening, "
                    f"{len(closing_tags)} closing"
                )

        return valid

    def validate_consistency(self) -> bool:
        """Validate consistency of terminology and style."""
        logger.debug("Validating consistency...")

        messages = self._load_messages()
        self.results['metrics']['total_keys'] = len(messages)

        # Check for common translation patterns
        term_usage: Dict[str, Set[str]] = {}

        for key, value in messages.items():
            if not isinstance(value, str):
                continue

            # Track key terms (longer words)
            words = re.findall(r'\b\w{4,}\b', value.lower())
            for word in words:
                if word not in term_usage:
                    term_usage[word] = set()
                term_usage[word].add(value)

        # Check for inconsistent translations of same terms
        inconsistencies = [
            (term, uses) for term, uses in term_usage.items()
            if len(uses) > 2 and term not in self._get_common_words()
        ]

        if inconsistencies:
            self.warnings.append(
                f"Found {len(inconsistencies)} terms with inconsistent usage"
            )

        return True

    def validate_special_characters(self) -> bool:
        """Validate special characters and diacritics."""
        logger.debug("Validating special characters...")
        valid = True

        messages = self._load_messages()

        for key, value in messages.items():
            if not isinstance(value, str):
                continue

            # Check for invalid control characters
            control_chars = [c for c in value if ord(c) < 32 and c not in '\t\n\r']
            if control_chars:
                self.errors.append(
                    f"Invalid control characters in '{key}'"
                )
                valid = False

            # Check for mixed script runs (potential encoding issues)
            scripts = self._detect_scripts(value)
            if len(scripts) > 3:
                self.warnings.append(
                    f"Multiple script systems in '{key}': {scripts}"
                )

        return valid

    def validate_punctuation(self) -> bool:
        """Validate punctuation usage."""
        logger.debug("Validating punctuation...")

        messages_en = self._load_messages_from_locale('en')
        messages_target = self._load_messages()

        for key in messages_en:
            if key not in messages_target:
                continue

            source = messages_en.get(key, '')
            target = messages_target.get(key, '')

            if not isinstance(source, str) or not isinstance(target, str):
                continue

            # Check terminal punctuation
            source_ends = source[-1] if source else ''
            target_ends = target[-1] if target else ''

            # Punctuation should generally match (with some exceptions)
            if source_ends in '.!?' and target_ends not in '.!?':
                self.warnings.append(
                    f"Punctuation mismatch in '{key}': "
                    f"source ends with '{source_ends}', target ends with '{target_ends}'"
                )

        return True

    def _load_messages(self) -> Dict:
        """Load messages from target locale."""
        messages_file = self.source_dir / 'messages.json'
        if not messages_file.exists():
            return {}

        try:
            with open(messages_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading messages: {e}")
            return {}

    def _load_messages_from_locale(self, locale: str) -> Dict:
        """Load messages from specific locale."""
        # This would need to be configured based on source structure
        return {}

    def _detect_scripts(self, text: str) -> List[str]:
        """Detect script systems in text."""
        scripts = set()
        for char in text:
            code = ord(char)
            if 0x0041 <= code <= 0x005A or 0x0061 <= code <= 0x007A:
                scripts.add('Latin')
            elif 0x0400 <= code <= 0x04FF:
                scripts.add('Cyrillic')
            elif 0x0600 <= code <= 0x06FF:
                scripts.add('Arabic')
            elif 0x4E00 <= code <= 0x9FFF:
                scripts.add('CJK')
            elif 0x3040 <= code <= 0x309F:
                scripts.add('Hiragana')
            elif 0x30A0 <= code <= 0x30FF:
                scripts.add('Katakana')

        return sorted(list(scripts))

    def _get_common_words(self) -> Set[str]:
        """Get set of common words to exclude from consistency checks."""
        return {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during',
        }

    def get_results(self) -> Dict:
        """Get validation results."""
        return self.results
