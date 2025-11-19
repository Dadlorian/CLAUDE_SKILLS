# Kafka Design Patterns for Real-Time Analytics

## Overview

This document covers essential Apache Kafka patterns for building real-time analytics systems, including streaming patterns, integration strategies, and best practices.

## Core Concepts

### Topics and Partitions

```
Topic: user_events
├── Partition 0: [e1, e4, e7, e10, ...]
├── Partition 1: [e2, e5, e8, e11, ...]
├── Partition 2: [e3, e6, e9, e12, ...]
└── Partition 3: [...]

Key-based partitioning ensures events for same user go to same partition
```

### Consumer Groups

```
Topic: events (3 partitions)
Consumer Group: analytics_processors
├── Consumer 1: Reads Partition 0
├── Consumer 2: Reads Partition 1
└── Consumer 3: Reads Partition 2

Parallelism = min(partitions, consumers in group)
```

## Streaming Patterns

### 1. Event Sourcing

**Pattern:** Store all state changes as immutable events

```java
// Event structure
public class UserEvent {
    private String userId;
    private EventType type;
    private long timestamp;
    private Map<String, Object> payload;
}

// Producer
public void publishEvent(UserEvent event) {
    ProducerRecord<String, UserEvent> record = new ProducerRecord<>(
        "user_events",
        event.getUserId(),  // Key for partitioning
        event
    );
    producer.send(record);
}

// Consumer rebuilds state
public UserState rebuildState(String userId) {
    consumer.subscribe("user_events");
    UserState state = new UserState();

    while (true) {
        ConsumerRecords<String, UserEvent> records = consumer.poll(Duration.ofMillis(100));
        for (ConsumerRecord<String, UserEvent> record : records) {
            if (record.key().equals(userId)) {
                state.apply(record.value());
            }
        }
    }
    return state;
}
```

**Use Cases:**
- Audit trails
- Time travel debugging
- Event replay for analytics
- Compliance and regulatory requirements

### 2. Change Data Capture (CDC)

**Pattern:** Stream database changes to Kafka

```json
{
  "name": "mysql-cdc-connector",
  "config": {
    "connector.class": "io.debezium.connector.mysql.MySqlConnector",
    "database.hostname": "localhost",
    "database.port": "3306",
    "database.user": "debezium",
    "database.password": "dbz",
    "database.server.id": "184054",
    "database.server.name": "production",
    "table.include.list": "ecommerce.orders,ecommerce.products",
    "database.history.kafka.bootstrap.servers": "kafka:9092",
    "database.history.kafka.topic": "schema-changes"
  }
}
```

**Event Structure:**
```json
{
  "before": {
    "id": 123,
    "status": "pending",
    "total": 99.99
  },
  "after": {
    "id": 123,
    "status": "completed",
    "total": 99.99,
    "completed_at": "2025-01-15T10:30:00Z"
  },
  "op": "u",
  "ts_ms": 1642246200000
}
```

**Use Cases:**
- Real-time data warehouse sync
- Materialized view updates
- Cross-system data synchronization
- Microservices data integration

### 3. CQRS (Command Query Responsibility Segregation)

**Pattern:** Separate write and read models

```java
// Command side - writes to database
public class OrderCommandHandler {
    public void createOrder(CreateOrderCommand cmd) {
        Order order = new Order(cmd);
        orderRepository.save(order);

        // Publish event
        OrderCreatedEvent event = new OrderCreatedEvent(order);
        kafkaProducer.send("order_events", event);
    }
}

// Query side - updates from Kafka stream
@KafkaListener(topics = "order_events")
public class OrderQueryUpdater {
    public void handleOrderEvent(OrderCreatedEvent event) {
        // Update read-optimized view
        OrderView view = new OrderView(event);
        elasticsearch.index(view);  // or ClickHouse, Druid, etc.
    }
}
```

**Benefits:**
- Optimized read and write models
- Independent scaling
- Better performance for analytics queries

### 4. Event-Carried State Transfer

**Pattern:** Include full state in events (avoid lookups)

```java
// Instead of:
{
  "userId": "12345",
  "action": "purchase"
}

// Send complete state:
{
  "userId": "12345",
  "userName": "John Doe",
  "userTier": "premium",
  "userCountry": "US",
  "action": "purchase",
  "productId": "P789",
  "productName": "Widget Pro",
  "productCategory": "Electronics",
  "price": 99.99
}
```

