# Troubleshooting Guide: Common Issues and Solutions

Having problems? This guide covers the most common issues and how to fix them.

## How to Troubleshoot

### Step 1: Check the Browser Console

Press `F12` to open Developer Tools, then click the "Console" tab.

Look for red error messages. These tell you what's wrong.

**Common errors:**
- `Uncaught SyntaxError` - Typo in your code
- `Uncaught TypeError` - Using a function/method that doesn't exist
- `Cannot read property` - Trying to access something that doesn't exist

### Step 2: Read the Error Message

Error messages say what's wrong and where:

```
Uncaught ReferenceError: taskInput is not defined
    at app.js:45
```

Translation:
- "ReferenceError" - Variable doesn't exist
- "taskInput is not defined" - You used `taskInput` but didn't define it
- "line 45" - The error is on line 45

### Step 3: Check Your Code

Look at the line mentioned in the error and see what's different from the tutorial.

### Step 4: Search Your Specific Error

Copy the error message into Google. Usually someone else had it and has a solution!

---

## Problem: "My tasks don't save"

**Symptoms:**
- Tasks disappear when I refresh the page
- Tasks disappear when I close the browser

### Cause 1: localStorage is disabled

Some browsers or settings disable localStorage.

**Solution:**
1. Check browser privacy settings
2. Try a different browser
3. Ensure you're not in Private/Incognito mode

### Cause 2: You didn't call `saveTasks()`

Tasks are only saved when you explicitly save them.

**Check your code:**
```javascript
// In addTask, you should have:
this.tasks.push(task);
this.saveTasks();  // ← Is this here?

// In removeTask, you should have:
this.tasks = this.tasks.filter(...);
this.saveTasks();  // ← Is this here?
```

**Solution:**
Make sure you call `saveTasks()` after any change.

### Cause 3: Wrong storage key

You save with one key but load with another.

**Check your code:**
```javascript
// When saving:
localStorage.setItem('tasks', JSON.stringify(this.tasks));

// When loading, use the SAME key:
const json = localStorage.getItem('tasks');
```

### Cause 4: Clearing localStorage

Some code clears your data.

**Check for:**
```javascript
localStorage.clear();  // ← This deletes everything!
localStorage.removeItem('tasks');  // ← This deletes just tasks
```

### Diagnostic: Check localStorage in Browser

1. Press F12 to open Developer Tools
2. Click "Application" tab
3. Click "Local Storage" on the left
4. Click your website
5. Look for an entry with key "tasks"

If you see it, the data is saved. If not, it's not being saved.

---

## Problem: "Buttons and inputs don't work"

**Symptoms:**
- Clicking a button does nothing
- Can't type in the input
- No errors in console

### Cause 1: Event listeners not attached

Event listeners need to be attached to elements that exist in the HTML.

**Check your HTML:**
```html
<!-- These must have matching ids: -->
<input id="taskInput">
<button id="addBtn">Add</button>
```

**Check your JavaScript:**
```javascript
// These must match the HTML ids:
const taskInput = document.getElementById('taskInput');  // ← Spelled correctly?
const addBtn = document.getElementById('addBtn');

addBtn.addEventListener('click', handleAddTask);  // ← Listener attached?
```

**Solution:**
1. Check that ids in HTML match ids in JavaScript
2. Check that event listeners are added (look for `addEventListener`)
3. Check that the function exists (is it spelled correctly?)

### Cause 2: Function doesn't exist

You reference a function that doesn't exist.

**Check your code:**
```javascript
addBtn.addEventListener('click', handleAddTask);
// But did you define handleAddTask? ↓
function handleAddTask() {
    // function body
}
```

**Solution:**
Make sure the function is defined before you use it.

### Cause 3: Code runs before HTML loads

Your JavaScript runs before the HTML elements exist.

```html
<script>
    // This runs immediately
    const button = document.getElementById('btn');  // ← button doesn't exist yet!
    button.addEventListener('click', ...);  // ← Error!
</script>

<button id="btn">Click</button>  <!-- Element is defined after -->
```

**Solutions:**

