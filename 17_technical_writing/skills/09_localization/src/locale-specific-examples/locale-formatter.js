/**
 * LocaleFormatter - Comprehensive locale-aware formatting utility
 * Supports dates, times, numbers, currencies across multiple locales
 */

class LocaleFormatter {
    constructor(locale = 'en-US') {
        this.locale = locale;
        this.dateOptions = {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        };
    }

    /**
     * Format date according to locale
     * @param {Date|string|number} date - Date to format
     * @param {string} format - 'short', 'medium', 'long', 'full'
     * @returns {string} Formatted date
     */
    formatDate(date, format = 'long') {
        const dateObj = new Date(date);

        const formats = {
            short: {
                year: '2-digit',
                month: '2-digit',
                day: '2-digit'
            },
            medium: {
                year: 'numeric',
                month: 'short',
                day: 'numeric'
            },
            long: {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            },
            full: {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                weekday: 'long'
            }
        };

        return new Intl.DateTimeFormat(this.locale, formats[format] || formats.long)
            .format(dateObj);
    }

    /**
     * Format time according to locale
     * @param {Date|string|number} date - Date to format time from
     * @param {string} format - '12h' or '24h'
     * @returns {string} Formatted time
     */
    formatTime(date, format = 'auto') {
        const dateObj = new Date(date);

        const use12Hour = format === '12h' ||
                         (format === 'auto' && ['en-US', 'en-AU', 'pt-BR'].includes(this.locale));

        const options = {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: use12Hour
        };

        return new Intl.DateTimeFormat(this.locale, options).format(dateObj);
    }

    /**
     * Format date and time together
     * @param {Date|string|number} date - Date to format
     * @returns {string} Formatted date and time
     */
    formatDateTime(date) {
        const dateObj = new Date(date);

        const options = {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: ['en-US', 'en-AU', 'pt-BR'].includes(this.locale)
        };

        return new Intl.DateTimeFormat(this.locale, options).format(dateObj);
    }

    /**
     * Format number according to locale
     * @param {number} number - Number to format
     * @param {number} decimals - Number of decimal places
     * @returns {string} Formatted number
     */
    formatNumber(number, decimals = 2) {
        const options = {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals,
            useGrouping: true
        };

        return new Intl.NumberFormat(this.locale, options).format(number);
    }

    /**
     * Format as currency
     * @param {number} amount - Amount to format
     * @param {string} currency - ISO 4217 currency code (e.g., 'USD', 'EUR')
     * @returns {string} Formatted currency
     */
    formatCurrency(amount, currency = 'USD') {
        const options = {
            style: 'currency',
            currency: currency,
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        };

        return new Intl.NumberFormat(this.locale, options).format(amount);
    }

    /**
     * Format as percentage
     * @param {number} value - Value as decimal (e.g., 0.75 for 75%)
     * @param {number} decimals - Number of decimal places
     * @returns {string} Formatted percentage
     */
    formatPercent(value, decimals = 2) {
        const options = {
            style: 'percent',
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        };

        return new Intl.NumberFormat(this.locale, options).format(value);
    }

    /**
     * Format file size (bytes to human-readable)
     * @param {number} bytes - File size in bytes
     * @returns {string} Human-readable file size
     */
    formatFileSize(bytes) {
        const units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB'];
        let size = bytes;
        let unitIndex = 0;

        while (size >= 1024 && unitIndex < units.length - 1) {
            size /= 1024;
            unitIndex++;
        }

        const number = size.toFixed(2);
        const unit = units[unitIndex];
        return `${this.formatNumber(parseFloat(number), 2)} ${unit}`;
    }

    /**
     * Format relative time (e.g., "2 hours ago")
     * @param {Date|number} date - Past or future date
     * @returns {string} Relative time string
     */
    formatRelativeTime(date) {
        const now = new Date();
        const dateObj = new Date(date);
        const diffMs = now - dateObj;
        const diffSeconds = Math.floor(diffMs / 1000);

        if (diffSeconds < 60) {
            return new Intl.RelativeTimeFormat(this.locale).format(-diffSeconds, 'second');
        }

        const diffMinutes = Math.floor(diffSeconds / 60);
        if (diffMinutes < 60) {
            return new Intl.RelativeTimeFormat(this.locale).format(-diffMinutes, 'minute');
        }

        const diffHours = Math.floor(diffMinutes / 60);
        if (diffHours < 24) {
            return new Intl.RelativeTimeFormat(this.locale).format(-diffHours, 'hour');
        }

        const diffDays = Math.floor(diffHours / 24);
        if (diffDays < 7) {
            return new Intl.RelativeTimeFormat(this.locale).format(-diffDays, 'day');
        }

        const diffWeeks = Math.floor(diffDays / 7);
        return new Intl.RelativeTimeFormat(this.locale).format(-diffWeeks, 'week');
    }

