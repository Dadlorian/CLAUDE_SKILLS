# Complete Step-by-Step Tutorial: Build a Task Management App

Learn to build a complete, functional web application by following this tutorial. You'll build a task management app with HTML, CSS, and JavaScript.

## Overview

**What You'll Build:** A task management app where users can:
- Add new tasks
- Mark tasks as complete
- Delete tasks
- See task statistics
- Have tasks saved automatically

**Time Estimate:** 45-60 minutes

**Difficulty:** Beginner to Intermediate

**Prerequisites:**
- Text editor (VS Code, Sublime, etc.)
- Web browser (Chrome, Firefox, Safari, etc.)
- Basic familiarity with HTML and CSS
- Basic JavaScript knowledge helpful but not required

## Phase 1: Create the HTML Structure (10 minutes)

### Objective
Create the semantic HTML structure for the app with a form for input and a list for tasks.

### Step 1.1: Create the HTML File

Create a new file called `index.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Task Management App</title>
    <style>
        /* CSS will go here in Phase 2 */
    </style>
</head>
<body>
    <!-- Content goes here -->

    <script>
        // JavaScript will go here in Phase 3
    </script>
</body>
</html>
```

**Why each part matters:**
- `<!DOCTYPE html>` tells the browser this is HTML5
- `<meta charset="UTF-8">` specifies text encoding
- `<meta viewport>` makes the app work on mobile
- `<title>` shows in the browser tab
- `<style>` will contain CSS
- `<script>` will contain JavaScript

### Step 1.2: Add the Container and Header

Replace the `<!-- Content goes here -->` comment with:

```html
<div class="container">
    <div class="header">
        <h1>Task Manager</h1>
        <p>Stay organized and productive</p>
    </div>

    <div class="main">
        <!-- Main content will go here -->
    </div>
</div>
```

**Semantic meaning:**
- `.container` wraps the entire app
- `.header` is the top section with title
- `.main` will contain the form and task list

### Step 1.3: Add the Input Form

Inside the `.main` div, add the form:

```html
<div class="input-group">
    <input
        type="text"
        id="taskInput"
        placeholder="What needs to be done?"
        aria-label="Enter a new task"
    >
    <button id="addBtn" class="btn-add">
        Add Task
    </button>
</div>
```

**Key attributes:**
- `id="taskInput"` lets JavaScript find this input
- `placeholder` shows helpful text
- `aria-label` helps screen readers

### Step 1.4: Add the Task List

Below the form, add:

```html
<ul class="task-list" id="taskList" aria-label="List of tasks"></ul>

<div class="empty-state" id="emptyState" hidden>
    <p>No tasks yet. Add one to get started!</p>
</div>
```

**Explanation:**
- `<ul>` is an unordered list (will contain tasks)
- `id="taskList"` lets JavaScript add tasks here
- `hidden` attribute hides the empty state until needed

### Verification Checkpoint

Your HTML should now look like a basic structure. Open it in your browser - it won't do anything yet, but you should see the title "Task Manager."

**Expected:** A page with a title and form (unstyled)

---

## Phase 2: Add CSS Styling (10 minutes)

### Objective
Make the app look professional with modern CSS including responsive design.

### Step 2.1: Add CSS Variables and Base Styles

Replace `<!-- CSS will go here -->` with:

```css
:root {
    --primary-color: #4f46e5;
    --danger-color: #ef4444;
    --gray-100: #f3f4f6;
    --gray-200: #e5e7eb;
    --gray-900: #111827;
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    padding: 2rem 1rem;
}
```

**Why CSS variables?**
Colors are stored in variables, so changing `--primary-color` updates all places it's used.

### Step 2.2: Style the Container and Header

```css
.container {
    max-width: 600px;
    margin: 0 auto;
    background: white;
    border-radius: 0.5rem;
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
}

.header {
    background: linear-gradient(135deg, var(--primary-color) 0%, #4338ca 100%);
    color: white;
    padding: 2rem;
    text-align: center;
}

.header h1 {
    font-size: 2rem;
    margin-bottom: 0.5rem;
}
```

**Result:** The header now has a nice gradient background.

### Step 2.3: Style the Form

```css
.main {
    padding: 2rem;
}

.input-group {
    display: flex;
    gap: 0.75rem;
    margin-bottom: 2rem;
}

.input-group input {
    flex: 1;
    padding: 0.75rem 1rem;
    border: 2px solid var(--gray-200);
    border-radius: 0.5rem;
    font-size: 1rem;
}

.input-group input:focus {
    outline: none;
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
}

.btn-add {
    padding: 0.75rem 1.5rem;
    background-color: var(--primary-color);
    color: white;
    border: none;
    border-radius: 0.5rem;
    cursor: pointer;
    font-weight: 600;
}

.btn-add:hover {
    background-color: #4338ca;
    transform: translateY(-2px);
}
```

**Interactive feedback:**
- `:focus` shows a blue ring when input is selected
- `:hover` makes button darker and lifts slightly

### Step 2.4: Style the Task List

