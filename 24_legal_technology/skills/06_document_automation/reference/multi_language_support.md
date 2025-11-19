# Multi-Language Support in Document Automation

## Overview

Supporting multiple languages in document automation enables firms to serve international clients, operate across jurisdictions, and comply with local language requirements.

## Internationalization (i18n) Strategies

### 1. Separate Templates per Language
- Maintain complete template for each language
- Full control over legal terminology
- Simpler logic, no translation layer needed
- Higher maintenance burden

### 2. Translation Files with Single Template
- One template with externalized strings
- Translation files for each language
- Centralized maintenance
- Requires translation management

### 3. Hybrid Approach
- Core template with translation files
- Language-specific template variants for complex sections
- Balance between maintainability and flexibility

## Implementation Approaches

### Translation File Structure

```json
{
  "en": {
    "document_title": "Stock Purchase Agreement",
    "effective_date": "Effective Date",
    "buyer": "Buyer",
    "seller": "Seller",
    "purchase_price": "Purchase Price",
    "recitals": {
      "header": "RECITALS",
      "whereas": "WHEREAS"
    },
    "signature_block": {
      "signed": "SIGNED on this {day} day of {month}, {year}",
      "witness": "In the presence of:",
      "title": "Title:"
    }
  },
  "es": {
    "document_title": "Contrato de Compraventa de Acciones",
    "effective_date": "Fecha Efectiva",
    "buyer": "Comprador",
    "seller": "Vendedor",
    "purchase_price": "Precio de Compra",
    "recitals": {
      "header": "RECITALES",
      "whereas": "CONSIDERANDO"
    },
    "signature_block": {
      "signed": "FIRMADO este día {day} de {month} de {year}",
      "witness": "En presencia de:",
      "title": "Título:"
    }
  },
  "fr": {
    "document_title": "Contrat d'Achat d'Actions",
    "effective_date": "Date d'Entrée en Vigueur",
    "buyer": "Acheteur",
    "seller": "Vendeur",
    "purchase_price": "Prix d'Achat",
    "recitals": {
      "header": "PRÉAMBULE",
      "whereas": "CONSIDÉRANT"
    },
    "signature_block": {
      "signed": "SIGNÉ le {day} {month} {year}",
      "witness": "En présence de:",
      "title": "Titre:"
    }
  },
  "de": {
    "document_title": "Aktienkaufvertrag",
    "effective_date": "Gültigkeitsdatum",
    "buyer": "Käufer",
    "seller": "Verkäufer",
    "purchase_price": "Kaufpreis",
    "recitals": {
      "header": "PRÄAMBEL",
      "whereas": "IN ANBETRACHT"
    },
    "signature_block": {
      "signed": "UNTERZEICHNET am {day}. {month} {year}",
      "witness": "In Anwesenheit von:",
      "title": "Titel:"
    }
  }
}
```

### Template with Translations

```python
from jinja2 import Template
import json

class MultilingualDocumentGenerator:
    def __init__(self, translations_file):
        with open(translations_file, 'r', encoding='utf-8') as f:
            self.translations = json.load(f)

    def t(self, key, language='en', **kwargs):
        """Translate a key in specified language"""
        keys = key.split('.')
        value = self.translations[language]

        for k in keys:
            value = value[k]

        # Format with any provided variables
        if kwargs:
            return value.format(**kwargs)
        return value

    def generate_document(self, data, language='en'):
        """Generate document in specified language"""

        template_text = """
{{ t('document_title') }}

{{ t('effective_date') }}: {{ effective_date }}
{{ t('buyer') }}: {{ buyer_name }}
{{ t('seller') }}: {{ seller_name }}
{{ t('purchase_price') }}: {{ purchase_price }}

{{ t('signature_block.signed', day=day, month=month, year=year) }}

_______________________________
{{ buyer_name }}
{{ t('signature_block.title') }} {{ buyer_title }}
"""

        template = Template(template_text)

        # Create translation function for template context
        def translate(key, **kwargs):
            return self.t(key, language, **kwargs)

        return template.render(
            t=translate,
            **data
        )
```

## Date and Number Formatting

### Locale-Specific Formatting

