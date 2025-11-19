/**
 * Dashboard Filter Patterns
 * Implementing Few-Tufte best practices for dashboard interactivity
 */

// Pattern 1: Single-Apply Filters (Performance-Optimized)
class SingleApplyFilter {
    constructor(dashboardId) {
        this.dashboardId = dashboardId;
        this.pendingFilters = {};
        this.activeFilters = {};
    }

    // User selects filter (doesn't apply yet)
    selectFilter(filterName, value) {
        this.pendingFilters[filterName] = value;
        this.updateFilterDisplay();
    }

    // User clicks "Apply" button
    applyFilters() {
        this.activeFilters = {...this.pendingFilters};
        this.refreshDashboard();
        this.updateActiveFilterChips();
    }

    // Clear all filters
    clearFilters() {
        this.pendingFilters = {};
        this.activeFilters = {};
        this.refreshDashboard();
        this.updateFilterDisplay();
        this.updateActiveFilterChips();
    }

    // Refresh dashboard with active filters
    refreshDashboard() {
        const queryParams = new URLSearchParams(this.activeFilters);
        fetch(`/api/dashboard/${this.dashboardId}?${queryParams}`)
            .then(response => response.json())
            .then(data => this.updateDashboardVisuals(data))
            .catch(error => this.handleError(error));
    }

    // Update filter chips to show active filters
    updateActiveFilterChips() {
        const container = document.getElementById('active-filters');
        container.innerHTML = '';
        
        Object.entries(this.activeFilters).forEach(([key, value]) => {
            const chip = document.createElement('div');
            chip.className = 'filter-chip';
            chip.innerHTML = `
                <span>${this.formatFilterLabel(key)}: ${value}</span>
                <button onclick="removeFilter('${key}')" aria-label="Remove ${key} filter">✕</button>
            `;
            container.appendChild(chip);
        });
    }

    formatFilterLabel(key) {
        return key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }

    updateFilterDisplay() {
        // Update UI to show pending filters
        Object.entries(this.pendingFilters).forEach(([key, value]) => {
            const element = document.querySelector(`[data-filter="${key}"]`);
            if (element) element.value = value;
        });
    }

    updateDashboardVisuals(data) {
        // Update all charts with new data
        data.charts.forEach(chart => {
            updateChart(chart.id, chart.data);
        });
    }

    handleError(error) {
        console.error('Filter error:', error);
        showNotification('Error applying filters. Please try again.', 'error');
    }
}

// Pattern 2: Cascading Filters (Hierarchical Dependencies)
class CascadingFilter {
    constructor() {
        this.hierarchy = [];
        this.filterData = {};
    }

    // Define filter hierarchy (e.g., Region → State → City)
    defineHierarchy(filters) {
        this.hierarchy = filters;
    }

    // When parent filter changes, update child filter options
    async onFilterChange(filterName, value) {
        const filterIndex = this.hierarchy.indexOf(filterName);
        
        // Clear all child filters
        for (let i = filterIndex + 1; i < this.hierarchy.length; i++) {
            this.clearFilter(this.hierarchy[i]);
        }

        // Update next filter options if exists
        if (filterIndex < this.hierarchy.length - 1) {
            const nextFilter = this.hierarchy[filterIndex + 1];
            const options = await this.fetchFilterOptions(nextFilter, {
                [filterName]: value
            });
            this.updateFilterOptions(nextFilter, options);
        }
    }

    async fetchFilterOptions(filterName, parentFilters) {
        const params = new URLSearchParams(parentFilters);
        const response = await fetch(`/api/filters/${filterName}?${params}`);
        return response.json();
    }

    updateFilterOptions(filterName, options) {
        const selectElement = document.querySelector(`select[name="${filterName}"]`);
        selectElement.innerHTML = '<option value="">Select...</option>';
        
        options.forEach(option => {
            const optionElement = document.createElement('option');
            optionElement.value = option.value;
            optionElement.textContent = option.label;
            selectElement.appendChild(optionElement);
        });
        
        selectElement.disabled = false;
    }

    clearFilter(filterName) {
        const selectElement = document.querySelector(`select[name="${filterName}"]`);
        selectElement.innerHTML = '<option value="">Select...</option>';
        selectElement.disabled = true;
    }
}

// Pattern 3: Search/Filter Combo (For High-Cardinality Dimensions)
class SearchableFilter {
    constructor(filterName, options) {
        this.filterName = filterName;
        this.allOptions = options;
        this.selectedValues = new Set();
    }

