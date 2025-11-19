# Translation Workflow Guide

## Overview

This document outlines the complete translation workflow for documentation, from content preparation through quality assurance and publication.

## Phase 1: Content Preparation (2 weeks)

### Step 1: Content Finalization

**Before sending content for translation, ensure**:

- [ ] Content is complete and reviewed
- [ ] All links are correct and functional
- [ ] Code samples are tested and working
- [ ] Screenshots are final (UI won't change)
- [ ] Terminology is consistent
- [ ] No placeholder text remains

**Checklist**:
```bash
# Check for incomplete content
grep -r "TODO\|FIXME\|XXX" docs/

# Check for broken links
npm run check:links

# Verify all code samples
npm run test:code-samples
```

### Step 2: Glossary Creation

**Create a standard glossary for consistent terminology**:

```csv
English,Spanish,French,Japanese,Chinese,Notes
API,API,API,API,API,Do not translate
endpoint,punto final,point de terminaison,エンドポイント,端点,Technical term
authentication,autenticación,authentification,認証,身份验证,Security term
charge,transacción,paiement,課金,收费,Payment term
refund,reembolso,remboursement,払い戻し,退款,Financial term
webhook,webhook,webhook,ウェブフック,网络挂钩,Newer term
rate limit,límite de tasa,limite de débit,レート制限,速率限制,API term
```

### Step 3: Translator Notes

**Add notes for translators in the source files**:

```markdown
<!-- Translator Note: "API key" should not be translated -->
Your API key (see [authentication](/docs/authentication))
is required for all requests.

<!-- Translator Note: Keep code examples exactly as shown -->
```

### Step 4: Extract Strings

**Prepare files for translation**:

```bash
# Extract translatable strings
npm run extract:strings

# This creates:
# - i18n/en/common.json
# - i18n/en/errors.json
# - i18n/en/guides.json
```

### Step 5: Screenshot Localization Plan

**For each screenshot**:

- List screenshots to localize (not code screenshots)
- Plan how to handle UI text in screenshots
- Decide: retake with locale UI, add translated labels, or use generic version

**Example**:
- ✅ Localize: UI screenshots with user-facing text
- ❌ Don't localize: Code editor screenshots, terminal output
- ⚠️ Consider: Maps, diagrams (if locale-specific)

---

## Phase 2: Translation (3-4 weeks)

### Step 1: Assign to Translation Provider

**Choose translation approach**:

1. **Professional Translation Agency** (High Quality)
   - Cost: $150-300 per 1000 words
   - Time: 2-3 weeks
   - Quality: 95%+
   - Examples: Linguee, Transifex, Crowdin

2. **Freelance Translators** (Medium Cost)
   - Cost: $50-150 per 1000 words
   - Time: 1-2 weeks
   - Quality: 85-95%
   - Platforms: Upwork, Fiverr, PeoplePerHour

3. **Community Translation** (Low Cost)
   - Cost: Free or small bounty
   - Time: 2-4 weeks
   - Quality: Variable
   - Platform: Crowdin community projects

### Step 2: Create Translation Project

**Using Crowdin** (recommended for docs):

```bash
# Install Crowdin CLI
npm install -g @crowdin/cli

# Initialize project
crowdin init

# Configure crowdin.yml
```

**crowdin.yml**:
```yaml
project_id: YOUR_PROJECT_ID
api_token: YOUR_API_TOKEN

files:
  - source: /docs/en/**/*.md
    translation: /i18n/%locale%/**/%original_file_name%
    languages_mapping:
      locale:
        de: de-DE
        fr: fr-FR
        ja: ja
        es: es-ES
        zh_CN: zh-CN
```

### Step 3: Provide Context

**For each translatable segment**:

1. **Add comments explaining context**:
   ```
   "API endpoint" - A web URL that receives requests
   ```

2. **Attach screenshots showing UI context**

3. **Explain technical terms**:
   ```
   "payload" - The data sent with a request
   ```

4. **Highlight which terms should NOT be translated**:
   ```
   API, JSON, REST, HTTP - do NOT translate
   ```

### Step 4: Machine Translation (Optional First Pass)

**Use machine translation for first draft**:

```python
from deepl import translate

text = "Create a charge using the API endpoint"
result = translate(text, target_lang="ES")
print(result)  # "Crear un cargo usando el punto final de la API"
```

**Advantages**:
- Fast initial draft
- Reduces translator costs by 30-50%
- Provides baseline for translators

**Always followed by professional translation**

### Step 5: Professional Translation

**Translator responsibilities**:

- [ ] Translate all text accurately
- [ ] Use glossary terms consistently
- [ ] Maintain code samples (don't translate)
- [ ] Preserve formatting and structure
- [ ] Handle special characters correctly
- [ ] Check for locale-specific conventions

**Translation Tips for Translators**:

```markdown
# Translation Guide for Spanish Translators

## Special Cases

1. **Code samples**: Never translate
   ```
   const user = { id: 1, name: 'John' };
   ```
   Remains exactly the same

2. **URLs**: Never translate
   ✅ https://api.example.com/v1/charges
   ❌ https://api.ejemplo.com/v1/cobros

3. **Parameter names**: Never translate
   ✅ amount: 2000
   ❌ cantidad: 2000

4. **Commands**: Translate explanations, not commands
   ✅ "Run this command: npm install"
   ❌ "Run this command: npm instalar"

5. **Notes and warnings**:
   ✅ Translate but keep bold/emphasis
   ✅ "⚠️ **Advertencia**: This is important"

## Terminology

Always use these terms:

| English | Spanish |
|---------|---------|
| API | API (no traducir) |
| endpoint | punto final |
| charge | transacción |
| refund | reembolso |
| payload | carga útil |
| header | encabezado |
```

---

## Phase 3: Quality Assurance (1-2 weeks)

### Step 1: Technical Review

**Reviewer checks**:

- [ ] All sections translated (100% complete)
- [ ] No mixed languages
- [ ] Code samples untouched
- [ ] URLs unchanged
- [ ] Terminology consistent (check glossary)
- [ ] Links functional
- [ ] Images localized where needed

**Checklist Script**:
```bash
#!/bin/bash

# Check for English words in Spanish file
grep -E "[a-zA-Z]{4,}" i18n/es/*.md | grep -v "API\|JSON\|HTTP"

# Check code samples are unchanged
diff docs/en/api.md i18n/es/api.md | grep -E "^\>" | head -5

# Verify glossary usage
for term in "API" "endpoint" "charge"; do
  echo "Checking: $term"
  grep -r "$term" i18n/es/
done
```

### Step 2: Translator Review

**Native speaker (not original translator) reviews**:

- [ ] Reads naturally in target language
- [ ] Follows target language conventions
- [ ] Tone matches source
- [ ] No awkward phrasings
- [ ] Cultural appropriateness
- [ ] Example: "Authorize the API" in Spanish

### Step 3: Content Review

**Subject Matter Expert reviews**:

- [ ] Technical accuracy preserved
- [ ] Concepts correctly explained
- [ ] Examples still valid for locale
- [ ] Steps still applicable

### Step 4: Accessibility Review

**Check translated content**:

- [ ] Heading hierarchy preserved
- [ ] Alt text for images translated
- [ ] Links still accessible
- [ ] Color contrast maintained

### Step 5: Proofreading

**Final proofreading checklist**:

```markdown
# Proofreading Checklist

- [ ] Spelling (use locale-specific spell checker)
- [ ] Grammar and syntax
- [ ] Punctuation (note: French uses spaces before colons)
- [ ] Whitespace and line breaks preserved
- [ ] Formatting (bold, italics) consistent
- [ ] Lists formatted correctly
- [ ] Tables aligned properly
- [ ] Code blocks formatted
- [ ] Special characters (quotes, dashes) correct

## Locale-Specific Rules

### French
- Space before: : ! ? « »
- Example: "Question ?" (not "Question?")

### Spanish
- ¡ and ¿ required for questions and exclamations
- Example: "¿Cómo?" (not "Cómo?")

### Japanese
- No spaces between words (handled by CJK processing)
- Full-width punctuation used

### Chinese
- Simplified characters (zh-CN) vs Traditional (zh-TW)
- Full-width punctuation
```

---

## Phase 4: Screenshot and Asset Localization (1 week)

### Step 1: Update Screenshots

**For user-facing UI screenshots**:

1. **Change system language** to target locale
2. **Retake screenshots**
3. **Rename files**:
   ```
   screenshots/en/dashboard.png
   → screenshots/es/dashboard.png
   ```

**For code/terminal screenshots**:
- No localization needed
- Use same image for all languages
- Code is universal

### Step 2: Update Diagrams

**For diagrams with text**:

1. **Export from diagram tool**
2. **Translate text**
3. **Re-export with new language**

**Skip localization for**:
- Architecture diagrams (code-focused)
- Mermaid diagrams (usually universal)
- Technical flowcharts

### Step 3: Update Links

**Verify all links point to correct locale**:

```markdown
❌ Bad: [See the guide](/en/guides/authentication)
✅ Good: [See the guide](./authentication)  # Relative link
✅ Good: [See the guide](/es/guides/authentication)  # For cross-locale links
```

---

## Phase 5: Quality Testing (3-5 days)

### Step 1: Build and Deploy to Staging

```bash
# Build documentation with translations
npm run build:i18n

# Deploy to staging environment
npm run deploy:staging

# Verify at: https://staging-docs.example.com/es/
```

### Step 2: Accessibility Testing

```bash
# Test with different locales
npm run test:a11y -- --locale es
npm run test:a11y -- --locale ja

# Check for RTL issues (Arabic)
npm run test:rtl
```

### Step 3: Content Testing

```bash
# Test all links
npm run test:links -- --locale es --locale fr

# Test code samples (if locale-specific)
npm run test:code-samples -- --locale es

# Visual regression testing
npm run test:visual -- --locales es,fr,ja
```

### Step 4: User Testing

**Have native speakers test**:

1. Navigate documentation
2. Follow code tutorials
3. Identify confusing sections
4. Check for formatting issues
5. Verify screenshots make sense

**Collect feedback on**:
- Clarity and readability
- Technical accuracy
- Navigation ease
- Visual consistency
- Cultural appropriateness

---

## Phase 6: Localization Review Meeting

**Schedule 1-hour review call**:

**Participants**:
- Project lead
- Translator(s)
- Subject matter expert
- Localization coordinator
- Representative from each language team

**Agenda**:
1. Review feedback from testing (15 min)
2. Discuss any remaining issues (20 min)
3. Approve for publication (10 min)
4. Plan ongoing maintenance (15 min)

**Decision**: Proceed to publication or request revisions

---

## Phase 7: Publication (2 days)

### Step 1: Final Staging Verification

```bash
# Do final build
npm run build:i18n

# Smoke test all locales
npm run test:smoke -- --locales en,es,fr,ja,zh-CN
```

### Step 2: Publish to Production

```bash
# Tag release
git tag -a v1.2.0 -m "Release with Spanish, French, Japanese, Chinese"

# Deploy
npm run deploy:production

# Verify in production
curl https://docs.example.com/es/  # Should return Spanish version
```

### Step 3: Monitor for Issues

**Set up monitoring**:

```javascript
// Monitor translated content
analytics.trackEvent('page_view', {
  locale: navigator.language,
  page: window.location.pathname,
  lang_loaded: document.documentElement.lang
});
```

**Monitor for errors**:

```yaml
# .github/workflows/monitor-translations.yml
name: Monitor Translations

on:
  schedule:
    - cron: '0 0 * * *'  # Daily

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - name: Check all translation links
        run: npm run test:links -- --all-locales

      - name: Check for untranslated content
        run: npm run check:coverage -- --min 99%
```

---

## Ongoing Maintenance

### Step 1: Keep Translations Current

**When content is updated**:

1. Update English version
2. Flag changes for translators
3. Update translations within 2 weeks
4. Re-test and publish

```bash
# Identify changes since last translation
git diff docs/en/ docs-original/

# Create change summary for translators
npm run generate:translation-brief
```

### Step 2: Gather Community Feedback

**Monitor for translation issues**:

```markdown
# Report Translation Issues

Found a translation error? Help us improve!

1. [Report an issue](https://github.com/example/docs/issues/new?template=translation)
2. [Join our translation team](https://crowdin.com/project/example)
3. [Send feedback](mailto:translations@example.com)
```

### Step 3: Quarterly Review

**Every 3 months**:

- [ ] Review translation quality metrics
- [ ] Identify stale translations (>6 months old)
- [ ] Update glossary with new terms
- [ ] Plan translation updates
- [ ] Celebrate translator contributions

---

## Tools and Resources

### Translation Management

- **Crowdin**: Full translation management platform
- **Transifex**: Alternative platform
- **Lokalise**: Developer-friendly option
- **Weblate**: Open source option

### Machine Translation (for first drafts)

- **DeepL**: Best for European languages
- **Google Translate API**: Free tier available
- **Microsoft Translator**: Enterprise option

### Quality Assurance

- **Grammarly**: English proofreading
- **LanguageTool**: Multilingual checking
- **Poedit**: PO file editor with QA

### Accessibility

- **WAVE**: Accessibility checker
- **Pa11y**: CLI accessibility tester
- **Lighthouse**: Built-in accessibility audit

---

## Metrics and Success

**Track translation quality**:

| Metric | Target | Tool |
|--------|--------|------|
| Translation Completeness | 100% | Crowdin dashboard |
| Quality Score | >95% | Translation QA |
| Time to Publish | <2 weeks | Project timeline |
| User Satisfaction | >80% NPS | In-app feedback |

---

## Contact and Support

- **Translation Questions**: translations@example.com
- **Crowdin Project**: crowdin.com/project/example
- **Discord Community**: discord.gg/example
- **GitHub Issues**: github.com/example/docs/issues

---

**Last Updated**: November 19, 2025
**Next Review**: February 19, 2026