```python
from babel.dates import format_date, format_datetime
from babel.numbers import format_currency, format_decimal

class LocaleFormatter:
    def __init__(self, locale='en_US'):
        self.locale = locale

    def format_date(self, date, format='long'):
        """Format date according to locale"""
        # en_US: November 19, 2025
        # es_ES: 19 de noviembre de 2025
        # fr_FR: 19 novembre 2025
        # de_DE: 19. November 2025
        return format_date(date, format=format, locale=self.locale)

    def format_currency(self, amount, currency='USD'):
        """Format currency according to locale"""
        # en_US: $5,000,000.00
        # es_ES: 5.000.000,00 US$
        # fr_FR: 5 000 000,00 $US
        # de_DE: 5.000.000,00 $
        return format_currency(amount, currency, locale=self.locale)

    def format_number(self, number):
        """Format number according to locale"""
        # en_US: 1,000,000.50
        # es_ES: 1.000.000,50
        # fr_FR: 1 000 000,50
        # de_DE: 1.000.000,50
        return format_decimal(number, locale=self.locale)

# Usage
formatter_en = LocaleFormatter('en_US')
formatter_es = LocaleFormatter('es_ES')

date_en = formatter_en.format_date(datetime.date(2025, 11, 19))  # "November 19, 2025"
date_es = formatter_es.format_date(datetime.date(2025, 11, 19))  # "19 de noviembre de 2025"

amount_en = formatter_en.format_currency(5000000)  # "$5,000,000.00"
amount_es = formatter_es.format_currency(5000000)  # "5.000.000,00 US$"
```

## Legal Term Translation

### Maintaining Legal Accuracy

```json
{
  "legal_terms": {
    "en": {
      "force_majeure": "Force Majeure",
      "indemnification": "Indemnification",
      "representations_and_warranties": "Representations and Warranties",
      "governing_law": "Governing Law"
    },
    "es": {
      "force_majeure": "Fuerza Mayor",
      "indemnification": "Indemnización",
      "representations_and_warranties": "Declaraciones y Garantías",
      "governing_law": "Ley Aplicable"
    },
    "fr": {
      "force_majeure": "Force Majeure",
      "indemnification": "Indemnisation",
      "representations_and_warranties": "Déclarations et Garanties",
      "governing_law": "Loi Applicable"
    }
  },
  "jurisdiction_specific": {
    "en_US": {
      "corporation": "Corporation",
      "limited_liability_company": "Limited Liability Company (LLC)"
    },
    "en_GB": {
      "corporation": "Company Limited by Shares",
      "limited_liability_company": "Limited Liability Partnership (LLP)"
    },
    "es_MX": {
      "corporation": "Sociedad Anónima (S.A.)",
      "limited_liability_company": "Sociedad de Responsabilidad Limitada (S. de R.L.)"
    }
  }
}
```

## Character Encoding

### UTF-8 Support

```python
# Always use UTF-8 encoding
with open('document.txt', 'w', encoding='utf-8') as f:
    f.write("Société Française™")

# DOCX automatically handles UTF-8
from docx import Document
doc = Document()
doc.add_paragraph("北京市 • München • Москва • São Paulo")
doc.save('multilingual.docx')

# PDF with UTF-8
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Register Unicode font
pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))

c = canvas.Canvas("multilingual.pdf")
c.setFont('Arial', 12)
c.drawString(100, 750, "English, Español, Français, Deutsch, 中文, 日本語")
c.save()
```

## Right-to-Left (RTL) Languages

### Hebrew and Arabic Support

```python
from bidi.algorithm import get_display
import arabic_reshaper

def prepare_rtl_text(text, language='ar'):
    """Prepare RTL text for display"""
    if language in ['ar', 'he']:
        if language == 'ar':
            # Reshape Arabic text
            reshaped_text = arabic_reshaper.reshape(text)
        else:
            reshaped_text = text

        # Apply BiDi algorithm
        bidi_text = get_display(reshaped_text)
        return bidi_text
    return text

# Arabic example
arabic_text = "اتفاقية شراء الأسهم"
display_text = prepare_rtl_text(arabic_text, 'ar')

# Use in document
doc = Document()
paragraph = doc.add_paragraph(display_text)
paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.RIGHT
```

## Questionnaire Localization

### Multi-Language Interviews

```javascript
const translations = {
  en: {
    questions: {
      buyer_name: {
        label: "Buyer's Legal Name",
        help: "Enter the full legal name of the buyer",
        placeholder: "e.g., Acme Corporation"
      },
      purchase_price: {
        label: "Purchase Price",
        help: "Enter the total purchase price",
        placeholder: "e.g., 5000000"
      }
    },
    errors: {
      required: "This field is required",
      invalid_email: "Please enter a valid email address",
      invalid_number: "Please enter a valid number"
    },
    buttons: {
      next: "Next",
      previous: "Previous",
      submit: "Submit",
      save_draft: "Save Draft"
    }
  },
  es: {
    questions: {
      buyer_name: {
        label: "Nombre Legal del Comprador",
        help: "Ingrese el nombre legal completo del comprador",
        placeholder: "ej., Corporación Acme"
      },
      purchase_price: {
        label: "Precio de Compra",
        help: "Ingrese el precio total de compra",
        placeholder: "ej., 5000000"
      }
    },
    errors: {
      required: "Este campo es obligatorio",
      invalid_email: "Por favor ingrese una dirección de correo válida",
      invalid_number: "Por favor ingrese un número válido"
    },
    buttons: {
      next: "Siguiente",
      previous: "Anterior",
      submit: "Enviar",
      save_draft: "Guardar Borrador"
    }
  }
};

function getTranslation(language, key) {
  const keys = key.split('.');
  let value = translations[language];
  for (const k of keys) {
    value = value[k];
  }
  return value;
}
```

