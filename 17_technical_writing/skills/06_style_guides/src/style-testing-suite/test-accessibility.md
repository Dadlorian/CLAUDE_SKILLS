# Test: Screen Reader Optimization

## Purpose

Validate that documentation is properly formatted for accessibility and screen readers.

## Passing Examples

### Proper Heading Hierarchy

# Main Title

## Section One

### Subsection A

Paragraph content here.

### Subsection B

More paragraph content.

## Section Two

Continuing with valid heading hierarchy.

### Proper Image Alt Text

![Architecture diagram showing client layer, API server layer, and database layer](architecture.png)

![User interface screenshot with login form highlighted](login-screenshot.png)

### Descriptive Link Text

Visit the [installation guide](install.md) for setup instructions.

Read the [API reference documentation](api.md) for endpoint details.

See the [troubleshooting FAQ](faq.md) for common issues.

### Proper List Structure

1. First step in the process
2. Second step in the process
3. Final step in the process

- Feature one available
- Feature two available
- Feature three available

### Table with Headers

| Header One | Header Two | Header Three |
|-----------|-----------|-------------|
| Data A    | Data B    | Data C      |
| Data D    | Data E    | Data F      |

## Failing Examples

### Improper Heading Hierarchy

# Main Title

### Subsection (skipped h2)

This violates proper heading hierarchy.

## Back to h2

Should not skip heading levels.

### Missing Image Alt Text

![](screenshot.png)

An image without descriptive alt text.

![](diagram.png)

Another image missing description.

### Non-Descriptive Link Text

Click [here](guide.md) for more information.

See [this](reference.md) for details.

Read [link](docs.md) for documentation.

### Improper List Usage

- Item 1
* Item 2 (mixed markers)
+ Item 3 (mixed markers)

This list uses inconsistent bullet markers.

### All Caps Text

This paragraph contains ALL CAPS WORDS that are harder to read.

AVOID USING ALL CAPS for regular text content.

## Notes

Screen reader users rely on:
- Proper heading hierarchy for navigation
- Descriptive alt text for images
- Meaningful link text (not "click here")
- Consistent list formatting
- Clear document structure

## Related Rules

- TechWriter.Headings - Heading structure
- TechWriter.Readability - Readability metrics
- TechWriter.CodeFormatting - Code block formatting
