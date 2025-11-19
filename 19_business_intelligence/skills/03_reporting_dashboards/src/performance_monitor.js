/**
 * Dashboard Performance Monitoring Utilities
 * Track load times, query performance, and user experience
 */

class PerformanceMonitor {
    constructor(dashboardId) {
        this.dashboardId = dashboardId;
        this.metrics = {
            loadStart: null,
            loadEnd: null,
            queryTimes: [],
            renderTimes: [],
            interactions: []
        };
        this.thresholds = {
            loadTime: 3000, // 3 seconds
            queryTime: 1000, // 1 second
            renderTime: 500 // 500ms
        };
    }

    // Start monitoring dashboard load
    startLoad() {
        this.metrics.loadStart = performance.now();
        console.log(`[Perf] Dashboard ${this.dashboardId} load started`);
    }

    // End monitoring dashboard load
    endLoad() {
        this.metrics.loadEnd = performance.now();
        const loadTime = this.metrics.loadEnd - this.metrics.loadStart;
        console.log(`[Perf] Dashboard load completed in ${loadTime.toFixed(2)}ms`);
        
        if (loadTime > this.thresholds.loadTime) {
            console.warn(`[Perf] Load time exceeded threshold: ${loadTime}ms > ${this.thresholds.loadTime}ms`);
        }
        
        this.sendMetric('dashboard_load_time', loadTime);
        return loadTime;
    }

    // Monitor individual query performance
    async monitorQuery(queryName, queryFunction) {
        const start = performance.now();
        
        try {
            const result = await queryFunction();
            const duration = performance.now() - start;
            
            this.metrics.queryTimes.push({
                name: queryName,
                duration: duration,
                timestamp: Date.now()
            });
            
            console.log(`[Perf] Query "${queryName}" completed in ${duration.toFixed(2)}ms`);
            
            if (duration > this.thresholds.queryTime) {
                console.warn(`[Perf] Slow query detected: ${queryName} (${duration}ms)`);
            }
            
            this.sendMetric('query_time', duration, { queryName });
            return result;
            
        } catch (error) {
            console.error(`[Perf] Query "${queryName}" failed:`, error);
            this.sendMetric('query_error', 1, { queryName, error: error.message });
            throw error;
        }
    }

    // Monitor chart rendering performance
    monitorRender(chartId, renderFunction) {
        const start = performance.now();
        
        renderFunction();
        
        const duration = performance.now() - start;
        this.metrics.renderTimes.push({
            chartId: chartId,
            duration: duration,
            timestamp: Date.now()
        });
        
        console.log(`[Perf] Chart "${chartId}" rendered in ${duration.toFixed(2)}ms`);
        
        if (duration > this.thresholds.renderTime) {
            console.warn(`[Perf] Slow render: ${chartId} (${duration}ms)`);
        }
        
        this.sendMetric('render_time', duration, { chartId });
    }

    // Track user interactions
    trackInteraction(interactionType, target) {
        this.metrics.interactions.push({
            type: interactionType,
            target: target,
            timestamp: Date.now()
        });
        
        this.sendMetric('user_interaction', 1, {
            type: interactionType,
            target: target
        });
    }

    // Get performance summary
    getSummary() {
        const loadTime = this.metrics.loadEnd - this.metrics.loadStart;
        const avgQueryTime = this.metrics.queryTimes.length > 0
            ? this.metrics.queryTimes.reduce((sum, q) => sum + q.duration, 0) / this.metrics.queryTimes.length
            : 0;
        const avgRenderTime = this.metrics.renderTimes.length > 0
            ? this.metrics.renderTimes.reduce((sum, r) => sum + r.duration, 0) / this.metrics.renderTimes.length
            : 0;
        
        return {
            dashboardId: this.dashboardId,
            loadTime: loadTime,
            avgQueryTime: avgQueryTime,
            avgRenderTime: avgRenderTime,
            totalQueries: this.metrics.queryTimes.length,
            totalRenders: this.metrics.renderTimes.length,
            totalInteractions: this.metrics.interactions.length,
            slowQueries: this.metrics.queryTimes.filter(q => q.duration > this.thresholds.queryTime),
            slowRenders: this.metrics.renderTimes.filter(r => r.duration > this.thresholds.renderTime)
        };
    }