Option 1: Put script at the end of body:
```html
<body>
    <button id="btn">Click</button>

    <script>
        // Now button exists
        const button = document.getElementById('btn');
    </script>
</body>
```

Option 2: Wait for page to load:
```javascript
document.addEventListener('DOMContentLoaded', () => {
    // Code here runs after HTML loads
    const button = document.getElementById('btn');
});
```

### Diagnostic: Check Elements Exist

1. Press F12
2. Click "Elements" tab
3. Search for your element with Ctrl+F
4. Does it exist in the HTML?

---

## Problem: "Styling looks wrong"

**Symptoms:**
- Layout is broken
- Colors are wrong
- Text is huge/tiny

### Cause 1: CSS not loading

Your styles aren't being applied.

**Check your code:**
```html
<head>
    <style>
        /* CSS should be here */
        .header {
            background: blue;
        }
    </style>
</head>
```

**Solution:**
Make sure `<style>` tags are in the `<head>` section.

### Cause 2: Wrong selectors

CSS selector doesn't match your HTML.

**Common mistakes:**
```css
/* HTML: <input id="taskInput"> */
.taskInput { }  /* ← WRONG: Uses class selector (.) */
#taskInput { }  /* ← CORRECT: Uses id selector (#) */

/* HTML: <button class="btn-add"> */
.btn_add { }    /* ← WRONG: Uses underscore, HTML uses dash */
.btn-add { }    /* ← CORRECT: Matches HTML */
```

**Solution:**
Check that your CSS selectors match your HTML exactly.

### Cause 3: Specificity conflicts

Later CSS overrides earlier CSS.

```css
.button {
    background: blue;
}

/* This overrides the above */
button {
    background: red;
}
```

**Solutions:**
- Check that your CSS is correct
- Put your CSS AFTER other CSS files
- Use more specific selectors if needed
- Use DevTools to see what's applied

### Diagnostic: Check Applied Styles

1. Press F12
2. Right-click the element that looks wrong
3. Click "Inspect"
4. Look at the "Styles" panel on the right
5. It shows what CSS is applied

If you see your style crossed out, something else overrode it.

### Cause 4: Mobile responsiveness

Your media queries might be wrong.

**Check this:**
```css
/* This applies on large screens */
@media (min-width: 768px) {
    /* But are you testing on a screen >= 768px? */
}
```

**Solution:**
Press F12, click the phone icon to view in mobile mode, then check if it looks right.

---

## Problem: "JavaScript errors in console"

### Error: "Cannot read property X of undefined"

**Meaning:** You tried to access a property on something that doesn't exist.

```javascript
const task = tasks[0];  // ← What if tasks is empty?
console.log(task.text); // ← Error! task is undefined
```

**Solution:**
Check that the thing exists before accessing it:
```javascript
const task = tasks[0];
if (task) {  // ← Check it exists
    console.log(task.text);
}
```

### Error: "X is not a function"

**Meaning:** You called something as a function, but it's not.

```javascript
const task = "Buy milk";
task();  // ← Error! task is a string, not a function
```

**Solution:**
Check what you're calling:
```javascript
// If you meant to call a method:
taskManager.addTask("Buy milk");  // ← Method exists

// If you're getting undefined:
const func = getSomeFunction();
if (typeof func === 'function') {
    func();
}
```

### Error: "Unexpected token"

**Meaning:** Syntax error - something is typed wrong.

```javascript
const x = [1, 2, 3  // ← Missing closing bracket
```

**Solution:**
1. Check for missing brackets, parentheses, quotes
2. Check that `{` and `}` match
3. Check that `(` and `)` match
4. Check that `[` and `]` match
5. Check for missing commas

### Error: "ReferenceError: X is not defined"

**Meaning:** You used a variable that doesn't exist.

```javascript
console.log(myVar);  // ← Did you create myVar?
// You forgot: const myVar = ...
```

**Solution:**
Define the variable before using it:
```javascript
const myVar = "Hello";
console.log(myVar);  // ← Works now
```

---

## Problem: "The app loads but nothing happens"

**Symptoms:**
- Page loads
- No errors in console
- But nothing works

### Cause 1: JavaScript doesn't run

