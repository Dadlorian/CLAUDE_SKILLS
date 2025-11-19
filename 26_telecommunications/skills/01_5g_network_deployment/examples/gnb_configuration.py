#!/usr/bin/env python3
"""
gNodeB Configuration and Management System
Automated configuration for 5G base stations
"""

import json
import yaml
import ipaddress
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
from enum import Enum


class FrequencyBand(Enum):
    """5G NR Frequency Bands"""
    N1 = (2100, "FDD")    # 2.1 GHz
    N3 = (1800, "FDD")    # 1.8 GHz
    N7 = (2600, "FDD")    # 2.6 GHz
    N28 = (700, "FDD")    # APT 700 MHz
    N41 = (2500, "TDD")   # 2.5 GHz TDD
    N77 = (3700, "TDD")   # 3.7 GHz (C-Band)
    N78 = (3500, "TDD")   # 3.5 GHz
    N79 = (4700, "TDD")   # 4.7 GHz
    N257 = (28000, "TDD") # 28 GHz mmWave
    N258 = (26000, "TDD") # 26 GHz mmWave


class CUDUSplitOption(Enum):
    """CU/DU Split Architecture Options"""
    OPTION_2 = "PDCP-RLC"      # Higher Layer Split
    OPTION_6 = "MAC-RLC"        # Mid-haul split
    OPTION_7_1 = "High-PHY-Low-PHY"  # Lower layer split (Intra-PHY)
    OPTION_7_2 = "MAC-PHY"      # Lower Layer Split
    OPTION_8 = "PHY-RF"         # Fronthaul split


@dataclass
class RFConfiguration:
    """RF Configuration Parameters"""
    frequency_band: FrequencyBand
    channel_bandwidth_mhz: int  # 5, 10, 15, 20, 40, 60, 80, 100
    dl_arfcn: int
    ul_arfcn: int
    subcarrier_spacing_khz: int  # 15, 30, 60, 120
    tx_power_dbm: float
    antenna_configuration: str  # e.g., "64T64R", "32T32R"
    mimo_layers: int
    beamforming_enabled: bool

    def validate(self) -> List[str]:
        """Validate RF configuration parameters"""
        errors = []

        # Validate bandwidth
        valid_bandwidths = [5, 10, 15, 20, 40, 60, 80, 100]
        if self.channel_bandwidth_mhz not in valid_bandwidths:
            errors.append(f"Invalid bandwidth: {self.channel_bandwidth_mhz}")

        # Validate SCS
        valid_scs = [15, 30, 60, 120]
        if self.subcarrier_spacing_khz not in valid_scs:
            errors.append(f"Invalid SCS: {self.subcarrier_spacing_khz}")

        # Validate power
        if not (20 <= self.tx_power_dbm <= 50):
            errors.append(f"TX power out of range: {self.tx_power_dbm}")

        return errors


@dataclass
class TimingSync:
    """Timing Synchronization Configuration"""
    primary_source: str  # "GPS", "PTP", "SyncE"
    gps_enabled: bool
    ptp_profile: str  # "G.8275.1", "G.8275.2"
    synce_enabled: bool
    holdover_capability_hours: int

    def get_config(self) -> Dict:
        """Generate timing sync configuration"""
        return {
            "primary_reference": self.primary_source,
            "gps": {
                "enabled": self.gps_enabled,
                "antenna_type": "active" if self.gps_enabled else None,
                "holdover_hours": self.holdover_capability_hours
            },
            "ptp": {
                "enabled": self.primary_source == "PTP",
                "profile": self.ptp_profile,
                "domain": 24,
                "priority1": 128,
                "priority2": 128
            },
            "synce": {
                "enabled": self.synce_enabled,
                "quality_level": "QL-PRC"
            }
        }


