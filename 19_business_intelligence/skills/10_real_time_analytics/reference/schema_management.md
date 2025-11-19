# Schema Management in Real-Time Analytics

## Overview

Schema management is critical for real-time analytics systems to ensure data consistency, enable evolution, and maintain compatibility across producers and consumers.

## Schema Registry

### Confluent Schema Registry

#### Architecture
```
Producer → Schema Registry (validate) → Kafka → Consumer (deserialize)
              ↓
         Schema Store
         (compatibility checks)
```

#### Configuration
```properties
# Schema Registry setup
schema.registry.url=http://localhost:8081

# Producer config
key.serializer=io.confluent.kafka.serializers.KafkaAvroSerializer
value.serializer=io.confluent.kafka.serializers.KafkaAvroSerializer

# Consumer config
key.deserializer=io.confluent.kafka.serializers.KafkaAvroDeserializer
value.deserializer=io.confluent.kafka.serializers.KafkaAvroDeserializer
specific.avro.reader=true
```

#### Avro Schema Example
```json
{
  "type": "record",
  "name": "UserEvent",
  "namespace": "com.example.events",
  "fields": [
    {
      "name": "event_id",
      "type": "string",
      "doc": "Unique event identifier"
    },
    {
      "name": "user_id",
      "type": "long"
    },
    {
      "name": "event_type",
      "type": {
        "type": "enum",
        "name": "EventType",
        "symbols": ["PAGE_VIEW", "CLICK", "PURCHASE"]
      }
    },
    {
      "name": "timestamp",
      "type": "long",
      "logicalType": "timestamp-millis"
    },
    {
      "name": "properties",
      "type": {
        "type": "map",
        "values": "string"
      },
      "default": {}
    }
  ]
}
```

## Compatibility Modes

### Backward Compatibility
```
New schema can read data written with old schema

Example: Adding optional field with default
Old schema: {name: string, age: int}
New schema: {name: string, age: int, email: string = ""}

✓ New consumer can read old data (uses default for email)
✗ Old consumer cannot read new data
```

```json
{
  "type": "record",
  "name": "User",
  "fields": [
    {"name": "name", "type": "string"},
    {"name": "age", "type": "int"},
    {"name": "email", "type": "string", "default": ""}
  ]
}
```

### Forward Compatibility
```
Old schema can read data written with new schema

Example: Adding optional field with default
Old schema: {name: string, age: int}
New schema: {name: string, age: int, phone: string = ""}

✓ Old consumer can read new data (ignores phone)
✗ New consumer cannot read old data
```

### Full Compatibility
```
Both backward and forward compatible

Example: Only adding optional fields with defaults
```

```json
{
  "compatibilityLevel": "FULL",
  "schema": {
    "type": "record",
    "name": "Event",
    "fields": [
      {"name": "id", "type": "string"},
      {"name": "timestamp", "type": "long"},
      {"name": "user_id", "type": "long"},
      {"name": "session_id", "type": ["null", "string"], "default": null}
    ]
  }
}
```

### None Compatibility
```
No compatibility checks
Use with caution - can break consumers
```

## Schema Evolution Patterns

### Adding Fields

#### Safe Addition (with default)
```avro
// Version 1
{
  "type": "record",
  "name": "Event",
  "fields": [
    {"name": "id", "type": "string"},
    {"name": "timestamp", "type": "long"}
  ]
}

// Version 2 - SAFE
{
  "type": "record",
  "name": "Event",
  "fields": [
    {"name": "id", "type": "string"},
    {"name": "timestamp", "type": "long"},
    {"name": "country", "type": "string", "default": "US"}
  ]
}
```

#### Unsafe Addition (no default)
```avro
// Version 2 - UNSAFE (breaks backward compatibility)
{
  "type": "record",
  "name": "Event",
  "fields": [
    {"name": "id", "type": "string"},
    {"name": "timestamp", "type": "long"},
    {"name": "country", "type": "string"}  // No default!
  ]
}
```

### Removing Fields

```avro
// Version 1
{
  "type": "record",
  "name": "Event",
  "fields": [
    {"name": "id", "type": "string"},
    {"name": "timestamp", "type": "long"},
    {"name": "deprecated_field", "type": "string", "default": ""}
  ]
}

// Version 2 - Safe if field had default
{
  "type": "record",
  "name": "Event",
  "fields": [
    {"name": "id", "type": "string"},
    {"name": "timestamp", "type": "long"}
  ]
}
```

### Changing Field Types

#### Union Types (Safe Evolution)
```avro
// Version 1
{"name": "age", "type": "int"}

// Version 2 - Allow null
{"name": "age", "type": ["null", "int"], "default": null}

// Version 3 - Support both int and string
{"name": "age", "type": ["null", "int", "string"], "default": null}
```

#### Type Promotion (Limited Support)
```
Supported promotions:
- int → long
- int → float
- int → double
- long → float
- long → double
- float → double
- string → bytes
- bytes → string
```

```avro
// Version 1
{"name": "count", "type": "int"}

// Version 2 - Safe promotion
{"name": "count", "type": "long"}
```

