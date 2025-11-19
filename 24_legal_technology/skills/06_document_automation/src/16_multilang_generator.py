#!/usr/bin/env python3
"""
Multilingual Document Generator - Generate legal documents in multiple languages.

Production-ready module for managing translations, locale-specific formatting,
and multilingual document generation with terminology databases.
"""

import logging
import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path
import uuid
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class Language(Enum):
    """Supported languages."""
    ENGLISH = "en"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"
    PORTUGUESE = "pt"
    CHINESE = "zh"
    JAPANESE = "ja"
    KOREAN = "ko"
    ITALIAN = "it"
    RUSSIAN = "ru"


class Locale(Enum):
    """Language and regional locales."""
    EN_US = "en_US"
    EN_GB = "en_GB"
    ES_ES = "es_ES"
    ES_MX = "es_MX"
    FR_FR = "fr_FR"
    FR_CA = "fr_CA"
    DE_DE = "de_DE"
    PT_BR = "pt_BR"
    PT_PT = "pt_PT"
    ZH_CN = "zh_CN"
    ZH_TW = "zh_TW"
    JA_JP = "ja_JP"
    KO_KR = "ko_KR"
    IT_IT = "it_IT"
    RU_RU = "ru_RU"


@dataclass
class Translation:
    """Represents a single translation."""
    key: str
    source_language: Language
    target_language: Language
    source_text: str
    target_text: str
    context: Optional[str] = None
    reviewed: bool = False
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    legal_verified: bool = False
    confidence_score: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['source_language'] = self.source_language.value
        data['target_language'] = self.target_language.value
        data['reviewed_at'] = self.reviewed_at.isoformat() if self.reviewed_at else None
        return data


@dataclass
class TerminologyEntry:
    """Legal terminology entry for consistent translation."""
    term_id: str
    source_term: str
    translations: Dict[str, str] = field(default_factory=dict)
    definition: str = ""
    jurisdiction: Optional[str] = None
    category: str = "general"
    approved: bool = False
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        return data


@dataclass
class LocaleFormatting:
    """Locale-specific formatting rules."""
    locale: Locale
    date_format: str
    time_format: str
    currency_format: str
    number_format: str
    decimal_separator: str
    thousands_separator: str
    text_direction: str = "ltr"  # ltr or rtl

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class TranslationMemory:
    """Manages translation memory database."""

    def __init__(self):
        """Initialize translation memory."""
        self.translations: Dict[str, Translation] = {}
        self.terminology: Dict[str, TerminologyEntry] = {}
        self.created_at = datetime.now()
        logger.info("Initialized translation memory")

    def add_translation(self, translation: Translation) -> None:
        """Add translation to memory."""
        key = f"{translation.key}_{translation.source_language.value}_{translation.target_language.value}"
        self.translations[key] = translation
        logger.debug(f"Added translation: {key}")

    def add_terminology(self, entry: TerminologyEntry) -> None:
        """Add terminology entry."""
        self.terminology[entry.term_id] = entry
        logger.debug(f"Added terminology entry: {entry.term_id}")

    def find_translation(
        self,
        key: str,
        source_language: Language,
        target_language: Language,
        reviewed_only: bool = False
    ) -> Optional[Translation]:
        """Find translation in memory."""
        translation_key = f"{key}_{source_language.value}_{target_language.value}"
        translation = self.translations.get(translation_key)

        if translation and reviewed_only and not translation.reviewed:
            return None

        return translation

    def find_similar_translations(
        self,
        text: str,
        source_language: Language,
        target_language: Language,
        min_similarity: float = 0.8
    ) -> List[Translation]:
        """Find similar translations based on fuzzy matching."""
        # Simplified similarity - in production use better algorithms
        matching = []
        for translation in self.translations.values():
            if (translation.source_language == source_language and
                translation.target_language == target_language):
                if len(text) > 5 and text.lower() in translation.source_text.lower():
                    matching.append(translation)

        return matching[:5]  # Return top 5

    def get_terminology(self, term: str, locale: Locale) -> Optional[Dict[str, str]]:
        """Get terminology entry for a term."""
        for entry in self.terminology.values():
            if entry.source_term.lower() == term.lower():
                lang_code = locale.value.split("_")[0]
                translation = entry.translations.get(lang_code)
                return {
                    "term": term,
                    "translation": translation,
                    "definition": entry.definition
                }
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "created_at": self.created_at.isoformat(),
            "total_translations": len(self.translations),
            "total_terminology_entries": len(self.terminology),
            "reviewed_translations": len([t for t in self.translations.values() if t.reviewed])
        }


