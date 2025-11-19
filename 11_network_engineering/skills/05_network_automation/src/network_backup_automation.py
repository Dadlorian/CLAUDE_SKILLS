#!/usr/bin/env python3
"""
Production-ready automated network configuration backup script
Features:
- Multi-vendor support (Cisco, Juniper, Arista, etc.)
- Git version control integration
- Differential backups (only save if config changed)
- Email notifications on failures
- Comprehensive logging
- Parallel execution for large deployments
- Retry logic with exponential backoff
"""

from napalm import get_network_driver
from netmiko import ConnectHandler
import os
import sys
import json
import yaml
import logging
import hashlib
import smtplib
import argparse
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import subprocess
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'backup_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class NetworkBackupManager:
    """Manages network device configuration backups with Git integration"""

    def __init__(self, backup_dir='backups', git_enabled=True, max_workers=10):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.git_enabled = git_enabled
        self.max_workers = max_workers
        self.backup_results = {'success': [], 'failed': []}

        if self.git_enabled:
            self._init_git_repo()

    def _init_git_repo(self):
        """Initialize Git repository for version control"""
        git_dir = self.backup_dir / '.git'
        if not git_dir.exists():
            logger.info(f"Initializing Git repository in {self.backup_dir}")
            try:
                subprocess.run(['git', 'init'], cwd=self.backup_dir, check=True,
                             capture_output=True)
                subprocess.run(['git', 'config', 'user.name', 'Network Backup Bot'],
                             cwd=self.backup_dir, check=True)
                subprocess.run(['git', 'config', 'user.email', 'backup@network.local'],
                             cwd=self.backup_dir, check=True)
                logger.info("Git repository initialized successfully")
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to initialize Git: {e}")
                self.git_enabled = False

    def _calculate_checksum(self, content):
        """Calculate MD5 checksum of configuration"""
        return hashlib.md5(content.encode()).hexdigest()

    def _has_config_changed(self, filepath, new_content):
        """Check if configuration has changed since last backup"""
        if not filepath.exists():
            return True

        with open(filepath, 'r') as f:
            old_content = f.read()

        return self._calculate_checksum(old_content) != self._calculate_checksum(new_content)

    def backup_device_napalm(self, device_info, retries=3):
        """
        Backup single device using NAPALM with retry logic

        Args:
            device_info: Dict with device connection details
            retries: Number of retry attempts

        Returns:
            Dict with backup status and details
        """
        hostname = device_info.get('hostname', device_info['host'])
        logger.info(f"Starting backup for {hostname}")

        for attempt in range(retries):
            try:
                # Get NAPALM driver
                driver = get_network_driver(device_info['driver'])

                # Connect to device
                device = driver(
                    hostname=device_info['host'],
                    username=device_info['username'],
                    password=device_info['password'],
                    timeout=device_info.get('timeout', 60),
                    optional_args=device_info.get('optional_args', {})
                )

                device.open()
                logger.info(f"Connected to {hostname}")

                # Get configurations
                configs = device.get_config()
                running_config = configs.get('running', '')
                startup_config = configs.get('startup', '')

                # Get device facts for metadata
                facts = device.get_facts()

                device.close()

                # Prepare backup directory for this device
                device_dir = self.backup_dir / hostname
                device_dir.mkdir(exist_ok=True)

                # File paths
                running_file = device_dir / 'running-config.txt'
                startup_file = device_dir / 'startup-config.txt'
                metadata_file = device_dir / 'metadata.json'

                # Check if configuration changed
                config_changed = self._has_config_changed(running_file, running_config)

                if config_changed or not running_file.exists():
                    # Save configurations
                    with open(running_file, 'w') as f:
                        f.write(running_config)
                    logger.info(f"Saved running config for {hostname}")

                    if startup_config:
                        with open(startup_file, 'w') as f:
                            f.write(startup_config)
                        logger.info(f"Saved startup config for {hostname}")

                    # Save metadata
                    metadata = {
                        'hostname': hostname,
                        'backup_time': datetime.now().isoformat(),
                        'vendor': facts.get('vendor', 'Unknown'),
                        'model': facts.get('model', 'Unknown'),
                        'os_version': facts.get('os_version', 'Unknown'),
                        'serial_number': facts.get('serial_number', 'Unknown'),
                        'checksum': self._calculate_checksum(running_config)
                    }

                    with open(metadata_file, 'w') as f:
                        json.dump(metadata, f, indent=2)

                    # Git commit if enabled
                    if self.git_enabled:
                        self._git_commit(hostname)

                    logger.info(f"✓ Successfully backed up {hostname}")
                    self.backup_results['success'].append(hostname)

                    return {
                        'status': 'success',
                        'hostname': hostname,
                        'changed': True,
                        'message': 'Backup completed successfully'
                    }
                else:
                    logger.info(f"No configuration changes detected for {hostname}")
                    self.backup_results['success'].append(hostname)

                    return {
                        'status': 'success',
                        'hostname': hostname,
                        'changed': False,
                        'message': 'No changes detected'
                    }

            except Exception as e:
                wait_time = 2 ** attempt  # Exponential backoff
                logger.warning(f"Attempt {attempt + 1}/{retries} failed for {hostname}: {e}")

                if attempt < retries - 1:
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"✗ Failed to backup {hostname} after {retries} attempts: {e}")
                    self.backup_results['failed'].append({
                        'hostname': hostname,
                        'error': str(e)
                    })

                    return {
                        'status': 'failed',
                        'hostname': hostname,
                        'error': str(e)
                    }

        return None

    def _git_commit(self, hostname):
        """Commit device backup to Git"""
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            device_dir = hostname

            # Git add
            subprocess.run(['git', 'add', device_dir],
                         cwd=self.backup_dir, check=True, capture_output=True)

            # Git commit
            commit_msg = f"Backup {hostname} - {timestamp}"
            subprocess.run(['git', 'commit', '-m', commit_msg],
                         cwd=self.backup_dir, check=True, capture_output=True)

            logger.info(f"Git commit created for {hostname}")
        except subprocess.CalledProcessError:
            # No changes to commit
            pass
        except Exception as e:
            logger.warning(f"Git commit failed for {hostname}: {e}")

    def backup_devices_parallel(self, devices):
        """Backup multiple devices in parallel"""
        logger.info(f"Starting parallel backup of {len(devices)} devices with {self.max_workers} workers")

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_device = {
                executor.submit(self.backup_device_napalm, device): device
                for device in devices
            }

            for future in as_completed(future_to_device):
                device = future_to_device[future]
                try:
                    result = future.result()
                    if result:
                        logger.info(f"Completed: {result['hostname']} - {result['message']}")
                except Exception as e:
                    logger.error(f"Unexpected error for device: {e}")

    def generate_report(self):
        """Generate backup summary report"""
        total = len(self.backup_results['success']) + len(self.backup_results['failed'])
        success_count = len(self.backup_results['success'])
        failed_count = len(self.backup_results['failed'])

        report = f"""
Network Backup Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'=' * 60}

Total Devices: {total}
Successful: {success_count}
Failed: {failed_count}
Success Rate: {(success_count/total*100) if total > 0 else 0:.1f}%

"""

        if self.backup_results['failed']:
            report += "\nFailed Backups:\n"
            for failure in self.backup_results['failed']:
                report += f"  - {failure['hostname']}: {failure['error']}\n"

        logger.info(report)
        return report

    def send_email_notification(self, smtp_config, recipients):
        """Send email notification with backup results"""
        try:
            msg = MIMEMultipart()
            msg['From'] = smtp_config['from']
            msg['To'] = ', '.join(recipients)
            msg['Subject'] = f"Network Backup Report - {datetime.now().strftime('%Y-%m-%d')}"

            body = self.generate_report()
            msg.attach(MIMEText(body, 'plain'))

            with smtplib.SMTP(smtp_config['server'], smtp_config['port']) as server:
                if smtp_config.get('use_tls'):
                    server.starttls()
                if smtp_config.get('username'):
                    server.login(smtp_config['username'], smtp_config['password'])
                server.send_message(msg)

            logger.info("Email notification sent successfully")
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")