## Schema Formats

### Apache Avro

#### Advantages
- Compact binary format
- Rich schema evolution support
- Code generation
- Schema embedded in data
- Fast serialization

#### Producer Example
```java
import org.apache.avro.specific.SpecificRecordBase;
import io.confluent.kafka.serializers.KafkaAvroSerializer;

Properties props = new Properties();
props.put("schema.registry.url", "http://localhost:8081");
props.put("value.serializer", KafkaAvroSerializer.class);

KafkaProducer<String, UserEvent> producer = new KafkaProducer<>(props);

UserEvent event = UserEvent.newBuilder()
    .setEventId("123")
    .setUserId(456L)
    .setEventType(EventType.PURCHASE)
    .setTimestamp(System.currentTimeMillis())
    .build();

producer.send(new ProducerRecord<>("events", event.getEventId(), event));
```

#### Consumer Example
```java
Properties props = new Properties();
props.put("schema.registry.url", "http://localhost:8081");
props.put("value.deserializer", KafkaAvroDeserializer.class);
props.put("specific.avro.reader", true);

KafkaConsumer<String, UserEvent> consumer = new KafkaConsumer<>(props);
consumer.subscribe(Collections.singletonList("events"));

while (true) {
    ConsumerRecords<String, UserEvent> records = consumer.poll(Duration.ofMillis(100));
    for (ConsumerRecord<String, UserEvent> record : records) {
        UserEvent event = record.value();
        System.out.println("Event: " + event.getEventType());
    }
}
```

### Protocol Buffers

#### Advantages
- Efficient binary format
- Strong typing
- Cross-language support
- Good evolution support
- Code generation

#### Schema Example
```protobuf
syntax = "proto3";

package events;

message UserEvent {
  string event_id = 1;
  int64 user_id = 2;
  EventType event_type = 3;
  int64 timestamp = 4;
  map<string, string> properties = 5;
}

enum EventType {
  UNKNOWN = 0;
  PAGE_VIEW = 1;
  CLICK = 2;
  PURCHASE = 3;
}
```

#### Evolution Rules
```protobuf
// Safe changes:
// - Add new fields (use new field numbers)
// - Make required → optional
// - Add new enum values

// Unsafe changes:
// - Change field number
// - Change field type
// - Make optional → required
// - Remove enum values
```

### JSON Schema

#### Advantages
- Human-readable
- Flexible
- Wide language support
- Easy debugging

#### Disadvantages
- Larger payload size
- Slower serialization
- Weaker type safety

#### Schema Example
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "UserEvent",
  "type": "object",
  "required": ["event_id", "user_id", "event_type", "timestamp"],
  "properties": {
    "event_id": {
      "type": "string",
      "pattern": "^[a-f0-9-]{36}$"
    },
    "user_id": {
      "type": "integer",
      "minimum": 1
    },
    "event_type": {
      "type": "string",
      "enum": ["page_view", "click", "purchase"]
    },
    "timestamp": {
      "type": "integer",
      "minimum": 0
    },
    "properties": {
      "type": "object",
      "additionalProperties": {"type": "string"}
    }
  }
}
```

## Schema Versioning Strategies

### Subject Name Strategy

#### TopicNameStrategy (Default)
```
Subject: <topic>-value
Example: events-value

All messages in topic must conform to same schema
```

```java
props.put("value.subject.name.strategy",
    "io.confluent.kafka.serializers.subject.TopicNameStrategy");
```

#### RecordNameStrategy
```
Subject: <namespace>.<name>
Example: com.example.events.UserEvent

Different record types can share same topic
```

```java
props.put("value.subject.name.strategy",
    "io.confluent.kafka.serializers.subject.RecordNameStrategy");
```

#### TopicRecordNameStrategy
```
Subject: <topic>-<namespace>.<name>
Example: events-com.example.events.UserEvent

Combination of topic and record name
```

### Version Management

```bash
# Register new schema version
curl -X POST -H "Content-Type: application/vnd.schemaregistry.v1+json" \
  --data '{"schema": "{...}"}' \
  http://localhost:8081/subjects/events-value/versions

# Get latest schema
curl http://localhost:8081/subjects/events-value/versions/latest

# Get specific version
curl http://localhost:8081/subjects/events-value/versions/3

# Check compatibility
curl -X POST -H "Content-Type: application/vnd.schemaregistry.v1+json" \
  --data '{"schema": "{...}"}' \
  http://localhost:8081/compatibility/subjects/events-value/versions/latest
```

## Migration Strategies

### Dual Write Pattern

```java
// Write to both old and new topics during migration
public void publishEvent(Event event) {
    // Old format
    LegacyEvent legacyEvent = convertToLegacy(event);
    producer.send(new ProducerRecord<>("events-v1", legacyEvent));

    // New format
    producer.send(new ProducerRecord<>("events-v2", event));
}

