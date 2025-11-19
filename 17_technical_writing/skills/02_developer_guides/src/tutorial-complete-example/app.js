/**
 * Task Management Application
 * Complete JavaScript logic separated from HTML
 * This file contains all the application code that's embedded in index.html
 */

// ==========================================
// Task Class - Represents a single task
// ==========================================
class Task {
    constructor(text, id = Date.now()) {
        this.id = id;
        this.text = text;
        this.completed = false;
        this.createdAt = new Date();
    }

    toggle() {
        this.completed = !this.completed;
    }
}

// ==========================================
// TaskManager Class - Manages all tasks
// ==========================================
class TaskManager {
    constructor(storageKey = 'tasks') {
        this.tasks = [];
        this.storageKey = storageKey;
        this.loadTasks();
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

    // Toggle task completion status
    toggleTask(taskId) {
        const task = this.tasks.find(t => t.id === taskId);
        if (task) {
            task.toggle();
            this.saveTasks();
        }
    }

    // Get statistics
    getStats() {
        return {
            total: this.tasks.length,
            completed: this.tasks.filter(t => t.completed).length,
            remaining: this.tasks.filter(t => !t.completed).length
        };
    }

    // Save tasks to localStorage
    saveTasks() {
        try {
            const json = JSON.stringify(this.tasks);
            localStorage.setItem(this.storageKey, json);
        } catch (error) {
            console.error('Error saving tasks:', error);
        }
    }

    // Load tasks from localStorage
    loadTasks() {
        try {
            const json = localStorage.getItem(this.storageKey);
            if (json) {
                const data = JSON.parse(json);
                // Reconstruct Task objects
                this.tasks = data.map(item =>
                    new Task(item.text, item.id)
                );
                // Restore completion status
                data.forEach((item, index) => {
                    this.tasks[index].completed = item.completed;
                });
            }
        } catch (error) {
            console.error('Error loading tasks:', error);
            this.tasks = [];
        }
    }

    // Clear all tasks
    clearAll() {
        this.tasks = [];
        this.saveTasks();
    }

    // Clear completed tasks
    clearCompleted() {
        this.tasks = this.tasks.filter(t => !t.completed);
        this.saveTasks();
    }
}

// ==========================================
// DOM Management and Event Listeners
// ==========================================

// Initialize the application
let taskManager = new TaskManager();

// Get DOM elements
const taskInput = document.getElementById('taskInput');
const addBtn = document.getElementById('addBtn');
const taskList = document.getElementById('taskList');
const emptyState = document.getElementById('emptyState');
const totalCount = document.getElementById('totalCount');
const completedCount = document.getElementById('completedCount');
const remainingCount = document.getElementById('remainingCount');

// ==========================================
// Rendering Functions
// ==========================================

// Render the complete task list
function renderTasks() {
    // Clear the list
    taskList.innerHTML = '';

    // Show empty state if no tasks
    if (taskManager.tasks.length === 0) {
        emptyState.hidden = false;
        return;
    }

    emptyState.hidden = true;

    // Render each task
    taskManager.tasks.forEach(task => {
        const li = document.createElement('li');

        // Create checkbox
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.checked = task.completed;
        checkbox.setAttribute('aria-label', `Mark "${task.text}" complete`);
        checkbox.addEventListener('change', () => {
            taskManager.toggleTask(task.id);
            renderTasks();
            updateStats();
        });

        // Create task text span
        const span = document.createElement('span');
        span.className = 'task-text';
        span.textContent = task.text;

        // Create delete button
        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'btn-delete';
        deleteBtn.textContent = 'Delete';
        deleteBtn.setAttribute('aria-label', `Delete "${task.text}"`);
        deleteBtn.addEventListener('click', () => {
            taskManager.removeTask(task.id);
            renderTasks();
            updateStats();
        });

        // Assemble the list item
        li.appendChild(checkbox);
        li.appendChild(span);
        li.appendChild(deleteBtn);

        taskList.appendChild(li);
    });
}

// Update statistics display
function updateStats() {
    const stats = taskManager.getStats();
    totalCount.textContent = stats.total;
    completedCount.textContent = stats.completed;
    remainingCount.textContent = stats.remaining;
}

// Add a task when button is clicked
function handleAddTask() {
    const text = taskInput.value.trim();

    // Validate input
    if (!text) {
        taskInput.focus();
        return;
    }

    // Add the task
    taskManager.addTask(text);

    // Clear input and re-render
    taskInput.value = '';
    taskInput.focus();
    renderTasks();
    updateStats();
}

// ==========================================
// Event Listeners
// ==========================================

// Add task on button click
addBtn.addEventListener('click', handleAddTask);

// Add task on Enter key
taskInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        handleAddTask();
    }
});

// ==========================================
// Initialization
// ==========================================

// Render initial state
renderTasks();
updateStats();

// Log to help with debugging
console.log('Task Manager initialized');
console.log('Loaded tasks:', taskManager.tasks);

// ==========================================
// Usage Examples
// ==========================================

/*
// Add a task programmatically:
taskManager.addTask('Buy groceries');
renderTasks();
updateStats();

// Get all tasks:
console.log(taskManager.tasks);

// Get statistics:
console.log(taskManager.getStats());

// Clear all tasks:
taskManager.clearAll();
renderTasks();
updateStats();

// Check localStorage:
console.log(localStorage.getItem('tasks'));
*/