@dataclass
class CUDUConfiguration:
    """CU/DU Split Configuration"""
    split_option: CUDUSplitOption
    fronthaul_interface: str  # "eCPRI", "CPRI", "Ethernet"
    fronthaul_bandwidth_mbps: int
    fronthaul_latency_ms: float
    compression_enabled: bool
    compression_ratio: Optional[float] = None

    def calculate_fronthaul_requirements(self, antenna_count: str,
                                         bandwidth_mhz: int) -> Dict:
        """Calculate fronthaul bandwidth requirements"""

        # Extract antenna count (e.g., "64T64R" -> 64)
        tx_count = int(antenna_count.split('T')[0])

        # Base calculation for Option 7-2 (most demanding)
        if self.split_option == CUDUSplitOption.OPTION_7_2:
            # Approximate: samples_per_sec * bits_per_sample * antennas
            samples_per_sec = bandwidth_mhz * 1e6 * 2  # IQ samples
            bits_per_sample = 16  # 16-bit IQ
            raw_bandwidth = samples_per_sec * bits_per_sample * tx_count / 1e6

            if self.compression_enabled and self.compression_ratio:
                effective_bandwidth = raw_bandwidth / self.compression_ratio
            else:
                effective_bandwidth = raw_bandwidth

            return {
                "raw_bandwidth_mbps": round(raw_bandwidth, 2),
                "effective_bandwidth_mbps": round(effective_bandwidth, 2),
                "compression": "enabled" if self.compression_enabled else "disabled",
                "compression_ratio": self.compression_ratio
            }
        else:
            # Higher layer splits require less bandwidth
            multiplier = {
                CUDUSplitOption.OPTION_2: 0.01,
                CUDUSplitOption.OPTION_6: 0.05,
                CUDUSplitOption.OPTION_7_1: 0.5
            }.get(self.split_option, 1.0)

            estimated_bandwidth = bandwidth_mhz * 10 * multiplier

            return {
                "estimated_bandwidth_mbps": round(estimated_bandwidth, 2),
                "split_type": self.split_option.value
            }


@dataclass
class NetworkConnectivity:
    """Network Connectivity Configuration"""
    amf_addresses: List[str]
    upf_n3_address: str
    local_n2_address: str
    local_n3_address: str
    vlan_id: Optional[int] = None

    def validate_addresses(self) -> List[str]:
        """Validate IP addresses"""
        errors = []

        # Validate AMF addresses
        for amf_addr in self.amf_addresses:
            try:
                # Remove port if present
                addr = amf_addr.split(':')[0]
                ipaddress.ip_address(addr)
            except ValueError:
                errors.append(f"Invalid AMF address: {amf_addr}")

        # Validate UPF and local addresses
        for addr_name, addr in [
            ("UPF N3", self.upf_n3_address),
            ("Local N2", self.local_n2_address),
            ("Local N3", self.local_n3_address)
        ]:
            try:
                ipaddress.ip_address(addr)
            except ValueError:
                errors.append(f"Invalid {addr_name} address: {addr}")

        return errors


