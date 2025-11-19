# Conceptual Foundations: Understanding the Technology

Deep dives into the concepts used in the task manager app. Read this when you want to understand "why" not just "how."

## Table of Contents

1. [JavaScript Classes](#javascript-classes)
2. [Event Handling](#event-handling)
3. [DOM Manipulation](#dom-manipulation)
4. [localStorage and Persistence](#localstorage)
5. [Array Methods](#array-methods)
6. [Responsive Design](#responsive-design)
7. [Accessibility](#accessibility)

---

## JavaScript Classes

### What are Classes?

A class is a blueprint for creating objects with shared structure and behavior.

### Without Classes (Early JavaScript)

```javascript
// Creating a task object manually
const task1 = {
    id: 1,
    text: 'Buy milk',
    completed: false,
    toggle: function() {
        this.completed = !this.completed;
    }
};

const task2 = {
    id: 2,
    text: 'Call mom',
    completed: false,
    toggle: function() {
        this.completed = !this.completed;
    }
};
```

**Problems:**
- Duplicated code
- Tedious to create many tasks
- Hard to maintain consistency

### With Classes (Modern JavaScript)

```javascript
class Task {
    constructor(text, id = Date.now()) {
        this.id = id;
        this.text = text;
        this.completed = false;
    }

    toggle() {
        this.completed = !this.completed;
    }
}

// Now creating tasks is easy
const task1 = new Task('Buy milk');
const task2 = new Task('Call mom');
```

**Benefits:**
- Code reuse
- Consistency
- Easy to maintain

### How `new` Works

When you write `new Task('Buy milk')`:

1. JavaScript creates a new empty object
2. Runs the `constructor` function with that object
3. `this` inside constructor refers to the new object
4. Returns the new object

```javascript
class Task {
    constructor(text) {
        this.text = text;      // Sets property on new object
        this.completed = false;
    }
}

const myTask = new Task('Buy milk');
// myTask is now: { text: 'Buy milk', completed: false }
```

### Methods vs Properties

```javascript
class Task {
    // Properties - data about the task
    constructor(text) {
        this.text = text;
        this.completed = false;
    }

    // Methods - things the task can do
    toggle() {
        this.completed = !this.completed;
    }

    getStatus() {
        return this.completed ? 'Done' : 'Todo';
    }
}
```

**Difference:**
- Properties: what the task *is*
- Methods: what the task *does*

---

## Event Handling

### What are Events?

Events are things that happen in the browser:
- User clicks a button
- User presses a key
- Page finishes loading
- Mouse moves

### Event Flow

When you click a button:

```javascript
const button = document.getElementById('myButton');

button.addEventListener('click', () => {
    console.log('Button was clicked!');
});
```

**What happens:**
1. User clicks the button
2. Browser creates an "click" event
3. Event is sent to the button element
4. Your function runs
5. You can respond to the click

### Common Events

| Event | Triggers | Example |
|-------|----------|---------|
| `click` | User clicks element | Button, link |
| `change` | Value changes (inputs, checkboxes) | Checkbox toggle |
| `keypress` | Key pressed | Form submission |
| `focus` | Element focused (tab to it) | Input selected |
| `blur` | Element loses focus | Click elsewhere |
| `submit` | Form submitted | Enter or submit button |
| `load` | Page finishes loading | Initial page load |

### Event Listener Syntax

```javascript
element.addEventListener('eventName', function);

// Example:
button.addEventListener('click', () => {
    console.log('Clicked!');
});
```

**What this does:**
- Registers a listener on the element
- When event happens, function runs
- Function can respond to the event

### The Event Object

Many event handlers receive an event object with info:

```javascript
input.addEventListener('keypress', (event) => {
    console.log('Key pressed:', event.key);
    if (event.key === 'Enter') {
        // Handle Enter key specially
    }
});
```

**event object properties:**
- `event.key` - Which key was pressed
- `event.target` - What element triggered event
- `event.preventDefault()` - Stop default behavior

### Event Delegation

You can listen to events on parent and check which child triggered:

```javascript
taskList.addEventListener('click', (event) => {
    if (event.target.classList.contains('btn-delete')) {
        const taskId = event.target.dataset.taskId;
        deleteTask(taskId);
    }
});
```

**Why useful:**
- One listener instead of many
- Works for dynamically added elements
- More efficient

---

## DOM Manipulation

### What is the DOM?

The DOM (Document Object Model) is a representation of the HTML as a tree of objects.

```html
<div class="container">
    <h1>Task Manager</h1>
    <input type="text">
    <button>Add</button>
</div>
```

Becomes a tree:
```
div.container
  ├─ h1 (text: "Task Manager")
  ├─ input
  └─ button (text: "Add")
```

### Selecting Elements

```javascript
// By ID (most specific)
const element = document.getElementById('myId');

// By class (less specific)
const elements = document.getElementsByClassName('myClass');

// Modern way (CSS selectors)
const element = document.querySelector('.myClass');      // First match
const elements = document.querySelectorAll('.myClass');  // All matches
```

**querySelector vs getElementById:**
- `querySelector` is more flexible (uses CSS selectors)
- `getElementById` is slightly faster
- Use `querySelector` for modern code

### Creating Elements

```javascript
// Create a new element
const li = document.createElement('li');

// Set properties
li.textContent = 'Buy milk';
li.className = 'task-item';

// Add to the page
taskList.appendChild(li);
```

**Alternative way:**
```javascript
// Using innerHTML (less safe, but simpler for small amounts)
taskList.innerHTML += '<li>Buy milk</li>';
```

**Why be careful with innerHTML:**
- Can execute JavaScript if content is untrusted
- Slower than createElement
- Harder to attach event listeners

### Modifying Elements

```javascript
const element = document.getElementById('myElement');

// Change text
element.textContent = 'New text';

// Change HTML (contains tags)
element.innerHTML = '<strong>Bold text</strong>';

// Change attributes
element.setAttribute('data-id', '123');
element.id = 'newId';

// Change classes
element.classList.add('active');
element.classList.remove('hidden');
element.classList.toggle('expanded');

// Change styles
element.style.color = 'red';
element.style.display = 'none';
```

### Removing Elements

```javascript
const element = document.getElementById('myElement');

// Remove from page
element.remove();

// Or from parent
parent.removeChild(element);
```

### Understanding `this`

In many situations, `this` refers to the element the listener is on:

```javascript
// In an element method
element.addEventListener('click', function() {
    console.log(this);  // The element that was clicked
    this.style.color = 'red';  // Make that element red
});

// But NOT with arrow functions!
element.addEventListener('click', () => {
    console.log(this);  // NOT the element! The window object
});
```

**Arrow functions don't have their own `this`.**

---

## localStorage and Persistence

### The Problem: Data Loss

Without storage, closing the browser loses all data:

```javascript
let tasks = [];  // In memory

function addTask(text) {
    tasks.push(text);  // Stored in RAM
}

addTask('Buy milk');
// Close browser... tasks are lost!
```

### The Solution: localStorage

Browser storage that persists after closing:

```javascript
// Save data
localStorage.setItem('myKey', 'myValue');

// Get data
const value = localStorage.getItem('myKey');
// Returns: 'myValue'

// Remove data
localStorage.removeItem('myKey');

// Clear all
localStorage.clear();
```

### localStorage Limitations

- **Same-origin only:** Cannot access from different domain
- **String storage:** Only stores text/JSON
- **~5-10 MB limit:** Varies by browser
- **No expiration:** Stays until manually cleared
- **Not secure:** Visible to JavaScript on the page

### Storing Objects

localStorage only stores strings, so convert objects to JSON:

```javascript
const task = { text: 'Buy milk', completed: false };

// Convert to JSON string
localStorage.setItem('task', JSON.stringify(task));

// Get and convert back
const stored = localStorage.getItem('task');
const task = JSON.parse(stored);
```

### Real Example from TaskManager

```javascript
// Save tasks
saveTasks() {
    const json = JSON.stringify(this.tasks);
    localStorage.setItem(this.storageKey, json);
}

// Load tasks
loadTasks() {
    const json = localStorage.getItem(this.storageKey);
    if (json) {
        this.tasks = JSON.parse(json);
    }
}
```

### When to Use localStorage

**Good for:**
- User preferences (theme, language)
- Form draft auto-save
- Simple task lists
- Shopping carts
- Offline support

**Bad for:**
- Large amounts of data (5MB limit)
- Sensitive data (not encrypted)
- Complex relationships (database better)
- High-frequency updates (database better)

---

## Array Methods

### Map - Transform Each Element

```javascript
const numbers = [1, 2, 3];

// Double each number
const doubled = numbers.map(n => n * 2);
// Result: [2, 4, 6]
```

**In our app:**
```javascript
// Convert plain objects to Task objects
const tasks = data.map(item => new Task(item.text, item.id));
```

### Filter - Keep Matching Elements

```javascript
const numbers = [1, 2, 3, 4, 5];

// Keep only even numbers
const evens = numbers.filter(n => n % 2 === 0);
// Result: [2, 4]
```

**In our app:**
```javascript
// Get only completed tasks
const completedTasks = tasks.filter(t => t.completed);

// Remove a specific task
tasks = tasks.filter(t => t.id !== taskToDelete.id);
```

### Find - Get First Match

```javascript
const users = [
    { name: 'Alice', age: 30 },
    { name: 'Bob', age: 25 }
];

// Find the first user named Alice
const alice = users.find(u => u.name === 'Alice');
```

**In our app:**
```javascript
// Find a specific task by ID
const task = this.tasks.find(t => t.id === taskId);
```

### Reduce - Combine into One Value

```javascript
const numbers = [1, 2, 3, 4, 5];

// Sum all numbers
const sum = numbers.reduce((total, n) => total + n, 0);
// Result: 15

// How it works:
// Iteration 1: total=0, n=1 → 0 + 1 = 1
// Iteration 2: total=1, n=2 → 1 + 2 = 3
// Iteration 3: total=3, n=3 → 3 + 3 = 6
// Iteration 4: total=6, n=4 → 6 + 4 = 10
// Iteration 5: total=10, n=5 → 10 + 5 = 15
```

### Chaining Methods

```javascript
const tasks = [
    { text: 'Buy milk', completed: true },
    { text: 'Call mom', completed: false },
    { text: 'Finish project', completed: true }
];

// Get text of completed tasks
const completedText = tasks
    .filter(t => t.completed)
    .map(t => t.text);
// Result: ['Buy milk', 'Finish project']
```

**How it works:**
1. `filter` keeps only completed tasks
2. `map` extracts just the text

---

## Responsive Design

### Mobile-First Approach

Design for mobile first, then add features for larger screens:

```css
/* Mobile (smallest screens) */
body {
    font-size: 14px;
    padding: 1rem;
}

input {
    width: 100%;
}

/* Tablet and larger */
@media (min-width: 768px) {
    body {
        font-size: 16px;
    }

    input {
        width: 50%;
    }
}
```

**Why:**
- Mobile is the majority of users
- Adding for large screens is easier than removing
- Performance is better on slow mobile connections

### Flexible Layout: Flexbox

```css
/* Make items line up horizontally with space between */
.container {
    display: flex;
    gap: 1rem;
    justify-content: space-between;
}

/* Make items wrap on small screens */
@media (max-width: 600px) {
    .container {
        flex-direction: column;
    }
}
```

**Flexbox concepts:**
- `flex-direction`: Row or column layout
- `gap`: Space between items
- `justify-content`: Horizontal alignment
- `align-items`: Vertical alignment

### Media Queries

Test screen size and apply styles:

```css
/* Default: desktop */
.container {
    width: 100%;
}

/* Tablet */
@media (max-width: 768px) {
    .container {
        padding: 1rem;
    }
}

/* Mobile */
@media (max-width: 480px) {
    .container {
        padding: 0.5rem;
    }
}
```

**Common breakpoints:**
- Mobile: 320-480px
- Tablet: 481-768px
- Desktop: 769px+

---

## Accessibility

### Why Accessibility Matters

"Accessibility" means your app works for everyone:
- Blind users (screen readers)
- Deaf users (captions, visual alerts)
- Motor impairments (keyboard only)
- Cognitive disabilities (clear language)

### ARIA Labels

Help screen readers understand your interface:

```html
<!-- Bad: What is this button for? -->
<button>Save</button>

<!-- Good: Clear purpose -->
<button aria-label="Save task">Save</button>

<!-- For input: -->
<input aria-label="Enter task text">

<!-- For lists: -->
<ul aria-label="List of tasks"></ul>
```

### Keyboard Navigation

Users should navigate using Tab and Enter:

```html
<!-- Make sure form works without a mouse -->
<input type="text">
<button>Submit</button>  <!-- Can tab to and press Enter -->

<!-- Links and buttons are naturally keyboard accessible -->
<!-- Custom elements (divs styled as buttons) are not! -->
```

### Color and Contrast

Don't rely only on color:

```css
/* Good: Uses color AND style */
.success {
    color: green;
    font-weight: bold;  /* Also visible if colorblind */
}

/* Bad: Only color */
.success {
    color: green;  /* Invisible to colorblind users */
}
```

**Contrast ratio:**
- 4.5:1 minimum for text
- 3:1 for large text
- Tools: WebAIM Contrast Checker

### Semantic HTML

Use correct HTML elements:

```html
<!-- Good: Semantic -->
<button>Click me</button>
<input type="checkbox">
<ul><li>Item</li></ul>

<!-- Bad: Non-semantic (works but confusing) -->
<div onclick="...">Click me</div>
<div class="checkbox"></div>
<div class="list"><div>Item</div></div>
```

**Why:**
- Screen readers understand semantic elements
- Keyboard navigation works automatically
- More accessible to all users

---

## Key Takeaways

1. **Classes** organize code and reduce repetition
2. **Events** let you respond to user interactions
3. **DOM** manipulation changes what users see
4. **localStorage** persists data between sessions
5. **Array methods** transform and filter data
6. **Responsive design** works on all screen sizes
7. **Accessibility** makes apps usable by everyone

These concepts apply to all web development, no matter the framework or technology.

---

## Learning More

- MDN Web Docs: https://developer.mozilla.org
- Web.dev: https://web.dev
- WCAG Accessibility Guidelines: https://www.w3.org/WAI/WCAG21/quickref/
- CSS Tricks: https://css-tricks.com

