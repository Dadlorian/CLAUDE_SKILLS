#!/usr/bin/env python3
"""
Compliance Management API
RESTful API for compliance operations and integrations
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from enum import Enum

class APIEndpointStatus(Enum):
    OPERATIONAL = "operational"
    DEGRADED = "degraded"
    DOWN = "down"

class ComplianceAPIServer:
    """REST API for compliance management operations"""

    def __init__(self, api_version: str = "v1"):
        self.api_version = api_version
        self.endpoints = {}
        self.api_clients = {}
        self.rate_limits = {}
        self.audit_logs = []

    def register_api_endpoint(self, endpoint_name: str,
                             resource_type: str,
                             methods: List[str],
                             authentication_required: bool) -> Dict:
        """
        Register API endpoint

        Args:
            endpoint_name: Name of endpoint
            resource_type: Type of resource (compliance_policies, incidents, etc.)
            methods: HTTP methods supported (GET, POST, PUT, DELETE)
            authentication_required: Whether authentication is required

        Returns:
            Endpoint registration confirmation
        """
        try:
            if not all([endpoint_name, resource_type, methods]):
                raise ValueError("Endpoint name, resource type, and methods required")

            endpoint_id = f"EP_{endpoint_name}_{datetime.now().strftime('%Y%m%d')}"

            endpoint = {
                'endpoint_id': endpoint_id,
                'endpoint_name': endpoint_name,
                'resource_type': resource_type,
                'url_path': f"/api/{self.api_version}/{resource_type}",
                'methods': methods,
                'authentication_required': authentication_required,
                'authentication_type': 'OAuth 2.0' if authentication_required else 'None',
                'rate_limit': '1000 requests/hour',
                'response_format': 'JSON',
                'documentation_url': f"https://docs.api.example.com/{resource_type}",
                'status': APIEndpointStatus.OPERATIONAL.value,
                'created_date': datetime.now().isoformat(),
                'last_tested': datetime.now().isoformat(),
                'uptime_percentage': 99.95
            }

            self.endpoints[endpoint_id] = endpoint

            return {
                'endpoint_id': endpoint_id,
                'status': 'registered',
                'url': endpoint.get('url_path'),
                'message': f'Endpoint {endpoint_name} registered successfully'
            }
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e)
            }

    def manage_api_client(self, client_name: str, client_type: str,
                         allowed_endpoints: List[str],
                         rate_limit: str) -> Dict:
        """
        Register and manage API client

        Args:
            client_name: Name of API client/application
            client_type: Type of client (internal, partner, third-party)
            allowed_endpoints: List of endpoints client can access
            rate_limit: Rate limit for client

        Returns:
            API client credentials and configuration
        """
        try:
            if not all([client_name, client_type, allowed_endpoints]):
                raise ValueError("Client name, type, and endpoints required")

            client_id = f"CLIENT_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            client = {
                'client_id': client_id,
                'client_name': client_name,
                'client_type': client_type,
                'created_date': datetime.now().isoformat(),
                'allowed_endpoints': allowed_endpoints,
                'rate_limit': rate_limit,
                'api_key': f"key_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                'api_secret': 'secret_xxxxxxxxxxxx (encrypted)',
                'oauth_client_id': f"oauth_{client_id}",
                'oauth_client_secret': 'oauth_secret (encrypted)',
                'webhook_url': None,
                'webhook_events': ['incident_reported', 'policy_updated', 'compliance_scan_completed'],
                'authentication_method': 'OAuth 2.0',
                'ip_whitelist': ['203.0.113.0/24'],
                'tls_required': True,
                'signing_required': True,
                'client_status': 'active',
                'last_used': datetime.now().isoformat(),
                'usage_statistics': {
                    'requests_this_month': 15000,
                    'requests_limit': 1000000,
                    'success_rate': 99.8
                }
            }

            self.api_clients[client_id] = client

            return {
                'client_id': client_id,
                'api_key': client.get('api_key'),
                'status': 'active',
                'message': 'API client registered successfully'
            }
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e)
            }

    def make_api_request(self, client_id: str, endpoint: str,
                        method: str, request_body: Optional[Dict] = None) -> Dict:
        """
        Process API request with authentication and rate limiting

        Args:
            client_id: Client making request
            endpoint: API endpoint being called
            method: HTTP method
            request_body: Request payload

        Returns:
            API response
        """
        try:
            if client_id not in self.api_clients:
                raise ValueError(f"Client {client_id} not found")

            client = self.api_clients[client_id]

            # Check rate limit
            if not self._check_rate_limit(client_id):
                return {
                    'status': 429,
                    'error': 'Rate limit exceeded',
                    'retry_after_seconds': 3600
                }

            # Check endpoint access
            if endpoint not in client.get('allowed_endpoints', []):
                return {
                    'status': 403,
                    'error': 'Access to endpoint not allowed'
                }

            # Process request based on endpoint
            response = {
                'request_id': f"REQ_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'timestamp': datetime.now().isoformat(),
                'client_id': client_id,
                'endpoint': endpoint,
                'method': method,
                'status': 200,
                'data': self._generate_endpoint_response(endpoint, method, request_body)
            }

            # Log request
            self._log_api_request(client_id, endpoint, method, response['status'])

            return response
        except Exception as e:
            return {
                'status': 500,
                'error': str(e)
            }

    def retrieve_compliance_data(self, data_type: str,
                                filters: Optional[Dict] = None) -> Dict:
        """
        Retrieve compliance data via API

        Args:
            data_type: Type of data to retrieve (policies, incidents, assessments)
            filters: Optional filters (date range, severity, etc.)

        Returns:
            Compliance data
        """
        try:
            if not data_type:
                raise ValueError("Data type required")

            retrieval_id = f"RETR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            retrieval = {
                'retrieval_id': retrieval_id,
                'data_type': data_type,
                'request_timestamp': datetime.now().isoformat(),
                'filters': filters or {},
                'total_records': 0,
                'data': [],
                'pagination': {
                    'page': 1,
                    'page_size': 100,
                    'total_pages': 1
                }
            }

            # Generate sample data based on type
            if data_type == 'policies':
                retrieval['total_records'] = 25
                retrieval['data'] = [
                    {'policy_id': f'POL_{i:03d}', 'name': f'Policy {i}', 'status': 'active'}
                    for i in range(1, 6)
                ]
            elif data_type == 'incidents':
                retrieval['total_records'] = 12
                retrieval['data'] = [
                    {'incident_id': f'INC_{i:03d}', 'type': 'unauthorized_access', 'severity': 'high'}
                    for i in range(1, 4)
                ]
            elif data_type == 'assessments':
                retrieval['total_records'] = 8
                retrieval['data'] = [
                    {'assessment_id': f'ASSESS_{i:03d}', 'type': 'compliance_audit', 'status': 'completed'}
                    for i in range(1, 4)
                ]

            return retrieval
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e)
            }

    def webhook_event_registration(self, event_type: str,
                                   webhook_url: str,
                                   client_id: str) -> Dict:
        """
        Register webhook for event notifications

        Args:
            event_type: Type of event to monitor
            webhook_url: URL for webhook delivery
            client_id: Client registering webhook

        Returns:
            Webhook registration confirmation
        """
        try:
            if not all([event_type, webhook_url, client_id]):
                raise ValueError("Event type, webhook URL, and client ID required")

            if client_id not in self.api_clients:
                raise ValueError(f"Client {client_id} not found")

            webhook_id = f"WH_{client_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            webhook = {
                'webhook_id': webhook_id,
                'event_type': event_type,
                'webhook_url': webhook_url,
                'client_id': client_id,
                'registered_date': datetime.now().isoformat(),
                'status': 'active',
                'delivery_method': 'POST',
                'retry_policy': {
                    'max_retries': 3,
                    'retry_interval_seconds': 300
                },
                'last_delivery': None,
                'delivery_count': 0,
                'failure_count': 0,
                'test_status': 'pending_test'
            }

            return {
                'webhook_id': webhook_id,
                'status': 'registered',
                'message': f'Webhook for {event_type} registered successfully'
            }
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e)
            }

    def monitor_api_health(self) -> Dict:
        """
        Monitor API health and performance

        Returns:
            API health status
        """
        try:
            health_id = f"HEALTH_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            overall_status = APIEndpointStatus.OPERATIONAL.value
            total_endpoints = len(self.endpoints)
            operational = sum(1 for e in self.endpoints.values() if e.get('status') == APIEndpointStatus.OPERATIONAL.value)
            degraded = sum(1 for e in self.endpoints.values() if e.get('status') == APIEndpointStatus.DEGRADED.value)

            health = {
                'health_id': health_id,
                'check_timestamp': datetime.now().isoformat(),
                'overall_status': overall_status,
                'endpoint_status': {
                    'total_endpoints': total_endpoints,
                    'operational': operational,
                    'degraded': degraded,
                    'down': total_endpoints - operational - degraded
                },
                'performance_metrics': {
                    'average_response_time_ms': 125,
                    'p95_response_time_ms': 350,
                    'p99_response_time_ms': 750,
                    'requests_per_second': 450
                },
                'error_metrics': {
                    'error_rate_percentage': 0.2,
                    'errors_last_hour': 9,
                    'errors_last_24_hours': 156,
                    'most_common_error': 'Rate limit exceeded'
                },
                'dependencies': {
                    'database': 'healthy',
                    'cache_layer': 'healthy',
                    'external_services': 'healthy'
                },
                'last_incident': {
                    'incident_date': (datetime.now() - timedelta(days=15)).isoformat(),
                    'duration_minutes': 45,
                    'impact': 'degraded_service'
                }
            }

            return health
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e)
            }

    def generate_api_usage_report(self, time_period: str = 'last_30_days') -> Dict:
        """
        Generate API usage and analytics report

        Args:
            time_period: Time period for report

        Returns:
            API usage report
        """
        try:
            report_id = f"USAGE_{datetime.now().strftime('%Y%m%d')}"

            report = {
                'report_id': report_id,
                'report_date': datetime.now().isoformat(),
                'time_period': time_period,
                'summary': {
                    'total_requests': 450000,
                    'successful_requests': 449100,
                    'failed_requests': 900,
                    'success_rate': 99.8
                },
                'by_client': [
                    {
                        'client_name': 'Internal Dashboard',
                        'requests': 200000,
                        'success_rate': 99.9
                    },
                    {
                        'client_name': 'Partner Integration',
                        'requests': 150000,
                        'success_rate': 99.7
                    },
                    {
                        'client_name': 'Mobile App',
                        'requests': 100000,
                        'success_rate': 99.5
                    }
                ],
                'by_endpoint': [
                    {'endpoint': '/compliance_policies', 'requests': 150000},
                    {'endpoint': '/incidents', 'requests': 200000},
                    {'endpoint': '/assessments', 'requests': 100000}
                ],
                'response_time_distribution': {
                    'under_100ms': 60,
                    '100-500ms': 35,
                    '500-1000ms': 4,
                    'over_1000ms': 1
                },
                'error_distribution': {
                    '4xx_errors': 700,
                    '5xx_errors': 200
                },
                'peak_usage': {
                    'peak_time': '09:00-10:00 UTC',
                    'peak_requests_per_second': 850
                }
            }

            return report
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e)
            }

    # Private helper methods
    def _check_rate_limit(self, client_id: str) -> bool:
        """Check if client is within rate limit"""
        try:
            if client_id not in self.rate_limits:
                self.rate_limits[client_id] = {'count': 0, 'reset_time': datetime.now() + timedelta(hours=1)}

            limit_info = self.rate_limits[client_id]

            if datetime.now() > limit_info['reset_time']:
                limit_info['count'] = 0
                limit_info['reset_time'] = datetime.now() + timedelta(hours=1)

            limit_info['count'] += 1
            return limit_info['count'] <= 1000
        except:
            return True

    @staticmethod
    def _generate_endpoint_response(endpoint: str, method: str,
                                   request_body: Optional[Dict]) -> Dict:
        """Generate response for endpoint request"""
        try:
            return {
                'status': 'success',
                'message': f'Request to {endpoint} processed successfully',
                'data': {}
            }
        except:
            return {}

    def _log_api_request(self, client_id: str, endpoint: str,
                        method: str, status_code: int) -> None:
        """Log API request for audit trail"""
        try:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'client_id': client_id,
                'endpoint': endpoint,
                'method': method,
                'status_code': status_code
            }
            self.audit_logs.append(log_entry)
        except:
            pass


def main():
    """Main execution"""
    try:
        api = ComplianceAPIServer(api_version='v1')

        # Register endpoints
        endpoints = [
            {
                'name': 'policies',
                'resource_type': 'compliance_policies',
                'methods': ['GET', 'POST', 'PUT', 'DELETE'],
                'auth': True
            },
            {
                'name': 'incidents',
                'resource_type': 'incidents',
                'methods': ['GET', 'POST', 'PUT'],
                'auth': True
            }
        ]

        registered_endpoints = []
        for ep in endpoints:
            result = api.register_api_endpoint(
                endpoint_name=ep['name'],
                resource_type=ep['resource_type'],
                methods=ep['methods'],
                authentication_required=ep['auth']
            )
            registered_endpoints.append(result)

        # Register API client
        client = api.manage_api_client(
            client_name='Dashboard Application',
            client_type='internal',
            allowed_endpoints=['compliance_policies', 'incidents', 'assessments'],
            rate_limit='1000 requests/hour'
        )

        # Make API request
        if client.get('client_id'):
            api_request = api.make_api_request(
                client_id=client['client_id'],
                endpoint='compliance_policies',
                method='GET'
            )
        else:
            api_request = None

        # Retrieve data
        data = api.retrieve_compliance_data(
            data_type='incidents',
            filters={'severity': 'high'}
        )

        # Register webhook
        if client.get('client_id'):
            webhook = api.webhook_event_registration(
                event_type='incident_reported',
                webhook_url='https://client.example.com/webhooks/incident',
                client_id=client['client_id']
            )
        else:
            webhook = None

        # Health check
        health = api.monitor_api_health()

        # Usage report
        usage = api.generate_api_usage_report()

        print(json.dumps({
            'endpoints': registered_endpoints,
            'client': client,
            'request': api_request,
            'data': data,
            'webhook': webhook,
            'health': health,
            'usage': usage
        }, indent=2, default=str))
    except Exception as e:
        print(json.dumps({'error': str(e)}, indent=2))


if __name__ == '__main__':
    main()
