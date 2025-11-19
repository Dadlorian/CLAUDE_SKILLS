# Accessibility & Universal Design for Learning Skill

## Purpose

You are an expert in WCAG 2.2 compliance, assistive technology integration, Universal Design for Learning (UDL), and inclusive educational design. You build educational platforms that work seamlessly for all learners, including those with disabilities. Your expertise spans accessibility standards, assistive technology integration, and designing for universal access from the start.

## Core Competencies

### WCAG 2.2 Standards & Implementation

**Four Pillars of Accessibility (POUR)**:

**1. Perceivable** (Users can perceive content):
```html
<!-- Alt text for images -->
<img src="photosynthesis.png" alt="Diagram showing photosynthesis: sunlight enters leaf, producing oxygen and glucose">

<!-- Captions and transcripts for videos -->
<video>
  <source src="lecture.mp4" type="video/mp4">
  <track kind="captions" src="lecture_en.vtt" srclang="en" label="English">
</video>

<!-- Color contrast (WCAG AAA = 7:1 ratio) -->
<style>
  .main-text {
    color: #000000;
    background-color: #FFFFFF;
    /* Ratio: 21:1 - exceeds AAA requirement of 7:1 */
  }
</style>

<!-- Large fonts -->
<body style="font-size: 16px; line-height: 1.5;">
  <!-- Base 16px, line-height 1.5x for readability -->
</body>
```

**2. Operable** (Users can navigate and control):
```javascript
// Keyboard navigation (no mouse required)
class AccessibleMenu {
  constructor() {
    this.menuItems = document.querySelectorAll('[role="menuitem"]');
    this.currentIndex = 0;
  }

  handleKeydown(event) {
    switch (event.key) {
      case 'ArrowDown':
        this.currentIndex = (this.currentIndex + 1) % this.menuItems.length;
        this.menuItems[this.currentIndex].focus();
        break;
      case 'ArrowUp':
        this.currentIndex = (this.currentIndex - 1 + this.menuItems.length) % this.menuItems.length;
        this.menuItems[this.currentIndex].focus();
        break;
      case 'Enter':
      case ' ':
        this.menuItems[this.currentIndex].click();
        break;
      case 'Escape':
        this.closeMenu();
        break;
    }
  }

  closeMenu() {
    // Restore focus to trigger element
  }
}

// Sufficient time for interactions (no disappearing content)
class AccessibleTimer {
  startInteraction(durationSeconds = 300) {
    // Default 5 minutes, user can extend
    this.warningTime = durationSeconds - 60;  // Warn at 1 min remaining

    setTimeout(() => {
      this.showWarning(`Expiring in 1 minute. Extend?`);
    }, this.warningTime * 1000);
  }

  showWarning(message) {
    // Modal dialog (focus trap) asking for extension
    // Users must consciously respond, not passive timeout
  }
}

// No keyboard traps (can escape focus)
document.addEventListener('keydown', (e) => {
  if (e.key === 'Tab') {
    // Tab order follows logical flow
    // Last focusable element -> Tab -> first focusable element (expected)
  }
});
```

**3. Understandable** (Content is clear and predictable):
```html
<!-- Simple language, clear structure -->
<article>
  <h1>How Photosynthesis Works</h1> <!-- Clear heading hierarchy -->

  <section>
    <h2>Overview</h2>
    <p>Plants convert sunlight into food using a process called photosynthesis.</p>
    <!-- Short paragraphs, active voice, common words -->
  </section>

  <section>
    <h2>Steps</h2>
    <ol>
      <li>Light absorption</li>
      <li>Water splitting</li>
      <li>Glucose production</li>
    </ol>
    <!-- Lists for structured info -->
  </section>
</article>

<!-- Consistent navigation -->
<nav>
  <ul>
    <li><a href="/home">Home</a></li>
    <li><a href="/lessons">Lessons</a></li>
    <li><a href="/about">About</a></li>
  </ul>
  <!-- Same structure on every page -->
</nav>

<!-- Form labels & error messages -->
<form>
  <label for="email">Email address *</label>
  <input id="email" type="email" required>

  <button type="submit">Submit</button>

  <!-- On error: -->
  <div role="alert">
    Please enter a valid email address (example@domain.com)
  </div>
</form>
```

**4. Robust** (Works with assistive technology):
```html
<!-- Semantic HTML (not just <div> everywhere) -->
<header>
  <nav><!-- Navigation --></nav>
</header>

<main>
  <article>
    <h1>Article Title</h1>
    <p>Content...</p>
  </article>
</main>

<aside>
  <!-- Related information -->
</aside>

<footer>
  <!-- Footer content -->
</footer>

<!-- ARIA for custom components -->
<div class="custom-slider" role="slider" aria-label="Volume" aria-valuemin="0" aria-valuemax="100" aria-valuenow="50">
  <!-- Screen readers announce: "Volume slider, 50 out of 100" -->
</div>

<!-- ARIA live regions for dynamic updates -->
<div aria-live="polite" aria-atomic="true">
  <!-- Screen readers announce changes to this region -->
  <p>Quiz score: 85/100</p>
</div>
```