// Consumers gradually migrate from v1 to v2
```

### Schema Translation

```java
// Consumer side translation
public class TranslatingConsumer {
    public void consume() {
        ConsumerRecords<String, GenericRecord> records = consumer.poll(...);

        for (ConsumerRecord<String, GenericRecord> record : records) {
            GenericRecord oldRecord = record.value();

            // Translate to new schema
            NewEvent newEvent = NewEvent.newBuilder()
                .setEventId(oldRecord.get("event_id").toString())
                .setUserId((Long) oldRecord.get("user_id"))
                .setEventType(translateEventType(oldRecord.get("event_type")))
                .setTimestamp((Long) oldRecord.get("timestamp"))
                .build();

            process(newEvent);
        }
    }
}
```

### Canary Deployment

```
1. Deploy new schema producer (write to new topic)
2. Deploy consumer reading both old and new topics
3. Gradually shift traffic to new topic
4. Monitor errors and rollback if needed
5. Deprecate old topic after full migration
```

## Best Practices

### Schema Design

1. **Use Namespaces**: Organize schemas logically
```avro
{
  "namespace": "com.example.events.user",
  "name": "ProfileUpdated"
}
```

2. **Document Fields**: Add descriptions
```avro
{
  "name": "email",
  "type": "string",
  "doc": "User email address, validated and lowercase"
}
```

3. **Use Logical Types**: For dates, timestamps, decimals
```avro
{
  "name": "created_at",
  "type": "long",
  "logicalType": "timestamp-millis"
}
```

4. **Provide Defaults**: Enable backward compatibility
```avro
{
  "name": "country",
  "type": "string",
  "default": "US"
}
```

5. **Use Enums Carefully**: Hard to evolve
```avro
// Better: Use string with documentation
{"name": "status", "type": "string", "doc": "Values: active, inactive, suspended"}

// Instead of:
{"name": "status", "type": {"type": "enum", "symbols": ["ACTIVE", "INACTIVE"]}}
```

### Schema Evolution

1. **Always Add Defaults**: For new fields
2. **Test Compatibility**: Before deploying
3. **Version Incrementally**: Small, frequent changes
4. **Maintain Compatibility**: Unless breaking change necessary
5. **Communicate Changes**: Document breaking changes
6. **Keep Old Versions**: For rollback capability

### Operational

1. **Monitor Schema Registry**: Track registrations
2. **Backup Schemas**: Regular backups
3. **Control Access**: Limit who can register schemas
4. **Use CI/CD**: Automated schema validation
5. **Document Decisions**: Why schemas evolved

## Schema Testing

```java
@Test
public void testBackwardCompatibility() {
    // Old schema
    Schema oldSchema = new Schema.Parser().parse(oldSchemaJson);

    // New schema
    Schema newSchema = new Schema.Parser().parse(newSchemaJson);

    // Test compatibility
    CompatibilityChecker checker = CompatibilityChecker.BACKWARD_CHECKER;
    boolean isCompatible = checker.isCompatible(newSchema, oldSchema);

    assertTrue("New schema is not backward compatible", isCompatible);
}

@Test
public void testRoundTrip() {
    // Create event with new schema
    UserEvent event = UserEvent.newBuilder()
        .setEventId("123")
        .setUserId(456L)
        .build();

    // Serialize
    byte[] bytes = serialize(event);

    // Deserialize with old schema
    GenericRecord oldEvent = deserializeWithOldSchema(bytes);

    // Verify fields
    assertEquals("123", oldEvent.get("event_id").toString());
    assertEquals(456L, oldEvent.get("user_id"));
}
```

## Monitoring

```java
// Track schema registry metrics
public class SchemaRegistryMonitor {
    private final MeterRegistry registry;

    public void recordSchemaRegistration(String subject, int version) {
        registry.counter("schema.registry.registrations",
            "subject", subject,
            "version", String.valueOf(version)
        ).increment();
    }

    public void recordSchemaFetch(String subject, boolean fromCache) {
        registry.counter("schema.registry.fetches",
            "subject", subject,
            "from_cache", String.valueOf(fromCache)
        ).increment();
    }

    public void recordCompatibilityCheck(String subject, boolean compatible) {
        registry.counter("schema.registry.compatibility_checks",
            "subject", subject,
            "compatible", String.valueOf(compatible)
        ).increment();
    }
}
```

## Troubleshooting

### Common Issues

**Schema Not Found**
```
Error: Schema not found for subject events-value

Solution:
1. Check subject name strategy
2. Verify schema is registered
3. Check Schema Registry connectivity
```

**Incompatible Schema**
```
Error: Schema being registered is incompatible with an earlier schema

Solution:
1. Check compatibility mode
2. Ensure new schema follows evolution rules
3. Consider using NONE compatibility if breaking change needed
```

**Serialization Error**
```
Error: Failed to serialize Avro message

Solution:
1. Verify schema matches data
2. Check required fields are provided
3. Validate data types
```

## Resources

- Confluent Schema Registry Documentation
- Avro Specification
- Protocol Buffers Documentation
- "Designing Data-Intensive Applications" - Kleppmann
- Schema Registry REST API Reference
