# Education Technology UI/UX Guidelines

## Purpose

This guide establishes UI/UX design standards for educational technology applications, ensuring learner-centered, accessible, and pedagogically sound interfaces.

## Core Principles

### 1. Learner-Centered Design

**Principle**: The learner's cognitive load, attention, and goals take priority over aesthetic preferences or technical complexity.

**Application**:
- Minimize distractions (no unnecessary animations, ads, or visual noise)
- Progressive disclosure: reveal complexity gradually
- Clear visual hierarchy: most important content prominent
- Support multiple learning modalities (visual, auditory, kinesthetic)

### 2. Accessibility First

**WCAG 2.2 AAA Compliance**:
- Color contrast ratio ≥ 7:1 for normal text, ≥ 4.5:1 for large text
- All functionality keyboard accessible
- ARIA landmarks and semantic HTML
- Screen reader tested and optimized
- No time limits without user control
- No flashing content >3Hz

**Inclusive Design**:
- Support for dyslexia (OpenDyslexic font option, increased spacing)
- Cognitive accessibility (clear language, simplified UI modes)
- Motor accessibility (large tap targets ≥44x44px, switch access)
- Vision accessibility (zoom up to 200%, high contrast modes)

### 3. Mobile-First & Responsive

**Design Breakpoints**:
- Mobile: 320px - 767px (phone portrait/landscape)
- Tablet: 768px - 1023px
- Desktop: 1024px - 1919px
- Large Desktop: 1920px+

**Touch Optimization**:
- Minimum touch target: 44x44px (iOS) / 48x48dp (Android)
- Thumb-friendly zones (bottom 1/3 of screen for primary actions)
- Swipe gestures for common actions (next/previous, complete/delete)
- Avoid hover-dependent interactions

### 4. Performance Budget

**Load Time Targets**:
- Time to First Byte (TTFB): <200ms
- First Contentful Paint (FCP): <1.5s
- Largest Contentful Paint (LCP): <2.5s
- Time to Interactive (TTI): <3.5s
- Cumulative Layout Shift (CLS): <0.1

**Asset Optimization**:
- Images: WebP/AVIF, responsive images, lazy loading
- Videos: Adaptive bitrate (HLS/DASH), thumbnail previews
- Fonts: Variable fonts, font-display: swap, subset fonts
- JavaScript: Code splitting, tree shaking, <200KB initial bundle

## Design Patterns

### Navigation

**Primary Navigation** (course structure):
```
[Home] > [Course: CS 101] > [Module 3: Algorithms] > [Lesson 3.2: Sorting]
```
- Breadcrumb trail always visible
- Persistent sidebar/navigation (collapsed on mobile)
- "Skip to main content" link for keyboard users
- Clear indication of current location

**Course Navigation Controls**:
- Previous/Next buttons always visible
- Progress indicator (e.g., "Lesson 5 of 12", 42% complete)
- Table of contents with completion checkmarks
- Keyboard shortcuts: ← Previous, → Next, Esc to course home

### Content Layout

**Optimal Reading Width**:
- 45-75 characters per line for body text
- Max-width: 800px for text-heavy content
- Generous line-height: 1.5-1.7 for paragraphs
- Font size: 16px minimum, 18-20px ideal for body text

**Whitespace**:
- Use whitespace to separate conceptual chunks
- Padding: at least 16px around interactive elements
- Margin: 24-32px between sections
- Avoid cramped layouts (cognitive overload)

### Interactive Elements

**Buttons**:
```css
/* Primary Action (e.g., Submit Assignment) */
.btn-primary {
  background: #0066cc; /* High contrast */
  color: #ffffff;
  padding: 12px 24px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 8px;
  min-height: 44px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.btn-primary:hover {
  background: #0052a3;
  box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

.btn-primary:focus {
  outline: 3px solid #ffd700; /* Highly visible focus indicator */
  outline-offset: 2px;
}

/* Secondary Action (e.g., Save Draft) */
.btn-secondary {
  background: #ffffff;
  color: #0066cc;
  border: 2px solid #0066cc;
  /* ... same sizing as primary */
}
```

**Form Inputs**:
- Labels always visible (no placeholder-only labels)
- Inline validation with helpful error messages
- Error states: red border + icon + descriptive text
- Success states: green checkmark + confirmation message
- Required fields clearly marked with asterisk and legend
- Field descriptions below label, before input

