/**
 * Mixpanel Event Tracking Integration
 * Production-ready browser-side implementation with queue management,
 * error handling, and automatic session tracking.
 *
 * Usage:
 *   const analytics = new MixpanelAnalytics('YOUR_TOKEN');
 *   analytics.trackEvent('feature_usage', { feature: 'export', duration: 1234 });
 */

class MixpanelAnalytics {
    /**
     * Initialize Mixpanel tracking
     * @param {string} token - Mixpanel project token
     * @param {Object} options - Configuration options
     */
    constructor(token, options = {}) {
        if (!token) {
            throw new Error('Mixpanel token is required');
        }

        this.token = token;
        this.config = {
            batchSize: options.batchSize || 50,
            flushInterval: options.flushInterval || 30000, // 30 seconds
            apiUrl: options.apiUrl || 'https://api.mixpanel.com/track',
            enableLogging: options.enableLogging !== false,
            enableSessionTracking: options.enableSessionTracking !== false,
            trackPageViews: options.trackPageViews !== false,
        };

        this.eventQueue = [];
        this.sessionId = this._generateSessionId();
        this.userId = null;
        this.userProperties = {};
        this.isOnline = navigator.onLine;

        // Initialize
        this._setupEventListeners();
        this._startFlushInterval();
        this._initializeSession();

        this.log('Analytics initialized', { sessionId: this.sessionId });
    }

    /**
     * Track an event
     * @param {string} eventName - Name of event to track
     * @param {Object} properties - Event properties
     * @returns {boolean} - Whether event was queued successfully
     *
     * Example:
     *   tracker.trackEvent('button_clicked', {
     *     buttonId: 'submit_btn',
     *     section: 'checkout',
     *     duration_ms: 500
     *   });
     */
    trackEvent(eventName, properties = {}) {
        try {
            // Validate event name
            if (!eventName || typeof eventName !== 'string') {
                this.log('Invalid event name', { eventName }, 'warn');
                return false;
            }

            // Enrich properties with context
            const enrichedProperties = this._enrichProperties(properties);

            // Create event object
            const event = {
                event: eventName,
                properties: {
                    token: this.token,
                    ...enrichedProperties,
                }
            };

            // Queue event
            this.eventQueue.push(event);
            this.log(`Event queued: ${eventName}`, enrichedProperties);

            // Check if we should flush
            if (this.eventQueue.length >= this.config.batchSize) {
                this.flush();
            }

            return true;
        } catch (error) {
            this.log('Error tracking event', { error: error.message }, 'error');
            return false;
        }
    }

    /**
     * Identify user
     * @param {string} userId - Unique user identifier
     * @param {Object} traits - User properties/traits
     *
     * Example:
     *   tracker.identify('user_12345', {
     *     email: 'user@example.com',
     *     name: 'John Doe',
     *     plan: 'premium',
     *     signup_date: '2024-01-15',
     *     lifetime_value: 299.99
     *   });
     */
    identify(userId, traits = {}) {
        try {
            if (!userId) {
                this.log('Invalid user ID', { userId }, 'warn');
                return false;
            }

            this.userId = userId;
            this.userProperties = traits;

            // Send identify event
            this.trackEvent('$identify', {
                $set: traits,
                ...traits
            });

            this.log('User identified', { userId, traits });
            return true;
        } catch (error) {
            this.log('Error identifying user', { error: error.message }, 'error');
            return false;
        }
    }

    /**
     * Track page view
     * @param {string} pageName - Name/identifier of page
     * @param {Object} properties - Additional page properties
     */
    trackPageView(pageName, properties = {}) {
        try {
            if (!pageName) {
                pageName = document.title || window.location.pathname;
            }

            this.trackEvent('page_view', {
                page_name: pageName,
                url: window.location.href,
                referrer: document.referrer,
                ...properties
            });

            return true;
        } catch (error) {
            this.log('Error tracking page view', { error: error.message }, 'error');
            return false;
        }
    }