@dataclass
class GNodeBConfiguration:
    """Complete gNodeB Configuration"""
    node_id: str
    site_name: str
    latitude: float
    longitude: float
    rf_config: RFConfiguration
    timing_sync: TimingSync
    cu_du_config: CUDUConfiguration
    network_connectivity: NetworkConnectivity
    max_ues: int = 10000
    max_active_bearers: int = 50000
    tracking_area_code: str = "000001"
    plmn_mcc: str = "310"
    plmn_mnc: str = "410"

    def validate(self) -> Dict[str, List[str]]:
        """Validate entire configuration"""
        validation_results = {}

        # Validate RF configuration
        rf_errors = self.rf_config.validate()
        if rf_errors:
            validation_results['rf_configuration'] = rf_errors

        # Validate network connectivity
        network_errors = self.network_connectivity.validate_addresses()
        if network_errors:
            validation_results['network_connectivity'] = network_errors

        # Validate coordinates
        if not (-90 <= self.latitude <= 90):
            validation_results.setdefault('location', []).append(
                f"Invalid latitude: {self.latitude}"
            )
        if not (-180 <= self.longitude <= 180):
            validation_results.setdefault('location', []).append(
                f"Invalid longitude: {self.longitude}"
            )

        return validation_results

    def to_yaml(self) -> str:
        """Export configuration as YAML"""
        config_dict = {
            "gNodeB": {
                "node_id": self.node_id,
                "site_name": self.site_name,
                "location": {
                    "latitude": self.latitude,
                    "longitude": self.longitude
                },
                "plmn": {
                    "mcc": self.plmn_mcc,
                    "mnc": self.plmn_mnc
                },
                "tracking_area_code": self.tracking_area_code,
                "rf_configuration": {
                    "frequency_band": self.rf_config.frequency_band.name,
                    "channel_bandwidth_mhz": self.rf_config.channel_bandwidth_mhz,
                    "dl_arfcn": self.rf_config.dl_arfcn,
                    "ul_arfcn": self.rf_config.ul_arfcn,
                    "subcarrier_spacing_khz": self.rf_config.subcarrier_spacing_khz,
                    "tx_power_dbm": self.rf_config.tx_power_dbm,
                    "antenna_configuration": self.rf_config.antenna_configuration,
                    "mimo_layers": self.rf_config.mimo_layers,
                    "beamforming_enabled": self.rf_config.beamforming_enabled
                },
                "timing_synchronization": self.timing_sync.get_config(),
                "cu_du_split": {
                    "split_option": self.cu_du_config.split_option.value,
                    "fronthaul_interface": self.cu_du_config.fronthaul_interface,
                    "fronthaul_bandwidth_mbps": self.cu_du_config.fronthaul_bandwidth_mbps,
                    "fronthaul_latency_ms": self.cu_du_config.fronthaul_latency_ms,
                    "compression": {
                        "enabled": self.cu_du_config.compression_enabled,
                        "ratio": self.cu_du_config.compression_ratio
                    },
                    "requirements": self.cu_du_config.calculate_fronthaul_requirements(
                        self.rf_config.antenna_configuration,
                        self.rf_config.channel_bandwidth_mhz
                    )
                },
                "network_connectivity": {
                    "amf_addresses": self.network_connectivity.amf_addresses,
                    "upf_n3_address": self.network_connectivity.upf_n3_address,
                    "local_n2_address": self.network_connectivity.local_n2_address,
                    "local_n3_address": self.network_connectivity.local_n3_address,
                    "vlan_id": self.network_connectivity.vlan_id
                },
                "capacity": {
                    "max_ues": self.max_ues,
                    "max_active_bearers": self.max_active_bearers
                }
            }
        }

        return yaml.dump(config_dict, default_flow_style=False, sort_keys=False)

    def to_json(self) -> str:
        """Export configuration as JSON"""
        config_dict = yaml.safe_load(self.to_yaml())
        return json.dumps(config_dict, indent=2)

    def generate_deployment_script(self) -> str:
        """Generate deployment script for gNodeB"""
        script = f"""#!/bin/bash
# gNodeB Deployment Script
# Node ID: {self.node_id}
# Site: {self.site_name}

set -e

echo "Starting gNodeB deployment for {self.node_id}..."

# Step 1: Network configuration
echo "[1/6] Configuring network interfaces..."
ip addr add {self.network_connectivity.local_n2_address}/24 dev eth0
ip addr add {self.network_connectivity.local_n3_address}/24 dev eth1

# Step 2: Timing synchronization
echo "[2/6] Configuring timing synchronization..."
systemctl start ptp4l
ptp4l -i eth0 -m -s &

# Step 3: Load gNodeB configuration
echo "[3/6] Loading gNodeB configuration..."
cp /tmp/gnb_config.yaml /etc/gnb/config.yaml

# Step 4: Start gNodeB service
echo "[4/6] Starting gNodeB service..."
systemctl start gnb

# Step 5: Verify N2 connectivity to AMF
echo "[5/6] Verifying N2 connectivity..."
for amf in {' '.join(self.network_connectivity.amf_addresses)}; do
    echo "Testing connectivity to $amf..."
    nc -zv $(echo $amf | cut -d: -f1) $(echo $amf | cut -d: -f2)
done

# Step 6: Check service status
echo "[6/6] Checking service status..."
systemctl status gnb

echo "gNodeB deployment completed successfully!"
echo "Node ID: {self.node_id}"
echo "Status: Active"
"""
        return script


