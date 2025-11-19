/**
 * Energy Dashboard - Real-time energy monitoring
 */
const express = require('express');
const { InfluxDB } = require('@influxdata/influxdb-client');

const app = express();
const influx = new InfluxDB({ url: 'http://localhost:8086', token: 'your-token' });
const queryApi = influx.getQueryApi('your-org');

// Get real-time power consumption
app.get('/api/energy/realtime', async (req, res) => {
  const query = `
    from(bucket: "building")
      |> range(start: -5m)
      |> filter(fn: (r) => r._measurement == "power")
      |> aggregateWindow(every: 1m, fn: mean)
  `;
  
  const data = [];
  const result = await queryApi.collectRows(query);
  
  result.forEach(row => {
    data.push({
      time: row._time,
      power: row._value,
      zone: row.zone
    });
  });
  
  res.json(data);
});

// Get daily energy consumption
app.get('/api/energy/daily', async (req, res) => {
  const query = `
    from(bucket: "building")
      |> range(start: -30d)
      |> filter(fn: (r) => r._measurement == "energy")
      |> aggregateWindow(every: 1d, fn: sum)
  `;
  
  const data = await queryApi.collectRows(query);
  res.json(data);
});

// Calculate cost
app.get('/api/energy/cost', async (req, res) => {
  const rate = 0.12; // $/kWh
  const query = `...`;
  const energy = await queryApi.collectRows(query);
  
  const cost = energy.reduce((sum, row) => sum + (row._value * rate), 0);
  res.json({ cost, currency: 'USD' });
});

app.listen(3000, () => console.log('Energy dashboard running on port 3000'));