    /**
     * Track user action with timing
     * @param {string} actionName - Name of action
     * @param {Function} callback - Action callback function
     * @returns {*} - Return value of callback
     *
     * Example:
     *   const result = tracker.trackAction('export_report', () => {
     *     return generatePDF();
     *   });
     */
    trackAction(actionName, callback) {
        const startTime = performance.now();

        try {
            const result = callback();
            const duration = performance.now() - startTime;

            this.trackEvent(`action_completed`, {
                action: actionName,
                duration_ms: Math.round(duration),
                success: true
            });

            return result;
        } catch (error) {
            const duration = performance.now() - startTime;

            this.trackEvent(`action_failed`, {
                action: actionName,
                duration_ms: Math.round(duration),
                success: false,
                error_message: error.message
            });

            throw error;
        }
    }

    /**
     * Track timing metric
     * @param {string} category - Category of timing
     * @param {string} variable - Variable name
     * @param {number} time - Time in milliseconds
     * @param {Object} properties - Additional properties
     */
    trackTiming(category, variable, time, properties = {}) {
        try {
            this.trackEvent('timing_event', {
                category,
                variable,
                time_ms: time,
                ...properties
            });
            return true;
        } catch (error) {
            this.log('Error tracking timing', { error: error.message }, 'error');
            return false;
        }
    }

    /**
     * Track error event
     * @param {string} errorMessage - Error message
     * @param {Object} errorDetails - Additional error details
     */
    trackError(errorMessage, errorDetails = {}) {
        try {
            this.trackEvent('error_occurred', {
                error_message: errorMessage,
                error_stack: errorDetails.stack || '',
                user_agent: navigator.userAgent,
                url: window.location.href,
                ...errorDetails
            });
            return true;
        } catch (error) {
            this.log('Error tracking error event', { error: error.message }, 'error');
            return false;
        }
    }

