# Hands-On Exercises: Challenge Your Skills

Three progressive exercises to extend the task manager and test your understanding.

## Exercise 1: Clear Completed Tasks (Beginner)

### Objective
Add a feature to clear all completed tasks with one button click.

### Requirements
- [ ] Add a "Clear Completed" button in the footer area
- [ ] When clicked, remove all tasks marked as complete
- [ ] Button should only appear when there are completed tasks
- [ ] Update statistics after clearing

### Scaffolding Code

Add to your HTML (in the footer area):

```html
<button id="clearBtn" class="btn-clear" hidden>
    Clear Completed Tasks
</button>
```

Add to your CSS:

```css
.btn-clear {
    background-color: var(--gray-400);
    color: white;
    padding: 0.75rem 1.5rem;
    border: none;
    border-radius: 0.5rem;
    cursor: pointer;
    margin-top: 1rem;
}

.btn-clear:hover {
    background-color: var(--gray-600);
}
```

### Hints

1. **Hint 1:** Add a method to TaskManager called `clearCompleted()`
   - Should filter out completed tasks
   - Should save the updated list

2. **Hint 2:** Create a function `updateClearButton()` that:
   - Gets the completed count
   - Shows button if count > 0
   - Hides button if count === 0

3. **Hint 3:** Add event listener to the button:
   ```javascript
   clearBtn.addEventListener('click', () => {
       // Call the manager method
       // Re-render
       // Update stats
   });
   ```

### Solution Path

See `SOLUTIONS/exercise-1-solution.js`

---

## Exercise 2: Task Categories (Intermediate)

### Objective
Add categories to tasks and filter by category.

### Requirements
- [ ] Modify Task class to include a `category` property
- [ ] Update input form to include category selection
- [ ] Display category with each task
- [ ] Add filter buttons to show tasks by category
- [ ] Show "All" tasks by default
- [ ] Update statistics for selected category

### Scaffolding Code

Update HTML form:

```html
<div class="input-group">
    <input
        type="text"
        id="taskInput"
        placeholder="Task text"
    >
    <select id="categorySelect" aria-label="Task category">
        <option value="work">Work</option>
        <option value="personal">Personal</option>
        <option value="shopping">Shopping</option>
        <option value="health">Health</option>
    </select>
    <button id="addBtn" class="btn-add">Add Task</button>
</div>
```

Add filter buttons:

```html
<div class="filters">
    <button class="filter-btn active" data-filter="all">All</button>
    <button class="filter-btn" data-filter="work">Work</button>
    <button class="filter-btn" data-filter="personal">Personal</button>
    <button class="filter-btn" data-filter="shopping">Shopping</button>
    <button class="filter-btn" data-filter="health">Health</button>
</div>
```

### Hints

1. **Modify Task Class:**
   ```javascript
   class Task {
       constructor(text, category, id = Date.now()) {
           this.id = id;
           this.text = text;
           this.category = category;  // NEW
           this.completed = false;
       }
   }
   ```

2. **Update TaskManager:**
   - When adding: `addTask(text, category)`
   - When loading: restore category from localStorage

3. **Filter Logic:**
   - Keep current filter in a variable
   - In renderTasks, filter by: `currentFilter === 'all' || task.category === currentFilter`

4. **Update Stats:**
   - Calculate stats only for visible (filtered) tasks

### Solution Path

See `SOLUTIONS/exercise-2-solution.js`

---

## Exercise 3: Due Dates and Sorting (Advanced)

### Objective
Add due dates to tasks and sort by due date.

### Requirements
- [ ] Add due date input to task form
- [ ] Display due date with task
- [ ] Show overdue indicator (red) for past dates
- [ ] Sort tasks by due date (earliest first)
- [ ] Handle tasks without due dates
- [ ] Show days remaining/overdue

### Scaffolding Code

Add to HTML form:

```html
<input
    type="date"
    id="dueDateInput"
    aria-label="Task due date"
>
```

Add styling for overdue:

