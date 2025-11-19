#!/usr/bin/env python3
"""
Advanced Nornir-based network automation framework
Features:
- Multi-vendor configuration deployment
- Network validation and compliance checking
- Performance metrics collection
- Automated troubleshooting
- Result aggregation and reporting
- Error handling and rollback capabilities
"""

from nornir import InitNornir
from nornir.core.task import Task, Result
from nornir.core.filter import F
from nornir_napalm.plugins.tasks import napalm_get, napalm_configure, napalm_cli
from nornir_netmiko.tasks import netmiko_send_command, netmiko_send_config
from nornir_utils.plugins.functions import print_result
from nornir_jinja2.plugins.tasks import template_file
import logging
import json
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class NornirAutomation:
    """Advanced Nornir automation framework"""

    def __init__(self, config_file="config.yaml"):
        self.nr = InitNornir(config_file=config_file)
        self.results_dir = Path("results")
        self.results_dir.mkdir(exist_ok=True)

    def get_device_facts(self, task: Task) -> Result:
        """
        Collect comprehensive device facts

        Args:
            task: Nornir task object

        Returns:
            Result object with device facts
        """
        logger.info(f"Collecting facts from {task.host.name}")

        try:
            # Get facts using NAPALM
            result = task.run(
                task=napalm_get,
                getters=["facts", "interfaces", "arp_table", "lldp_neighbors", "bgp_neighbors"]
            )

            data = result[0].result

            # Extract and structure facts
            facts = {
                'hostname': data['facts']['hostname'],
                'vendor': data['facts']['vendor'],
                'model': data['facts']['model'],
                'os_version': data['facts']['os_version'],
                'serial_number': data['facts']['serial_number'],
                'uptime': data['facts']['uptime'],
                'interface_count': len(data['interfaces']),
                'interfaces_up': sum(1 for i in data['interfaces'].values() if i['is_up']),
                'arp_entries': len(data.get('arp_table', [])),
                'lldp_neighbors': len(data.get('lldp_neighbors', {})),
                'bgp_neighbors': len(data.get('bgp_neighbors', {}).get('global', {}).get('peers', {}))
            }

            logger.info(f"✓ Successfully collected facts from {task.host.name}")
            return Result(host=task.host, result=facts)

        except Exception as e:
            logger.error(f"✗ Failed to collect facts from {task.host.name}: {e}")
            return Result(host=task.host, failed=True, exception=e)

    def deploy_configuration(self, task: Task, config_template: str, **kwargs) -> Result:
        """
        Deploy configuration using Jinja2 templates

        Args:
            task: Nornir task object
            config_template: Path to Jinja2 template
            **kwargs: Template variables

        Returns:
            Result object with deployment status
        """
        logger.info(f"Deploying configuration to {task.host.name}")

        try:
            # Render template
            template_result = task.run(
                task=template_file,
                template=config_template,
                path="templates/",
                **kwargs
            )

            rendered_config = template_result[0].result

            # Deploy configuration
            deploy_result = task.run(
                task=napalm_configure,
                configuration=rendered_config,
                replace=False,
                dry_run=kwargs.get('dry_run', False)
            )

            if kwargs.get('dry_run'):
                logger.info(f"Dry-run completed for {task.host.name}")
                diff = deploy_result[0].result.get('diff', 'No changes')
                return Result(host=task.host, result={'diff': diff, 'dry_run': True})
            else:
                logger.info(f"✓ Successfully deployed configuration to {task.host.name}")
                return Result(host=task.host, result={'status': 'deployed'})

        except Exception as e:
            logger.error(f"✗ Failed to deploy configuration to {task.host.name}: {e}")
            return Result(host=task.host, failed=True, exception=e)

    def validate_connectivity(self, task: Task, targets: List[str]) -> Result:
        """
        Validate network connectivity using ping

        Args:
            task: Nornir task object
            targets: List of IP addresses to ping

        Returns:
            Result object with connectivity test results
        """
        logger.info(f"Validating connectivity from {task.host.name}")

        results = {}
        for target in targets:
            try:
                # Execute ping command
                if 'cisco' in task.host.platform.lower():
                    command = f"ping {target} repeat 5"
                elif 'juniper' in task.host.platform.lower():
                    command = f"ping {target} count 5"
                else:
                    command = f"ping {target}"

                output = task.run(
                    task=netmiko_send_command,
                    command_string=command
                )

                # Parse ping results (simplified)
                success = 'success rate is 100' in output[0].result.lower() or \
                         '5 packets transmitted, 5 received' in output[0].result.lower()

                results[target] = {
                    'reachable': success,
                    'output': output[0].result[:200]  # First 200 chars
                }

            except Exception as e:
                results[target] = {
                    'reachable': False,
                    'error': str(e)
                }

        all_reachable = all(r['reachable'] for r in results.values())
        if all_reachable:
            logger.info(f"✓ All connectivity tests passed for {task.host.name}")
        else:
            logger.warning(f"⚠ Some connectivity tests failed for {task.host.name}")

        return Result(host=task.host, result=results, failed=not all_reachable)

    def compliance_check(self, task: Task, compliance_rules: Dict[str, Any]) -> Result:
        """
        Check device compliance against defined rules

        Args:
            task: Nornir task object
            compliance_rules: Dictionary of compliance rules

        Returns:
            Result object with compliance status
        """
        logger.info(f"Running compliance checks on {task.host.name}")

        compliance_results = {}

        try:
            # Get device configuration
            config_result = task.run(task=napalm_get, getters=["config"])
            config = config_result[0].result['config']['running']

            # Check each compliance rule
            for rule_name, rule in compliance_rules.items():
                if rule['type'] == 'contains':
                    # Check if config contains required string
                    passed = rule['value'] in config
                elif rule['type'] == 'not_contains':
                    # Check if config does NOT contain string
                    passed = rule['value'] not in config
                elif rule['type'] == 'regex':
                    # Check if config matches regex
                    import re
                    passed = bool(re.search(rule['value'], config))
                else:
                    passed = False

                compliance_results[rule_name] = {
                    'passed': passed,
                    'severity': rule.get('severity', 'medium'),
                    'description': rule.get('description', '')
                }

            # Overall compliance status
            failed_checks = [r for r in compliance_results.values() if not r['passed']]
            compliance_passed = len(failed_checks) == 0

            if compliance_passed:
                logger.info(f"✓ Compliance checks passed for {task.host.name}")
            else:
                logger.warning(f"⚠ {len(failed_checks)} compliance check(s) failed for {task.host.name}")

            return Result(
                host=task.host,
                result=compliance_results,
                failed=not compliance_passed
            )

        except Exception as e:
            logger.error(f"✗ Compliance check failed for {task.host.name}: {e}")
            return Result(host=task.host, failed=True, exception=e)

    def collect_performance_metrics(self, task: Task) -> Result:
        """
        Collect performance metrics from device

        Args:
            task: Nornir task object

        Returns:
            Result object with performance metrics
        """
        logger.info(f"Collecting performance metrics from {task.host.name}")

        metrics = {}

        try:
            # Commands vary by platform
            if 'cisco_ios' in task.host.platform:
                commands = {
                    'cpu': 'show processes cpu',
                    'memory': 'show memory statistics',
                    'interfaces': 'show interfaces summary'
                }
            elif 'juniper' in task.host.platform:
                commands = {
                    'cpu': 'show system processes',
                    'memory': 'show system memory',
                    'interfaces': 'show interfaces terse'
                }
            else:
                commands = {}

            for metric_name, command in commands.items():
                result = task.run(
                    task=netmiko_send_command,
                    command_string=command
                )
                metrics[metric_name] = result[0].result

            logger.info(f"✓ Collected metrics from {task.host.name}")
            return Result(host=task.host, result=metrics)

        except Exception as e:
            logger.error(f"✗ Failed to collect metrics from {task.host.name}: {e}")
            return Result(host=task.host, failed=True, exception=e)

    def save_results(self, results, output_file: str):
        """Save results to JSON file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filepath = self.results_dir / f"{output_file}_{timestamp}.json"

        results_dict = {}
        for host, result in results.items():
            results_dict[host] = {
                'failed': result.failed,
                'result': result.result if hasattr(result, 'result') else None,
                'exception': str(result.exception) if result.failed else None
            }

        with open(filepath, 'w') as f:
            json.dump(results_dict, f, indent=2, default=str)

        logger.info(f"Results saved to {filepath}")
        return filepath

    def generate_summary(self, results) -> str:
        """Generate summary report of results"""
        total = len(results)
        success = sum(1 for r in results.values() if not r.failed)
        failed = sum(1 for r in results.values() if r.failed)

        summary = f"""