    /**
     * Flush all queued events
     * @returns {Promise<boolean>}
     */
    async flush() {
        if (this.eventQueue.length === 0) {
            return true;
        }

        if (!this.isOnline) {
            this.log('Device offline, events will be sent when online', {}, 'warn');
            return false;
        }

        try {
            const events = [...this.eventQueue];
            this.eventQueue = [];

            // Create batch payload
            const payload = events.map(event => ({
                data: btoa(JSON.stringify(event.properties)),
                ip: 1 // Let server determine IP
            }));

            // Send batch
            const response = await fetch(this.config.apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `data=${encodeURIComponent(JSON.stringify(payload))}`,
                keepalive: true
            });

            if (response.ok) {
                this.log(`Flushed ${events.length} events successfully`);
                return true;
            } else {
                // Re-queue events on failure
                this.eventQueue.unshift(...events);
                this.log(
                    `Failed to flush events: ${response.status}`,
                    { status: response.status },
                    'error'
                );
                return false;
            }
        } catch (error) {
            this.log('Error flushing events', { error: error.message }, 'error');
            return false;
        }
    }

    /**
     * Set user properties (super properties that attach to all events)
     * @param {Object} properties - Properties to set
     */
    setSuperProperties(properties = {}) {
        try {
            this.userProperties = { ...this.userProperties, ...properties };
            this.log('Super properties set', properties);
            return true;
        } catch (error) {
            this.log('Error setting super properties', { error: error.message }, 'error');
            return false;
        }
    }

    /**
     * Get current session info
     * @returns {Object}
     */
    getSessionInfo() {
        return {
            sessionId: this.sessionId,
            userId: this.userId,
            isOnline: this.isOnline,
            queuedEvents: this.eventQueue.length,
            userProperties: this.userProperties
        };
    }

    /**
     * Reset session and user
     */
    reset() {
        try {
            this.flush();
            this.sessionId = this._generateSessionId();
            this.userId = null;
            this.userProperties = {};
            this.log('Analytics reset');
            return true;
        } catch (error) {
            this.log('Error resetting analytics', { error: error.message }, 'error');
            return false;
        }
    }

    /**
     * Shutdown analytics
     */
    shutdown() {
        try {
            this.flush();
            if (this.flushIntervalId) {
                clearInterval(this.flushIntervalId);
            }
            window.removeEventListener('online', this._handleOnline);
            window.removeEventListener('offline', this._handleOffline);
            window.removeEventListener('beforeunload', this._handleUnload);
            this.log('Analytics shutdown complete');
        } catch (error) {
            this.log('Error shutting down analytics', { error: error.message }, 'error');
        }
    }

    // ===== PRIVATE METHODS =====

    /**
     * Enrich event properties with context
     * @private
     */
    _enrichProperties(properties) {
        return {
            time: Date.now(),
            session_id: this.sessionId,
            user_id: this.userId,
            url: window.location.href,
            user_agent: navigator.userAgent,
            timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
            language: navigator.language,
            ...this.userProperties,
            ...properties
        };
    }

    /**
     * Setup event listeners
     * @private
     */
    _setupEventListeners() {
        // Online/offline detection
        this._handleOnline = () => {
            this.isOnline = true;
            this.log('Device came online');
            this.flush();
        };

        this._handleOffline = () => {
            this.isOnline = false;
            this.log('Device went offline');
        };

        // Flush before page unload
        this._handleUnload = () => {
            this.flush();
        };

        window.addEventListener('online', this._handleOnline);
        window.addEventListener('offline', this._handleOffline);
        window.addEventListener('beforeunload', this._handleUnload);
    }

    /**
     * Start periodic flush interval
     * @private
     */
    _startFlushInterval() {
        this.flushIntervalId = setInterval(
            () => this.flush(),
            this.config.flushInterval
        );
    }

    /**
     * Initialize session
     * @private
     */
    _initializeSession() {
        if (this.config.enableSessionTracking) {
            this.trackEvent('session_started', {
                session_id: this.sessionId
            });
        }

        if (this.config.trackPageViews) {
            this.trackPageView();
        }
    }

    /**
     * Generate unique session ID
     * @private
     */
    _generateSessionId() {
        return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    /**
     * Logging utility
     * @private
     */
    log(message, data = {}, level = 'log') {
        if (!this.config.enableLogging) return;

        const timestamp = new Date().toISOString();
        const prefix = `[Mixpanel ${timestamp}]`;

        const logData = {
            message,
            ...data
        };

        if (level === 'error') {
            console.error(prefix, logData);
        } else if (level === 'warn') {
            console.warn(prefix, logData);
        } else {
            console.log(prefix, logData);
        }
    }
}

// ===== EXPORT FOR MODULES =====
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MixpanelAnalytics;
}

// ===== BROWSER USAGE EXAMPLE =====
/*
// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    const analytics = new MixpanelAnalytics('YOUR_MIXPANEL_TOKEN');

    // Identify user
    analytics.identify('user_12345', {
        email: 'user@example.com',
        name: 'John Doe',
        plan: 'premium',
        signup_date: '2024-01-15'
    });

    // Track button click
    document.getElementById('submit-btn').addEventListener('click', () => {
        analytics.trackAction('form_submission', () => {
            // Perform action
            document.getElementById('myForm').submit();
        });
    });

    // Track feature usage
    document.getElementById('export-btn').addEventListener('click', () => {
        const startTime = performance.now();
        exportData();
        const duration = performance.now() - startTime;

        analytics.trackEvent('feature_usage', {
            feature: 'export_data',
            format: 'csv',
            duration_ms: Math.round(duration)
        });
    });

    // Set super properties
    analytics.setSuperProperties({
        app_version: '1.2.3',
        environment: 'production'
    });

    // Flush before leaving page
    window.addEventListener('beforeunload', () => {
        analytics.flush();
    });

    // Shutdown on page unload
    window.addEventListener('unload', () => {
        analytics.shutdown();
    });

    // Error tracking
    window.addEventListener('error', (event) => {
        analytics.trackError(event.message, {
            stack: event.error?.stack,
            filename: event.filename,
            lineno: event.lineno,
            colno: event.colno
        });
    });
});
*/
