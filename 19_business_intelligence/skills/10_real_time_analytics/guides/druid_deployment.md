# Apache Druid Deployment Guide

## Architecture Components

- **Coordinator**: Manages data availability
- **Overlord**: Manages ingestion tasks
- **Broker**: Routes queries
- **Historical**: Serves historical segments
- **MiddleManager**: Executes ingestion tasks

## Docker Compose Setup

```yaml
version: '3'
services:
  postgres:
    image: postgres:13
    environment:
      POSTGRES_PASSWORD: druid
      POSTGRES_USER: druid
      POSTGRES_DB: druid

  zookeeper:
    image: zookeeper:3.7
    
  coordinator:
    image: apache/druid:27.0.0
    command: coordinator
    environment:
      - druid_metadata_storage_type=postgresql
      - druid_metadata_storage_connector_connectURI=jdbc:postgresql://postgres:5432/druid
    depends_on:
      - postgres
      - zookeeper

  broker:
    image: apache/druid:27.0.0
    command: broker
    ports:
      - "8082:8082"

  historical:
    image: apache/druid:27.0.0
    command: historical
    
  middlemanager:
    image: apache/druid:27.0.0
    command: middleManager

  router:
    image: apache/druid:27.0.0
    command: router
    ports:
      - "8888:8888"
```

## Kafka Ingestion Spec

```json
{
  "type": "kafka",
  "spec": {
    "dataSchema": {
      "dataSource": "events",
      "timestampSpec": {
        "column": "timestamp",
        "format": "millis"
      },
      "dimensionsSpec": {
        "dimensions": [
          "user_id",
          "event_type",
          "country",
          {"name": "device_type", "type": "string"}
        ]
      },
      "metricsSpec": [
        {"type": "count", "name": "count"},
        {"type": "longSum", "name": "revenue", "fieldName": "revenue"},
        {"type": "hyperUnique", "name": "unique_users", "fieldName": "user_id"}
      ],
      "granularitySpec": {
        "type": "uniform",
        "segmentGranularity": "HOUR",
        "queryGranularity": "MINUTE",
        "rollup": true
      }
    },
    "ioConfig": {
      "topic": "events",
      "consumerProperties": {
        "bootstrap.servers": "kafka:9092"
      },
      "taskCount": 4,
      "replicas": 2,
      "taskDuration": "PT1H"
    },
    "tuningConfig": {
      "type": "kafka",
      "maxRowsPerSegment": 5000000
    }
  }
}
```

## Best Practices

1. Set appropriate segment granularity
2. Enable rollup for better performance
3. Use approximate aggregations
4. Monitor segment count
5. Configure retention rules
