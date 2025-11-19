/**
 * Drill-Down Pattern Implementation
 * Three-level drill-down: Overview → Detail → Transaction
 */

class DrillDownController {
    constructor() {
        this.currentLevel = 1;
        this.maxLevels = 3;
        this.breadcrumbs = [];
        this.state = {};
    }

    // Level 1: Overview (e.g., Revenue by Region)
    renderOverview() {
        this.currentLevel = 1;
        this.breadcrumbs = [{level: 1, label: 'Overview'}];
        
        fetch('/api/revenue/by-region')
            .then(res => res.json())
            .then(data => {
                this.renderChart('overview-chart', {
                    type: 'bar',
                    data: data,
                    onClick: (region) => this.drillToRegion(region)
                });
                this.updateBreadcrumbs();
            });
    }

    // Level 2: Regional Detail (e.g., North Region by State)
    drillToRegion(region) {
        if (this.currentLevel >= this.maxLevels) return;
        
        this.currentLevel = 2;
        this.state.region = region;
        this.breadcrumbs.push({level: 2, label: region});
        
        fetch(`/api/revenue/region/${region}/by-state`)
            .then(res => res.json())
            .then(data => {
                this.renderChart('detail-chart', {
                    type: 'bar',
                    data: data,
                    onClick: (state) => this.drillToState(state)
                });
                this.updateBreadcrumbs();
            });
    }

    // Level 3: State Detail (e.g., NY Top Customers)
    drillToState(state) {
        if (this.currentLevel >= this.maxLevels) return;
        
        this.currentLevel = 3;
        this.state.state = state;
        this.breadcrumbs.push({level: 3, label: state});
        
        fetch(`/api/revenue/region/${this.state.region}/state/${state}/customers`)
            .then(res => res.json())
            .then(data => {
                this.renderTable('detail-table', data);
                this.updateBreadcrumbs();
            });
    }

    // Navigate back using breadcrumbs
    navigateToLevel(targetLevel) {
        if (targetLevel < 1 || targetLevel > this.currentLevel) return;
        
        // Remove breadcrumbs after target level
        this.breadcrumbs = this.breadcrumbs.slice(0, targetLevel);
        this.currentLevel = targetLevel;
        
        // Re-render appropriate level
        switch(targetLevel) {
            case 1:
                this.renderOverview();
                break;
            case 2:
                this.drillToRegion(this.state.region);
                break;
            case 3:
                this.drillToState(this.state.state);
                break;
        }
    }

    // Update breadcrumb navigation
    updateBreadcrumbs() {
        const breadcrumbContainer = document.getElementById('breadcrumbs');
        breadcrumbContainer.innerHTML = this.breadcrumbs.map((crumb, index) => `
            <button 
                class="breadcrumb-item ${index === this.breadcrumbs.length - 1 ? 'active' : ''}"
                onclick="drillDown.navigateToLevel(${crumb.level})"
                ${index === this.breadcrumbs.length - 1 ? 'aria-current="page"' : ''}
            >
                ${crumb.label}
            </button>
            ${index < this.breadcrumbs.length - 1 ? '<span class="breadcrumb-separator">></span>' : ''}
        `).join('');
    }

    // Render chart with click handler
    renderChart(containerId, config) {
        const container = document.getElementById(containerId);
        container.innerHTML = ''; // Clear previous chart
        
        // Use your charting library here (Chart.js, D3, etc.)
        // This is a simplified example
        config.data.forEach(item => {
            const bar = document.createElement('div');
            bar.className = 'interactive-bar';
            bar.style.width = `${item.value / config.data[0].value * 100}%`;
            bar.innerHTML = `<span>${item.label}: $${item.value}M</span>`;
            bar.onclick = () => config.onClick(item.id);
            container.appendChild(bar);
        });
    }

    // Render data table
    renderTable(containerId, data) {
        const container = document.getElementById(containerId);
        const table = document.createElement('table');
        table.className = 'data-table';
        
        // Header
        const thead = document.createElement('thead');
        thead.innerHTML = `
            <tr>
                <th>Customer</th>
                <th>Revenue</th>
                <th>Orders</th>
                <th>Last Order</th>
            </tr>
        `;
        table.appendChild(thead);
        
        // Body
        const tbody = document.createElement('tbody');
        data.forEach(row => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${row.customer_name}</td>
                <td>$${row.revenue.toLocaleString()}</td>
                <td>${row.order_count}</td>
                <td>${row.last_order_date}</td>
            `;
            tbody.appendChild(tr);
        });
        table.appendChild(tbody);
        
        container.innerHTML = '';
        container.appendChild(table);
    }

    // Export data at current level
    exportCurrentLevel() {
        const exportUrl = this.getExportUrl();
        window.open(exportUrl, '_blank');
    }

    getExportUrl() {
        switch(this.currentLevel) {
            case 1:
                return '/api/export/overview';
            case 2:
                return `/api/export/region/${this.state.region}`;
            case 3:
                return `/api/export/region/${this.state.region}/state/${this.state.state}`;
            default:
                return '/api/export/overview';
        }
    }
}

// Initialize drill-down controller
const drillDown = new DrillDownController();

// HTML structure for drill-down dashboard
const drillDownHTML = `
<div class="dashboard-container">
    <!-- Breadcrumb Navigation -->
    <nav id="breadcrumbs" aria-label="Breadcrumb navigation"></nav>
    
    <!-- Chart/Table Container -->
    <div id="overview-chart" class="chart-container"></div>
    <div id="detail-chart" class="chart-container" style="display: none;"></div>
    <div id="detail-table" class="table-container" style="display: none;"></div>
    
    <!-- Actions -->
    <div class="actions">
        <button onclick="drillDown.exportCurrentLevel()" class="btn btn-secondary">
            Export Data
        </button>
        ${this.currentLevel > 1 ? `
            <button onclick="drillDown.navigateToLevel(${this.currentLevel - 1})" class="btn btn-secondary">
                ← Back
            </button>
        ` : ''}
    </div>
</div>
`;