class Translator(ABC):
    """Abstract base class for translators."""

    @abstractmethod
    def translate(self, text: str, source_language: Language, target_language: Language) -> str:
        """Translate text."""
        pass


class TranslationService:
    """Service for managing translations."""

    def __init__(self, translation_memory: TranslationMemory):
        """Initialize service."""
        self.memory = translation_memory
        self.translators: Dict[str, Translator] = {}
        logger.info("Initialized translation service")

    def register_translator(self, language_pair: str, translator: Translator) -> None:
        """Register translator for language pair."""
        self.translators[language_pair] = translator
        logger.debug(f"Registered translator: {language_pair}")

    def translate(
        self,
        text: str,
        source_language: Language,
        target_language: Language,
        use_terminology: bool = True
    ) -> str:
        """Translate text with fallback strategies."""
        if source_language == target_language:
            return text

        # Check translation memory
        key = hashlib.md5(text.encode()).hexdigest()
        memory_translation = self.memory.find_translation(
            key,
            source_language,
            target_language,
            reviewed_only=True
        )

        if memory_translation:
            logger.debug(f"Using translation from memory")
            return memory_translation.target_text

        # Check terminology
        if use_terminology:
            terms = text.split()
            for term in terms:
                terminology = self.memory.get_terminology(term, Locale.EN_US)
                if terminology:
                    text = text.replace(term, terminology.get("translation", term))

        # Call translator
        translator_key = f"{source_language.value}_{target_language.value}"
        if translator_key in self.translators:
            translator = self.translators[translator_key]
            translated = translator.translate(text, source_language, target_language)
            logger.debug(f"Translated using {translator_key}")
            return translated

        logger.warning(f"No translator for {translator_key}")
        return text


class LocalizationFormatter:
    """Formats content according to locale rules."""

    def __init__(self):
        """Initialize formatter."""
        self.locale_rules: Dict[str, LocaleFormatting] = {}
        self._setup_default_locales()
        logger.info("Initialized localization formatter")

    def _setup_default_locales(self) -> None:
        """Setup default locale formatting rules."""
        default_rules = [
            LocaleFormatting(
                locale=Locale.EN_US,
                date_format="MM/DD/YYYY",
                time_format="HH:mm:ss AM/PM",
                currency_format="$#,##0.00",
                number_format="#,##0.00",
                decimal_separator=".",
                thousands_separator=","
            ),
            LocaleFormatting(
                locale=Locale.DE_DE,
                date_format="DD.MM.YYYY",
                time_format="HH:mm:ss",
                currency_format="#,##0.00 EUR",
                number_format="#.##0,00",
                decimal_separator=",",
                thousands_separator="."
            ),
            LocaleFormatting(
                locale=Locale.FR_FR,
                date_format="DD/MM/YYYY",
                time_format="HH:mm:ss",
                currency_format="#,##0.00 EUR",
                number_format="#.##0,00",
                decimal_separator=",",
                thousands_separator="."
            )
        ]

        for rule in default_rules:
            self.locale_rules[rule.locale.value] = rule

    def format_date(self, date: datetime, locale: Locale) -> str:
        """Format date according to locale."""
        rule = self.locale_rules.get(locale.value)
        if not rule:
            return str(date)

        # Simplified formatting - in production use proper library
        return date.strftime("%d/%m/%Y")

    def format_currency(self, amount: float, locale: Locale) -> str:
        """Format currency according to locale."""
        rule = self.locale_rules.get(locale.value)
        if not rule:
            return f"${amount:,.2f}"

        # Simplified - in production handle all locales
        if locale == Locale.EN_US:
            return f"${amount:,.2f}"
        else:
            return f"{amount:,.2f} EUR"

    def format_number(self, number: float, locale: Locale) -> str:
        """Format number according to locale."""
        rule = self.locale_rules.get(locale.value)
        if not rule:
            return f"{number:,.2f}"

        # Simplified formatting
        return f"{number:,.2f}"