**Links**:
- Underlined by default (don't rely on color alone)
- 4.5:1 contrast ratio minimum
- Descriptive link text (not "click here" or "read more")
- External links indicated with icon

### Feedback & Notifications

**Toast Notifications**:
- Position: Top-right or top-center
- Auto-dismiss after 5-7 seconds (success, info)
- Require dismissal for warnings/errors
- Accessible: ARIA live region, keyboard dismissible

**Progress Indicators**:
- Determinate progress bars for known durations
- Spinner + estimated time for unknown durations
- Skeleton screens for content loading
- Optimistic UI updates for fast perceived performance

**Validation Feedback**:
- Inline validation on blur (not on every keystroke)
- Summary of errors at top of form on submit
- Scroll to first error + focus on error field
- Positive feedback for correct inputs (green checkmark)

### Assessment & Testing UI

**Question Display**:
- One question per screen for focus (or paginated groups)
- Question number + total (e.g., "Question 7 of 20")
- Clear indication of answered vs. unanswered
- Ability to flag questions for review
- Timer (if applicable) with warning at 5 minutes remaining

**Answer Input**:
- Multiple choice: Large radio buttons, full-width clickable labels
- Checkboxes: Clear "select all that apply" instruction
- Text input: Auto-save every 30 seconds, visual save indicator
- File upload: Drag-and-drop + browse, preview uploaded files
- Equation editor: MathJax or similar, with preview

**Navigation**:
- Question palette (overview of all questions with status)
- Next/Previous with visual disable state if not allowed
- Review page before final submission
- Confirmation dialog for submit ("You have 3 unanswered questions. Submit anyway?")

### Video & Multimedia

**Video Player**:
- Accessible controls (keyboard, screen reader announcements)
- Captions/subtitles toggle (CC button)
- Playback speed control (0.5x, 0.75x, 1x, 1.25x, 1.5x, 2x)
- Transcript below or beside video
- Keyboard shortcuts: Space (play/pause), ← (rewind 5s), → (forward 5s), F (fullscreen)
- Progress bar with thumbnail preview on hover
- Interactive elements: quizzes embedded at specific timestamps

**Audio Player**:
- Same keyboard accessibility as video
- Waveform visualization
- Transcript with synchronized highlighting
- Downloadable audio file

### Discussion & Collaboration

**Discussion Thread**:
- Threaded replies (max 3 levels deep)
- Upvote/downvote or like functionality
- Instructor/TA badges for official responses
- "Mark as resolved" for Q&A forums
- Rich text editor with formatting options
- @mentions with autocomplete
- Notification preferences (email, in-app, push)

**Real-Time Collaboration**:
- Presence indicators (who's online, typing indicators)
- Collaborative cursor (show other users' cursors in shared docs)
- Change attribution (color-coded by user)
- Conflict resolution UI for simultaneous edits
- Activity feed ("Jane added a comment", "John completed Task 3")

### Gamification UI

**Progress & Achievements**:
- Progress bars with percentage + visual fill
- Badge showcase (earned badges prominent, locked badges grayed)
- Leaderboards with privacy controls (opt-in, display name only)
- XP/points counter with level-up animations
- Skill trees with prerequisite connections visualized

**Motivational Elements**:
- Streak counter ("5-day streak!" with fire icon)
- Daily goals/challenges with completion checkboxes
- Unlockable content (visual lock icon → unlock animation)
- Celebratory micro-animations (confetti on achievement)
- Personalized encouragement ("You're 80% there!")

**Caution**:
- Provide "focus mode" to hide gamification elements
- Don't make leaderboards default (causes anxiety for some)
- Allow opting out of public-facing game elements

## Accessibility Checklist

### Keyboard Navigation
- [ ] All interactive elements focusable
- [ ] Logical tab order (follows visual layout)
- [ ] No keyboard traps
- [ ] Visible focus indicators (3px outline, high contrast)
- [ ] Keyboard shortcuts documented and customizable

### Screen Reader Support
- [ ] Semantic HTML (headings, landmarks, lists)
- [ ] ARIA labels for icon buttons
- [ ] ARIA live regions for dynamic content
- [ ] Skip links to main content, navigation
- [ ] Image alt text (descriptive, concise)
- [ ] Form labels programmatically associated

### Visual Accessibility
- [ ] Color contrast meets WCAG AAA (7:1)
- [ ] Information not conveyed by color alone
- [ ] Text resizable to 200% without loss of functionality
- [ ] No horizontal scrolling at 320px width
- [ ] High contrast mode available

### Cognitive Accessibility
- [ ] Clear, simple language (readability: Grade 8-10 level)
- [ ] Consistent navigation and layout
- [ ] Error messages are specific and helpful
- [ ] Instructions provided before actions
- [ ] Ability to extend time limits or remove them

### Motor Accessibility
- [ ] Touch targets ≥44x44px
- [ ] No hover-only content (provide alternative)
- [ ] Clickable areas generous (not just text)
- [ ] No precise timing required
- [ ] Switch access support (single-switch scanning)

## Responsive Design Patterns

### Mobile-Specific Considerations

**Navigation**:
- Hamburger menu with clear label ("Menu")
- Bottom navigation bar for primary actions
- Sticky header with minimal height (conserve vertical space)
- Pull-to-refresh for content updates

**Content**:
- Single-column layout on mobile
- Collapsible sections (accordions) to reduce scrolling
- Lazy loading for images and videos
- Truncated text with "Read more" expansion

**Input**:
- Native mobile keyboards (email, tel, number)
- Date/time pickers using native widgets
- File upload optimized for mobile (camera access)
- Voice input for text fields

**Offline**:
- Clear indication of offline status
- Cache critical content for offline access
- Queue actions for sync when online (with visual indicator)

### Tablet Considerations

**Layout**:
- Two-column layouts where appropriate
- Sidebars visible on landscape orientation
- Optimized for both portrait and landscape
- Split-view support (iPad multitasking)

**Input**:
- Support for Apple Pencil / stylus input (drawing, handwriting)
- Keyboard shortcuts (Bluetooth keyboard users)
- Drag-and-drop interactions

## Performance Guidelines

### Image Optimization
```html
<!-- Responsive images with art direction -->
<picture>
  <source
    media="(min-width: 1024px)"
    srcset="lecture-diagram-large.webp"
    type="image/webp">
  <source
    media="(min-width: 768px)"
    srcset="lecture-diagram-medium.webp"
    type="image/webp">
  <img
    src="lecture-diagram-small.jpg"
    alt="Diagram showing the four stages of cellular respiration"
    loading="lazy"
    width="800"
    height="600">
</picture>
```

### Video Optimization
- Use adaptive bitrate streaming (HLS, DASH)
- Provide multiple quality options (360p, 720p, 1080p)
- Thumbnail preview (poster image)
- Lazy load videos (don't autoplay)
- Consider bandwidth: default to lower quality on mobile

### Code Splitting
```javascript
// Route-based code splitting (React example)
const CourseHomepage = lazy(() => import('./CourseHomepage'));
const Assignment = lazy(() => import('./Assignment'));
const Gradebook = lazy(() => import('./Gradebook'));

<Suspense fallback={<LoadingSpinner />}>
  <Route path="/courses/:id" component={CourseHomepage} />
  <Route path="/assignments/:id" component={Assignment} />
  <Route path="/gradebook" component={Gradebook} />
</Suspense>
```

## Dark Mode Support

**Color Palette**:
```css
:root {
  /* Light mode (default) */
  --background: #ffffff;
  --surface: #f5f5f5;
  --text-primary: #1a1a1a;
  --text-secondary: #666666;
  --primary: #0066cc;
  --error: #d32f2f;
  --success: #388e3c;
}

@media (prefers-color-scheme: dark) {
  :root {
    --background: #121212;
    --surface: #1e1e1e;
    --text-primary: #e0e0e0;
    --text-secondary: #a0a0a0;
    --primary: #3399ff; /* Lighter for contrast */
    --error: #ff5252;
    --success: #66bb6a;
  }
}
```

**User Override**:
- Provide toggle for manual dark mode selection
- Remember user preference (localStorage)
- Smooth transition between modes (CSS transition)

## Typography

**Font Families**:
- **Body**: System font stack for performance
  ```css
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  ```
- **Headings**: Same as body (consistency) or humanist sans-serif
- **Code**: Monospace stack
  ```css
  font-family: "SF Mono", Monaco, "Cascadia Code", "Roboto Mono", Consolas, monospace;
  ```
- **Dyslexia-Friendly** (optional): OpenDyslexic, Lexend

**Type Scale**:
```css
--font-size-xs: 0.75rem;   /* 12px */
--font-size-sm: 0.875rem;  /* 14px */
--font-size-base: 1rem;    /* 16px - body text */
--font-size-lg: 1.125rem;  /* 18px */
--font-size-xl: 1.25rem;   /* 20px */
--font-size-2xl: 1.5rem;   /* 24px - h3 */
--font-size-3xl: 1.875rem; /* 30px - h2 */
--font-size-4xl: 2.25rem;  /* 36px - h1 */
```

**Line Height**:
- Headings: 1.2-1.3
- Body text: 1.5-1.7
- Dense UI (tables, lists): 1.4

## Animation & Transitions

**Principles**:
- Respect `prefers-reduced-motion` for accessibility
- Animations should be purposeful (provide feedback, guide attention)
- Keep durations short (<300ms for most transitions)
- Use CSS transitions/animations over JavaScript when possible

**Common Transitions**:
```css
/* Button hover */
.btn {
  transition: background-color 150ms ease-in-out,
              box-shadow 150ms ease-in-out;
}

/* Modal entrance */
.modal {
  animation: fadeIn 200ms ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-20px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Respect reduced motion preference */
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

## Micro-Interactions

**Assignment Submission**:
1. Button: "Submit Assignment"
2. On click: Button disabled, spinner appears, text changes to "Submitting..."
3. On success: Checkmark icon, text changes to "Submitted!", green background
4. After 2s: Redirect to confirmation page or next assignment

**Favoriting/Bookmarking**:
- Star icon outline → filled star on click
- Brief scale animation (0.8x → 1.2x → 1x)
- Optional haptic feedback on mobile

**Loading States**:
- Skeleton screens for content (gray boxes mimicking layout)
- Shimmer effect to indicate loading
- Spinners for indeterminate progress
- Progress bars for determinate progress

## Error States & Empty States

**Error States**:
- Friendly, non-technical language ("Oops! Something went wrong.")
- Specific action to take ("Please refresh the page or contact support.")
- Error code for support reference (in small text)
- Illustration or icon to soften the message

**Empty States**:
- Explain why it's empty ("You haven't submitted any assignments yet.")
- Guide user to take action ("Get started by clicking 'New Assignment'")
- Illustration to fill the space (not just text)
- Avoid generic "No data" messages

## Testing Checklist

### Browser Testing
- [ ] Chrome (latest, latest-1)
- [ ] Firefox (latest, latest-1)
- [ ] Safari (latest, latest-1)
- [ ] Edge (latest)
- [ ] Mobile Safari (iOS 15+)
- [ ] Chrome Mobile (Android 11+)

### Device Testing
- [ ] iPhone (various sizes: SE, 13, 13 Pro Max)
- [ ] iPad (portrait and landscape)
- [ ] Android phone (various sizes)
- [ ] Android tablet
- [ ] Desktop (various resolutions)

### Accessibility Testing
- [ ] Keyboard navigation (Tab, Enter, Esc, arrows)
- [ ] Screen reader (JAWS, NVDA, VoiceOver, TalkBack)
- [ ] Color contrast (automated and manual)
- [ ] Zoom to 200% (no horizontal scroll, no loss of function)
- [ ] Automated tools (axe DevTools, WAVE, Lighthouse)

### Performance Testing
- [ ] Lighthouse score ≥90 (Performance, Accessibility, Best Practices, SEO)
- [ ] WebPageTest (First Contentful Paint <1.5s)
- [ ] Test on 3G connection (mobile users)
- [ ] Bundle size analysis (webpack-bundle-analyzer)

## Resources

- **WCAG 2.2 Guidelines**: https://www.w3.org/WAI/WCAG22/quickref/
- **Material Design**: https://material.io/design (for component patterns)
- **Apple Human Interface Guidelines**: https://developer.apple.com/design/human-interface-guidelines/
- **Inclusive Components**: https://inclusive-components.design/
- **A11y Project**: https://www.a11yproject.com/

---

**Version**: 1.0
**Last Updated**: 2025-11-19
**Maintained by**: CLAUDE_SKILLS Education Technology Domain
