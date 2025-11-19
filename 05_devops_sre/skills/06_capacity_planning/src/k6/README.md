# k6 Load Test Scripts

This directory contains k6 load testing scripts for capacity planning.

## Available Tests

### 1. smoke-test.js
Minimal load test to verify system works with minimal load.
```bash
k6 run smoke-test.js
```

### 2. load-test.js
Standard load test with gradual ramp-up to expected load levels.
```bash
k6 run load-test.js
# Or with custom base URL
k6 run --env BASE_URL=https://api.example.com load-test.js
```

### 3. stress-test.js
Find the breaking point of the system by gradually increasing load.
```bash
k6 run stress-test.js
```

### 4. spike-test.js
Test sudden traffic spikes to validate autoscaling response.
```bash
k6 run spike-test.js
```

## Running Tests

### Basic Execution
```bash
k6 run <test-file>.js
```

### With InfluxDB Output
```bash
k6 run --out influxdb=http://localhost:8086/k6 load-test.js
```

### With JSON Output
```bash
k6 run --out json=results.json load-test.js
```

### With Environment Variables
```bash
k6 run --env BASE_URL=https://api.example.com load-test.js
```

### Docker Execution
```bash
docker run -i grafana/k6:latest run - <load-test.js
```

## Analyzing Results

Results are saved in JSON format and can be analyzed with:
- Grafana + InfluxDB for real-time monitoring
- k6 Cloud for detailed analysis
- Custom scripts for specific metrics
