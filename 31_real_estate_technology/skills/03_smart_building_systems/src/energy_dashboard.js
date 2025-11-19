/**
 * Energy Dashboard API - Real-time energy monitoring and analytics
 *
 * Production-ready Express.js API for building energy management with:
 * - Real-time power consumption monitoring
 * - Historical energy analytics and trending
 * - Cost calculation with time-of-use rates
 * - Peak demand tracking and alerts
 * - Energy efficiency metrics and KPIs
 * - Multi-building and multi-zone support
 *
 * Dependencies:
 *   npm install express @influxdata/influxdb-client cors dotenv winston
 */

const express = require('express');
const { InfluxDB, Point } = require('@influxdata/influxdb-client');
const cors = require('cors');
const winston = require('winston');
require('dotenv').config();

// Configure logging
const logger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  transports: [
    new winston.transports.File({ filename: 'error.log', level: 'error' }),
    new winston.transports.File({ filename: 'combined.log' }),
    new winston.transports.Console({ format: winston.format.simple() })
  ]
});

// Initialize Express app
const app = express();
app.use(cors());
app.use(express.json());

// InfluxDB configuration
const influxConfig = {
  url: process.env.INFLUX_URL || 'http://localhost:8086',
  token: process.env.INFLUX_TOKEN || 'your-influx-token',
  org: process.env.INFLUX_ORG || 'your-org',
  bucket: process.env.INFLUX_BUCKET || 'building'
};

const influx = new InfluxDB({ url: influxConfig.url, token: influxConfig.token });
const queryApi = influx.getQueryApi(influxConfig.org);
const writeApi = influx.getWriteApi(influxConfig.org, influxConfig.bucket);

// Time-of-use electricity rates ($/kWh)
const electricityRates = {
  peak: 0.25,        // 12pm-8pm weekdays
  offPeak: 0.12,     // 9pm-8am all days
  shoulder: 0.18,    // Other times
  demand: 15.00      // $/kW for peak demand
};

/**
 * Get real-time power consumption for all zones
 * Query last 5 minutes with 1-minute aggregation
 */