    // Filter options based on search text
    search(searchText) {
        const filtered = this.allOptions.filter(option =>
            option.label.toLowerCase().includes(searchText.toLowerCase())
        );
        this.renderOptions(filtered);
    }

    // Toggle option selection
    toggleOption(value) {
        if (this.selectedValues.has(value)) {
            this.selectedValues.delete(value);
        } else {
            this.selectedValues.add(value);
        }
        this.updateSelectedDisplay();
    }

    // Select all visible options
    selectAll(visibleOptions) {
        visibleOptions.forEach(option => {
            this.selectedValues.add(option.value);
        });
        this.updateSelectedDisplay();
    }

    // Clear all selections
    clearAll() {
        this.selectedValues.clear();
        this.updateSelectedDisplay();
    }

    getSelected() {
        return Array.from(this.selectedValues);
    }

    renderOptions(options) {
        const container = document.getElementById(`${this.filterName}-options`);
        container.innerHTML = options.map(option => `
            <div class="filter-option">
                <label>
                    <input type="checkbox"
                           value="${option.value}"
                           ${this.selectedValues.has(option.value) ? 'checked' : ''}
                           onchange="filter.toggleOption('${option.value}')">
                    ${option.label} (${option.count})
                </label>
            </div>
        `).join('');
    }

    updateSelectedDisplay() {
        const count = this.selectedValues.size;
        const displayElement = document.getElementById(`${this.filterName}-selected`);
        displayElement.textContent = count > 0
            ? `${count} selected`
            : 'None selected';
    }
}

// Pattern 4: Date Range Filter with Presets
class DateRangeFilter {
    constructor() {
        this.presets = {
            'today': () => [new Date(), new Date()],
            'yesterday': () => {
                const yesterday = new Date();
                yesterday.setDate(yesterday.getDate() - 1);
                return [yesterday, yesterday];
            },
            'last_7_days': () => {
                const end = new Date();
                const start = new Date();
                start.setDate(start.getDate() - 7);
                return [start, end];
            },
            'last_30_days': () => {
                const end = new Date();
                const start = new Date();
                start.setDate(start.getDate() - 30);
                return [start, end];
            },
            'this_month': () => {
                const now = new Date();
                const start = new Date(now.getFullYear(), now.getMonth(), 1);
                return [start, now];
            },
            'last_month': () => {
                const now = new Date();
                const start = new Date(now.getFullYear(), now.getMonth() - 1, 1);
                const end = new Date(now.getFullYear(), now.getMonth(), 0);
                return [start, end];
            },
            'this_quarter': () => {
                const now = new Date();
                const quarter = Math.floor(now.getMonth() / 3);
                const start = new Date(now.getFullYear(), quarter * 3, 1);
                return [start, now];
            },
            'this_year': () => {
                const now = new Date();
                const start = new Date(now.getFullYear(), 0, 1);
                return [start, now];
            }
        };
        
        this.selectedPreset = 'last_30_days';
        this.customRange = null;
    }

    selectPreset(presetName) {
        this.selectedPreset = presetName;
        this.customRange = null;
        const [start, end] = this.presets[presetName]();
        return this.formatDateRange(start, end);
    }

    setCustomRange(startDate, endDate) {
        this.selectedPreset = null;
        this.customRange = [startDate, endDate];
        return this.formatDateRange(startDate, endDate);
    }

    getCurrentRange() {
        if (this.customRange) {
            return this.formatDateRange(...this.customRange);
        } else {
            const [start, end] = this.presets[this.selectedPreset]();
            return this.formatDateRange(start, end);
        }
    }

    formatDateRange(start, end) {
        return {
            start: this.formatDate(start),
            end: this.formatDate(end),
            display: `${this.formatDate(start)} to ${this.formatDate(end)}`
        };
    }

    formatDate(date) {
        return date.toISOString().split('T')[0];
    }
}

// Utility: Show loading state during filter apply
function showLoading(show = true) {
    const loadingOverlay = document.getElementById('loading-overlay');
    loadingOverlay.style.display = show ? 'flex' : 'none';
}

// Utility: Show notification to user
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.setAttribute('role', 'alert');
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Export for use in dashboards
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        SingleApplyFilter,
        CascadingFilter,
        SearchableFilter,
        DateRangeFilter
    };
}
