# Real-Time Analytics Systems Subskill

## Overview

This subskill provides comprehensive knowledge and practical examples for building and operating real-time analytics systems using modern streaming technologies.

## Contents

### 1. skill.md
Master skill document covering:
- Core competencies in real-time analytics
- Technology stack overview
- Learning path from foundation to expert
- Best practices and common challenges
- Key metrics and use cases

### 2. reference/ (14 files)
Comprehensive reference documentation:
- **streaming_architectures_comparison.md** - Lambda, Kappa, and unified approaches
- **clickhouse_guide.md** - Complete ClickHouse reference
- **druid_overview.md** - Apache Druid architecture and features
- **pinot_features.md** - Apache Pinot capabilities
- **kafka_patterns.md** - Design patterns for Kafka-based systems
- **realtime_olap_comparison.md** - Database comparison matrix
- **latency_requirements.md** - Latency measurement and optimization
- **flink_architecture.md** - Apache Flink concepts and patterns
- **spark_streaming_guide.md** - Spark Structured Streaming
- **data_quality_streaming.md** - Quality assurance in streams
- **schema_management.md** - Schema evolution and registry
- **state_management_patterns.md** - Stateful processing patterns
- **monitoring_observability.md** - Metrics, logging, and tracing
- **performance_tuning.md** - Optimization across the stack

### 3. guides/ (14 files)
Step-by-step implementation guides:
- **lambda_architecture_impl.md** - Build Lambda architecture
- **kappa_architecture_impl.md** - Build Kappa architecture
- **clickhouse_realtime_setup.md** - ClickHouse deployment
- **druid_deployment.md** - Druid cluster setup
- **streaming_ingestion_pipeline.md** - End-to-end ingestion
- **flink_stateful_processing.md** - Stateful Flink jobs
- **real_time_dashboards.md** - WebSocket dashboards
- **event_stream_analytics.md** - Event analytics patterns
- **kafka_streams_application.md** - Kafka Streams apps
- **spark_streaming_pipeline.md** - Spark streaming jobs
- **real_time_joins.md** - Stream join implementations
- **windowing_aggregations.md** - Window functions
- **stream_to_warehouse_sync.md** - CDC and sync patterns
- **monitoring_alerting_setup.md** - Observability setup

### 4. src/ (25 files)
Production-ready code examples:

#### Python (9 files)
- kafka_producer.py - Kafka event producer
- kafka_consumer.py - Kafka consumer with error handling
- realtime_dashboard_api.py - Flask API for dashboards
- event_validator.py - Event validation logic
- schema_registry_client.py - Avro serialization
- stream_processor.py - PyFlink streaming job
- session_analytics.py - Session analytics with Spark
- cdc_processor.py - Change data capture
- metrics_collector.py - Prometheus metrics

#### Java (8 files)
- flink_streaming_job.java - Main Flink application
- flink_aggregator.java - Custom aggregation functions
- clickhouse_sink.java - ClickHouse sink connector
- deduplication.java - Event deduplication
- windowing_example.java - Window operations
- kafka_streams_app.java - Kafka Streams topology
- state_management.java - Stateful processing

#### Scala (2 files)
- spark_streaming_job.scala - Spark Structured Streaming

#### JavaScript (1 file)
- websocket_updates.js - Real-time WebSocket server

#### Configuration (5 files)
- clickhouse_schema.sql - Database schema
- druid_ingestion_spec.json - Druid ingestion config
- alerting_rules.yaml - Prometheus alerts
- docker_compose.yaml - Local development stack
- kubernetes_deployment.yaml - K8s deployment
- monitoring_dashboard.json - Grafana dashboard
- sql_queries.sql - Sample analytics queries

## Technology Coverage

### Stream Processing
- Apache Flink
- Apache Spark Streaming
- Kafka Streams
- PyFlink

### Message Brokers
- Apache Kafka
- Schema Registry
- Kafka Connect

### Real-Time OLAP
- ClickHouse
- Apache Druid
- Apache Pinot

### Monitoring
- Prometheus
- Grafana
- Distributed tracing

### Deployment
- Docker Compose
- Kubernetes
- Cloud platforms

## Learning Path

### Beginner
1. Read skill.md for overview
2. Study streaming_architectures_comparison.md
3. Follow clickhouse_realtime_setup.md
4. Run docker_compose.yaml examples
5. Explore kafka_producer.py and kafka_consumer.py

### Intermediate
1. Study kafka_patterns.md
2. Build lambda_architecture_impl.md
3. Implement flink_streaming_job.java
4. Setup monitoring with metrics_collector.py
5. Create real_time_dashboards.md

### Advanced
1. Compare systems in realtime_olap_comparison.md
2. Optimize with performance_tuning.md
3. Implement state_management patterns
4. Build production deployment with kubernetes
5. Master data_quality_streaming.md

## Quick Start

### 1. Start Local Environment
```bash
cd src/
docker-compose up -d
```

### 2. Create ClickHouse Tables
```bash
clickhouse-client --host localhost < clickhouse_schema.sql
```

### 3. Send Test Events
```bash
python kafka_producer.py
```

### 4. Start Processing
```bash
python stream_processor.py
```

### 5. View Dashboard
```bash
python realtime_dashboard_api.py
# Open http://localhost:5000/api/stats/realtime
```

## Best Practices

1. **Start Simple**: Begin with Kappa if possible
2. **Monitor Everything**: Use provided metrics examples
3. **Test at Scale**: Validate with production data volumes
4. **Plan for Failures**: Implement error handling early
5. **Schema Management**: Use Schema Registry from day one
6. **State Management**: Choose appropriate backend
7. **Optimize Iteratively**: Measure before optimizing

## Common Use Cases

- **Product Analytics**: User behavior, funnels, cohorts
- **Operational Monitoring**: Logs, metrics, traces
- **Business Metrics**: Sales, inventory, KPIs
- **IoT Analytics**: Sensor data, device telemetry
- **Fraud Detection**: Real-time anomaly detection
- **Recommendation Systems**: Personalization engines

## Resources

- Apache Kafka documentation
- Flink training materials
- ClickHouse documentation
- Confluent resources
- "Streaming Systems" by Tyler Akidau
- "Designing Data-Intensive Applications" by Martin Kleppmann

## Contributing

This subskill is maintained as part of the CLAUDE_SKILLS repository. Contributions welcome for:
- New code examples
- Updated configurations
- Performance benchmarks
- Real-world case studies

## License

Apache 2.0 (matching parent repository)