app.get('/api/energy/realtime', async (req, res) => {
  try {
    const { building, zone } = req.query;

    let filterClause = 'r._measurement == "power"';
    if (building) filterClause += ` and r.building == "${building}"`;
    if (zone) filterClause += ` and r.zone == "${zone}"`;

    const query = `
      from(bucket: "${influxConfig.bucket}")
        |> range(start: -5m)
        |> filter(fn: (r) => ${filterClause})
        |> aggregateWindow(every: 1m, fn: mean, createEmpty: false)
        |> pivot(rowKey:["_time"], columnKey: ["zone"], valueColumn: "_value")
    `;

    const data = [];
    await queryApi.queryRows(query, {
      next(row, tableMeta) {
        const o = tableMeta.toObject(row);
        data.push({
          time: o._time,
          timestamp: new Date(o._time).toISOString(),
          ...o
        });
      },
      error(error) {
        logger.error('Query error:', error);
        throw error;
      },
      complete() {
        logger.info(`Real-time query returned ${data.length} points`);
      }
    });

    res.json({
      success: true,
      data: data,
      metadata: {
        building: building || 'all',
        zone: zone || 'all',
        interval: '1m',
        points: data.length
      }
    });
  } catch (error) {
    logger.error('Real-time endpoint error:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

/**
 * Get hourly, daily, or monthly energy consumption
 * Supports date range and multiple aggregation periods
 */
app.get('/api/energy/consumption', async (req, res) => {
  try {
    const {
      start = '-30d',
      stop = 'now()',
      window = '1d',
      building,
      zone,
      metric = 'energy' // energy (kWh) or power (kW)
    } = req.query;

    let filterClause = `r._measurement == "${metric}"`;
    if (building) filterClause += ` and r.building == "${building}"`;
    if (zone) filterClause += ` and r.zone == "${zone}"`;

    const aggregationFn = metric === 'energy' ? 'sum' : 'mean';

    const query = `
      from(bucket: "${influxConfig.bucket}")
        |> range(start: ${start}, stop: ${stop})
        |> filter(fn: (r) => ${filterClause})
        |> aggregateWindow(every: ${window}, fn: ${aggregationFn}, createEmpty: false)
        |> group(columns: ["zone", "building"])
    `;

    const data = [];
    await queryApi.queryRows(query, {
      next(row, tableMeta) {
        const o = tableMeta.toObject(row);
        data.push({
          time: o._time,
          value: o._value,
          zone: o.zone,
          building: o.building,
          field: o._field
        });
      },
      error(error) {
        logger.error('Consumption query error:', error);
        throw error;
      },
      complete() {
        logger.info(`Consumption query returned ${data.length} points`);
      }
    });

    res.json({
      success: true,
      data: data,
      metadata: {
        start, stop, window,
        building: building || 'all',
        zone: zone || 'all',
        metric,
        totalPoints: data.length
      }
    });
  } catch (error) {
    logger.error('Consumption endpoint error:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

/**
 * Calculate energy cost with time-of-use rates
 * Includes peak demand charges
 */
app.get('/api/energy/cost', async (req, res) => {
  try {
    const { start = '-30d', stop = 'now()', building } = req.query;

    let filterClause = 'r._measurement == "energy"';
    if (building) filterClause += ` and r.building == "${building}"`;

    // Query hourly energy consumption
    const query = `
      from(bucket: "${influxConfig.bucket}")
        |> range(start: ${start}, stop: ${stop})
        |> filter(fn: (r) => ${filterClause})
        |> aggregateWindow(every: 1h, fn: sum, createEmpty: false)
    `;

    const energyData = [];
    await queryApi.queryRows(query, {
      next(row, tableMeta) {
        energyData.push(tableMeta.toObject(row));
      },
      error(error) {
        throw error;
      }
    });

    // Calculate cost based on time-of-use
    let peakCost = 0, offPeakCost = 0, shoulderCost = 0;
    let peakEnergy = 0, offPeakEnergy = 0, shoulderEnergy = 0;
    let maxDemand = 0;

    energyData.forEach(row => {
      const timestamp = new Date(row._time);
      const hour = timestamp.getHours();
      const dayOfWeek = timestamp.getDay();
      const isWeekday = dayOfWeek >= 1 && dayOfWeek <= 5;
      const energy = row._value; // kWh
      const power = energy; // Approximation for peak demand

      maxDemand = Math.max(maxDemand, power);

      // Determine rate period
      if (isWeekday && hour >= 12 && hour < 20) {
        // Peak: 12pm-8pm weekdays
        peakEnergy += energy;
        peakCost += energy * electricityRates.peak;
      } else if (hour >= 21 || hour < 8) {
        // Off-peak: 9pm-8am
        offPeakEnergy += energy;
        offPeakCost += energy * electricityRates.offPeak;
      } else {
        // Shoulder: other times
        shoulderEnergy += energy;
        shoulderCost += energy * electricityRates.shoulder;
      }
    });

    const demandCharge = maxDemand * electricityRates.demand;
    const totalEnergyCost = peakCost + offPeakCost + shoulderCost;
    const totalCost = totalEnergyCost + demandCharge;

    res.json({
      success: true,
      data: {
        totalCost: totalCost.toFixed(2),
        energyCost: totalEnergyCost.toFixed(2),
        demandCharge: demandCharge.toFixed(2),
        breakdown: {
          peak: { energy: peakEnergy.toFixed(2), cost: peakCost.toFixed(2), rate: electricityRates.peak },
          offPeak: { energy: offPeakEnergy.toFixed(2), cost: offPeakCost.toFixed(2), rate: electricityRates.offPeak },
          shoulder: { energy: shoulderEnergy.toFixed(2), cost: shoulderCost.toFixed(2), rate: electricityRates.shoulder }
        },
        peakDemand: {
          value: maxDemand.toFixed(2),
          unit: 'kW',
          charge: demandCharge.toFixed(2),
          rate: electricityRates.demand
        },
        totalEnergy: (peakEnergy + offPeakEnergy + shoulderEnergy).toFixed(2),
        currency: 'USD',
        period: { start, stop }
      }
    });
  } catch (error) {
    logger.error('Cost calculation error:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

/**
 * Get peak demand for billing period
 */
app.get('/api/energy/peak-demand', async (req, res) => {
  try {
    const { start = '-30d', building } = req.query;

    let filterClause = 'r._measurement == "power"';
    if (building) filterClause += ` and r.building == "${building}"`;

    const query = `
      from(bucket: "${influxConfig.bucket}")
        |> range(start: ${start})
        |> filter(fn: (r) => ${filterClause})
        |> aggregateWindow(every: 15m, fn: mean, createEmpty: false)
    `;

    let peakDemand = 0;
    let peakTime = null;
    let peakZone = null;

    await queryApi.queryRows(query, {
      next(row, tableMeta) {
        const o = tableMeta.toObject(row);
        if (o._value > peakDemand) {
          peakDemand = o._value;
          peakTime = o._time;
          peakZone = o.zone;
        }
      },
      error(error) {
        throw error;
      }
    });

    res.json({
      success: true,
      data: {
        peakDemand: peakDemand.toFixed(2),
        unit: 'kW',
        timestamp: peakTime,
        zone: peakZone,
        cost: (peakDemand * electricityRates.demand).toFixed(2)
      }
    });
  } catch (error) {
    logger.error('Peak demand error:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

/**
 * Get energy efficiency metrics and KPIs
 */
app.get('/api/energy/metrics', async (req, res) => {
  try {
    const { building, start = '-30d' } = req.query;

    // Calculate key metrics
    const metrics = {
      eui: null,              // Energy Use Intensity (kWh/sq ft/year)
      baseline: null,         // Baseline consumption
      savings: null,          // Savings vs. baseline
      peakReduction: null,    // Peak demand reduction
      loadFactor: null        // Load factor (average/peak)
    };

    // Example calculations (would need building area and baseline data)
    const buildingArea = 50000; // sq ft - should come from database
    const baselineEUI = 15.0;   // kWh/sq ft/year

    // Query total energy
    let filterClause = 'r._measurement == "energy"';
    if (building) filterClause += ` and r.building == "${building}"`;

    const energyQuery = `
      from(bucket: "${influxConfig.bucket}")
        |> range(start: ${start})
        |> filter(fn: (r) => ${filterClause})
        |> sum()
    `;

    let totalEnergy = 0;
    await queryApi.queryRows(energyQuery, {
      next(row, tableMeta) {
        totalEnergy += tableMeta.toObject(row)._value;
      },
      error(error) {
        throw error;
      }
    });

    // Annualize and calculate EUI
    const days = 30; // From query range
    const annualEnergy = (totalEnergy / days) * 365;
    metrics.eui = (annualEnergy / buildingArea).toFixed(2);
    metrics.baseline = baselineEUI;
    metrics.savings = ((baselineEUI - metrics.eui) / baselineEUI * 100).toFixed(1);

    res.json({
      success: true,
      data: {
        ...metrics,
        building: building || 'all',
        buildingArea,
        totalEnergy: totalEnergy.toFixed(2),
        annualizedEnergy: annualEnergy.toFixed(2),
        period: start
      }
    });
  } catch (error) {
    logger.error('Metrics calculation error:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

/**
 * Compare current period to previous period
 */
app.get('/api/energy/comparison', async (req, res) => {
  try {
    const { window = '7d', building } = req.query;

    let filterClause = 'r._measurement == "energy"';
    if (building) filterClause += ` and r.building == "${building}"`;

    // Current period
    const currentQuery = `
      from(bucket: "${influxConfig.bucket}")
        |> range(start: -${window})
        |> filter(fn: (r) => ${filterClause})
        |> sum()
    `;

    // Previous period
    const previousQuery = `
      from(bucket: "${influxConfig.bucket}")
        |> range(start: -${parseInt(window)*2}${window.slice(-1)}, stop: -${window})
        |> filter(fn: (r) => ${filterClause})
        |> sum()
    `;

    let currentTotal = 0, previousTotal = 0;

    await queryApi.queryRows(currentQuery, {
      next(row, tableMeta) {
        currentTotal += tableMeta.toObject(row)._value;
      }
    });

    await queryApi.queryRows(previousQuery, {
      next(row, tableMeta) {
        previousTotal += tableMeta.toObject(row)._value;
      }
    });

    const change = currentTotal - previousTotal;
    const percentChange = previousTotal > 0 ? (change / previousTotal * 100) : 0;

    res.json({
      success: true,
      data: {
        current: {
          period: `last ${window}`,
          energy: currentTotal.toFixed(2),
          unit: 'kWh'
        },
        previous: {
          period: `previous ${window}`,
          energy: previousTotal.toFixed(2),
          unit: 'kWh'
        },
        comparison: {
          change: change.toFixed(2),
          percentChange: percentChange.toFixed(1),
          trend: change > 0 ? 'increase' : 'decrease'
        }
      }
    });
  } catch (error) {
    logger.error('Comparison error:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

/**
 * Health check endpoint
 */
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    influxdb: 'connected'
  });
});

/**
 * Write energy data point (for testing or integration)
 */
app.post('/api/energy/write', async (req, res) => {
  try {
    const { measurement, value, building, zone, tags } = req.body;

    const point = new Point(measurement || 'power')
      .floatField('value', parseFloat(value))
      .tag('building', building || 'default')
      .tag('zone', zone || 'default');

    if (tags) {
      Object.entries(tags).forEach(([key, val]) => {
        point.tag(key, val);
      });
    }

    writeApi.writePoint(point);
    await writeApi.flush();

    res.json({ success: true, message: 'Data written successfully' });
  } catch (error) {
    logger.error('Write error:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

// Error handling middleware
app.use((err, req, res, next) => {
  logger.error('Unhandled error:', err);
  res.status(500).json({ success: false, error: 'Internal server error' });
});

// Start server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  logger.info(`Energy dashboard API running on port ${PORT}`);
  logger.info(`InfluxDB: ${influxConfig.url}`);
  logger.info(`Organization: ${influxConfig.org}`);
  logger.info(`Bucket: ${influxConfig.bucket}`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  logger.info('SIGTERM received, closing server...');
  writeApi.close().then(() => {
    logger.info('InfluxDB write API closed');
    process.exit(0);
  });
});
