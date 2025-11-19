# Real-Time Dashboard Implementation Guide

## WebSocket Server
```python
from flask import Flask
from flask_socketio import SocketIO, emit
from clickhouse_driver import Client

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
clickhouse = Client(host='clickhouse')

@socketio.on('subscribe')
def handle_subscription(data):
    # Subscribe to real-time updates
    emit('subscribed', {'status': 'success'})

def push_updates():
    while True:
        metrics = clickhouse.execute("""
            SELECT * FROM hourly_stats 
            WHERE hour >= now() - INTERVAL 1 HOUR
        """)
        socketio.emit('update', {'data': metrics})
        time.sleep(5)
```

## React Frontend
```javascript
import io from 'socket.io-client';

const socket = io('http://localhost:5000');

socket.on('update', (data) => {
    updateChart(data);
});

socket.emit('subscribe', {metrics: ['revenue', 'users']});
```

## Best Practices
- Use WebSockets for live updates
- Implement throttling
- Cache frequent queries
- Use incremental updates
- Handle disconnections gracefully
