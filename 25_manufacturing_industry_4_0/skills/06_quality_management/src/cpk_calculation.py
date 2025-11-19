"""
Process Capability Index (Cpk) Calculation Module

This module provides comprehensive process capability analysis tools,
including Cp, Cpk, Pp, Ppk calculations and interpretations.

Author: Quality Engineering
License: MIT
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict
from enum import Enum


class CapabilityLevel(Enum):
    """Capability assessment levels"""
    INCAPABLE = "Incapable (< 1.0)"
    MARGINAL = "Marginal (1.0-1.33)"
    ACCEPTABLE = "Acceptable (1.33-1.67)"
    EXCELLENT = "Excellent (> 1.67)"


@dataclass
class SpecificationLimits:
    """Specification limit container"""
    nominal: float
    lower_spec: float  # LSL
    upper_spec: float  # USL

    @property
    def tolerance(self) -> float:
        """Total tolerance (USL - LSL)"""
        return self.upper_spec - self.lower_spec

    @property
    def is_two_sided(self) -> bool:
        """Check if both limits are specified"""
        return self.lower_spec is not None and self.upper_spec is not None


@dataclass
class ProcessStatistics:
    """Process performance statistics"""
    mean: float
    std_dev: float
    min_value: float
    max_value: float
    n_samples: int

    @property
    def range(self) -> float:
        """Range of measurements"""
        return self.max_value - self.min_value


class CapabilityIndex:
    """Calculate and interpret process capability indices"""

    def __init__(self, data: List[float], spec_limits: SpecificationLimits):
        """
        Initialize capability calculation

        Args:
            data: List of measurements
            spec_limits: SpecificationLimits object with LSL, nominal, USL
        """
        self.data = np.array(data)
        self.spec = spec_limits
        self.n = len(self.data)

        # Calculate statistics
        self.mean = np.mean(self.data)
        self.std_dev = np.std(self.data, ddof=1)  # Sample std dev
        self.pop_std_dev = np.std(self.data, ddof=0)  # Population std dev

        # Process statistics
        self.process_stats = ProcessStatistics(
            mean=self.mean,
            std_dev=self.std_dev,
            min_value=np.min(self.data),
            max_value=np.max(self.data),
            n_samples=self.n
        )

    def calculate_cp(self) -> float:
        """
        Calculate Cp - Process Capability Index (potential)

        Cp = (USL - LSL) / (6 * σ)

        Assumes process is centered on nominal.
        Cp > 1.33 is generally acceptable for most industries.
        Cp > 1.67 is required for automotive (IATF 16949).
        Cp > 2.0 is required for aerospace (AS9100D).

        Returns:
            Cp value
        """
        if not self.spec.is_two_sided:
            raise ValueError("Two-sided specification required for Cp")

        return self.spec.tolerance / (6 * self.std_dev)

    def calculate_cpk(self) -> float:
        """
        Calculate Cpk - Process Capability Index (centered)

        Cpk = min(CPU, CPL)
        where:
            CPU = (USL - Mean) / (3 * σ)  [Upper capability]
            CPL = (Mean - LSL) / (3 * σ)  [Lower capability]

        Cpk accounts for process centering.
        Values reflect actual process performance.

        Returns:
            Cpk value
        """
        if not self.spec.is_two_sided:
            raise ValueError("Two-sided specification required for Cpk")

        cpu = (self.spec.upper_spec - self.mean) / (3 * self.std_dev)
        cpl = (self.mean - self.spec.lower_spec) / (3 * self.std_dev)

        return min(cpu, cpl)

    def calculate_cpu(self) -> float:
        """Calculate upper process capability"""
        return (self.spec.upper_spec - self.mean) / (3 * self.std_dev)

    def calculate_cpl(self) -> float:
        """Calculate lower process capability"""
        return (self.mean - self.spec.lower_spec) / (3 * self.std_dev)

    def calculate_pp(self) -> float:
        """
        Calculate Pp - Performance Index (short-term potential)

        Similar to Cp but uses population standard deviation.
        Generally used for assessing performance over short periods.

        Returns:
            Pp value
        """
        if not self.spec.is_two_sided:
            raise ValueError("Two-sided specification required for Pp")

        return self.spec.tolerance / (6 * self.pop_std_dev)

    def calculate_ppk(self) -> float:
        """
        Calculate Ppk - Performance Index (centered)

        Similar to Cpk but uses population standard deviation.
        Reflects actual observed performance.

        Returns:
            Ppk value
        """
        if not self.spec.is_two_sided:
            raise ValueError("Two-sided specification required for Ppk")

        ppu = (self.spec.upper_spec - self.mean) / (3 * self.pop_std_dev)
        ppl = (self.mean - self.spec.lower_spec) / (3 * self.pop_std_dev)

        return min(ppu, ppl)

    def calculate_cpm(self, target: Optional[float] = None) -> float:
        """
        Calculate Cpm - Taguchi's Capability Index

        Cpm accounts for variation around a target value.
        Cpm = (USL - LSL) / (6 * √(σ² + (μ - T)²))

        where:
            T = target value (defaults to nominal)

        Returns:
            Cpm value
        """
        if target is None:
            target = self.spec.nominal

        variance = self.std_dev ** 2
        target_offset = (self.mean - target) ** 2
        denominator = 6 * np.sqrt(variance + target_offset)

        return self.spec.tolerance / denominator

    def calculate_sigma_level(self) -> float:
        """
        Convert Cpk to sigma level

        Sigma level = (Cpk × 3) + 1.5

        The 1.5 represents a shift in the process mean over time.
        6-sigma means Cpk ≥ 1.67 in short term.

        Returns:
            Sigma level (approximately)
        """
        cpk = self.calculate_cpk()
        return 3 * cpk + 1.5

    def calculate_dpmo(self) -> float:
        """
        Calculate DPMO - Defects Per Million Opportunities

        Based on sigma level using normal distribution.

        Returns:
            DPMO value
        """
        from scipy.stats import norm

        # Calculate defect rates from both tails
        cpu = self.calculate_cpu()
        cpl = self.calculate_cpl()

        # Probability of exceeding upper spec
        z_upper = cpu * 3
        p_upper = 1 - norm.cdf(z_upper) if z_upper > 0 else 1.0

        # Probability of going below lower spec
        z_lower = cpl * 3
        p_lower = norm.cdf(-z_lower) if z_lower > 0 else 1.0

        # Total defect probability
        p_defect = p_upper + p_lower

        # Convert to DPMO
        dpmo = p_defect * 1_000_000

        return max(0, min(dpmo, 1_000_000))

    def get_defect_count(self, total_parts: int) -> float:
        """
        Calculate expected defect count for a production run

        Args:
            total_parts: Number of parts produced

        Returns:
            Expected number of defects
        """
        dpmo = self.calculate_dpmo()
        return (dpmo / 1_000_000) * total_parts

    def assess_capability(self) -> CapabilityLevel:
        """Assess capability level based on Cpk"""
        cpk = self.calculate_cpk()

        if cpk < 1.0:
            return CapabilityLevel.INCAPABLE
        elif cpk < 1.33:
            return CapabilityLevel.MARGINAL
        elif cpk < 1.67:
            return CapabilityLevel.ACCEPTABLE
        else:
            return CapabilityLevel.EXCELLENT

    def get_centering_analysis(self) -> Dict[str, float]:
        """Analyze process centering"""
        nominal = self.spec.nominal
        center = (self.spec.lower_spec + self.spec.upper_spec) / 2

        offset = self.mean - nominal
        offset_percent = (offset / (self.spec.tolerance / 2)) * 100
        distance_to_lower = self.mean - self.spec.lower_spec
        distance_to_upper = self.spec.upper_spec - self.mean

        return {
            "mean": self.mean,
            "nominal": nominal,
            "center": center,
            "offset": offset,
            "offset_percent": offset_percent,
            "distance_to_lsl": distance_to_lower,
            "distance_to_usl": distance_to_upper,
            "percent_to_lsl": (distance_to_lower / self.spec.tolerance) * 100,
            "percent_to_usl": (distance_to_upper / self.spec.tolerance) * 100
        }

    def get_full_report(self) -> Dict:
        """Generate comprehensive capability report"""
        centering = self.get_centering_analysis()
        sigma = self.calculate_sigma_level()
        dpmo = self.calculate_dpmo()

        return {
            "specification": {
                "lsl": self.spec.lower_spec,
                "nominal": self.spec.nominal,
                "usl": self.spec.upper_spec,
                "tolerance": self.spec.tolerance
            },
            "process_statistics": {
                "mean": self.mean,
                "std_dev": self.std_dev,
                "min": self.process_stats.min_value,
                "max": self.process_stats.max_value,
                "range": self.process_stats.range,
                "n_samples": self.n
            },
            "capability_indices": {
                "cp": self.calculate_cp(),
                "cpk": self.calculate_cpk(),
                "cpu": self.calculate_cpu(),
                "cpl": self.calculate_cpl(),
                "pp": self.calculate_pp(),
                "ppk": self.calculate_ppk(),
                "cpm": self.calculate_cpm()
            },
            "sigma_level": sigma,
            "dpmo": dpmo,
            "capability_level": self.assess_capability().value,
            "centering": centering
        }

    def print_report(self, verbose: bool = True):
        """Print capability report"""
        report = self.get_full_report()

        print("\n" + "=" * 70)
        print("PROCESS CAPABILITY ANALYSIS REPORT")
        print("=" * 70)

        print("\nSPECIFICATION LIMITS:")
        print(f"  Lower Spec Limit (LSL): {report['specification']['lsl']:.4f}")
        print(f"  Nominal:                {report['specification']['nominal']:.4f}")
        print(f"  Upper Spec Limit (USL): {report['specification']['usl']:.4f}")
        print(f"  Tolerance:              {report['specification']['tolerance']:.4f}")

        print("\nPROCESS STATISTICS:")
        print(f"  Mean (μ):        {report['process_statistics']['mean']:.4f}")
        print(f"  Std Dev (σ):     {report['process_statistics']['std_dev']:.4f}")
        print(f"  Min Value:       {report['process_statistics']['min']:.4f}")
        print(f"  Max Value:       {report['process_statistics']['max']:.4f}")
        print(f"  Range:           {report['process_statistics']['range']:.4f}")
        print(f"  Sample Size:     {report['process_statistics']['n_samples']}")

        print("\nCAPABILITY INDICES:")
        print(f"  Cp (Potential):     {report['capability_indices']['cp']:.3f}")
        print(f"  Cpk (Actual):       {report['capability_indices']['cpk']:.3f}")
        print(f"    CPU (Upper):      {report['capability_indices']['cpu']:.3f}")
        print(f"    CPL (Lower):      {report['capability_indices']['cpl']:.3f}")
        print(f"  Pp (Short-term):    {report['capability_indices']['pp']:.3f}")
        print(f"  Ppk (Performance):  {report['capability_indices']['ppk']:.3f}")
        print(f"  Cpm (Taguchi):      {report['capability_indices']['cpm']:.3f}")

        print("\nPERFORMANCE METRICS:")
        print(f"  Sigma Level:    {report['sigma_level']:.2f} σ")
        print(f"  DPMO:           {report['dpmo']:.0f} defects per million")
        print(f"  Capability:     {report['capability_level']}")

        centering = report['centering']
        print("\nCENTERING ANALYSIS:")
        print(f"  Process Mean Offset:    {centering['offset']:+.4f} ({centering['offset_percent']:+.1f}%)")
        print(f"  Distance to LSL:        {centering['distance_to_lsl']:.4f} ({centering['percent_to_lsl']:.1f}%)")
        print(f"  Distance to USL:        {centering['distance_to_usl']:.4f} ({centering['percent_to_usl']:.1f}%)")

        if verbose:
            print("\nINTERPRETATION GUIDELINES:")
            cpk = report['capability_indices']['cpk']
            if cpk < 1.0:
                print("  ❌ INCAPABLE: Process cannot reliably meet specifications.")
                print("     Action: STOP production, investigate root causes, improve process.")
            elif cpk < 1.33:
                print("  ⚠️  MARGINAL: Process barely capable with high defect risk.")
                print("     Action: Implement corrective actions, increase monitoring.")
            elif cpk < 1.67:
                print("  ✓ ACCEPTABLE: Process meets minimum capability requirements.")
                print("     Action: Continue monitoring, plan long-term improvements.")
            else:
                print("  ✅ EXCELLENT: Process exceeds capability requirements.")
                print("     Action: Maintain current controls, continuous improvement.")

            print("\nRECOMMENDED ACTIONS:")
            if centering['offset_percent'] > 20:
                print("  • Process is significantly off-center toward upper spec.")
                print("    - Adjust process mean downward to improve Cpk.")
            elif centering['offset_percent'] < -20:
                print("  • Process is significantly off-center toward lower spec.")
                print("    - Adjust process mean upward to improve Cpk.")

            if report['capability_indices']['cp'] > 1.33 and cpk < 1.33:
                print("  • Process has good potential but poor centering.")
                print("    - Focus on centering adjustment rather than variation reduction.")

            print("\n" + "=" * 70)


class MultiCharacteristicAnalysis:
    """Analyze capability across multiple characteristics"""

    def __init__(self):
        self.characteristics = {}

    def add_characteristic(self, name: str, capability_index: CapabilityIndex):
        """Add a characteristic analysis"""
        self.characteristics[name] = capability_index

    def get_summary(self) -> pd.DataFrame:
        """Get summary of all characteristics"""
        data = []

        for name, cap in self.characteristics.items():
            report = cap.get_full_report()
            data.append({
                "Characteristic": name,
                "Cpk": report['capability_indices']['cpk'],
                "DPMO": report['dpmo'],
                "Sigma": report['sigma_level'],
                "Capable": report['capability_level']
            })

        return pd.DataFrame(data)

    def get_weakest_link(self) -> Tuple[str, float]:
        """Return characteristic with lowest Cpk"""
        cpk_values = {
            name: cap.calculate_cpk()
            for name, cap in self.characteristics.items()
        }

        return min(cpk_values.items(), key=lambda x: x[1])

    def print_summary(self):
        """Print summary of all characteristics"""
        summary = self.get_summary()
        print("\nMULTI-CHARACTERISTIC CAPABILITY SUMMARY:")
        print(summary.to_string(index=False))

        weakest_name, weakest_cpk = self.get_weakest_link()
        print(f"\nWeakest Link: {weakest_name} (Cpk = {weakest_cpk:.3f})")
        print("Focus improvement efforts on this characteristic.")


# Example usage
if __name__ == "__main__":
    # Example: Shaft Diameter Capability Analysis
    print("\n" + "=" * 70)
    print("EXAMPLE: Shaft Diameter Capability Analysis")
    print("=" * 70)

    # Simulate production data
    np.random.seed(42)
    shaft_data = np.random.normal(25.010, 0.020, 100)  # Mean slightly high

    # Define specifications
    shaft_spec = SpecificationLimits(
        nominal=25.000,
        lower_spec=24.950,
        upper_spec=25.050
    )

    # Perform capability analysis
    capability = CapabilityIndex(shaft_data.tolist(), shaft_spec)
    capability.print_report(verbose=True)

    # Example 2: Compare multiple characteristics
    print("\n\n" + "=" * 70)
    print("EXAMPLE 2: Multi-Characteristic Analysis")
    print("=" * 70)

    multi_analysis = MultiCharacteristicAnalysis()

    # Add multiple characteristics
    characteristics = {
        "OD (Outer Diameter)": {
            "data": np.random.normal(25.010, 0.020, 100),
            "spec": SpecificationLimits(25.000, 24.950, 25.050)
        },
        "ID (Inner Diameter)": {
            "data": np.random.normal(15.005, 0.025, 100),
            "spec": SpecificationLimits(15.000, 14.950, 15.050)
        },
        "Length": {
            "data": np.random.normal(50.015, 0.030, 100),
            "spec": SpecificationLimits(50.000, 49.900, 50.100)
        }
    }

    for char_name, char_data in characteristics.items():
        cap = CapabilityIndex(char_data["data"].tolist(), char_data["spec"])
        multi_analysis.add_characteristic(char_name, cap)

    multi_analysis.print_summary()

    # Example 3: Defect projection
    print("\n\n" + "DEFECT PROJECTION ANALYSIS:")
    capability = CapabilityIndex(shaft_data.tolist(), shaft_spec)
    dpmo = capability.calculate_dpmo()

    for volume in [1000, 10000, 100000, 1000000]:
        defects = capability.get_defect_count(volume)
        print(f"  Volume: {volume:>7} parts → Expected defects: {defects:>6.1f} "
              f"({defects/volume*100:>5.2f}%)")