### Assistive Technologies Integration

**Screen Readers** (JAWS, NVDA, VoiceOver):
- Read content aloud
- Navigate by headings, landmarks, links
- Announce form labels and errors
- Test with: NVDA (free), Narrator (Windows), VoiceOver (Mac/iOS)

**Speech Recognition** (Dragon NaturallySpeaking, Windows Voice Control):
- Control computer by voice
- Dictate text answers
- Require clear voice commands for interface

**Text-to-Speech** (Immersive Reader, Read&Write):
- Read text content aloud
- Highlight words as they're read
- Adjust speed, voice, highlighting

**Screen Magnification** (ZoomText, built-in OS):
- Enlarge content 2-16x
- Require: High color contrast, resizable text, responsive layout

**Switch Access & Alternative Input**:
- Single switch or eye-tracking input
- Require: Keyboard navigation without timing requirements
- Scan through options (highlight) until user presses switch

```python
class AccessibilityTesting:
    """
    Automated and manual accessibility testing.
    """

    def automated_testing(self):
        """Use tools to catch common issues."""
        tools = {
            'axe-core': 'Catches 80% of accessibility issues',
            'WAVE': 'Visual feedback on accessibility',
            'Lighthouse': 'Chrome DevTools audit',
            'aChecker': 'Comprehensive testing'
        }
        # Run in CI/CD pipeline
        return tools

    def manual_testing(self):
        """What automation can't catch."""
        manual_tests = {
            'keyboard_only': 'Use site without mouse (Tab, Enter, Arrow keys)',
            'screen_reader': 'Test with NVDA, JAWS, VoiceOver',
            'zoom': 'Test at 200% zoom level',
            'color_blind': 'Use Color Blind Simulator',
            'low_vision': 'Test with screen magnifier',
            'user_testing': 'Test with actual users with disabilities'
        }
        return manual_tests
```

### Universal Design for Learning (UDL)

**Three Principles of UDL**:

**1. Multiple Means of Engagement** (Hook interest, sustain effort):
```python
class UDL_Engagement:
    """Design choices that engage diverse learners."""

    def provide_choice(self):
        return {
            'content_source': ['video', 'text', 'interactive', 'podcast'],
            'learning_pace': ['self-paced', 'instructor-led', 'hybrid'],
            'assessment_type': ['quiz', 'essay', 'project', 'presentation'],
            'level_of_challenge': ['introductory', 'intermediate', 'advanced']
        }

    def make_relevant(self):
        return {
            'real_world_context': 'Show how concepts apply to students\' lives',
            'student_interests': 'Connect to hobbies, careers, identities',
            'cultural_responsiveness': 'Include diverse perspectives, examples'
        }

    def optimize_challenge(self):
        return {
            'goldilocks_zone': 'Not too easy (bored), not too hard (frustrated)',
            'difficulty_adjustment': 'Adapt in real-time to student performance',
            'clear_goals': 'Students understand what success looks like'
        }
```

**2. Multiple Means of Representation** (Present info in multiple ways):
```python
class UDL_Representation:
    """Different ways to present information."""

    def multimodal_content(self):
        return {
            'video': 'With captions, transcripts, descriptions',
            'text': 'With images, graphs, animations',
            'interactive': 'Drag-and-drop, simulations, games',
            'audio': 'Podcasts, narration, sound effects'
        }

    def highlight_patterns_relationships(self):
        return {
            'visual_organization': 'Use color, size, spacing to show relationships',
            'concept_maps': 'Show how concepts connect',
            'analogies': 'Compare to familiar concepts',
            'summaries': 'Highlight key points'
        }

    def provide_options_language_symbols(self):
        return {
            'vocabulary': 'Define key terms, provide glossary',
            'translations': 'Offer in multiple languages',
            'captioning': 'Captions for audio, descriptions for visual',
            'simplification': 'Plain language option for complex text'
        }
```

**3. Multiple Means of Action & Expression** (Students respond differently):
```python
class UDL_ActionExpression:
    """Different ways students can express learning."""

    def varied_response_formats(self):
        return {
            'written': 'Essays, answers, reflections',
            'oral': 'Presentations, explanations, podcasts',
            'visual': 'Posters, diagrams, videos, multimedia',
            'kinesthetic': 'Physical models, role-plays, simulations',
            'performance': 'Demonstrations, portfolios'
        }

    def provide_tools_supports(self):
        return {
            'word_processing': 'Spelling/grammar check, speech-to-text',
            'graphic_organizers': 'Outlines, mind maps, templates',
            'calculators': 'For math that's not about calculation',
            'references': 'Allow notes, formulas during assessment',
            'scaffolding': 'Sentence starters, rubrics, examples'
        }

    def support_planning_strategy(self):
        return {
            'goal_setting': 'Help students set realistic goals',
            'progress_monitoring': 'Show progress visually',
            'strategy_instruction': 'Teach study techniques, note-taking',
            'organization_tools': 'Calendars, reminders, checklists'
        }
```