**Trade-offs:**
- **Pro:** No downstream lookups needed, faster processing
- **Con:** Larger messages, potential staleness
- **When:** Dimensions don't change frequently

### 5. Outbox Pattern

**Pattern:** Ensure atomic database writes and event publishing

```sql
-- Transaction writes to both business table and outbox
BEGIN;
  INSERT INTO orders (id, user_id, total) VALUES (123, 456, 99.99);
  INSERT INTO outbox (event_type, payload)
    VALUES ('OrderCreated', '{"orderId": 123, "userId": 456, "total": 99.99}');
COMMIT;
```

```java
// Separate process polls outbox and publishes to Kafka
@Scheduled(fixedDelay = 1000)
public void publishOutboxEvents() {
    List<OutboxEvent> events = outboxRepository.findPendingEvents();
    for (OutboxEvent event : events) {
        kafkaProducer.send("orders", event.getPayload());
        outboxRepository.markPublished(event.getId());
    }
}
```

**Ensures:**
- At-least-once delivery
- No lost events
- Transactional consistency

### 6. Stream-Table Duality

**Pattern:** Treat streams as tables and vice versa

```java
// Stream to Table
KTable<String, UserProfile> userTable = builder
    .stream("user_events")
    .groupByKey()
    .aggregate(
        UserProfile::new,
        (key, event, profile) -> profile.apply(event),
        Materialized.as("user_profiles_store")
    );

// Table to Stream (changelog)
KStream<String, UserProfileChange> changeStream = userTable.toStream();
```

**Use Cases:**
- Maintaining local state in stream processors
- Joining streams with reference data
- Building materialized views

### 7. Join Patterns

#### Stream-Stream Join
```java
// Join page views with purchases within 5-minute window
KStream<String, PageView> pageViews = builder.stream("page_views");
KStream<String, Purchase> purchases = builder.stream("purchases");

KStream<String, Conversion> conversions = pageViews
    .join(
        purchases,
        (view, purchase) -> new Conversion(view, purchase),
        JoinWindows.ofTimeDifferenceWithNoGrace(Duration.ofMinutes(5)),
        StreamJoined.with(Serdes.String(), pageViewSerde, purchaseSerde)
    );
```

#### Stream-Table Join
```java
// Enrich events with user profile data
KStream<String, Event> events = builder.stream("events");
KTable<String, UserProfile> users = builder.table("user_profiles");

KStream<String, EnrichedEvent> enrichedEvents = events
    .join(
        users,
        (event, user) -> new EnrichedEvent(event, user),
        Joined.with(Serdes.String(), eventSerde, userSerde)
    );
```

#### Global Table Join
```java
// Join with reference data available to all partitions
GlobalKTable<String, Country> countries = builder.globalTable("countries");

KStream<String, EnrichedEvent> enriched = events
    .join(
        countries,
        (userId, event) -> event.getCountryCode(),
        (event, country) -> event.withCountry(country)
    );
```

### 8. Windowing Patterns

#### Tumbling Window
```java
// Non-overlapping fixed windows
KStream<String, Event> events = builder.stream("events");

KTable<Windowed<String>, Long> counts = events
    .groupByKey()
    .windowedBy(TimeWindows.ofSizeWithNoGrace(Duration.ofMinutes(5)))
    .count();

// Output: [00:00-00:05): 100, [00:05-00:10): 150, [00:10-00:15): 120
```

#### Hopping Window
```java
// Overlapping windows (5-min window, 1-min advance)
KTable<Windowed<String>, Long> counts = events
    .groupByKey()
    .windowedBy(TimeWindows
        .ofSizeWithNoGrace(Duration.ofMinutes(5))
        .advanceBy(Duration.ofMinutes(1)))
    .count();

// Output: [00:00-00:05), [00:01-00:06), [00:02-00:07), ...
```

#### Sliding Window
```java
// Window includes all events within time difference
KTable<Windowed<String>, Long> counts = events
    .groupByKey()
    .windowedBy(SlidingWindows
        .ofTimeDifferenceWithNoGrace(Duration.ofMinutes(5)))
    .count();
```

#### Session Window
```java
// Windows based on inactivity gaps
KTable<Windowed<String>, Long> sessionCounts = events
    .groupByKey()
    .windowedBy(SessionWindows
        .ofInactivityGapWithNoGrace(Duration.ofMinutes(30)))
    .count();

// User sessions: window closes after 30 minutes of inactivity
```

