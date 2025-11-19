// Exercise 1 Solution: Clear Completed Tasks
// This solution shows how to add a button to clear all completed tasks

// ==========================================
// Step 1: Add clearCompleted method to TaskManager
// ==========================================

// Add this method to your TaskManager class:
class TaskManager {
    // ... existing methods ...

    // Clear all completed tasks
    clearCompleted() {
        const before = this.tasks.length;
        this.tasks = this.tasks.filter(t => !t.completed);
        const after = this.tasks.length;
        const cleared = before - after;

        this.saveTasks();
        console.log(`Cleared ${cleared} completed tasks`);

        return cleared;
    }
}

// ==========================================
// Step 2: Get the button element
// ==========================================

const clearBtn = document.getElementById('clearBtn');

// ==========================================
// Step 3: Update the button visibility
// ==========================================

// Call this function whenever tasks change
function updateClearButton() {
    const completedCount = taskManager.tasks.filter(t => t.completed).length;

    if (completedCount > 0) {
        clearBtn.hidden = false;
    } else {
        clearBtn.hidden = true;
    }
}

// ==========================================
// Step 4: Add event listener to button
// ==========================================

clearBtn.addEventListener('click', () => {
    // Ask user for confirmation (optional but good UX)
    if (confirm('Remove all completed tasks? This cannot be undone.')) {
        taskManager.clearCompleted();
        renderTasks();
        updateStats();
        updateClearButton();  // Hide button if no more completed
    }
});

// ==========================================
// Step 5: Call updateClearButton in key places
// ==========================================

// In handleAddTask:
function handleAddTask() {
    const text = taskInput.value.trim();
    if (!text) {
        taskInput.focus();
        return;
    }

    taskManager.addTask(text);
    taskInput.value = '';
    taskInput.focus();
    renderTasks();
    updateStats();
    updateClearButton();  // Add this line
}

// In renderTasks, when you toggle:
checkbox.addEventListener('change', () => {
    taskManager.toggleTask(task.id);
    renderTasks();
    updateStats();
    updateClearButton();  // Add this line
});

// ==========================================
// Step 6: Initial render
// ==========================================

// At the end of your script:
renderTasks();
updateStats();
updateClearButton();  // Add this line

// ==========================================
// Alternative Implementation
// ==========================================

// If you don't want confirmation dialog, simpler version:

/*
clearBtn.addEventListener('click', () => {
    taskManager.clearCompleted();
    renderTasks();
    updateStats();
    updateClearButton();
});
*/

// ==========================================
// Key Concepts Used
// ==========================================

// 1. Array.filter() - Keep only non-completed tasks
//    this.tasks.filter(t => !t.completed)

// 2. Conditional rendering - Show/hide based on state
//    if (completedCount > 0) { ... }

// 3. Event listeners - Respond to clicks
//    addEventListener('click', function)

// 4. State management - Update after changes
//    updateClearButton() after any change

// ==========================================
// Testing Checklist
// ==========================================

// [ ] Add a task
// [ ] Complete the task (checkbox)
// [ ] "Clear Completed" button appears
// [ ] Click button - task disappears
// [ ] Add another task
// [ ] Button disappears (no completed tasks)
// [ ] Refresh page - tasks still there

