/**
 * Accessibility Helpers for Dashboards
 * WCAG 2.1 AA Compliance Utilities
 */

// Color Contrast Checker
class ContrastChecker {
    // Calculate relative luminance
    static getLuminance(r, g, b) {
        const [rs, gs, bs] = [r, g, b].map(c => {
            c = c / 255;
            return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
        });
        return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
    }

    // Calculate contrast ratio
    static getContrastRatio(rgb1, rgb2) {
        const lum1 = this.getLuminance(...rgb1);
        const lum2 = this.getLuminance(...rgb2);
        const brightest = Math.max(lum1, lum2);
        const darkest = Math.min(lum1, lum2);
        return (brightest + 0.05) / (darkest + 0.05);
    }

    // Convert hex to RGB
    static hexToRgb(hex) {
        const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
        return result ? [
            parseInt(result[1], 16),
            parseInt(result[2], 16),
            parseInt(result[3], 16)
        ] : null;
    }

    // Check if contrast meets WCAG AA
    static meetsWCAG_AA(foreground, background, isLargeText = false) {
        const fgRgb = this.hexToRgb(foreground);
        const bgRgb = this.hexToRgb(background);
        const ratio = this.getContrastRatio(fgRgb, bgRgb);
        const required = isLargeText ? 3.0 : 4.5;
        return {
            ratio: ratio.toFixed(2),
            passes: ratio >= required,
            required: required
        };
    }
}

// ARIA Label Generator
class ARIALabelGenerator {
    // Generate label for chart
    static forChart(chartType, data, title) {
        const dataPoints = data.length;
        const trend = this.calculateTrend(data);
        return `${title}. ${chartType} showing ${dataPoints} data points with ${trend} trend.`;
    }

    // Generate label for KPI
    static forKPI(label, value, change, comparison) {
        const changeDirection = change >= 0 ? 'increased' : 'decreased';
        const changeValue = Math.abs(change);
        return `${label}: ${value}, ${changeDirection} by ${changeValue}% ${comparison}`;
    }

    // Generate label for table
    static forTable(headers, rowCount) {
        const columnList = headers.join(', ');
        return `Data table with ${rowCount} rows and ${headers.length} columns: ${columnList}`;
    }

    static calculateTrend(data) {
        if (data.length < 2) return 'stable';
        const first = data[0].value || data[0];
        const last = data[data.length - 1].value || data[data.length - 1];
        if (last > first * 1.1) return 'increasing';
        if (last < first * 0.9) return 'decreasing';
        return 'stable';
    }
}

// Keyboard Navigation Manager
class KeyboardNavigation {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.focusableElements = [];
        this.currentIndex = -1;
        this.init();
    }

    init() {
        this.updateFocusableElements();
        this.attachKeyListeners();
    }

    updateFocusableElements() {
        const selector = 'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])';
        this.focusableElements = Array.from(this.container.querySelectorAll(selector));
    }

    attachKeyListeners() {
        this.container.addEventListener('keydown', (e) => {
            switch(e.key) {
                case 'Tab':
                    this.handleTab(e);
                    break;
                case 'ArrowDown':
                case 'ArrowUp':
                    if (e.target.getAttribute('role') === 'menu') {
                        e.preventDefault();
                        this.handleArrowNav(e.key);
                    }
                    break;
                case 'Escape':
                    this.handleEscape(e);
                    break;
            }
        });
    }

    handleTab(e) {
        // Allow normal tab behavior
        // Could add custom logic for complex components
    }

    handleArrowNav(key) {
        const direction = key === 'ArrowDown' ? 1 : -1;
        const newIndex = this.currentIndex + direction;
        if (newIndex >= 0 && newIndex < this.focusableElements.length) {
            this.currentIndex = newIndex;
            this.focusableElements[this.currentIndex].focus();
        }
    }

    handleEscape(e) {
        // Close modals, dropdowns, etc.
        const modal = e.target.closest('[role="dialog"]');
        if (modal) {
            this.closeModal(modal);
        }
    }

    closeModal(modal) {
        modal.style.display = 'none';
        // Return focus to trigger element
        const triggerId = modal.getAttribute('data-triggered-by');
        if (triggerId) {
            document.getElementById(triggerId).focus();
        }
    }
}

// Screen Reader Announcer
class ScreenReaderAnnouncer {
    constructor() {
        this.liveRegion = this.createLiveRegion();
    }

    createLiveRegion() {
        const region = document.createElement('div');
        region.setAttribute('role', 'status');
        region.setAttribute('aria-live', 'polite');
        region.setAttribute('aria-atomic', 'true');
        region.className = 'sr-only';
        document.body.appendChild(region);
        return region;
    }

    announce(message, priority = 'polite') {
        this.liveRegion.setAttribute('aria-live', priority);
        this.liveRegion.textContent = message;
        
        // Clear after announcement
        setTimeout(() => {
            this.liveRegion.textContent = '';
        }, 1000);
    }

    announceFilterChange(filterName, value) {
        this.announce(`${filterName} filter set to ${value}. Dashboard updating.`);
    }

    announceDataUpdate() {
        this.announce('Dashboard data updated.');
    }

    announceError(error) {
        this.announce(`Error: ${error}`, 'assertive');
    }
}

// Focus Management
class FocusManager {
    static trapFocus(element) {
        const focusableElements = element.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        const firstFocusable = focusableElements[0];
        const lastFocusable = focusableElements[focusableElements.length - 1];

        element.addEventListener('keydown', function(e) {
            if (e.key === 'Tab') {
                if (e.shiftKey) {
                    if (document.activeElement === firstFocusable) {
                        lastFocusable.focus();
                        e.preventDefault();
                    }
                } else {
                    if (document.activeElement === lastFocusable) {
                        firstFocusable.focus();
                        e.preventDefault();
                    }
                }
            }
        });

        firstFocusable.focus();
    }

    static restoreFocus(previouslyFocused) {
        if (previouslyFocused) {
            previouslyFocused.focus();
        }
    }
}

// Export utilities
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        ContrastChecker,
        ARIALabelGenerator,
        KeyboardNavigation,
        ScreenReaderAnnouncer,
        FocusManager
    };
}
