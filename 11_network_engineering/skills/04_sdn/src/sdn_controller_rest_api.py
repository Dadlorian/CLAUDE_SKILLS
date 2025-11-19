#!/usr/bin/env python3
"""
SDN Controller REST API
ONOS-compatible API server
"""

from flask import Flask, jsonify, request
import json
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In-memory data store (would use database in production)
devices = {}
flows = {}
networks = {}

@app.route('/api/devices', methods=['GET'])
def get_devices():
    """Get all devices"""
    device_list = []
    for dev_id, dev_info in devices.items():
        device_list.append({
            'id': dev_id,
            'available': dev_info.get('available', True),
            'role': dev_info.get('role', 'UNSPECIFIED'),
            'mfr': dev_info.get('manufacturer', 'Unknown')
        })
    return jsonify({'devices': device_list})

@app.route('/api/devices/<device_id>', methods=['GET'])
def get_device(device_id):
    """Get specific device"""
    if device_id in devices:
        return jsonify(devices[device_id])
    return jsonify({'error': 'Device not found'}), 404

@app.route('/api/flows', methods=['GET'])
def get_flows():
    """Get all flow rules"""
    flow_list = []
    for flow_id, flow_info in flows.items():
        flow_list.append(flow_info)
    return jsonify({'flows': flow_list})

@app.route('/api/flows/<device_id>', methods=['POST'])
def add_flow(device_id):
    """Add flow rule to device"""
    flow_config = request.get_json()
    
    if device_id not in devices:
        return jsonify({'error': 'Device not found'}), 404
    
    flow_id = f"{device_id}-{len(flows)}"
    flow_config['id'] = flow_id
    flow_config['device_id'] = device_id
    flow_config['status'] = 'INSTALLED'
    
    flows[flow_id] = flow_config
    logger.info(f"Flow installed: {flow_id}")
    
    return jsonify(flow_config), 201

@app.route('/api/networks', methods=['GET'])
def get_networks():
    """Get all logical networks"""
    network_list = list(networks.values())
    return jsonify({'networks': network_list})

@app.route('/api/networks', methods=['POST'])
def create_network():
    """Create logical network"""
    network_config = request.get_json()
    
    network_id = network_config.get('id', f"net-{len(networks)}")
    network_config['id'] = network_id
    network_config['status'] = 'CREATED'
    
    networks[network_id] = network_config
    logger.info(f"Network created: {network_id}")
    
    return jsonify(network_config), 201

@app.route('/api/policies', methods=['POST'])
def create_policy():
    """Create security policy"""
    policy_config = request.get_json()
    
    policy_id = policy_config.get('id', f"policy-{len(networks)}")
    policy_config['id'] = policy_id
    policy_config['status'] = 'ACTIVE'
    
    logger.info(f"Policy created: {policy_id}")
    logger.info(f"  Source: {policy_config.get('source')}")
    logger.info(f"  Dest: {policy_config.get('destination')}")
    logger.info(f"  Action: {policy_config.get('action')}")
    
    return jsonify(policy_config), 201

@app.route('/api/statistics/devices', methods=['GET'])
def get_device_stats():
    """Get device statistics"""
    stats = {
        'total_devices': len(devices),
        'online_devices': sum(1 for d in devices.values() if d.get('available')),
        'total_flows': len(flows),
        'timestamp': 'now'
    }
    return jsonify(stats)

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def server_error(error):
    logger.error(f"Server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Add sample device
    devices['of:0000000000000001'] = {
        'available': True,
        'role': 'MASTER',
        'manufacturer': 'Cisco'
    }
    
    app.run(host='0.0.0.0', port=8181, debug=False)