### 9. Aggregation Patterns

#### Simple Aggregation
```java
KTable<String, Long> userEventCounts = events
    .groupBy((key, event) -> event.getUserId())
    .count();
```

#### Complex Aggregation
```java
public class UserMetrics {
    private long eventCount;
    private double totalRevenue;
    private Set<String> uniqueSessions;

    public UserMetrics add(Event event) {
        this.eventCount++;
        this.totalRevenue += event.getRevenue();
        this.uniqueSessions.add(event.getSessionId());
        return this;
    }
}

KTable<String, UserMetrics> metrics = events
    .groupByKey()
    .aggregate(
        UserMetrics::new,
        (key, event, metrics) -> metrics.add(event),
        Materialized.with(Serdes.String(), userMetricsSerde)
    );
```

### 10. Deduplication Pattern

```java
// Using state store for deduplication
KStream<String, Event> dedupedEvents = events
    .transformValues(() -> new ValueTransformer<Event, Event>() {
        private KeyValueStore<String, Long> store;

        @Override
        public void init(ProcessorContext context) {
            this.store = context.getStateStore("dedup_store");
        }

        @Override
        public Event transform(Event event) {
            String eventId = event.getId();
            Long lastSeen = store.get(eventId);

            if (lastSeen == null) {
                store.put(eventId, System.currentTimeMillis());
                return event;
            }

            return null;  // Duplicate, filter out
        }
    }, "dedup_store");
```

## Integration Patterns

### 1. Kafka Connect

**Source Connector (Database to Kafka):**
```json
{
  "name": "postgres-source",
  "config": {
    "connector.class": "io.confluent.connect.jdbc.JdbcSourceConnector",
    "connection.url": "jdbc:postgresql://localhost/ecommerce",
    "mode": "timestamp+incrementing",
    "timestamp.column.name": "updated_at",
    "incrementing.column.name": "id",
    "topic.prefix": "postgres_",
    "poll.interval.ms": "1000"
  }
}
```

**Sink Connector (Kafka to Database):**
```json
{
  "name": "clickhouse-sink",
  "config": {
    "connector.class": "com.clickhouse.kafka.connect.ClickHouseSinkConnector",
    "topics": "events",
    "clickhouse.server.url": "jdbc:clickhouse://localhost:8123",
    "clickhouse.table.name": "events",
    "key.converter": "org.apache.kafka.connect.storage.StringConverter",
    "value.converter": "org.apache.kafka.connect.json.JsonConverter"
  }
}
```

### 2. Schema Registry Pattern

```java
// Producer with Avro schema
Properties props = new Properties();
props.put("schema.registry.url", "http://localhost:8081");

KafkaProducer<String, GenericRecord> producer = new KafkaProducer<>(
    props,
    new StringSerializer(),
    new KafkaAvroSerializer()
);

// Schema evolution - backward compatible
Schema schema = SchemaBuilder
    .record("UserEvent")
    .fields()
        .requiredString("userId")
        .requiredString("eventType")
        .optionalString("newField")  // Added field with default
    .endRecord();
```

### 3. Multi-Datacenter Replication

```properties
# MirrorMaker 2 configuration
clusters = source, target
source.bootstrap.servers = source-kafka:9092
target.bootstrap.servers = target-kafka:9092

source->target.enabled = true
source->target.topics = events, user_profiles

# Bidirectional replication
target->source.enabled = true
target->source.topics = events, user_profiles
```

## Performance Patterns

### 1. Batching

```java
// Producer batching
Properties props = new Properties();
props.put("batch.size", 16384);           // 16 KB
props.put("linger.ms", 10);               // Wait 10ms
props.put("compression.type", "snappy");  // Compress batches

// Consumer batching
props.put("max.poll.records", 500);       // Poll 500 records at a time
```

### 2. Partitioning Strategy

```java
// Custom partitioner for hot partition avoidance
public class PowerOfTwoPartitioner implements Partitioner {
    private final Random random = new Random();

    @Override
    public int partition(String topic, Object key, byte[] keyBytes,
                        Object value, byte[] valueBytes, Cluster cluster) {
        int numPartitions = cluster.partitionCountForTopic(topic);

        // Power of two choices for better distribution
        int p1 = random.nextInt(numPartitions);
        int p2 = random.nextInt(numPartitions);

        return getPartitionLoad(p1) < getPartitionLoad(p2) ? p1 : p2;
    }
}
```