Your script tag might be wrong.

**Check this:**
```html
<!-- WRONG: Missing closing tag -->
<script>
    // code here
<!-- Missing </script> -->

<!-- RIGHT: Has closing tag -->
<script>
    // code here
</script>
```

### Cause 2: Tasks aren't being rendered

RenderTasks isn't being called.

**Check:**
```javascript
// At the end of your script, is this called?
renderTasks();

// If not, add it:
// Initial render
renderTasks();
updateStats();
```

### Cause 3: Task list element doesn't exist

```javascript
const taskList = document.getElementById('taskList');
// If taskList is null, the script might fail silently
```

**Check:**
Make sure you have:
```html
<ul id="taskList"></ul>
```

And that the id matches in JavaScript:
```javascript
const taskList = document.getElementById('taskList');  // ← Same id
```

### Diagnostic: Add Logging

Add console.log statements to see what's running:

```javascript
console.log('Script started');

function renderTasks() {
    console.log('renderTasks called');
    // ...
}

renderTasks();
console.log('Script finished');
```

Then press F12 and look for these messages in the console.

---

## Problem: "Data isn't persisting in localStorage"

### Check 1: Browser Console

```javascript
// In browser console (F12), type:
localStorage.getItem('tasks');

// If you see "null", no data is saved
// If you see JSON, data is there
```

### Check 2: Private/Incognito Mode

localStorage doesn't work in Private mode. Use normal mode.

### Check 3: localStorage is Disabled

Some browsers disable it for security. Try a different browser.

### Check 4: JSON Parsing Error

If your saved data is malformed, JSON.parse fails.

**Debug this:**
```javascript
try {
    const json = localStorage.getItem('tasks');
    const tasks = JSON.parse(json);
    console.log('Loaded:', tasks);
} catch (error) {
    console.error('Error loading tasks:', error);
    console.log('Raw data:', json);
}
```

---

## Problem: "Tasks don't appear when I refresh"

### Step 1: Check localStorage

Press F12, Application tab, Local Storage, look for 'tasks' key.

If the key exists with JSON, the data is there.

### Step 2: Check loadTasks runs

Add this to your code:
```javascript
loadTasks() {
    const json = localStorage.getItem(this.storageKey);
    console.log('Loading... Found:', json);
    if (json) {
        // parse and set tasks
        console.log('Tasks loaded:', this.tasks);
    }
}
```

### Step 3: Check renderTasks runs on load

At the end of your script:
```javascript
// Initialize
let taskManager = new TaskManager();
// ...
renderTasks();  // ← Is this called?
```

If not, add it.

---

## Debugging Workflow

When something breaks:

1. **Read the error message** - It usually tells you what's wrong
2. **Check the console** - F12 to see all errors
3. **Add logging** - Use `console.log()` to track execution
4. **Check HTML** - Elements must have correct ids
5. **Check JavaScript** - ids must match, functions must exist
6. **Test incrementally** - Build step by step, test after each
7. **Compare to tutorial** - Look for differences

## Resources for Help

- **MDN Web Docs**: https://developer.mozilla.org
- **Stack Overflow**: https://stackoverflow.com (search your error)
- **Console Errors**: Copy the error message into Google
- **Browser DevTools**: F12, incredibly useful for debugging

---

## Quick Checklist

If nothing works:

- [ ] Check for errors in F12 console
- [ ] Check that HTML element ids match JavaScript ids
- [ ] Check that functions are defined
- [ ] Check that event listeners are attached
- [ ] Check that saveTasks() is called
- [ ] Check that renderTasks() is called
- [ ] Check that CSS is in `<style>` tags
- [ ] Check that localStorage has data (F12 → Application)
- [ ] Try a different browser

---

## Still Stuck?

1. **Re-read the error message carefully** - It usually explains the issue
2. **Look at a working example** - The complete code is in `index.html`
3. **Compare side-by-side** - Put your code and working code next to each other
4. **Take a break** - Fresh eyes help
5. **Rubber duck debugging** - Explain your code to a rubber duck (or person). Often you'll see the issue!

You've got this! Debugging is a normal part of programming. Every developer does it.

