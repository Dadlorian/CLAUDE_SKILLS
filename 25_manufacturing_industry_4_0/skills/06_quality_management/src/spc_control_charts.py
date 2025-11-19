"""
Statistical Process Control (SPC) Control Chart Implementation

This module provides tools for creating and analyzing control charts
used in quality management and statistical process control.

Author: Quality Engineering
License: MIT
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import List, Tuple, Optional
from enum import Enum


class ChartType(Enum):
    """Supported control chart types"""
    XBAR_R = "X-bar/R"          # Variables data with rational subgroups
    XBAR_S = "X-bar/S"          # Variables data, larger samples
    I_MR = "I-MR"               # Individual and Moving Range
    P_CHART = "P Chart"          # Proportion defective
    NP_CHART = "NP Chart"        # Number defective
    C_CHART = "C Chart"          # Count of defects
    U_CHART = "U Chart"          # Defects per unit


@dataclass
class ControlChartConstants:
    """Control chart constants by sample size"""

    # Constants for X-bar/R chart
    A2_VALUES = {
        2: 1.880, 3: 1.023, 4: 0.729, 5: 0.577,
        6: 0.483, 7: 0.419, 8: 0.373, 9: 0.337, 10: 0.308
    }
    D3_VALUES = {
        2: 0.000, 3: 0.000, 4: 0.000, 5: 0.000,
        6: 0.000, 7: 0.076, 8: 0.136, 9: 0.184, 10: 0.223
    }
    D4_VALUES = {
        2: 3.267, 3: 2.575, 4: 2.282, 5: 2.114,
        6: 2.004, 7: 1.924, 8: 1.864, 9: 1.816, 10: 1.777
    }

    # Constants for X-bar/S chart
    A3_VALUES = {
        2: 2.659, 3: 1.954, 4: 1.628, 5: 1.427,
        6: 1.287, 7: 1.182, 8: 1.099, 9: 1.032, 10: 0.975
    }
    B3_VALUES = {
        2: 0.000, 3: 0.000, 4: 0.000, 5: 0.000,
        6: 0.030, 7: 0.118, 8: 0.185, 9: 0.239, 10: 0.284
    }
    B4_VALUES = {
        2: 3.267, 3: 2.568, 4: 2.266, 5: 2.089,
        6: 1.970, 7: 1.882, 8: 1.815, 9: 1.761, 10: 1.716
    }

    # For Individual/Moving Range chart
    D2_MR = 1.128  # d2 factor for moving range of 2


class XbarRChart:
    """X-bar and R Control Chart Implementation

    Used for monitoring process mean (X-bar) and variation (Range)
    with rational subgroups of size 2-10.
    """

    def __init__(self, sample_size: int, process_name: str = "Process"):
        """
        Initialize X-bar/R chart

        Args:
            sample_size: Subgroup size (n = 2-10)
            process_name: Name of process being monitored
        """
        if sample_size < 2 or sample_size > 10:
            raise ValueError("Sample size must be between 2 and 10")

        self.sample_size = sample_size
        self.process_name = process_name
        self.constants = ControlChartConstants()
        self.samples = []
        self.ucl_x = None
        self.lcl_x = None
        self.cl_x = None
        self.ucl_r = None
        self.lcl_r = None
        self.cl_r = None

    def add_sample(self, measurements: List[float]) -> None:
        """Add a rational subgroup of measurements"""
        if len(measurements) != self.sample_size:
            raise ValueError(f"Expected {self.sample_size} measurements, got {len(measurements)}")
        self.samples.append(measurements)

    def add_samples_from_data(self, data: np.ndarray) -> None:
        """
        Add samples from numpy array (each row is a sample)

        Args:
            data: Array of shape (n_samples, sample_size)
        """
        for row in data:
            self.add_sample(row.tolist())

    def calculate_control_limits(self) -> Tuple[float, float, float, float, float, float]:
        """
        Calculate control limits from collected samples

        Returns:
            Tuple of (UCL_X, CL_X, LCL_X, UCL_R, CL_R, LCL_R)
        """
        if len(self.samples) < 3:
            raise ValueError("Need at least 3 samples to calculate control limits")

        # Calculate X-bar values (mean of each sample)
        xbar_values = [np.mean(sample) for sample in self.samples]

        # Calculate R values (range of each sample)
        r_values = [max(sample) - min(sample) for sample in self.samples]

        # Calculate overall averages
        xbar_bar = np.mean(xbar_values)
        rbar = np.mean(r_values)

        # Get constants for this sample size
        a2 = self.constants.A2_VALUES[self.sample_size]
        d3 = self.constants.D3_VALUES[self.sample_size]
        d4 = self.constants.D4_VALUES[self.sample_size]

        # Calculate control limits
        self.ucl_x = xbar_bar + a2 * rbar
        self.cl_x = xbar_bar
        self.lcl_x = xbar_bar - a2 * rbar

        self.ucl_r = d4 * rbar
        self.cl_r = rbar
        self.lcl_r = d3 * rbar if d3 * rbar > 0 else 0

        return self.ucl_x, self.cl_x, self.lcl_x, self.ucl_r, self.cl_r, self.lcl_r

    def get_xbar_data(self) -> Tuple[List[float], List[float]]:
        """Get X-bar values and range values"""
        xbar_values = [np.mean(sample) for sample in self.samples]
        r_values = [max(sample) - min(sample) for sample in self.samples]
        return xbar_values, r_values

    def check_control_status(self, tolerance: float = None) -> pd.DataFrame:
        """
        Check if each sample is in statistical control

        Args:
            tolerance: Optional specification tolerance (for capability calculation)

        Returns:
            DataFrame with control status for each sample
        """
        if self.cl_x is None:
            self.calculate_control_limits()

        xbar_values, r_values = self.get_xbar_data()

        results = []
        for i, (xbar, r) in enumerate(zip(xbar_values, r_values)):
            xbar_status = "IN_CONTROL" if self.lcl_x <= xbar <= self.ucl_x else "OUT_OF_CONTROL"
            r_status = "IN_CONTROL" if r <= self.ucl_r else "OUT_OF_CONTROL"

            result = {
                "Sample": i + 1,
                "X-bar": xbar,
                "X-bar_Status": xbar_status,
                "Range": r,
                "Range_Status": r_status,
                "Overall": "IN_CONTROL" if (xbar_status == "IN_CONTROL" and r_status == "IN_CONTROL") else "OUT_OF_CONTROL"
            }
            results.append(result)

        return pd.DataFrame(results)

    def get_statistics(self) -> dict:
        """Get summary statistics"""
        xbar_values, r_values = self.get_xbar_data()

        # Estimate standard deviation from range
        d2 = {2: 1.128, 3: 1.693, 4: 2.059, 5: 2.326,
              6: 2.534, 7: 2.704, 8: 2.847, 9: 2.970, 10: 3.078}
        rbar = np.mean(r_values)
        sigma = rbar / d2[self.sample_size]

        return {
            "process_mean": np.mean(xbar_values),
            "range_mean": rbar,
            "standard_deviation": sigma,
            "min_xbar": min(xbar_values),
            "max_xbar": max(xbar_values),
            "num_samples": len(self.samples)
        }


class ProcessCapability:
    """Process Capability Analysis

    Calculates Cp, Cpk, Pp, and Ppk indices to assess
    whether a process meets specification limits.
    """

    def __init__(self, data: List[float], lsl: float = None, usl: float = None):
        """
        Initialize capability analysis

        Args:
            data: List of individual measurements
            lsl: Lower specification limit
            usl: Upper specification limit
        """
        self.data = np.array(data)
        self.lsl = lsl
        self.usl = usl
        self.mean = np.mean(data)
        self.std_dev = np.std(data, ddof=1)  # Sample std dev

    def calculate_cp(self) -> float:
        """
        Calculate Cp (Process Capability, assumes centered)

        Cp = (USL - LSL) / (6 * σ)
        """
        if self.lsl is None or self.usl is None:
            raise ValueError("LSL and USL required for Cp calculation")

        return (self.usl - self.lsl) / (6 * self.std_dev)

    def calculate_cpk(self) -> float:
        """
        Calculate Cpk (Process Capability, accounts for centering)

        Cpk = min((USL - mean) / (3 * σ), (mean - LSL) / (3 * σ))
        """
        if self.lsl is None or self.usl is None:
            raise ValueError("LSL and USL required for Cpk calculation")

        cpu = (self.usl - self.mean) / (3 * self.std_dev)
        cpl = (self.mean - self.lsl) / (3 * self.std_dev)

        return min(cpu, cpl)

    def calculate_pp(self) -> float:
        """
        Calculate Pp (Performance Index, short-term potential)
        Similar to Cp but based on overall population std dev
        """
        if self.lsl is None or self.usl is None:
            raise ValueError("LSL and USL required for Pp calculation")

        # Use population std dev for Pp
        pop_std = np.std(self.data, ddof=0)
        return (self.usl - self.lsl) / (6 * pop_std)

    def calculate_ppk(self) -> float:
        """
        Calculate Ppk (Performance Index Centered)
        """
        if self.lsl is None or self.usl is None:
            raise ValueError("LSL and USL required for Ppk calculation")

        pop_std = np.std(self.data, ddof=0)
        ppu = (self.usl - self.mean) / (3 * pop_std)
        ppl = (self.mean - self.lsl) / (3 * pop_std)

        return min(ppu, ppl)

    def get_sigma_level(self) -> float:
        """
        Convert Cpk to sigma level
        Sigma = Cpk / 0.33 (approximately)
        """
        cpk = self.calculate_cpk()
        # More precise conversion
        return 3 * cpk + 1.5  # Accounts for 1.5 sigma shift

    def get_dpmo(self) -> float:
        """
        Calculate DPMO (Defects Per Million Opportunities)
        from sigma level
        """
        sigma = self.get_sigma_level()

        # DPMO table (approximate)
        dpmo_table = {
            3.0: 66807,
            3.5: 22750,
            4.0: 6210,
            4.5: 1350,
            5.0: 233,
            5.5: 32,
            6.0: 3.4,
            6.5: 0.2
        }

        # Find closest sigma and interpolate
        for s in sorted(dpmo_table.keys()):
            if sigma <= s:
                return dpmo_table[s]

        return 0.0  # Very high sigma

    def get_capability_report(self) -> dict:
        """Generate comprehensive capability report"""
        return {
            "mean": self.mean,
            "std_dev": self.std_dev,
            "lsl": self.lsl,
            "usl": self.usl,
            "cp": self.calculate_cp(),
            "cpk": self.calculate_cpk(),
            "pp": self.calculate_pp(),
            "ppk": self.calculate_ppk(),
            "sigma_level": self.get_sigma_level(),
            "dpmo": self.get_dpmo(),
            "process_centered": abs(self.mean - (self.lsl + self.usl) / 2) < 0.01 * (self.usl - self.lsl),
            "capable": self.calculate_cpk() >= 1.33
        }


class PChart:
    """P Chart for monitoring proportion defective

    Used for attribute data when tracking the fraction/proportion
    of defective items in samples.
    """

    def __init__(self, process_name: str = "Process"):
        self.process_name = process_name
        self.samples = []  # List of (n_inspected, n_defective)
        self.p_bar = None
        self.ucl = None
        self.lcl = None
        self.cl = None

    def add_sample(self, n_inspected: int, n_defective: int) -> None:
        """Add sample data"""
        if n_defective > n_inspected:
            raise ValueError("Defective units cannot exceed inspected units")
        self.samples.append((n_inspected, n_defective))

    def calculate_control_limits(self) -> Tuple[float, float, float]:
        """Calculate control limits"""
        if len(self.samples) < 3:
            raise ValueError("Need at least 3 samples")

        total_inspected = sum(n for n, _ in self.samples)
        total_defective = sum(d for _, d in self.samples)

        self.p_bar = total_defective / total_inspected
        self.cl = self.p_bar

        # Calculate limits - note: varies by sample size
        # Here we use average sample size
        avg_n = total_inspected / len(self.samples)

        sigma_p = np.sqrt(self.p_bar * (1 - self.p_bar) / avg_n)
        self.ucl = self.p_bar + 3 * sigma_p
        self.lcl = max(0, self.p_bar - 3 * sigma_p)

        return self.ucl, self.cl, self.lcl

    def get_proportions(self) -> List[float]:
        """Get proportion defective for each sample"""
        return [d / n for n, d in self.samples]

    def check_control_status(self) -> pd.DataFrame:
        """Check control status of each sample"""
        if self.cl is None:
            self.calculate_control_limits()

        proportions = self.get_proportions()
        results = []

        for i, (n, d) in enumerate(self.samples):
            p = d / n
            status = "IN_CONTROL" if self.lcl <= p <= self.ucl else "OUT_OF_CONTROL"
            results.append({
                "Sample": i + 1,
                "Inspected": n,
                "Defective": d,
                "Proportion": p,
                "Percent": p * 100,
                "Status": status
            })

        return pd.DataFrame(results)


class CChart:
    """C Chart for monitoring count of defects

    Used for attribute data when tracking number of defects
    in a constant inspection unit.
    """

    def __init__(self, process_name: str = "Process"):
        self.process_name = process_name
        self.defect_counts = []
        self.c_bar = None
        self.ucl = None
        self.lcl = None
        self.cl = None

    def add_sample(self, defect_count: int) -> None:
        """Add sample (count of defects)"""
        if defect_count < 0:
            raise ValueError("Defect count cannot be negative")
        self.defect_counts.append(defect_count)

    def calculate_control_limits(self) -> Tuple[float, float, float]:
        """Calculate control limits"""
        if len(self.defect_counts) < 3:
            raise ValueError("Need at least 3 samples")

        self.c_bar = np.mean(self.defect_counts)
        self.cl = self.c_bar

        # C-chart limits: c-bar ± 3*sqrt(c-bar)
        sigma_c = np.sqrt(self.c_bar)
        self.ucl = self.c_bar + 3 * sigma_c
        self.lcl = max(0, self.c_bar - 3 * sigma_c)

        return self.ucl, self.cl, self.lcl

    def check_control_status(self) -> pd.DataFrame:
        """Check control status"""
        if self.cl is None:
            self.calculate_control_limits()

        results = []
        for i, count in enumerate(self.defect_counts):
            status = "IN_CONTROL" if self.lcl <= count <= self.ucl else "OUT_OF_CONTROL"
            results.append({
                "Sample": i + 1,
                "Defect_Count": count,
                "Status": status
            })

        return pd.DataFrame(results)


class ControlChartAnalyzer:
    """Analyzer for detecting out-of-control patterns

    Implements Western Electric rules for detecting special cause variation
    """

    @staticmethod
    def check_run_test(values: List[float], center: float, num_consecutive: int = 8) -> bool:
        """Check for run of n consecutive points on same side of center"""
        above = sum(1 for v in values if v > center)
        below = sum(1 for v in values if v < center)

        if above >= num_consecutive or below >= num_consecutive:
            return True
        return False

    @staticmethod
    def check_trend(values: List[float], num_consecutive: int = 6) -> bool:
        """Check for trend (6 consecutive increasing or decreasing)"""
        if len(values) < num_consecutive:
            return False

        for i in range(len(values) - num_consecutive + 1):
            segment = values[i:i + num_consecutive]

            # Check increasing trend
            increasing = all(segment[j] < segment[j + 1] for j in range(len(segment) - 1))
            # Check decreasing trend
            decreasing = all(segment[j] > segment[j + 1] for j in range(len(segment) - 1))

            if increasing or decreasing:
                return True

        return False

    @staticmethod
    def analyze_chart(values: List[float], center: float,
                     sigma_1: float, sigma_2: float, sigma_3: float) -> dict:
        """
        Analyze chart for patterns

        Args:
            values: Chart values
            center: Center line value
            sigma_1: 1-sigma limits (68%)
            sigma_2: 2-sigma limits (95%)
            sigma_3: 3-sigma limits (99.7%)

        Returns:
            Dictionary of detected patterns
        """
        patterns = {
            "out_of_control": [],  # Points beyond 3-sigma
            "warning": [],         # Points beyond 2-sigma
            "runs": False,
            "trends": False,
            "mixed": False
        }

        # Check for out-of-control points
        ucl_3 = center + sigma_3
        lcl_3 = center - sigma_3
        ucl_2 = center + sigma_2
        lcl_2 = center - sigma_2

        for i, val in enumerate(values):
            if val > ucl_3 or val < lcl_3:
                patterns["out_of_control"].append(i)
            elif val > ucl_2 or val < lcl_2:
                patterns["warning"].append(i)

        # Check for runs
        if ControlChartAnalyzer.check_run_test(values, center):
            patterns["runs"] = True

        # Check for trends
        if ControlChartAnalyzer.check_trend(values):
            patterns["trends"] = True

        # Check for mixed signals
        upper_values = sum(1 for v in values if v > center + sigma_1)
        lower_values = sum(1 for v in values if v < center - sigma_1)

        if upper_values > len(values) * 0.5 and lower_values > len(values) * 0.3:
            patterns["mixed"] = True

        return patterns


# Example usage and testing
if __name__ == "__main__":
    # Example 1: X-bar/R Chart
    print("=" * 60)
    print("EXAMPLE 1: X-bar/R Chart Implementation")
    print("=" * 60)

    chart = XbarRChart(sample_size=5, process_name="Shaft Diameter")

    # Simulate 25 samples of 5 measurements each
    np.random.seed(42)
    data = np.random.normal(25.0, 0.015, size=(25, 5))
    chart.add_samples_from_data(data)

    # Calculate control limits
    ucl_x, cl_x, lcl_x, ucl_r, cl_r, lcl_r = chart.calculate_control_limits()

    print(f"\nX-bar Chart Limits:")
    print(f"  UCL = {ucl_x:.4f} mm")
    print(f"  CL  = {cl_x:.4f} mm")
    print(f"  LCL = {lcl_x:.4f} mm")

    print(f"\nR Chart Limits:")
    print(f"  UCL = {ucl_r:.4f} mm")
    print(f"  CL  = {cl_r:.4f} mm")
    print(f"  LCL = {lcl_r:.4f} mm")

    # Check control status
    status_df = chart.check_control_status()
    print(f"\nControl Status Summary:")
    print(f"  In Control: {(status_df['Overall'] == 'IN_CONTROL').sum()}/{len(status_df)}")
    print(f"  Out of Control: {(status_df['Overall'] == 'OUT_OF_CONTROL').sum()}/{len(status_df)}")

    # Example 2: Process Capability
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Process Capability Analysis")
    print("=" * 60)

    capability = ProcessCapability(data.flatten(), lsl=24.95, usl=25.05)
    report = capability.get_capability_report()

    print(f"\nCapability Indices:")
    print(f"  Cp  = {report['cp']:.2f}")
    print(f"  Cpk = {report['cpk']:.2f}")
    print(f"  Pp  = {report['pp']:.2f}")
    print(f"  Ppk = {report['ppk']:.2f}")
    print(f"\nSigma Level: {report['sigma_level']:.2f}")
    print(f"DPMO: {report['dpmo']:.1f}")
    print(f"Capable: {report['capable']}")

    # Example 3: P Chart
    print("\n" + "=" * 60)
    print("EXAMPLE 3: P Chart for Defect Rate")
    print("=" * 60)

    p_chart = PChart("Assembly Line")

    # Simulate defect data
    for _ in range(20):
        n_inspected = 100
        n_defective = np.random.binomial(n_inspected, 0.02)  # 2% defect rate
        p_chart.add_sample(n_inspected, n_defective)

    p_chart.calculate_control_limits()
    print(f"\nP Chart Limits (n={100}):")
    print(f"  UCL = {p_chart.ucl:.4f} ({p_chart.ucl*100:.2f}%)")
    print(f"  CL  = {p_chart.cl:.4f} ({p_chart.cl*100:.2f}%)")
    print(f"  LCL = {p_chart.lcl:.4f} ({p_chart.lcl*100:.2f}%)")

    # Check status
    status_df = p_chart.check_control_status()
    in_control = (status_df['Status'] == 'IN_CONTROL').sum()
    print(f"\nSamples in control: {in_control}/{len(status_df)}")