def load_inventory(inventory_file):
    """Load device inventory from YAML file"""
    with open(inventory_file, 'r') as f:
        return yaml.safe_load(f)


def main():
    parser = argparse.ArgumentParser(description='Network Configuration Backup Tool')
    parser.add_argument('-i', '--inventory', required=True, help='Inventory file (YAML)')
    parser.add_argument('-d', '--backup-dir', default='backups', help='Backup directory')
    parser.add_argument('--no-git', action='store_true', help='Disable Git integration')
    parser.add_argument('-w', '--workers', type=int, default=10, help='Number of parallel workers')
    parser.add_argument('--email', help='Email notification config file (YAML)')

    args = parser.parse_args()

    # Load inventory
    logger.info(f"Loading inventory from {args.inventory}")
    inventory = load_inventory(args.inventory)
    devices = inventory.get('devices', [])

    if not devices:
        logger.error("No devices found in inventory")
        sys.exit(1)

    # Initialize backup manager
    backup_manager = NetworkBackupManager(
        backup_dir=args.backup_dir,
        git_enabled=not args.no_git,
        max_workers=args.workers
    )

    # Run backups
    backup_manager.backup_devices_parallel(devices)

    # Generate report
    report = backup_manager.generate_report()

    # Send email notification if configured
    if args.email:
        email_config = load_inventory(args.email)
        backup_manager.send_email_notification(
            email_config['smtp'],
            email_config['recipients']
        )

    # Exit with appropriate code
    if backup_manager.backup_results['failed']:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