class MultilingualDocumentGenerator:
    """Generates documents in multiple languages."""

    def __init__(
        self,
        translation_service: TranslationService,
        formatter: LocalizationFormatter
    ):
        """Initialize generator."""
        self.translation_service = translation_service
        self.formatter = formatter
        self.generated_documents: Dict[str, Dict[str, Any]] = {}
        logger.info("Initialized multilingual document generator")

    def generate(
        self,
        template: Dict[str, Any],
        data: Dict[str, Any],
        source_language: Language,
        target_languages: List[Language],
        locale: Locale
    ) -> Dict[str, Dict[str, Any]]:
        """Generate document in multiple languages."""
        generated = {}

        for target_language in target_languages:
            logger.info(f"Generating document in {target_language.value}")

            translated_content = {}
            for key, value in template.items():
                if isinstance(value, str):
                    translated_value = self.translation_service.translate(
                        value,
                        source_language,
                        target_language
                    )
                    translated_content[key] = translated_value
                else:
                    translated_content[key] = value

            # Apply localization
            if "date" in data:
                translated_content["date"] = self.formatter.format_date(
                    data["date"],
                    locale
                )

            if "amount" in data:
                translated_content["amount"] = self.formatter.format_currency(
                    data["amount"],
                    locale
                )

            document_id = str(uuid.uuid4())
            generated[target_language.value] = {
                "id": document_id,
                "language": target_language.value,
                "locale": locale.value,
                "content": translated_content,
                "generated_at": datetime.now().isoformat()
            }

            self.generated_documents[document_id] = generated[target_language.value]

        return generated

    def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get generated document."""
        return self.generated_documents.get(document_id)


def create_sample_translation_memory() -> TranslationMemory:
    """Create sample translation memory."""
    memory = TranslationMemory()

    # Add translations
    translations = [
        Translation(
            key="agreement_title",
            source_language=Language.ENGLISH,
            target_language=Language.SPANISH,
            source_text="Service Agreement",
            target_text="Acuerdo de Servicio",
            reviewed=True,
            reviewed_by="translator@example.com"
        ),
        Translation(
            key="client_name",
            source_language=Language.ENGLISH,
            target_language=Language.FRENCH,
            source_text="Client Name",
            target_text="Nom du Client",
            reviewed=True
        )
    ]

    for translation in translations:
        memory.add_translation(translation)

    # Add terminology
    terminology = [
        TerminologyEntry(
            term_id="contract",
            source_term="Contract",
            translations={"es": "Contrato", "fr": "Contrat", "de": "Vertrag"},
            definition="A binding agreement between parties",
            category="legal"
        )
    ]

    for entry in terminology:
        memory.add_terminology(entry)

    return memory


if __name__ == "__main__":
    # Setup
    memory = create_sample_translation_memory()
    service = TranslationService(memory)
    formatter = LocalizationFormatter()
    generator = MultilingualDocumentGenerator(service, formatter)

    # Generate
    template = {
        "title": "Service Agreement",
        "body": "This agreement is made between parties"
    }

    data = {
        "date": datetime.now(),
        "amount": 50000
    }

    documents = generator.generate(
        template,
        data,
        Language.ENGLISH,
        [Language.SPANISH, Language.FRENCH],
        Locale.EN_US
    )

    print("Generated Documents:")
    print(json.dumps(documents, indent=2, default=str))

    print("\nTranslation Memory Statistics:")
    print(json.dumps(memory.to_dict(), indent=2))