def create_sample_configuration() -> GNodeBConfiguration:
    """Create a sample gNodeB configuration"""

    rf_config = RFConfiguration(
        frequency_band=FrequencyBand.N78,
        channel_bandwidth_mhz=100,
        dl_arfcn=632628,
        ul_arfcn=632628,
        subcarrier_spacing_khz=30,
        tx_power_dbm=43.0,
        antenna_configuration="64T64R",
        mimo_layers=4,
        beamforming_enabled=True
    )

    timing_sync = TimingSync(
        primary_source="GPS",
        gps_enabled=True,
        ptp_profile="G.8275.1",
        synce_enabled=True,
        holdover_capability_hours=72
    )

    cu_du_config = CUDUConfiguration(
        split_option=CUDUSplitOption.OPTION_7_2,
        fronthaul_interface="eCPRI",
        fronthaul_bandwidth_mbps=25000,
        fronthaul_latency_ms=3.0,
        compression_enabled=True,
        compression_ratio=4.0
    )

    network_connectivity = NetworkConnectivity(
        amf_addresses=["10.0.1.10:38412", "10.0.1.11:38412"],
        upf_n3_address="10.0.2.10",
        local_n2_address="10.10.1.100",
        local_n3_address="10.10.2.100",
        vlan_id=100
    )

    return GNodeBConfiguration(
        node_id="gnb_sf_001",
        site_name="San Francisco Downtown",
        latitude=37.7749,
        longitude=-122.4194,
        rf_config=rf_config,
        timing_sync=timing_sync,
        cu_du_config=cu_du_config,
        network_connectivity=network_connectivity,
        max_ues=10000,
        max_active_bearers=50000,
        tracking_area_code="000001",
        plmn_mcc="310",
        plmn_mnc="410"
    )


if __name__ == "__main__":
    print("gNodeB Configuration Generator")
    print("=" * 60)

    # Create sample configuration
    gnb_config = create_sample_configuration()

    # Validate configuration
    print("\n[Validation]")
    validation_errors = gnb_config.validate()
    if validation_errors:
        print("❌ Configuration has errors:")
        for category, errors in validation_errors.items():
            print(f"\n{category}:")
            for error in errors:
                print(f"  - {error}")
    else:
        print("✅ Configuration is valid")

    # Calculate fronthaul requirements
    print("\n[Fronthaul Requirements]")
    requirements = gnb_config.cu_du_config.calculate_fronthaul_requirements(
        gnb_config.rf_config.antenna_configuration,
        gnb_config.rf_config.channel_bandwidth_mhz
    )
    for key, value in requirements.items():
        print(f"  {key}: {value}")

    # Export configuration
    print("\n[Export]")
    with open("/tmp/gnb_config.yaml", "w") as f:
        f.write(gnb_config.to_yaml())
    print("✅ YAML configuration saved to /tmp/gnb_config.yaml")

    with open("/tmp/gnb_config.json", "w") as f:
        f.write(gnb_config.to_json())
    print("✅ JSON configuration saved to /tmp/gnb_config.json")

    # Generate deployment script
    with open("/tmp/deploy_gnb.sh", "w") as f:
        f.write(gnb_config.generate_deployment_script())
    print("✅ Deployment script saved to /tmp/deploy_gnb.sh")

    print("\n" + "=" * 60)
    print("Configuration generation complete!")
