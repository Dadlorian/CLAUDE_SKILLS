"""Real-Time Dashboard API"""
from flask import Flask, jsonify, request
from flask_cors import CORS
from clickhouse_driver import Client
import logging

app = Flask(__name__)
CORS(app)
clickhouse = Client(host='clickhouse', port=9000)
logger = logging.getLogger(__name__)

@app.route('/api/stats/realtime', methods=['GET'])
def get_realtime_stats():
    """Get real-time statistics"""
    query = """
        SELECT
            toStartOfMinute(event_time) AS minute,
            event_type,
            count() AS events,
            sum(revenue) AS revenue,
            uniq(user_id) AS unique_users
        FROM events
        WHERE event_time >= now() - INTERVAL 1 HOUR
        GROUP BY minute, event_type
        ORDER BY minute DESC
    """
    results = clickhouse.execute(query)
    return jsonify([{
        'minute': str(row[0]),
        'event_type': row[1],
        'events': row[2],
        'revenue': float(row[3]) if row[3] else 0,
        'unique_users': row[4]
    } for row in results])

@app.route('/api/users/<user_id>/timeline', methods=['GET'])
def get_user_timeline(user_id):
    """Get user event timeline"""
    limit = request.args.get('limit', 100, type=int)
    query = """
        SELECT event_time, event_type, properties
        FROM events
        WHERE user_id = %(user_id)s
        ORDER BY event_time DESC
        LIMIT %(limit)s
    """
    results = clickhouse.execute(query, {'user_id': int(user_id), 'limit': limit})
    return jsonify([{
        'timestamp': str(row[0]),
        'event_type': row[1],
        'properties': row[2]
    } for row in results])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