    // Send metrics to analytics service
    sendMetric(metricName, value, metadata = {}) {
        // Integration with analytics service (Google Analytics, Mixpanel, etc.)
        if (window.analytics) {
            window.analytics.track(metricName, {
                dashboardId: this.dashboardId,
                value: value,
                ...metadata
            });
        }
        
        // Also send to custom backend if available
        if (window.dashboardAnalytics) {
            window.dashboardAnalytics.logMetric({
                dashboard: this.dashboardId,
                metric: metricName,
                value: value,
                metadata: metadata,
                timestamp: Date.now()
            });
        }
    }

    // Generate performance report
    generateReport() {
        const summary = this.getSummary();
        
        console.group(`Performance Report: ${this.dashboardId}`);
        console.log(`Load Time: ${summary.loadTime.toFixed(2)}ms`);
        console.log(`Avg Query Time: ${summary.avgQueryTime.toFixed(2)}ms (${summary.totalQueries} queries)`);
        console.log(`Avg Render Time: ${summary.avgRenderTime.toFixed(2)}ms (${summary.totalRenders} renders)`);
        console.log(`User Interactions: ${summary.totalInteractions}`);
        
        if (summary.slowQueries.length > 0) {
            console.warn(`Slow Queries (>${this.thresholds.queryTime}ms):`);
            summary.slowQueries.forEach(q => {
                console.warn(`  - ${q.name}: ${q.duration.toFixed(2)}ms`);
            });
        }
        
        if (summary.slowRenders.length > 0) {
            console.warn(`Slow Renders (>${this.thresholds.renderTime}ms):`);
            summary.slowRenders.forEach(r => {
                console.warn(`  - ${r.chartId}: ${r.duration.toFixed(2)}ms`);
            });
        }
        
        console.groupEnd();
        
        return summary;
    }

    // Monitor Web Vitals
    monitorWebVitals() {
        // First Contentful Paint (FCP)
        const fcpObserver = new PerformanceObserver((list) => {
            for (const entry of list.getEntries()) {
                console.log(`[Perf] FCP: ${entry.startTime.toFixed(2)}ms`);
                this.sendMetric('fcp', entry.startTime);
            }
        });
        fcpObserver.observe({ type: 'paint', buffered: true });

        // Largest Contentful Paint (LCP)
        const lcpObserver = new PerformanceObserver((list) => {
            const entries = list.getEntries();
            const lastEntry = entries[entries.length - 1];
            console.log(`[Perf] LCP: ${lastEntry.startTime.toFixed(2)}ms`);
            this.sendMetric('lcp', lastEntry.startTime);
        });
        lcpObserver.observe({ type: 'largest-contentful-paint', buffered: true });

        // Cumulative Layout Shift (CLS)
        let clsScore = 0;
        const clsObserver = new PerformanceObserver((list) => {
            for (const entry of list.getEntries()) {
                if (!entry.hadRecentInput) {
                    clsScore += entry.value;
                }
            }
            console.log(`[Perf] CLS: ${clsScore.toFixed(3)}`);
            this.sendMetric('cls', clsScore);
        });
        clsObserver.observe({ type: 'layout-shift', buffered: true });
    }
}

// Usage Example
const monitor = new PerformanceMonitor('executive-dashboard');

// Monitor full dashboard load
monitor.startLoad();

// Monitor individual queries
async function loadDashboardData() {
    const revenue = await monitor.monitorQuery('revenue_query', async () => {
        return fetch('/api/revenue').then(r => r.json());
    });
    
    const customers = await monitor.monitorQuery('customers_query', async () => {
        return fetch('/api/customers').then(r => r.json());
    });
    
    return { revenue, customers };
}

// Monitor chart rendering
function renderChart(chartId, data) {
    monitor.monitorRender(chartId, () => {
        // Chart rendering logic here
        createChart(chartId, data);
    });
}

// Track user interactions
document.getElementById('apply-filters').addEventListener('click', () => {
    monitor.trackInteraction('filter_apply', 'date_range');
});

// End load monitoring
window.addEventListener('load', () => {
    monitor.endLoad();
    monitor.monitorWebVitals();
    
    // Generate report after 5 seconds
    setTimeout(() => {
        monitor.generateReport();
    }, 5000);
});

// Export
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PerformanceMonitor;
}
