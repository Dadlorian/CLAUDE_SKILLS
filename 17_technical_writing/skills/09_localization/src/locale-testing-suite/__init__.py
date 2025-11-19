"""
Locale Testing Suite - Comprehensive Localization Testing Framework

Provides automated testing for localized content across multiple dimensions:
- Encoding validation
- Character rendering
- Locale-specific formatting
- RTL language support
- Pluralization rules
- Currency and number formatting
- Date/time formatting
- Text overflow and layout issues

Usage:
    from locale_testing_suite import LocaleValidator, LocaleRenderer

    validator = LocaleValidator(locale='fr', source_dir='./locales/fr')
    validator.validate_all()
"""

__version__ = '1.0.0'
__author__ = 'Technical Writing Team'

from .validator import LocaleValidator
from .renderer import LocaleRenderer
from .encoding import EncodingValidator
from .rtl import RTLValidator
from .formatting import FormattingValidator

__all__ = [
    'LocaleValidator',
    'LocaleRenderer',
    'EncodingValidator',
    'RTLValidator',
    'FormattingValidator',
]
