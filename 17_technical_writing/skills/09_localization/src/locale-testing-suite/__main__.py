"""
CLI Entry Point for Locale Testing Suite

Usage:
    python -m locale_testing_suite --locale fr --source-dir ./locales/fr
"""

import argparse
import json
import logging
import sys
from pathlib import Path

from .validator import LocaleValidator
from .renderer import LocaleRenderer
from .encoding import EncodingValidator
from .rtl import RTLValidator
from .formatting import FormattingValidator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Comprehensive Locale Testing Suite'
    )
    parser.add_argument(
        '--locale',
        required=True,
        help='Locale code (e.g., fr, es, de)'
    )
    parser.add_argument(
        '--source-dir',
        required=True,
        help='Source directory containing locale files'
    )
    parser.add_argument(
        '--output-dir',
        default='.',
        help='Output directory for reports'
    )
    parser.add_argument(
        '--strict',
        action='store_true',
        help='Enable strict validation mode'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    locale = args.locale
    source_dir = Path(args.source_dir)
    output_dir = Path(args.output_dir)

    if not source_dir.exists():
        logger.error(f"Source directory not found: {source_dir}")
        return 1

    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"Starting locale testing for: {locale}")

    results = {
        'locale': locale,
        'summary': {},
        'validators': {},
    }

    # Run validators
    try:
        # Validation
        logger.info("Running validation checks...")
        validator = LocaleValidator(locale, str(source_dir), strict=args.strict)
        validator.validate_all()
        results['validators']['validation'] = validator.get_results()

        # Rendering
        logger.info("Rendering locale content...")
        renderer = LocaleRenderer(locale, str(source_dir))
        renderer.render_all()
        html_output = output_dir / f'render-{locale}.html'
        renderer.save_render(str(html_output))
        logger.info(f"Rendered output: {html_output}")

        # Encoding
        logger.info("Validating character encoding...")
        encoding_validator = EncodingValidator(locale, str(source_dir))
        encoding_validator.validate_encoding()
        encoding_validator.validate_normalization()
        encoding_validator.check_combining_characters()
        encoding_validator.check_surrogate_pairs()
        results['validators']['encoding'] = encoding_validator.results

        # RTL
        if locale in ['ar', 'he', 'ur', 'fa']:
            logger.info("Validating RTL support...")
            rtl_validator = RTLValidator(locale, str(source_dir))
            rtl_validator.validate_rtl()
            results['validators']['rtl'] = rtl_validator.results

        # Formatting
        logger.info("Validating locale formatting...")
        formatting_validator = FormattingValidator(locale, str(source_dir))
        formatting_validator.validate_formatting()
        results['validators']['formatting'] = formatting_validator.results

        # Summary
        all_valid = all(
            not validator_result.get('errors', [])
            for validator_result in results['validators'].values()
            if isinstance(validator_result, dict)
        )

        results['summary'] = {
            'all_valid': all_valid,
            'validators_run': list(results['validators'].keys()),
        }

        # Save results
        results_file = output_dir / f'validate-{locale}.json'
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        logger.info(f"Validation results saved to: {results_file}")
        logger.info(f"Validation {'PASSED' if all_valid else 'FAILED'}")

        return 0 if all_valid else 1

    except Exception as e:
        logger.error(f"Error during locale testing: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