    /**
     * Format phone number (basic examples for common locales)
     * @param {string} phoneNumber - Phone number string (digits only)
     * @returns {string} Formatted phone number
     */
    formatPhoneNumber(phoneNumber) {
        const digits = phoneNumber.replace(/\D/g, '');

        const formats = {
            'en-US': (n) => `(${n.slice(0, 3)}) ${n.slice(3, 6)}-${n.slice(6)}`,
            'en-GB': (n) => `+44 ${n.slice(1, 5)} ${n.slice(5)}`,
            'de-DE': (n) => `+49 ${n.slice(1, 3)} ${n.slice(3)}`,
            'fr-FR': (n) => `+33 ${n.slice(1)} `,
            'ja-JP': (n) => `+81 ${n.slice(1, 3)}-${n.slice(3, 7)}-${n.slice(7)}`,
            'es-ES': (n) => `+34 ${n.slice(0, 3)} ${n.slice(3)}`,
        };

        const formatter = formats[this.locale] || ((n) => n);
        return formatter(digits);
    }

    /**
     * Get locale-specific decimal separator
     * @returns {string} Decimal separator
     */
    getDecimalSeparator() {
        const parts = new Intl.NumberFormat(this.locale).formatToParts(1.1);
        return parts.find(p => p.type === 'decimal')?.value || '.';
    }

    /**
     * Get locale-specific thousands separator
     * @returns {string} Thousands separator
     */
    getThousandsSeparator() {
        const parts = new Intl.NumberFormat(this.locale).formatToParts(1111);
        return parts.find(p => p.type === 'group')?.value || ',';
    }

    /**
     * Get locale info for display
     * @returns {object} Locale information
     */
    getLocaleInfo() {
        const testDate = new Date(2024, 10, 19, 14, 30, 45);
        const testNumber = 1234567.89;

        return {
            locale: this.locale,
            formattedDate: this.formatDate(testDate, 'long'),
            formattedTime: this.formatTime(testDate),
            formattedNumber: this.formatNumber(testNumber),
            formattedCurrency: this.formatCurrency(testNumber, 'USD'),
            decimalSeparator: this.getDecimalSeparator(),
            thousandsSeparator: this.getThousandsSeparator(),
            uses12HourTime: ['en-US', 'en-AU', 'pt-BR'].includes(this.locale),
            weekStartDay: this.locale === 'en-US' ? 'Sunday' : 'Monday'
        };
    }
}

// CloudSync Pro Specific Formatter
class CloudSyncFormatter extends LocaleFormatter {
    /**
     * Format sync activity timestamp
     * @param {Date} date - Activity date
     * @returns {string} Formatted timestamp
     */
    formatSyncTimestamp(date) {
        const now = new Date();
        const diff = now - new Date(date);
        const diffMinutes = Math.floor(diff / 60000);

        if (diffMinutes < 60) {
            return this.formatRelativeTime(date);
        }
        return this.formatDateTime(date);
    }

    /**
     * Format storage quota information
     * @param {number} used - Used storage in bytes
     * @param {number} total - Total storage in bytes
     * @returns {string} Formatted storage info
     */
    formatStorageQuota(used, total) {
        const usedFormatted = this.formatFileSize(used);
        const totalFormatted = this.formatFileSize(total);
        const percentUsed = this.formatPercent(used / total, 1);

        return `${usedFormatted} of ${totalFormatted} (${percentUsed})`;
    }

    /**
     * Format transfer speed
     * @param {number} bytesPerSecond - Transfer speed in bytes/second
     * @returns {string} Formatted speed
     */
    formatTransferSpeed(bytesPerSecond) {
        const mbps = (bytesPerSecond * 8) / 1000000;

        if (mbps < 1) {
            const kbps = (bytesPerSecond * 8) / 1000;
            return `${this.formatNumber(kbps, 2)} Kbps`;
        }
        return `${this.formatNumber(mbps, 2)} Mbps`;
    }

    /**
     * Format estimated time remaining
     * @param {number} seconds - Seconds remaining
     * @returns {string} Formatted time
     */
    formatTimeRemaining(seconds) {
        if (seconds < 60) {
            return `${Math.round(seconds)}s`;
        }

        const minutes = Math.floor(seconds / 60);
        const secs = seconds % 60;

        if (minutes < 60) {
            return `${minutes}m ${Math.round(secs)}s`;
        }

        const hours = Math.floor(minutes / 60);
        const mins = minutes % 60;
        return `${hours}h ${mins}m`;
    }
}

// Export for use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { LocaleFormatter, CloudSyncFormatter };
}

// Example usage
if (typeof window !== 'undefined') {
    window.LocaleFormatter = LocaleFormatter;
    window.CloudSyncFormatter = CloudSyncFormatter;
}
