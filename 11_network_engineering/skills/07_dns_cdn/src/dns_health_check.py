#!/usr/bin/env python3
"""
DNS Server Health Check Script
Monitors DNS nameserver health and updates Route53/DNS records

Usage:
    python dns_health_check.py --nameservers ns1.example.com ns2.example.com --interval 30
    python dns_health_check.py --zone example.com --check-health
"""

import argparse
import dns.resolver
import logging
import time
import sys
from typing import List, Dict, Optional
from datetime import datetime
import boto3

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DNSHealthCheck:
    """DNS nameserver health checker"""

    def __init__(self, nameservers: List[str], test_domain: str = "example.com"):
        self.nameservers = nameservers
        self.test_domain = test_domain
        self.resolver = dns.resolver.Resolver()
        self.health_status = {ns: True for ns in nameservers}

    def check_nameserver(self, nameserver: str, timeout: int = 5) -> bool:
        """Check if nameserver responds to queries"""
        try:
            # Create resolver for this nameserver
            ns_resolver = dns.resolver.Resolver()
            ns_resolver.nameservers = [nameserver]
            ns_resolver.lifetime = timeout

            # Query test domain
            answers = ns_resolver.resolve(self.test_domain, "A")

            logger.info(f"✓ {nameserver}: Healthy (responded in <{timeout}s)")
            return True

        except dns.exception.Timeout:
            logger.error(f"✗ {nameserver}: Timeout")
            return False

        except dns.resolver.NXDOMAIN:
            logger.error(f"✗ {nameserver}: NXDOMAIN")
            return False

        except dns.exception.DNSException as e:
            logger.error(f"✗ {nameserver}: {str(e)}")
            return False

        except Exception as e:
            logger.error(f"✗ {nameserver}: Unexpected error: {e}")
            return False

    def check_all(self) -> Dict[str, bool]:
        """Check health of all nameservers"""
        logger.info(f"Checking health of {len(self.nameservers)} nameservers...")

        results = {}
        for nameserver in self.nameservers:
            results[nameserver] = self.check_nameserver(nameserver)

            # Update status
            if results[nameserver] != self.health_status[nameserver]:
                self.health_status[nameserver] = results[nameserver]
                status = "recovered" if results[nameserver] else "failed"
                logger.warning(f"Nameserver {nameserver} has {status}")

        return results

    def get_status_summary(self) -> Dict:
        """Get health check summary"""
        healthy = sum(1 for v in self.health_status.values() if v)
        total = len(self.health_status)

        return {
            "timestamp": datetime.now().isoformat(),
            "healthy_count": healthy,
            "total_count": total,
            "health_percentage": (healthy / total * 100) if total > 0 else 0,
            "nameservers": self.health_status
        }


class Route53HealthCheck:
    """AWS Route53 health check management"""

    def __init__(self, region: str = "us-east-1"):
        self.route53 = boto3.client("route53", region_name=region)
        self.cloudwatch = boto3.client("cloudwatch", region_name=region)

    def create_health_check(self, ip: str, port: int = 53,
                          check_type: str = "TCP",
                          failure_threshold: int = 3) -> Optional[str]:
        """Create Route53 health check"""
        try:
            response = self.route53.create_health_check(
                HealthCheckConfig={
                    "Type": check_type,
                    "IPAddress": ip,
                    "Port": port,
                    "RequestInterval": 30,
                    "FailureThreshold": failure_threshold,
                    "MeasureLatency": True
                },
                HealthCheckTags=[
                    {"Key": "Name", "Value": f"DNS-{ip}-{port}"}
                ]
            )

            health_check_id = response["HealthCheck"]["Id"]
            logger.info(f"Created health check: {health_check_id} for {ip}:{port}")
            return health_check_id

        except Exception as e:
            logger.error(f"Failed to create health check: {e}")
            return None

    def get_health_status(self, health_check_id: str) -> Dict:
        """Get health check status"""
        try:
            response = self.route53.get_health_check_status(
                HealthCheckId=health_check_id
            )

            status = response["HealthCheckObservations"][0]["StatusReport"]["Status"]
            return {
                "health_check_id": health_check_id,
                "status": status,
                "is_healthy": status == "Success"
            }

        except Exception as e:
            logger.error(f"Failed to get health check status: {e}")
            return {}

    def publish_metrics(self, metrics: Dict) -> bool:
        """Publish metrics to CloudWatch"""
        try:
            self.cloudwatch.put_metric_data(
                Namespace="DNS",
                MetricData=[
                    {
                        "MetricName": "NameserverHealth",
                        "Value": metrics["health_percentage"],
                        "Unit": "Percent",
                        "Timestamp": datetime.now()
                    },
                    {
                        "MetricName": "HealthyNameservers",
                        "Value": metrics["healthy_count"],
                        "Unit": "Count",
                        "Timestamp": datetime.now()
                    }
                ]
            )

            logger.info("Published metrics to CloudWatch")
            return True

        except Exception as e:
            logger.error(f"Failed to publish metrics: {e}")
            return False