### 3. Consumer Lag Monitoring

```java
public Map<TopicPartition, Long> getConsumerLag() {
    Map<TopicPartition, Long> lag = new HashMap<>();

    for (TopicPartition partition : consumer.assignment()) {
        long currentPosition = consumer.position(partition);
        long endOffset = consumer.endOffsets(
            Collections.singleton(partition)
        ).get(partition);

        lag.put(partition, endOffset - currentPosition);
    }

    return lag;
}
```

## Reliability Patterns

### 1. Exactly-Once Semantics

```java
// Producer with idempotence
Properties props = new Properties();
props.put("enable.idempotence", true);
props.put("transactional.id", "my-transactional-id");

KafkaProducer<String, String> producer = new KafkaProducer<>(props);
producer.initTransactions();

try {
    producer.beginTransaction();
    producer.send(new ProducerRecord<>("topic", "key", "value"));
    producer.commitTransaction();
} catch (Exception e) {
    producer.abortTransaction();
}
```

### 2. Error Handling

```java
// Dead Letter Queue pattern
KStream<String, Event> events = builder.stream("events");

KStream<String, Event>[] branches = events.branch(
    (key, event) -> isValid(event),      // Valid events
    (key, event) -> true                 // Invalid events (catch-all)
);

branches[0].to("valid_events");
branches[1].to("dead_letter_queue");
```

### 3. Retry Pattern

```java
public class RetryingConsumer {
    private int maxRetries = 3;
    private Duration retryDelay = Duration.ofSeconds(5);

    @KafkaListener(topics = "events")
    public void processEvent(Event event) {
        int attempt = 0;
        while (attempt < maxRetries) {
            try {
                process(event);
                return;  // Success
            } catch (RetryableException e) {
                attempt++;
                if (attempt >= maxRetries) {
                    sendToDeadLetterQueue(event, e);
                } else {
                    Thread.sleep(retryDelay.toMillis() * attempt);
                }
            }
        }
    }
}
```

## Monitoring Patterns

### 1. Metrics Collection

```java
// JMX metrics
kafka.server:type=BrokerTopicMetrics,name=MessagesInPerSec
kafka.server:type=BrokerTopicMetrics,name=BytesInPerSec
kafka.server:type=BrokerTopicMetrics,name=BytesOutPerSec
kafka.consumer:type=consumer-fetch-manager-metrics,client-id=*
kafka.producer:type=producer-metrics,client-id=*
```

### 2. Lag Alerting

```java
public class LagMonitor {
    private static final long MAX_LAG_THRESHOLD = 10000;

    @Scheduled(fixedDelay = 60000)
    public void checkLag() {
        Map<TopicPartition, Long> lag = getConsumerLag();

        lag.forEach((partition, lagValue) -> {
            if (lagValue > MAX_LAG_THRESHOLD) {
                alerting.send(String.format(
                    "High lag detected: %s has lag of %d",
                    partition, lagValue
                ));
            }
        });
    }
}
```

## Best Practices

### Producer Best Practices
1. Use async sends with callbacks
2. Enable compression (snappy or lz4)
3. Batch messages appropriately
4. Set appropriate acks level (acks=all for durability)
5. Monitor send failures and retry

### Consumer Best Practices
1. Commit offsets after processing
2. Handle rebalances gracefully
3. Monitor lag continuously
4. Use appropriate session timeout
5. Process records in batches

### Topic Design
1. Choose partition count based on throughput
2. Use meaningful topic naming conventions
3. Set appropriate retention policies
4. Enable log compaction for changelog topics
5. Use separate topics for different data types

### Schema Management
1. Use Schema Registry for schema evolution
2. Version all schemas
3. Ensure backward compatibility
4. Document schema changes
5. Use Avro or Protobuf for efficiency

## Anti-Patterns to Avoid

1. **Single Partition**: Limits parallelism
2. **Too Many Partitions**: Increases overhead
3. **Large Messages**: Use references instead
4. **Synchronous Processing**: Blocks consumer
5. **No Error Handling**: Lost messages
6. **Ignoring Lag**: Performance degradation
7. **Not Using Keys**: Random partitioning
8. **SELECT * Syndrome**: Read only what you need

## Resources

- Kafka: The Definitive Guide (O'Reilly)
- Confluent documentation
- Kafka Streams in Action
- Event Streaming Patterns (Confluent)
