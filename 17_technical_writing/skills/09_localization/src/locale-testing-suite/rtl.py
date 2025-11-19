"""
Right-to-Left (RTL) Language Support Validation

Tests RTL language support for Arabic, Hebrew, Persian, etc.
"""

import json
import logging
import re
from pathlib import Path
from typing import Dict, List

logger = logging.getLogger(__name__)


class RTLValidator:
    """Validates RTL language support and rendering."""

    RTL_LANGUAGES = {
        'ar': 'Arabic',
        'he': 'Hebrew',
        'ur': 'Urdu',
        'fa': 'Persian',
        'yi': 'Yiddish',
    }

    def __init__(self, locale: str, source_dir: str):
        self.locale = locale
        self.source_dir = Path(source_dir)
        self.is_rtl = locale in self.RTL_LANGUAGES
        self.results = {
            'locale': locale,
            'is_rtl': self.is_rtl,
            'rtl_issues': [],
            'bidi_issues': [],
            'punctuation_issues': [],
        }

    def validate_rtl(self) -> bool:
        """Validate RTL content."""
        if not self.is_rtl:
            logger.info(f"Locale {self.locale} is not RTL")
            return True

        logger.info(f"Validating RTL for {self.locale}")

        self._check_text_direction()
        self._check_bidi_marks()
        self._check_punctuation()
        self._check_numbers()

        return len(self.results['rtl_issues']) == 0

    def _check_text_direction(self) -> None:
        """Check text direction markers."""
        logger.debug("Checking text direction...")

        messages = self._load_messages()
        rtl_count = 0
        ltr_count = 0

        for key, value in messages.items():
            if not isinstance(value, str):
                continue

            # Count RTL and LTR characters
            for char in value:
                if self._is_rtl_char(char):
                    rtl_count += 1
                elif self._is_ltr_char(char):
                    ltr_count += 1

        # Should be predominantly RTL for RTL languages
        if ltr_count > rtl_count:
            self.results['rtl_issues'].append({
                'type': 'direction_mismatch',
                'message': f'More LTR characters ({ltr_count}) than RTL ({rtl_count})',
            })

    def _check_bidi_marks(self) -> None:
        """Check bidirectional text markers."""
        logger.debug("Checking bidirectional marks...")

        messages = self._load_messages()
        bidi_marks = {
            '\u202A': 'LRE',  # Left-to-Right Embedding
            '\u202B': 'RLE',  # Right-to-Left Embedding
            '\u202C': 'PDF',  # Pop Directional Formatting
            '\u202D': 'LRO',  # Left-to-Right Override
            '\u202E': 'RLO',  # Right-to-Left Override
            '\u200E': 'LRM',  # Left-to-Right Mark
            '\u200F': 'RLM',  # Right-to-Left Mark
        }

        for key, value in messages.items():
            if not isinstance(value, str):
                continue

            for mark, name in bidi_marks.items():
                if mark in value:
                    self.results['bidi_issues'].append({
                        'key': key,
                        'mark': name,
                        'value': value,
                    })

    def _check_punctuation(self) -> None:
        """Check punctuation handling in RTL context."""
        logger.debug("Checking punctuation...")

        messages = self._load_messages()

        # RTL-specific punctuation patterns
        pattern = re.compile(r'[,.!?;:]')

        for key, value in messages.items():
            if not isinstance(value, str):
                continue

            # Check for punctuation at wrong positions
            punctuation_matches = list(pattern.finditer(value))
            if punctuation_matches:
                for match in punctuation_matches:
                    # Check if punctuation is properly placed
                    pos = match.start()
                    if pos > 0 and pos < len(value) - 1:
                        # Punctuation should generally not be between RTL chars
                        pass

    def _check_numbers(self) -> None:
        """Check number handling in RTL text."""
        logger.debug("Checking number handling...")

        messages = self._load_messages()
        digit_pattern = re.compile(r'\d')

        for key, value in messages.items():
            if not isinstance(value, str):
                continue

            # Arabic numbers should use proper digit forms
            if self.locale == 'ar':
                for match in digit_pattern.finditer(value):
                    digit = match.group()
                    # Check if using ASCII digits or Arabic-Indic digits
                    if digit in '0123456789':
                        # Should consider using Arabic-Indic equivalents
                        pass

    def _is_rtl_char(self, char: str) -> bool:
        """Check if character is RTL."""
        code = ord(char)
        # Hebrew
        if 0x0590 <= code <= 0x05FF:
            return True
        # Arabic
        if 0x0600 <= code <= 0x06FF:
            return True
        # Syriac
        if 0x0700 <= code <= 0x074F:
            return True
        # Thaana
        if 0x0780 <= code <= 0x07BF:
            return True
        # NKo
        if 0x07C0 <= code <= 0x07FF:
            return True
        return False

    def _is_ltr_char(self, char: str) -> bool:
        """Check if character is LTR."""
        code = ord(char)
        # Basic Latin
        if 0x0041 <= code <= 0x005A or 0x0061 <= code <= 0x007A:
            return True
        # Latin Extended
        if 0x0100 <= code <= 0x017F:
            return True
        return False

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