class DNSRecordUpdateAlert:
    """Alert on DNS record changes"""

    def __init__(self, zone_id: str):
        self.route53 = boto3.client("route53")
        self.zone_id = zone_id

    def check_ns_records(self, expected_ns: List[str]) -> bool:
        """Check if NS records match expected values"""
        try:
            response = self.route53.list_resource_record_sets(
                HostedZoneId=self.zone_id,
                StartRecordName="example.com",
                StartRecordType="NS",
                MaxItems="1"
            )

            current_ns = set()
            for record in response["ResourceRecordSets"]:
                if record["Type"] == "NS":
                    for rr in record["ResourceRecords"]:
                        current_ns.add(rr["Value"].rstrip("."))

            expected_ns_set = set(expected_ns)

            if current_ns == expected_ns_set:
                logger.info("NS records match expected values")
                return True
            else:
                logger.error(f"NS records mismatch!")
                logger.error(f"Expected: {expected_ns_set}")
                logger.error(f"Current: {current_ns}")
                return False

        except Exception as e:
            logger.error(f"Failed to check NS records: {e}")
            return False


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="DNS server health check utility"
    )

    parser.add_argument(
        "--nameservers",
        nargs="+",
        required=True,
        help="List of nameserver IPs to check"
    )

    parser.add_argument(
        "--test-domain",
        default="example.com",
        help="Domain to query for health checks"
    )

    parser.add_argument(
        "--interval",
        type=int,
        default=30,
        help="Health check interval in seconds"
    )

    parser.add_argument(
        "--continuous",
        action="store_true",
        help="Run continuous health checks"
    )

    parser.add_argument(
        "--publish-metrics",
        action="store_true",
        help="Publish metrics to CloudWatch"
    )

    args = parser.parse_args()

    # Initialize health checker
    health_check = DNSHealthCheck(args.nameservers, args.test_domain)

    # Single check
    if not args.continuous:
        results = health_check.check_all()
        summary = health_check.get_status_summary()

        logger.info(f"Health Summary: {summary['healthy_count']}/{summary['total_count']} healthy")
        print(f"\nHealth Status: {summary['health_percentage']:.1f}% healthy")

        if args.publish_metrics:
            route53 = Route53HealthCheck()
            route53.publish_metrics(summary)

        return 0 if summary["healthy_count"] == summary["total_count"] else 1

    # Continuous checks
    logger.info(f"Starting continuous health checks every {args.interval} seconds")

    try:
        while True:
            health_check.check_all()
            summary = health_check.get_status_summary()

            logger.info(f"Summary: {summary['healthy_count']}/{summary['total_count']} healthy")

            if args.publish_metrics:
                route53 = Route53HealthCheck()
                route53.publish_metrics(summary)

            time.sleep(args.interval)

    except KeyboardInterrupt:
        logger.info("Health check stopped")
        return 0


if __name__ == "__main__":
    sys.exit(main())
