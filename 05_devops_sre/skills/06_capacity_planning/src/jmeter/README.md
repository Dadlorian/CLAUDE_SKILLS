# JMeter Test Plans

This directory contains Apache JMeter test plans for load testing.

## Available Test Plans

### 1. basic-load-test.jmx
Basic API load test with 100 concurrent users over 10 minutes.

## Running Tests

### GUI Mode (for test development)
```bash
jmeter -t basic-load-test.jmx
```

### CLI Mode (for actual load testing)
```bash
jmeter -n -t basic-load-test.jmx -l results.jtl -e -o report/
```

Parameters:
- `-n`: Non-GUI mode
- `-t`: Test plan file
- `-l`: Results log file
- `-e`: Generate report dashboard
- `-o`: Output folder for report

### With Custom Properties
```bash
jmeter -n -t basic-load-test.jmx \
  -JBASE_URL=https://api.example.com \
  -l results.jtl \
  -e -o report/
```

### Distributed Testing

Start JMeter server on remote machines:
```bash
jmeter-server
```

Run test from master:
```bash
jmeter -n -t basic-load-test.jmx \
  -R server1,server2,server3 \
  -l results.jtl
```

## Viewing Results

### Generate HTML Report from Existing Results
```bash
jmeter -g results.jtl -o report/
```

### Open Report
Open `report/index.html` in your browser.

## Best Practices

1. Always run load tests in CLI mode (not GUI)
2. Use distributed mode for high load
3. Monitor system resources during tests
4. Save results in CSV/JTL format for analysis
5. Generate HTML reports for visualization

## JMeter Plugins

Install useful plugins via JMeter Plugins Manager:
- Custom Thread Groups
- Throughput Shaping Timer
- PerfMon (Server Monitoring)
- Backend Listener (InfluxDB, Graphite)
