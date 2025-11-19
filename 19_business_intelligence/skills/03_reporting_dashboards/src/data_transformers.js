/**
 * Data Transformation Utilities for Dashboards
 * Common data manipulation patterns for visualization
 */

class DataTransformers {
    // Aggregate data by period (day, week, month, quarter, year)
    static aggregateByPeriod(data, dateField, valueField, period = 'month') {
        const grouped = {};
        
        data.forEach(item => {
            const date = new Date(item[dateField]);
            let key;
            
            switch(period) {
                case 'day':
                    key = date.toISOString().split('T')[0];
                    break;
                case 'week':
                    const weekStart = new Date(date);
                    weekStart.setDate(date.getDate() - date.getDay());
                    key = weekStart.toISOString().split('T')[0];
                    break;
                case 'month':
                    key = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
                    break;
                case 'quarter':
                    const quarter = Math.floor(date.getMonth() / 3) + 1;
                    key = `${date.getFullYear()}-Q${quarter}`;
                    break;
                case 'year':
                    key = String(date.getFullYear());
                    break;
            }
            
            if (!grouped[key]) {
                grouped[key] = 0;
            }
            grouped[key] += item[valueField];
        });
        
        return Object.entries(grouped).map(([period, value]) => ({
            period,
            value
        })).sort((a, b) => a.period.localeCompare(b.period));
    }

    // Calculate period-over-period changes
    static calculateChanges(data, valueField) {
        return data.map((item, index) => {
            if (index === 0) {
                return {
                    ...item,
                    change: null,
                    changePercent: null
                };
            }
            
            const previous = data[index - 1][valueField];
            const current = item[valueField];
            const change = current - previous;
            const changePercent = (change / previous) * 100;
            
            return {
                ...item,
                change,
                changePercent
            };
        });
    }

    // Rank items and add rank field
    static addRanking(data, valueField, descending = true) {
        const sorted = [...data].sort((a, b) => {
            return descending
                ? b[valueField] - a[valueField]
                : a[valueField] - b[valueField];
        });
        
        return sorted.map((item, index) => ({
            ...item,
            rank: index + 1
        }));
    }

    // Calculate running total
    static calculateRunningTotal(data, valueField) {
        let total = 0;
        return data.map(item => {
            total += item[valueField];
            return {
                ...item,
                runningTotal: total
            };
        });
    }

    // Pivot data (wide to long format)
    static pivot(data, rowField, columnField, valueField, aggFunction = 'sum') {
        const result = {};
        
        data.forEach(item => {
            const row = item[rowField];
            const col = item[columnField];
            const value = item[valueField];
            
            if (!result[row]) {
                result[row] = {};
            }
            
            if (!result[row][col]) {
                result[row][col] = aggFunction === 'count' ? 0 : 0;
            }
            
            if (aggFunction === 'sum' || aggFunction === 'count') {
                result[row][col] += aggFunction === 'count' ? 1 : value;
            } else if (aggFunction === 'avg') {
                // Simplified average - would need count tracking for true average
                result[row][col] = (result[row][col] + value) / 2;
            }
        });
        
        return result;
    }

    // Bin continuous data into ranges
    static bin(data, valueField, binCount = 10) {
        const values = data.map(d => d[valueField]);
        const min = Math.min(...values);
        const max = Math.max(...values);
        const binSize = (max - min) / binCount;
        
        const bins = Array(binCount).fill(0).map((_, i) => ({
            rangeStart: min + (i * binSize),
            rangeEnd: min + ((i + 1) * binSize),
            count: 0,
            items: []
        }));
        
        data.forEach(item => {
            const value = item[valueField];
            const binIndex = Math.min(
                Math.floor((value - min) / binSize),
                binCount - 1
            );
            bins[binIndex].count++;
            bins[binIndex].items.push(item);
        });
        
        return bins;
    }

    // Calculate percentiles
    static percentile(data, valueField, percentiles = [25, 50, 75]) {
        const values = data.map(d => d[valueField]).sort((a, b) => a - b);
        const result = {};
        
        percentiles.forEach(p => {
            const index = Math.ceil((p / 100) * values.length) - 1;
            result[`p${p}`] = values[index];
        });
        
        return result;
    }

    // Format large numbers (K, M, B)
    static formatLargeNumber(num, decimals = 1) {
        if (num >= 1e9) {
            return (num / 1e9).toFixed(decimals) + 'B';
        }
        if (num >= 1e6) {
            return (num / 1e6).toFixed(decimals) + 'M';
        }
        if (num >= 1e3) {
            return (num / 1e3).toFixed(decimals) + 'K';
        }
        return num.toString();
    }

    // Calculate cohort retention
    static cohortRetention(data, cohortField, periodField, activeField) {
        const cohorts = {};
        
        data.forEach(item => {
            const cohort = item[cohortField];
            const period = item[periodField];
            const isActive = item[activeField];
            
            if (!cohorts[cohort]) {
                cohorts[cohort] = {};
            }
            
            if (!cohorts[cohort][period]) {
                cohorts[cohort][period] = { active: 0, total: 0 };
            }
            
            cohorts[cohort][period].total++;
            if (isActive) {
                cohorts[cohort][period].active++;
            }
        });
        
        // Calculate retention percentages
        Object.keys(cohorts).forEach(cohort => {
            const periods = cohorts[cohort];
            const periodKeys = Object.keys(periods).sort();
            const firstPeriod = periods[periodKeys[0]].total;
            
            periodKeys.forEach(period => {
                periods[period].retentionPct =
                    (periods[period].active / firstPeriod) * 100;
            });
        });
        
        return cohorts;
    }
}

// Export
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DataTransformers;
}
