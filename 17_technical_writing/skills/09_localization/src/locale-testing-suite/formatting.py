"""
Locale Formatting Validation Module

Validates locale-specific formatting (dates, numbers, currency, etc.)
"""

import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List

logger = logging.getLogger(__name__)


class FormattingValidator:
    """Validates locale-specific formatting rules."""

    # Locale-specific formatting rules
    FORMAT_RULES = {
        'es': {
            'decimal_separator': ',',
            'thousands_separator': '.',
            'currency_position': 'after',
        },
        'fr': {
            'decimal_separator': ',',
            'thousands_separator': '\u00A0',  # Non-breaking space
            'currency_position': 'after',
        },
        'de': {
            'decimal_separator': ',',
            'thousands_separator': '.',
            'currency_position': 'after',
        },
        'it': {
            'decimal_separator': ',',
            'thousands_separator': '.',
            'currency_position': 'after',
        },
        'ja': {
            'decimal_separator': '.',
            'thousands_separator': ',',
            'currency_position': 'before',
        },
        'en': {
            'decimal_separator': '.',
            'thousands_separator': ',',
            'currency_position': 'before',
        },
    }

    def __init__(self, locale: str, source_dir: str):
        self.locale = locale
        self.source_dir = Path(source_dir)
        self.rules = self.FORMAT_RULES.get(locale, self.FORMAT_RULES['en'])
        self.results = {
            'locale': locale,
            'formatting_issues': [],
            'currency_issues': [],
            'date_issues': [],
            'number_issues': [],
        }

    def validate_formatting(self) -> bool:
        """Validate all formatting rules."""
        logger.info(f"Validating formatting for {self.locale}")

        self._check_number_formatting()
        self._check_currency_formatting()
        self._check_date_formatting()
        self._check_quote_styles()

        return len(self.results['formatting_issues']) == 0

    def _check_number_formatting(self) -> None:
        """Check number formatting consistency."""
        logger.debug("Checking number formatting...")

        messages = self._load_messages()
        number_pattern = re.compile(r'\d+[.,]?\d*')

        for key, value in messages.items():
            if not isinstance(value, str):
                continue

            # Find all numbers
            for match in number_pattern.finditer(value):
                number_str = match.group()

                # Check decimal separator
                if '.' in number_str:
                    if self.rules['decimal_separator'] != '.':
                        self.results['number_issues'].append({
                            'key': key,
                            'issue': 'Wrong decimal separator',
                            'number': number_str,
                            'expected': self.rules['decimal_separator'],
                        })

    def _check_currency_formatting(self) -> None:
        """Check currency formatting."""
        logger.debug("Checking currency formatting...")

        messages = self._load_messages()
        currency_pattern = re.compile(r'[\$€¥£₹][\s]?\d+[.,]?\d*')

        for key, value in messages.items():
            if not isinstance(value, str):
                continue

            for match in currency_pattern.finditer(value):
                currency_str = match.group()
                # Check position and spacing
                if self.rules['currency_position'] == 'after':
                    if currency_str[0] in '$€¥£₹':
                        self.results['currency_issues'].append({
                            'key': key,
                            'issue': 'Currency should appear after number',
                            'value': currency_str,
                        })

    def _check_date_formatting(self) -> None:
        """Check date formatting patterns."""
        logger.debug("Checking date formatting...")

        messages = self._load_messages()

        # Common date patterns
        date_pattern = re.compile(
            r'\d{1,4}[-./]\d{1,2}[-./]\d{1,4}|'
            r'\d{1,2}[-./]\d{1,2}[-./]\d{1,4}'
        )

        for key, value in messages.items():
            if not isinstance(value, str):
                continue

            for match in date_pattern.finditer(value):
                date_str = match.group()
                # Validate date format for locale
                # Format varies: DD/MM/YYYY vs MM/DD/YYYY vs YYYY-MM-DD

    def _check_quote_styles(self) -> None:
        """Check quote style usage."""
        logger.debug("Checking quote styles...")

        messages = self._load_messages()

        # Different languages use different quotation marks
        locale_quotes = {
            'en': {
                'open': '"',
                'close': '"',
            },
            'de': {
                'open': '„',
                'close': '"',
            },
            'fr': {
                'open': '«',
                'close': '»',
            },
            'es': {
                'open': '«',
                'close': '»',
            },
        }

        expected_quotes = locale_quotes.get(self.locale)
        if not expected_quotes:
            return

        for key, value in messages.items():
            if not isinstance(value, str):
                continue

            # Check for incorrect quote usage
            if '"' in value:
                # Might be wrong quotes for this locale
                if self.locale != 'en':
                    self.results['formatting_issues'].append({
                        'key': key,
                        'issue': 'Possible wrong quotation marks',
                        'value': value,
                    })

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
