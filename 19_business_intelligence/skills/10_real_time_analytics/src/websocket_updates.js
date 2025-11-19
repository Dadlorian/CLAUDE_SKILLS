/**
 * WebSocket Real-Time Updates
 * Pushes live analytics to dashboard
 */
const WebSocket = require('ws');
const { Client } = require('@clickhouse/client');

const wss = new WebSocket.Server({ port: 8080 });
const clickhouse = new Client({ host: 'http://clickhouse:8123' });

// Broadcast to all clients
function broadcast(data) {
    wss.clients.forEach(client => {
        if (client.readyState === WebSocket.OPEN) {
            client.send(JSON.stringify(data));
        }
    });
}

// Poll for updates every 5 seconds
setInterval(async () => {
    const result = await clickhouse.query({
        query: `
            SELECT 
                toStartOfMinute(event_time) AS minute,
                count() AS events,
                sum(revenue) AS revenue
            FROM events
            WHERE event_time >= now() - INTERVAL 5 MINUTE
            GROUP BY minute
        `
    });
    
    const data = await result.json();
    broadcast({ type: 'stats', data });
}, 5000);

wss.on('connection', (ws) => {
    console.log('Client connected');
    ws.on('close', () => console.log('Client disconnected'));
});