Nornir Automation Summary
{'=' * 60}
Total Devices: {total}
Successful: {success}
Failed: {failed}
Success Rate: {(success/total*100) if total > 0 else 0:.1f}%

"""

        if failed > 0:
            summary += "Failed Devices:\n"
            for host, result in results.items():
                if result.failed:
                    summary += f"  - {host}: {result.exception}\n"

        return summary


def main():
    parser = argparse.ArgumentParser(description='Advanced Nornir Network Automation')
    parser.add_argument('action', choices=[
        'facts', 'deploy', 'validate', 'compliance', 'metrics'
    ], help='Action to perform')
    parser.add_argument('-c', '--config', default='config.yaml', help='Nornir config file')
    parser.add_argument('-f', '--filter', help='Filter hosts (e.g., "site=dc1")')
    parser.add_argument('--template', help='Template file for deployment')
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode')
    parser.add_argument('--compliance-file', help='Compliance rules YAML file')
    parser.add_argument('--output', help='Output file name')

    args = parser.parse_args()

    # Initialize Nornir
    automation = NornirAutomation(config_file=args.config)

    # Apply filter if specified
    if args.filter:
        key, value = args.filter.split('=')
        nr = automation.nr.filter(F(**{key: value}))
    else:
        nr = automation.nr

    # Execute action
    if args.action == 'facts':
        logger.info("Collecting device facts...")
        results = nr.run(task=automation.get_device_facts)
        print_result(results)
        automation.save_results(results, args.output or 'facts')

    elif args.action == 'deploy':
        if not args.template:
            logger.error("Template file required for deployment")
            return

        logger.info(f"Deploying configuration from template: {args.template}")
        results = nr.run(
            task=automation.deploy_configuration,
            config_template=args.template,
            dry_run=args.dry_run
        )
        print_result(results)
        automation.save_results(results, args.output or 'deploy')

    elif args.action == 'validate':
        targets = ['8.8.8.8', '1.1.1.1']  # Default targets
        logger.info(f"Validating connectivity to: {targets}")
        results = nr.run(task=automation.validate_connectivity, targets=targets)
        print_result(results)
        automation.save_results(results, args.output or 'validate')

    elif args.action == 'compliance':
        if not args.compliance_file:
            logger.error("Compliance rules file required")
            return

        with open(args.compliance_file, 'r') as f:
            rules = yaml.safe_load(f)

        logger.info("Running compliance checks...")
        results = nr.run(task=automation.compliance_check, compliance_rules=rules)
        print_result(results)
        automation.save_results(results, args.output or 'compliance')

    elif args.action == 'metrics':
        logger.info("Collecting performance metrics...")
        results = nr.run(task=automation.collect_performance_metrics)
        print_result(results)
        automation.save_results(results, args.output or 'metrics')

    # Print summary
    summary = automation.generate_summary(results)
    print(summary)


if __name__ == '__main__':
    main()