```css
.task-list {
    list-style: none;
    margin-bottom: 2rem;
}

.task-list li {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem;
    border-bottom: 1px solid var(--gray-200);
}

.task-list input[type="checkbox"] {
    width: 20px;
    height: 20px;
    cursor: pointer;
    accent-color: var(--primary-color);
}

.task-text {
    flex: 1;
}

.task-list li input[type="checkbox"]:checked ~ .task-text {
    color: var(--gray-200);
    text-decoration: line-through;
}

.btn-delete {
    background-color: var(--danger-color);
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 0.5rem;
    cursor: pointer;
}

.btn-delete:hover {
    background-color: #dc2626;
}
```

**Highlights:**
- Flexbox makes items line up nicely
- `:checked ~ .task-text` styles text after completed checkbox

### Step 2.5: Add Responsive Design

Add this at the end of your CSS:

```css
@media (max-width: 600px) {
    .header h1 {
        font-size: 1.5rem;
    }

    .input-group {
        flex-direction: column;
    }

    .input-group input,
    .btn-add {
        width: 100%;
    }
}
```

**Mobile Optimization:**
- On small screens, input and button stack vertically
- Header text shrinks for readability

### Verification Checkpoint

Refresh your browser. The app should now look good with:
- Colored header
- Styled input form
- Professional appearance

**Expected:** Nice-looking form, but still not functional

---

## Phase 3: Add JavaScript Logic (15 minutes)

### Objective
Make the app functional with JavaScript. Users can add, complete, and delete tasks.

### Step 3.1: Create the Task Class

Replace `<!-- JavaScript will go here -->` with:

```javascript
// Task Class - represents a single task
class Task {
    constructor(text, id = Date.now()) {
        this.id = id;           // Unique identifier
        this.text = text;       // Task text
        this.completed = false; // Is it done?
    }

    toggle() {
        this.completed = !this.completed;
    }
}
```

**What this does:**
- When you create `new Task("Buy milk")`, it creates an object
- Each task has an id, text, and completion status
- `toggle()` flips the completed status

### Step 3.2: Create the TaskManager Class

Add this after the Task class:

```javascript
// TaskManager Class - manages all tasks
class TaskManager {
    constructor(storageKey = 'tasks') {
        this.tasks = [];        // Array of all tasks
        this.storageKey = storageKey; // Where to save
        this.loadTasks();       // Load from browser storage
    }

    // Add a new task
    addTask(taskText) {
        const task = new Task(taskText);
        this.tasks.push(task);
        this.saveTasks();
        return task;
    }

    // Remove a task by ID
    removeTask(taskId) {
        this.tasks = this.tasks.filter(task => task.id !== taskId);
        this.saveTasks();
    }

    // Toggle task completion
    toggleTask(taskId) {
        const task = this.tasks.find(t => t.id === taskId);
        if (task) {
            task.toggle();
            this.saveTasks();
        }
    }

    // Save to browser storage
    saveTasks() {
        localStorage.setItem(this.storageKey, JSON.stringify(this.tasks));
    }

    // Load from browser storage
    loadTasks() {
        const json = localStorage.getItem(this.storageKey);
        if (json) {
            const data = JSON.parse(json);
            this.tasks = data.map(item => new Task(item.text, item.id));
            data.forEach((item, index) => {
                this.tasks[index].completed = item.completed;
            });
        }
    }
}
```