```css
.task-overdue {
    border-left: 4px solid var(--danger-color);
}

.due-date {
    font-size: 0.85rem;
    color: var(--gray-600);
}

.due-date.overdue {
    color: var(--danger-color);
    font-weight: 600;
}
```

### Hints

1. **Update Task Class:**
   ```javascript
   constructor(text, category, dueDate = null, id = Date.now()) {
       this.id = id;
       this.text = text;
       this.category = category;
       this.dueDate = dueDate;  // NEW - ISO date string
       this.completed = false;
   }
   ```

2. **Helper Functions:**
   ```javascript
   function isOverdue(dueDate) {
       if (!dueDate) return false;
       return new Date(dueDate) < new Date();
   }

   function daysRemaining(dueDate) {
       if (!dueDate) return null;
       const days = Math.ceil(
           (new Date(dueDate) - new Date()) / (1000 * 60 * 60 * 24)
       );
       return days;
   }
   ```

3. **Sorting:**
   ```javascript
   // Sort tasks before rendering
   const sorted = taskManager.tasks.sort((a, b) => {
       // Tasks without due dates go to end
       if (!a.dueDate) return 1;
       if (!b.dueDate) return -1;
       // Compare dates
       return new Date(a.dueDate) - new Date(b.dueDate);
   });
   ```

4. **Display Due Date:**
   - Show "Due: Jan 15" format
   - Show "Overdue by 2 days" if past
   - Show "Due in 3 days" if upcoming
   - Show nothing if no due date

### Solution Path

See `SOLUTIONS/exercise-3-solution.js`

---

## How to Approach These Exercises

### Before Coding

1. **Read the requirements** - Understand what should happen
2. **Map out changes** - What files need to change?
3. **Identify the trickiest part** - What will be hardest?
4. **Sketch the logic** - Draw how it works

### While Coding

1. **Start with the data** - Modify the Task class first
2. **Then the UI** - Add HTML elements
3. **Then the logic** - Add JavaScript functions
4. **Test as you go** - Don't write everything then test

### Debugging Tips

- **Check the console** - F12 to see errors
- **Log values** - `console.log(task)` to see what you have
- **Test incrementally** - Test each piece as you build it
- **Use the inspector** - Check HTML elements with F12

### When Stuck

1. **Re-read the hints** - Important clues there
2. **Check the solution** - See how they did it
3. **Try a different approach** - Maybe there's another way
4. **Take a break** - Fresh perspective helps

---

## Testing Your Solution

For each exercise, verify:

- [ ] No JavaScript errors in console (F12)
- [ ] Feature works as described in requirements
- [ ] Statistics update correctly
- [ ] Data persists (close and reopen)
- [ ] Responsive on mobile (press F12, toggle device mode)
- [ ] Keyboard navigation works (Tab through controls)

---

## What You Learned

### Exercise 1 (Beginner)
- Event listeners
- Conditional rendering
- Array methods

### Exercise 2 (Intermediate)
- Modifying existing structures
- Managing multiple states
- Filter logic
- DOM manipulation with data attributes

### Exercise 3 (Advanced)
- Working with dates
- Complex sorting logic
- Formatting and display logic
- Multiple dependencies

---

## Ideas for Extensions

After completing these exercises, try:

1. **Priority Levels** - High/Medium/Low priority with color coding
2. **Recurring Tasks** - Daily/Weekly/Monthly tasks
3. **Time Tracking** - How long each task takes
4. **Notes** - Add detailed notes to tasks
5. **Import/Export** - Save/load tasks as JSON
6. **Themes** - Light/dark mode toggle
7. **Undo/Redo** - Revert accidental deletions
8. **Sharing** - Send tasks to others

---

## Challenge: Build From Scratch

Can you build a new feature from scratch without hints?

**Feature: Task Search**

Build a search box that:
- Filters tasks by text match
- Works across all categories
- Case-insensitive matching
- Real-time as you type

This combines everything you've learned!

---

## Congratulations!

Completing these exercises means you understand:
- Object-oriented JavaScript
- DOM manipulation
- Event handling
- Data persistence
- Complex UI interactions

You're ready to build real applications!

