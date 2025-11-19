# Supply Chain Visibility Platform Architecture

## Overview

This document outlines the architecture, components, and best practices for building a comprehensive supply chain visibility platform that provides end-to-end tracking and monitoring capabilities.

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Data Collection Layer](#data-collection-layer)
3. [Event Processing](#event-processing)
4. [Analytics and Insights](#analytics-and-insights)
5. [User Experience](#user-experience)
6. [Integration Patterns](#integration-patterns)

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Data Sources                              │
│  Carriers │ WMS │ TMS │ ERP │ IoT Sensors │ EDI │ APIs          │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Data Collection Layer                          │
│  • API Gateways  • Message Queues  • Data Ingestion             │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Event Processing Engine                        │
│  • Stream Processing  • CEP  • Rules Engine                      │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Data Storage                                │
│  • Time-Series DB  • Document Store  • Data Warehouse            │
└────────────────────────┬────────────────────────────────────────┘
                         │
             ┌───────────┼────────────┐
             ▼           ▼            ▼
      ┌──────────┐ ┌─────────┐ ┌──────────┐
      │Analytics │ │  APIs   │ │   UI     │
      │ Engine   │ │         │ │Dashboard │
      └──────────┘ └─────────┘ └──────────┘
```

### Technology Stack

| Layer | Technologies | Purpose |
|-------|-------------|---------|
| **Data Ingestion** | Apache Kafka, RabbitMQ, AWS Kinesis | Event streaming and message queuing |
| **API Gateway** | Kong, AWS API Gateway, Apigee | API management and routing |
| **Stream Processing** | Apache Flink, Kafka Streams, Spark Streaming | Real-time event processing |
| **Storage** | TimescaleDB, MongoDB, PostgreSQL, Elasticsearch | Multi-model data storage |
| **Analytics** | Apache Spark, Presto, BigQuery | Batch analytics and reporting |
| **Cache** | Redis, Memcached | High-speed data access |
| **Application** | Node.js, Python, Java, Go | Business logic and APIs |
| **Frontend** | React, Vue.js, Angular | User interface |
| **ML/AI** | TensorFlow, PyTorch, scikit-learn | Predictive analytics |
| **Monitoring** | Prometheus, Grafana, ELK Stack | System observability |

---

## Data Collection Layer

### Multi-Source Data Ingestion

```python
from kafka import KafkaProducer
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, Any
import json

@dataclass
class ShipmentEvent:
    """Standardized shipment event"""
    event_id: str
    event_type: str
    timestamp: datetime
    shipment_id: str
    carrier: str
    tracking_number: str
    location: Dict[str, Any]
    status: str
    metadata: Dict[str, Any]

class DataIngestionService:
    """Ingest data from multiple sources into event stream"""

    def __init__(self, kafka_bootstrap_servers: List[str]):
        self.producer = KafkaProducer(
            bootstrap_servers=kafka_bootstrap_servers,
            value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8'),
            compression_type='gzip',
            linger_ms=10,  # Batch messages for 10ms
            batch_size=16384  # 16KB batch size
        )

    def ingest_carrier_event(self, event: ShipmentEvent):
        """Ingest carrier tracking event"""
        self.producer.send(
            topic='shipment.events.raw',
            value=asdict(event),
            key=event.shipment_id.encode('utf-8')
        )

    def ingest_wms_event(self, warehouse_event: Dict):
        """Ingest warehouse management event"""
        self.producer.send(
            topic='warehouse.events.raw',
            value=warehouse_event,
            key=warehouse_event['order_id'].encode('utf-8')
        )

    def ingest_iot_sensor_data(self, sensor_data: Dict):
        """Ingest IoT sensor data (temperature, location, etc.)"""
        self.producer.send(
            topic='iot.sensor.data',
            value=sensor_data,
            key=sensor_data['device_id'].encode('utf-8')
        )

    def flush(self):
        """Flush pending messages"""
        self.producer.flush()
```

### API Gateway for External Systems

```python
from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Optional
import hmac
import hashlib

app = FastAPI(title="Visibility Platform Ingestion API")

class TrackingEventRequest(BaseModel):
    shipment_id: str
    tracking_number: str
    carrier: str
    event_type: str
    status: str
    timestamp: str
    location: Optional[Dict] = None
    metadata: Optional[Dict] = None

async def verify_api_key(x_api_key: str = Header(...)):
    """Verify API key"""
    # In production, check against database or cache
    valid_keys = ["key1", "key2", "key3"]
    if x_api_key not in valid_keys:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key

@app.post("/api/v1/events/tracking")
async def ingest_tracking_event(
    event: TrackingEventRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Ingest tracking event from external system.
    Authenticated via API key.
    """
    # Validate and transform event
    shipment_event = ShipmentEvent(
        event_id=generate_event_id(),
        event_type=event.event_type,
        timestamp=datetime.fromisoformat(event.timestamp),
        shipment_id=event.shipment_id,
        carrier=event.carrier,
        tracking_number=event.tracking_number,
        location=event.location or {},
        status=event.status,
        metadata=event.metadata or {}
    )

    # Send to ingestion service
    ingestion_service.ingest_carrier_event(shipment_event)

    return {
        "status": "accepted",
        "event_id": shipment_event.event_id,
        "timestamp": shipment_event.timestamp
    }

@app.post("/api/v1/events/warehouse")
async def ingest_warehouse_event(
    event: Dict,
    api_key: str = Depends(verify_api_key)
):
    """Ingest warehouse event"""
    ingestion_service.ingest_wms_event(event)

    return {"status": "accepted", "timestamp": datetime.now()}
```

---

## Event Processing

### Real-Time Stream Processing

```python
from kafka import KafkaConsumer
from datetime import datetime, timedelta
from collections import defaultdict
import json

class RealTimeEventProcessor:
    """
    Process shipment events in real-time.
    - Detect exceptions and delays
    - Calculate ETAs
    - Trigger alerts
    """

    def __init__(self, kafka_bootstrap_servers: List[str]):
        self.consumer = KafkaConsumer(
            'shipment.events.raw',
            bootstrap_servers=kafka_bootstrap_servers,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            group_id='event-processor',
            auto_offset_reset='latest'
        )

        # In-memory state (in production, use distributed cache)
        self.shipment_state = {}
        self.expected_delivery = {}

    def process_events(self):
        """Process event stream"""
        for message in self.consumer:
            event = message.value

            try:
                self.process_event(event)
            except Exception as e:
                print(f"Error processing event: {e}")
                # Send to DLQ
                self.send_to_dead_letter_queue(event, str(e))

    def process_event(self, event: Dict):
        """Process single event"""
        shipment_id = event['shipment_id']

        # Update shipment state
        self.update_shipment_state(shipment_id, event)

        # Check for exceptions
        if self.is_exception_event(event):
            self.handle_exception(shipment_id, event)

        # Check for delays
        if self.is_delay_detected(shipment_id, event):
            self.handle_delay(shipment_id, event)

        # Update ETA
        self.update_eta(shipment_id, event)

        # Check milestones
        self.check_milestones(shipment_id, event)

    def update_shipment_state(self, shipment_id: str, event: Dict):
        """Update current state of shipment"""
        if shipment_id not in self.shipment_state:
            self.shipment_state[shipment_id] = {
                'events': [],
                'current_status': None,
                'last_location': None,
                'last_update': None
            }

        state = self.shipment_state[shipment_id]
        state['events'].append(event)
        state['current_status'] = event['status']
        state['last_location'] = event.get('location')
        state['last_update'] = event['timestamp']

    def is_exception_event(self, event: Dict) -> bool:
        """Check if event indicates an exception"""
        exception_statuses = ['exception', 'delivery_failure', 'damaged', 'lost']
        return event['status'] in exception_statuses

    def handle_exception(self, shipment_id: str, event: Dict):
        """Handle exception event"""
        print(f"EXCEPTION detected for {shipment_id}: {event['status']}")

        # Create alert
        alert = {
            'alert_id': generate_alert_id(),
            'shipment_id': shipment_id,
            'alert_type': 'exception',
            'severity': 'high',
            'message': f"Exception: {event['status']}",
            'timestamp': event['timestamp'],
            'event': event
        }

        # Send alert
        self.send_alert(alert)

    def is_delay_detected(self, shipment_id: str, event: Dict) -> bool:
        """Detect if shipment is delayed"""
        if shipment_id not in self.expected_delivery:
            return False

        expected = self.expected_delivery[shipment_id]
        current_time = datetime.fromisoformat(event['timestamp'])

        # Check if current time exceeds expected delivery
        if current_time > expected and event['status'] != 'delivered':
            return True

        return False

    def handle_delay(self, shipment_id: str, event: Dict):
        """Handle delay detection"""
        print(f"DELAY detected for {shipment_id}")

        alert = {
            'alert_id': generate_alert_id(),
            'shipment_id': shipment_id,
            'alert_type': 'delay',
            'severity': 'medium',
            'message': f"Shipment delayed",
            'timestamp': event['timestamp']
        }

        self.send_alert(alert)

    def update_eta(self, shipment_id: str, event: Dict):
        """Update estimated time of arrival"""
        # Use ML model to predict ETA based on current location and historical data
        # Simplified version here
        if event['status'] == 'out_for_delivery':
            eta = datetime.now() + timedelta(hours=4)
            self.expected_delivery[shipment_id] = eta

    def check_milestones(self, shipment_id: str, event: Dict):
        """Check if event is a key milestone"""
        milestones = ['picked_up', 'in_transit', 'customs_cleared', 'out_for_delivery', 'delivered']

        if event['status'] in milestones:
            print(f"Milestone reached for {shipment_id}: {event['status']}")

            # Publish milestone event
            self.publish_milestone(shipment_id, event)

    def send_alert(self, alert: Dict):
        """Send alert to notification service"""
        # In production, send to notification queue
        print(f"ALERT: {alert}")

    def publish_milestone(self, shipment_id: str, event: Dict):
        """Publish milestone event"""
        # Send to milestone topic for further processing
        pass
```

### Complex Event Processing (CEP)

```python
from dataclasses import dataclass
from typing import List, Callable
from datetime import datetime, timedelta

@dataclass
class Rule:
    """Event processing rule"""
    name: str
    condition: Callable[[Dict], bool]
    action: Callable[[Dict], None]
    window_seconds: Optional[int] = None

class ComplexEventProcessor:
    """
    Process complex patterns across multiple events.
    Example: Detect if shipment has been stuck in same location for >24 hours
    """

    def __init__(self):
        self.rules: List[Rule] = []
        self.event_history: Dict[str, List[Dict]] = defaultdict(list)

    def add_rule(self, rule: Rule):
        """Add processing rule"""
        self.rules.append(rule)

    def process_event(self, event: Dict):
        """Process event against all rules"""
        shipment_id = event['shipment_id']

        # Add to history
        self.event_history[shipment_id].append(event)

        # Trim old events based on largest window
        max_window = max((r.window_seconds for r in self.rules if r.window_seconds), default=86400)
        cutoff_time = datetime.fromisoformat(event['timestamp']) - timedelta(seconds=max_window)

        self.event_history[shipment_id] = [
            e for e in self.event_history[shipment_id]
            if datetime.fromisoformat(e['timestamp']) > cutoff_time
        ]

        # Evaluate rules
        for rule in self.rules:
            try:
                if rule.condition(event):
                    rule.action(event)
            except Exception as e:
                print(f"Error evaluating rule {rule.name}: {e}")

# Example rules
def stuck_in_transit_rule():
    """Detect if shipment stuck at same location for >24 hours"""

    def condition(event: Dict) -> bool:
        shipment_id = event['shipment_id']
        history = cep_processor.event_history[shipment_id]

        if len(history) < 2:
            return False

        # Check if location hasn't changed in 24 hours
        recent_events = [e for e in history if
                        datetime.fromisoformat(e['timestamp']) >
                        datetime.fromisoformat(event['timestamp']) - timedelta(hours=24)]

        if len(recent_events) < 2:
            return False

        # Check if all recent events have same location
        locations = [e.get('location', {}).get('city') for e in recent_events]
        locations = [loc for loc in locations if loc]  # Remove None

        if len(locations) > 0 and len(set(locations)) == 1:
            return True

        return False

    def action(event: Dict):
        print(f"ALERT: Shipment {event['shipment_id']} stuck at {event['location']} for >24h")
        # Send alert
        pass

    return Rule(
        name="stuck_in_transit",
        condition=condition,
        action=action,
        window_seconds=86400  # 24 hours
    )

# Initialize CEP
cep_processor = ComplexEventProcessor()
cep_processor.add_rule(stuck_in_transit_rule())
```

---

## Analytics and Insights

### Predictive ETA Model

```python
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from datetime import datetime, timedelta

class PredictiveETAEngine:
    """
    Machine learning model for predicting shipment ETAs.
    Features: carrier, origin, destination, distance, current location, time of day, day of week
    """

    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.is_trained = False

    def train(self, historical_data: pd.DataFrame):
        """
        Train model on historical shipment data.
        Required columns: carrier, origin_zip, dest_zip, distance_miles,
                         current_lat, current_lon, hour_of_day, day_of_week,
                         remaining_hours (target)
        """
        features = [
            'carrier_encoded', 'origin_zip', 'dest_zip', 'distance_miles',
            'current_lat', 'current_lon', 'hour_of_day', 'day_of_week',
            'stops_remaining'
        ]

        X = historical_data[features]
        y = historical_data['remaining_hours']

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        self.model.fit(X_train, y_train)

        # Evaluate
        score = self.model.score(X_test, y_test)
        print(f"Model R² score: {score:.3f}")

        self.is_trained = True

    def predict_eta(self, shipment_data: Dict) -> datetime:
        """Predict ETA for shipment"""
        if not self.is_trained:
            raise ValueError("Model not trained")

        # Prepare features
        features = np.array([[
            self._encode_carrier(shipment_data['carrier']),
            int(shipment_data['origin_zip']),
            int(shipment_data['dest_zip']),
            shipment_data['distance_miles'],
            shipment_data['current_lat'],
            shipment_data['current_lon'],
            datetime.now().hour,
            datetime.now().weekday(),
            shipment_data.get('stops_remaining', 0)
        ]])

        # Predict remaining hours
        remaining_hours = self.model.predict(features)[0]

        # Calculate ETA
        eta = datetime.now() + timedelta(hours=remaining_hours)

        return eta

    def _encode_carrier(self, carrier: str) -> int:
        """Encode carrier name to numeric"""
        carrier_map = {'FedEx': 1, 'UPS': 2, 'USPS': 3, 'DHL': 4}
        return carrier_map.get(carrier, 0)
```

### Performance Analytics

```python
class VisibilityAnalytics:
    """Generate insights and analytics from visibility data"""

    def __init__(self, db_connection):
        self.db = db_connection

    def carrier_performance_report(self, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """
        Generate carrier performance report.
        Metrics: on-time delivery, average transit time, exception rate
        """
        query = """
        SELECT
            carrier,
            COUNT(*) as total_shipments,
            SUM(CASE WHEN actual_delivery <= estimated_delivery THEN 1 ELSE 0 END) as on_time_deliveries,
            AVG(EXTRACT(EPOCH FROM (actual_delivery - ship_date)) / 3600) as avg_transit_hours,
            SUM(CASE WHEN status = 'exception' THEN 1 ELSE 0 END) as exceptions,
            AVG(delay_hours) as avg_delay_hours
        FROM shipments
        WHERE ship_date BETWEEN %s AND %s
        GROUP BY carrier
        ORDER BY on_time_deliveries DESC
        """

        df = pd.read_sql(query, self.db, params=[start_date, end_date])

        # Calculate percentages
        df['on_time_pct'] = (df['on_time_deliveries'] / df['total_shipments'] * 100).round(2)
        df['exception_pct'] = (df['exceptions'] / df['total_shipments'] * 100).round(2)

        return df

    def lane_analysis(self, origin_zip: str, dest_zip: str) -> Dict:
        """
        Analyze specific shipping lane.
        Identify best carrier, typical transit times, reliability
        """
        query = """
        SELECT
            carrier,
            COUNT(*) as shipments,
            AVG(transit_time_hours) as avg_transit,
            STDDEV(transit_time_hours) as transit_variance,
            SUM(CASE WHEN on_time THEN 1 ELSE 0 END)::FLOAT / COUNT(*) as on_time_rate,
            AVG(cost) as avg_cost
        FROM shipments
        WHERE origin_zip = %s AND dest_zip = %s
        GROUP BY carrier
        """

        df = pd.read_sql(query, self.db, params=[origin_zip, dest_zip])

        # Find best carrier (weighted score)
        df['score'] = (
            df['on_time_rate'] * 0.5 +
            (1 / df['avg_transit']) * 0.3 +
            (1 / df['transit_variance']) * 0.2
        )

        best_carrier = df.loc[df['score'].idxmax(), 'carrier']

        return {
            'lane': f"{origin_zip} → {dest_zip}",
            'best_carrier': best_carrier,
            'carrier_analysis': df.to_dict('records')
        }
```

---

## User Experience

### Real-Time Dashboard Components

```javascript
// React component for real-time shipment tracking dashboard
import React, { useState, useEffect } from 'react';
import { useWebSocket } from 'react-use-websocket';

const ShipmentDashboard = () => {
  const [shipments, setShipments] = useState([]);
  const [alerts, setAlerts] = useState([]);

  // WebSocket connection for real-time updates
  const { lastMessage } = useWebSocket('wss://api.example.com/ws/shipments', {
    onOpen: () => console.log('WebSocket connected'),
    shouldReconnect: () => true,
  });

  useEffect(() => {
    if (lastMessage !== null) {
      const event = JSON.parse(lastMessage.data);

      if (event.type === 'shipment_update') {
        // Update shipment in list
        setShipments(prev => {
          const index = prev.findIndex(s => s.id === event.shipment_id);
          if (index >= 0) {
            const updated = [...prev];
            updated[index] = { ...updated[index], ...event.data };
            return updated;
          }
          return [...prev, event.data];
        });
      } else if (event.type === 'alert') {
        // Add alert
        setAlerts(prev => [event.data, ...prev].slice(0, 10)); // Keep last 10
      }
    }
  }, [lastMessage]);

  return (
    <div className="dashboard">
      <AlertPanel alerts={alerts} />
      <ShipmentList shipments={shipments} />
      <MetricsPanel shipments={shipments} />
    </div>
  );
};

const AlertPanel = ({ alerts }) => (
  <div className="alerts">
    <h2>Recent Alerts</h2>
    {alerts.map(alert => (
      <div key={alert.id} className={`alert alert-${alert.severity}`}>
        <span className="time">{new Date(alert.timestamp).toLocaleString()}</span>
        <span className="message">{alert.message}</span>
      </div>
    ))}
  </div>
);

const ShipmentList = ({ shipments }) => (
  <div className="shipments">
    <h2>Active Shipments</h2>
    <table>
      <thead>
        <tr>
          <th>Tracking #</th>
          <th>Status</th>
          <th>Origin</th>
          <th>Destination</th>
          <th>ETA</th>
          <th>Last Update</th>
        </tr>
      </thead>
      <tbody>
        {shipments.map(shipment => (
          <tr key={shipment.id}>
            <td>{shipment.tracking_number}</td>
            <td><StatusBadge status={shipment.status} /></td>
            <td>{shipment.origin}</td>
            <td>{shipment.destination}</td>
            <td>{new Date(shipment.eta).toLocaleString()}</td>
            <td>{new Date(shipment.last_update).toLocaleString()}</td>
          </tr>
        ))}
      </tbody>
    </table>
  </div>
);
```

---

## Conclusion

A comprehensive supply chain visibility platform requires:

1. **Robust Data Ingestion**: Handle multiple data sources and formats
2. **Real-Time Processing**: Detect issues as they occur
3. **Intelligent Analytics**: Provide predictive insights
4. **User-Friendly Interface**: Make data actionable
5. **Scalable Architecture**: Handle growth in data volume
6. **Reliable Integration**: Connect seamlessly with existing systems

This architecture provides the foundation for building a world-class visibility solution that drives operational efficiency and customer satisfaction.