**Key method:**
- `saveTasks()` and `loadTasks()` use localStorage (browser's built-in database)
- Tasks persist even after closing the browser

### Step 3.3: Initialize and Get DOM Elements

Add after the classes:

```javascript
// Initialize
let taskManager = new TaskManager();

// Get DOM elements
const taskInput = document.getElementById('taskInput');
const addBtn = document.getElementById('addBtn');
const taskList = document.getElementById('taskList');
const emptyState = document.getElementById('emptyState');
```

**Explanation:**
- `document.getElementById()` finds elements by their id
- Store references so we can use them later

### Step 3.4: Create the Render Function

```javascript
// Render the task list
function renderTasks() {
    taskList.innerHTML = '';  // Clear the list

    // Show empty state if no tasks
    if (taskManager.tasks.length === 0) {
        emptyState.hidden = false;
        return;
    }

    emptyState.hidden = true;

    // Create an element for each task
    taskManager.tasks.forEach(task => {
        const li = document.createElement('li');

        // Checkbox
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.checked = task.completed;
        checkbox.addEventListener('change', () => {
            taskManager.toggleTask(task.id);
            renderTasks();
        });

        // Task text
        const span = document.createElement('span');
        span.className = 'task-text';
        span.textContent = task.text;

        // Delete button
        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'btn-delete';
        deleteBtn.textContent = 'Delete';
        deleteBtn.addEventListener('click', () => {
            taskManager.removeTask(task.id);
            renderTasks();
        });

        // Assemble
        li.appendChild(checkbox);
        li.appendChild(span);
        li.appendChild(deleteBtn);
        taskList.appendChild(li);
    });
}
```

**How it works:**
1. Clear the current list
2. For each task, create a list item with checkbox, text, and delete button
3. Add event listeners for checkbox and delete button

### Step 3.5: Create the Add Task Function

```javascript
// Handle adding a task
function handleAddTask() {
    const text = taskInput.value.trim();

    // Don't add empty tasks
    if (!text) {
        taskInput.focus();
        return;
    }

    // Add and re-render
    taskManager.addTask(text);
    taskInput.value = '';
    taskInput.focus();
    renderTasks();
}
```

**Trim removes whitespace:**
- Prevents tasks like "   " from being added

### Step 3.6: Add Event Listeners

```javascript
// Click the button
addBtn.addEventListener('click', handleAddTask);

// Or press Enter in the input
taskInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        handleAddTask();
    }
});

// Initial render
renderTasks();
```

### Verification Checkpoint

Now the app should work! Try:
1. Type "Buy milk"
2. Click "Add Task"
3. Your task appears in the list
4. Click the checkbox to mark it done (text strikes through)
5. Click Delete to remove it
6. Close the browser and reopen - tasks are still there!

**Expected:** Fully functional task manager

---

## Phase 4: Add Statistics Display (5 minutes)

### Objective
Show how many tasks total, completed, and remaining.

### Step 4.1: Add HTML

Add this to your `.main` section, after the input-group:

```html
<div class="stats">
    <div class="stat">
        <div class="stat-value" id="totalCount">0</div>
        <div class="stat-label">Total</div>
    </div>
    <div class="stat">
        <div class="stat-value" id="completedCount">0</div>
        <div class="stat-label">Completed</div>
    </div>
    <div class="stat">
        <div class="stat-value" id="remainingCount">0</div>
        <div class="stat-label">Remaining</div>
    </div>
</div>
```

### Step 4.2: Add CSS

```css
.stats {
    background-color: var(--gray-100);
    padding: 1rem;
    border-radius: 0.5rem;
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
    margin-bottom: 2rem;
}

.stat {
    text-align: center;
}

.stat-value {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--primary-color);
}

.stat-label {
    font-size: 0.875rem;
    color: var(--gray-600);
    margin-top: 0.25rem;
}
```

### Step 4.3: Add JavaScript

Add method to TaskManager:

```javascript
// In TaskManager class
getStats() {
    return {
        total: this.tasks.length,
        completed: this.tasks.filter(t => t.completed).length,
        remaining: this.tasks.filter(t => !t.completed).length
    };
}
```

Add update function:

```javascript
// Update the stats display
function updateStats() {
    const stats = taskManager.getStats();
    document.getElementById('totalCount').textContent = stats.total;
    document.getElementById('completedCount').textContent = stats.completed;
    document.getElementById('remainingCount').textContent = stats.remaining;
}
```

Update renderTasks to call updateStats:

```javascript
function handleAddTask() {
    // ... existing code ...
    renderTasks();
    updateStats();  // Add this line
}
```

Also update the toggle:

```javascript
checkbox.addEventListener('change', () => {
    taskManager.toggleTask(task.id);
    renderTasks();
    updateStats();  // Add this line
});
```

And delete:

```javascript
deleteBtn.addEventListener('click', () => {
    taskManager.removeTask(task.id);
    renderTasks();
    updateStats();  // Add this line
});
```

Initialize:

```javascript
// At the end
renderTasks();
updateStats();  // Add this line
```

---

## Phase 5: Polish and Refinement (5 minutes)

### Step 5.1: Add Animations

Add to your CSS:

```css
@keyframes slideIn {
    from {
        opacity: 0;
        transform: translateY(-10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.task-list li {
    animation: slideIn 0.3s ease;
}
```

### Step 5.2: Add Accessibility Improvements

Update your input:

```html
<input
    type="text"
    id="taskInput"
    placeholder="What needs to be done?"
    aria-label="Enter a new task"
>
```

### Step 5.3: Add Footer

Add after `.main` closing tag:

```html
<div class="footer">
    <p>Tasks are saved automatically to your browser</p>
</div>
```

And CSS:

```css
.footer {
    background-color: var(--gray-100);
    padding: 1.5rem;
    text-align: center;
    font-size: 0.875rem;
    color: var(--gray-600);
    border-top: 1px solid var(--gray-200);
}
```

---

## Congratulations!

You've built a complete, functional task management application with:
- ✓ Add tasks
- ✓ Mark complete/incomplete
- ✓ Delete tasks
- ✓ Statistics display
- ✓ Persistent storage
- ✓ Responsive design
- ✓ Accessibility features
- ✓ Professional styling

## Next Steps

Want to extend this project? Try:

1. **Clear Completed Tasks Button** - Add a button to remove all completed tasks at once
2. **Edit Tasks** - Allow editing task text after creation
3. **Categories** - Add categories/tags to tasks
4. **Due Dates** - Add due dates and sort by date
5. **Local Storage Export** - Download tasks as JSON

See `EXERCISES.md` for guided exercises!

## Key Learnings

- **HTML:** Semantic structure with accessibility
- **CSS:** Modern layout (Flexbox), responsive design, variables
- **JavaScript:** Classes, array methods, DOM manipulation, event listeners
- **Storage:** Browser's localStorage for persistence
- **UX:** User feedback with animations and clear states

You now have the foundation to build more complex web applications!