## Best Practices

### 1. Separate Content from Code
```
Don't: Hard-code text in templates
Do: Externalize all user-facing text
```

### 2. Use Professional Translators
```
Don't: Rely on machine translation for legal documents
Do: Engage qualified legal translators for each language
```

### 3. Handle Plurals Correctly
```javascript
// English
const items_en = {
  one: "1 item",
  other: "{count} items"
};

// Russian (has more plural forms)
const items_ru = {
  one: "{count} элемент",    // 1, 21, 31...
  few: "{count} элемента",   // 2-4, 22-24...
  many: "{count} элементов", // 0, 5-20, 25-30...
  other: "{count} элементов"
};

function pluralize(count, translations, language) {
  const rule = new Intl.PluralRules(language).select(count);
  return translations[rule].replace('{count}', count);
}
```

### 4. Consider Text Expansion
```
Allow 30-40% more space for translations:
- German text is often 30% longer than English
- French text is often 15-20% longer
- Asian languages may be more compact

Design templates with flexible layouts
```

### 5. Test with Actual Languages
```
Don't test with Lorem Ipsum
Do test with actual target language content
- Check character display
- Verify text wrapping
- Confirm formatting
- Test special characters
```

### 6. Maintain Translation Memory
```
Use CAT (Computer-Assisted Translation) tools:
- Store previously translated segments
- Ensure consistency across documents
- Reduce translation time and cost
- Maintain terminology databases
```

## Jurisdiction-Specific Content

### Conditional Content by Jurisdiction

```python
def get_governing_law_clause(jurisdiction, language):
    """Get appropriate governing law clause based on jurisdiction"""

    clauses = {
        ('US', 'Delaware', 'en'): "This Agreement shall be governed by the laws of the State of Delaware.",
        ('US', 'California', 'en'): "This Agreement shall be governed by the laws of the State of California.",
        ('MX', 'Federal', 'es'): "Este Acuerdo se regirá por las leyes federales de México.",
        ('FR', 'National', 'fr'): "Le présent accord est régi par le droit français.",
        ('DE', 'National', 'de'): "Dieser Vertrag unterliegt deutschem Recht."
    }

    country = jurisdiction['country']
    state = jurisdiction.get('state', 'National')

    return clauses.get((country, state, language), "")

def get_signature_requirements(jurisdiction, language):
    """Get signature requirements based on jurisdiction"""

    requirements = {
        ('US', 'en'): {
            'witnesses': 0,
            'notary': False,
            'instructions': "Signatures of all parties required."
        },
        ('MX', 'es'): {
            'witnesses': 2,
            'notary': True,
            'instructions': "Requiere dos testigos y notarización."
        },
        ('FR', 'fr'): {
            'witnesses': 0,
            'notary': True,
            'instructions': "Signature notariée requise pour les transactions immobilières."
        }
    }

    return requirements.get((jurisdiction['country'], language), {})
```

## Testing Multi-Language Templates

```python
def test_multilingual_document_generation():
    """Test document generation in multiple languages"""

    test_data = {
        'buyer_name': 'Acme Corporation',
        'seller_name': 'Smith Industries',
        'purchase_price': 5000000,
        'effective_date': datetime.date(2025, 11, 19)
    }

    for language in ['en', 'es', 'fr', 'de']:
        # Generate document
        doc = generate_document(test_data, language=language)

        # Verify generation succeeded
        assert doc is not None

        # Verify language-specific content
        doc_text = extract_text(doc)

        if language == 'en':
            assert 'Stock Purchase Agreement' in doc_text
        elif language == 'es':
            assert 'Contrato de Compraventa de Acciones' in doc_text
        elif language == 'fr':
            assert "Contrat d'Achat d'Actions" in doc_text
        elif language == 'de':
            assert 'Aktienkaufvertrag' in doc_text

        # Verify proper character encoding
        assert doc.encoding == 'utf-8' or doc.encoding is None

        # Verify date formatting
        # Each language should have appropriately formatted dates
```

Multi-language support requires careful planning, professional translation, and thorough testing to ensure legal accuracy and cultural appropriateness across all target languages.