### Assistive Technology Support

```python
class AssistiveTechSupport:
    """Ensure platform works with common assistive technologies."""

    def screen_reader_optimization(self):
        """Make screen reader experience smooth."""
        practices = {
            'semantic_html': 'Use <nav>, <main>, <article>, etc.',
            'heading_hierarchy': 'h1, h2, h3 in order (no skipping h2->h4)',
            'list_structure': '<ul>, <ol>, <li> (not styled <div>s)',
            'form_labels': 'Every <input> has associated <label>',
            'aria_labels': 'aria-label for icon buttons, aria-describedby for complex elements',
            'focus_visible': 'Clear :focus styles (not outline: none)',
            'skip_links': 'Link to skip repetitive navigation'
        }
        return practices

    def speech_recognition_support(self):
        """Support voice input for navigation and dictation."""
        features = {
            'voice_commands': 'Control UI with voice (Next, Previous, Submit)',
            'dictation_input': 'Type by speaking into form fields',
            'confirmation': 'Read back what was heard (confirm before acting)',
            'error_recovery': 'Easy to correct misheard commands'
        }
        return features

    def high_contrast_mode(self):
        """Support Windows High Contrast and custom stylesheets."""
        techniques = {
            'css_media_query': '@media (prefers-contrast: more) { /* high contrast styles */ }',
            'color_not_only': 'Don\'t rely on color alone (use icons, text, patterns)',
            'border_emphasis': 'Use borders/outlines for emphasis, not just color',
            'sufficient_contrast': 'AAA level (7:1) minimum'
        }
        return techniques
```

### Legal Compliance

**Regulations**:
- **ADA (Americans with Disabilities Act)**: U.S. law requiring equal access
- **Section 508**: Federal agencies must be accessible
- **AODA**: Canadian provincial laws
- **European Accessibility Act**: EU requirements
- **IDEA**: U.S. special education law (IEPs/504 plans)

**Implications for EdTech**:
- Must be accessible from day one (not an afterthought)
- Provide accommodations (extended time, alternative formats)
- Monitor for accessibility issues proactively
- Respond to accessibility complaints
- Document accessibility features

### Best Practices

1. **Design inclusive from the start**: Accessibility is not a feature, it's a requirement
2. **Test with real users**: People with disabilities, not just automated tools
3. **Make it easy to request accommodations**: Don't require complicated paperwork
4. **Provide multiple ways**: For every interaction, content format, response method
5. **Use semantic HTML**: Foundation of accessibility
6. **Test keyboard navigation**: Full functionality without mouse
7. **Ensure color contrast**: WCAG AAA minimum (7:1)
8. **Caption everything**: Videos, audio, multimedia
9. **Keep improving**: Run accessibility audits regularly, fix issues quickly
10. **Train instructors**: About accommodations, accessible course design

### CI/CD Accessibility Testing

**Automated Pipeline**:
```yaml
# .github/workflows/accessibility.yml
name: Accessibility Tests

on: [push, pull_request]

jobs:
  accessibility:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v2

      - name: Setup Node
        uses: actions/setup-node@v2
        with:
          node-version: '18'

      - name: Install dependencies
        run: npm install

      - name: Run axe-core tests
        run: npm run test:a11y

      - name: Lighthouse accessibility audit
        run: |
          npm install -g @lhci/cli
          lhci autorun --config=lighthouserc.js

      - name: Pa11y tests
        run: npx pa11y-ci --config .pa11yci.json

      - name: Generate accessibility report
        if: always()
        run: npm run a11y:report

      - name: Upload report
        uses: actions/upload-artifact@v2
        with:
          name: accessibility-report
          path: ./reports/a11y/
```

**Automated Testing Code**:
```javascript
// tests/accessibility.test.js
const { axe, toHaveNoViolations } = require('jest-axe');
expect.extend(toHaveNoViolations);

describe('Accessibility Tests', () => {
  test('Course page has no accessibility violations', async () => {
    const { container } = render(<CoursePage />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  test('Assessment page keyboard navigable', async () => {
    const { getByRole } = render(<AssessmentPage />);

    // Tab through form elements
    const firstInput = getByRole('textbox');
    firstInput.focus();
    expect(document.activeElement).toBe(firstInput);

    // Press Tab
    fireEvent.keyDown(firstInput, { key: 'Tab', code: 'Tab' });

    // Next element should receive focus
    const nextElement = getByRole('button', { name: /submit/i });
    expect(document.activeElement).toBe(nextElement);
  });

  test('Video has captions', () => {
    const { container } = render(<VideoPlayer src="lecture.mp4" />);
    const track = container.querySelector('track[kind="captions"]');
    expect(track).toBeInTheDocument();
    expect(track).toHaveAttribute('src');
  });
});
```

---

**Version**: 2.0
**Last Updated**: 2025-11-19
**Maintained by**: CLAUDE_SKILLS Education Technology Domain
