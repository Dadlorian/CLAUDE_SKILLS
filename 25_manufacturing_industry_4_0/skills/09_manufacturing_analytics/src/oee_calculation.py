"""
Overall Equipment Effectiveness (OEE) Calculation and Analysis

This module provides comprehensive OEE calculation, tracking, and analysis capabilities
for manufacturing equipment and production lines.

OEE = Availability × Performance × Quality

Key Features:
- Real-time and historical OEE calculation
- Component analysis (Availability, Performance, Quality)
- Trend analysis and forecasting
- Root cause analysis by component
- Industry benchmarking
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
import json


@dataclass
class OEEResult:
    """Data class for OEE calculation results"""
    timestamp: datetime
    availability: float
    performance: float
    quality: float
    oee: float
    scheduled_time: float
    downtime: float
    run_time: float
    total_units: int
    good_units: int
    theoretical_time: float
    actual_time: float


class OEECalculator:
    """
    Calculate Overall Equipment Effectiveness (OEE) with component analysis
    """

    def __init__(self):
        self.results_history = []
        self.configuration = {
            'include_planned_downtime': False,
            'rounding_precision': 2,
        }

    def calculate_oee(
        self,
        scheduled_time: float,
        downtime: float,
        run_time: float,
        total_units: int,
        good_units: int,
        theoretical_cycle_time: float
    ) -> OEEResult:
        """
        Calculate OEE and component metrics

        Args:
            scheduled_time: Total scheduled production time (minutes)
            downtime: Equipment downtime (minutes)
            run_time: Actual equipment run time (minutes)
            total_units: Total units produced
            good_units: Units passing all quality checks
            theoretical_cycle_time: Ideal cycle time per unit (seconds)

        Returns:
            OEEResult object with calculated metrics
        """
        # Calculate Availability
        availability = self._calculate_availability(scheduled_time, downtime)

        # Calculate Performance
        performance = self._calculate_performance(
            theoretical_cycle_time, run_time, total_units
        )

        # Calculate Quality
        quality = self._calculate_quality(total_units, good_units)

        # Calculate Overall OEE
        oee = (availability / 100) * (performance / 100) * (quality / 100)

        result = OEEResult(
            timestamp=datetime.now(),
            availability=round(availability, self.configuration['rounding_precision']),
            performance=round(performance, self.configuration['rounding_precision']),
            quality=round(quality, self.configuration['rounding_precision']),
            oee=round(oee * 100, self.configuration['rounding_precision']),
            scheduled_time=scheduled_time,
            downtime=downtime,
            run_time=run_time,
            total_units=total_units,
            good_units=good_units,
            theoretical_time=(total_units * theoretical_cycle_time) / 60,
            actual_time=run_time,
        )

        self.results_history.append(result)
        return result

    @staticmethod
    def _calculate_availability(scheduled_time: float, downtime: float) -> float:
        """
        Calculate Availability %

        Availability = (Scheduled Time - Downtime) / Scheduled Time × 100%
        """
        if scheduled_time == 0:
            return 0.0

        operating_time = scheduled_time - downtime
        availability = (operating_time / scheduled_time) * 100

        return min(100.0, max(0.0, availability))

    @staticmethod
    def _calculate_performance(
        theoretical_cycle_time: float, actual_run_time: float, units_produced: int
    ) -> float:
        """
        Calculate Performance %

        Performance = (Ideal Cycle Time × Units Produced) / Actual Run Time × 100%

        Ideal Cycle Time = theoretical_cycle_time (in seconds)
        Actual Run Time = actual_run_time (in minutes)
        """
        if actual_run_time == 0:
            return 0.0

        theoretical_time_minutes = (units_produced * theoretical_cycle_time) / 60
        performance = (theoretical_time_minutes / actual_run_time) * 100

        return min(100.0, max(0.0, performance))

    @staticmethod
    def _calculate_quality(total_units: int, good_units: int) -> float:
        """
        Calculate Quality %

        Quality = Good Units / Total Units × 100%
        """
        if total_units == 0:
            return 0.0

        quality = (good_units / total_units) * 100
        return min(100.0, max(0.0, quality))

    def get_oee_trend(
        self, days: int = 7
    ) -> pd.DataFrame:
        """
        Get OEE trend over specified number of days

        Args:
            days: Number of days to analyze

        Returns:
            DataFrame with daily OEE metrics
        """
        if not self.results_history:
            return pd.DataFrame()

        cutoff_date = datetime.now() - timedelta(days=days)
        recent_results = [
            r for r in self.results_history
            if r.timestamp >= cutoff_date
        ]

        return pd.DataFrame([
            {
                'date': r.timestamp.date(),
                'availability': r.availability,
                'performance': r.performance,
                'quality': r.quality,
                'oee': r.oee,
            }
            for r in recent_results
        ])

    def get_oee_class(self, oee: float) -> str:
        """
        Classify OEE value according to industry standards

        Returns:
            Classification string (World Class, Excellent, Good, Fair, Poor)
        """
        if oee >= 85:
            return "World Class"
        elif oee >= 75:
            return "Excellent"
        elif oee >= 65:
            return "Good"
        elif oee >= 50:
            return "Fair"
        else:
            return "Poor"

    def get_improvement_recommendations(
        self, oee_result: OEEResult
    ) -> Dict[str, List[str]]:
        """
        Generate improvement recommendations based on OEE components

        Args:
            oee_result: OEE calculation result

        Returns:
            Dictionary with recommendations by component
        """
        recommendations = {
            'availability': [],
            'performance': [],
            'quality': [],
            'overall': []
        }

        # Availability recommendations
        if oee_result.availability < 85:
            recommendations['availability'].extend([
                "Review and implement preventive maintenance program",
                "Conduct root cause analysis on equipment failures",
                "Reduce planned downtime through better scheduling",
                "Improve response time to equipment issues"
            ])

        # Performance recommendations
        if oee_result.performance < 85:
            recommendations['performance'].extend([
                "Optimize equipment speeds and feeds",
                "Review and improve operator training",
                "Analyze minor stops and idle time",
                "Ensure material supply meets production demand",
                "Upgrade outdated equipment or controls"
            ])

        # Quality recommendations
        if oee_result.quality < 99:
            recommendations['quality'].extend([
                "Implement Statistical Process Control (SPC)",
                "Conduct Design of Experiments (DoE) optimization",
                "Review and tighten process parameters",
                "Improve raw material quality and consistency",
                "Increase inspection frequency during startups"
            ])

        # Overall OEE
        if oee_result.oee < 85:
            recommendations['overall'].append(
                f"Target OEE of 85% (World Class). Current: {oee_result.oee}%"
            )

        return recommendations

    def simulate_improvements(
        self,
        base_result: OEEResult,
        availability_improvement: float = 0,
        performance_improvement: float = 0,
        quality_improvement: float = 0
    ) -> OEEResult:
        """
        Simulate impact of component improvements on OEE

        Args:
            base_result: Baseline OEE result
            availability_improvement: Percentage point improvement (e.g., 5.0 for +5%)
            performance_improvement: Percentage point improvement
            quality_improvement: Percentage point improvement

        Returns:
            Simulated OEE result
        """
        new_availability = min(100, base_result.availability + availability_improvement)
        new_performance = min(100, base_result.performance + performance_improvement)
        new_quality = min(100, base_result.quality + quality_improvement)

        new_oee = (
            (new_availability / 100) *
            (new_performance / 100) *
            (new_quality / 100) * 100
        )

        return OEEResult(
            timestamp=datetime.now(),
            availability=new_availability,
            performance=new_performance,
            quality=new_quality,
            oee=round(new_oee, 2),
            scheduled_time=base_result.scheduled_time,
            downtime=base_result.downtime,
            run_time=base_result.run_time,
            total_units=base_result.total_units,
            good_units=base_result.good_units,
            theoretical_time=base_result.theoretical_time,
            actual_time=base_result.actual_time,
        )


class OEETracker:
    """
    Track OEE metrics in real-time with historical analysis
    """

    def __init__(self, equipment_id: str):
        self.equipment_id = equipment_id
        self.daily_metrics = {}
        self.shift_metrics = {}
        self.hourly_metrics = {}
        self.calculator = OEECalculator()

    def record_production_event(
        self,
        event_type: str,
        duration: float,
        units_produced: int = 0,
        units_good: int = 0,
        details: Optional[Dict] = None
    ):
        """
        Record production event (run, downtime, quality check)

        Args:
            event_type: 'run', 'downtime', 'quality_check'
            duration: Duration in minutes
            units_produced: Number of units in this event
            units_good: Number of good units
            details: Additional event details
        """
        timestamp = datetime.now()
        hour_key = timestamp.strftime("%Y-%m-%d %H:00")
        day_key = timestamp.strftime("%Y-%m-%d")

        # Initialize if not exists
        if hour_key not in self.hourly_metrics:
            self.hourly_metrics[hour_key] = {
                'scheduled_time': 0,
                'downtime': 0,
                'run_time': 0,
                'total_units': 0,
                'good_units': 0,
                'theoretical_cycle_time': 30,  # seconds, needs to be configured
                'events': []
            }

        # Record event
        event = {
            'type': event_type,
            'duration': duration,
            'units_produced': units_produced,
            'units_good': units_good,
            'timestamp': timestamp.isoformat(),
            'details': details
        }
        self.hourly_metrics[hour_key]['events'].append(event)

        # Update metrics
        if event_type == 'run':
            self.hourly_metrics[hour_key]['scheduled_time'] += duration
            self.hourly_metrics[hour_key]['run_time'] += duration
            self.hourly_metrics[hour_key]['total_units'] += units_produced
            self.hourly_metrics[hour_key]['good_units'] += units_good

        elif event_type == 'downtime':
            self.hourly_metrics[hour_key]['scheduled_time'] += duration
            self.hourly_metrics[hour_key]['downtime'] += duration

    def calculate_hourly_oee(self, hour_key: str) -> Optional[OEEResult]:
        """Calculate OEE for specific hour"""
        if hour_key not in self.hourly_metrics:
            return None

        metrics = self.hourly_metrics[hour_key]
        if metrics['scheduled_time'] == 0:
            return None

        return self.calculator.calculate_oee(
            scheduled_time=metrics['scheduled_time'],
            downtime=metrics['downtime'],
            run_time=metrics['run_time'],
            total_units=metrics['total_units'],
            good_units=metrics['good_units'],
            theoretical_cycle_time=metrics['theoretical_cycle_time']
        )

    def get_current_shift_oee(self) -> Optional[OEEResult]:
        """Get OEE for current shift (last 8 hours)"""
        now = datetime.now()
        shift_hours = 8
        shift_start = now - timedelta(hours=shift_hours)

        total_scheduled = 0
        total_downtime = 0
        total_run_time = 0
        total_units = 0
        total_good = 0
        theoretical_cycle = 30

        for hour_key, metrics in self.hourly_metrics.items():
            hour_time = datetime.fromisoformat(hour_key + ':00')
            if shift_start <= hour_time <= now:
                total_scheduled += metrics['scheduled_time']
                total_downtime += metrics['downtime']
                total_run_time += metrics['run_time']
                total_units += metrics['total_units']
                total_good += metrics['good_units']

        if total_scheduled == 0:
            return None

        return self.calculator.calculate_oee(
            scheduled_time=total_scheduled,
            downtime=total_downtime,
            run_time=total_run_time,
            total_units=total_units,
            good_units=total_good,
            theoretical_cycle_time=theoretical_cycle
        )

    def get_daily_summary(self, date: str) -> Optional[Dict]:
        """
        Get daily OEE summary

        Args:
            date: Date in format YYYY-MM-DD

        Returns:
            Dictionary with daily metrics and OEE
        """
        daily_data = []

        for hour_key, metrics in self.hourly_metrics.items():
            if hour_key.startswith(date):
                oee_result = self.calculate_hourly_oee(hour_key)
                if oee_result:
                    daily_data.append(oee_result)

        if not daily_data:
            return None

        avg_oee = np.mean([r.oee for r in daily_data])
        avg_availability = np.mean([r.availability for r in daily_data])
        avg_performance = np.mean([r.performance for r in daily_data])
        avg_quality = np.mean([r.quality for r in daily_data])

        return {
            'date': date,
            'equipment_id': self.equipment_id,
            'oee': round(avg_oee, 2),
            'availability': round(avg_availability, 2),
            'performance': round(avg_performance, 2),
            'quality': round(avg_quality, 2),
            'oee_class': self.calculator.get_oee_class(avg_oee),
            'hourly_samples': len(daily_data),
            'total_units_produced': sum([r.total_units for r in daily_data]),
            'good_units': sum([r.good_units for r in daily_data]),
            'total_downtime_hours': sum([r.downtime for r in daily_data]) / 60
        }

    def compare_performance(
        self, baseline_date: str, comparison_date: str
    ) -> Dict:
        """
        Compare OEE performance between two dates

        Args:
            baseline_date: YYYY-MM-DD format
            comparison_date: YYYY-MM-DD format

        Returns:
            Comparison metrics and improvements
        """
        baseline = self.get_daily_summary(baseline_date)
        comparison = self.get_daily_summary(comparison_date)

        if not baseline or not comparison:
            return {}

        return {
            'baseline_date': baseline_date,
            'comparison_date': comparison_date,
            'oee_improvement': round(comparison['oee'] - baseline['oee'], 2),
            'availability_improvement': round(
                comparison['availability'] - baseline['availability'], 2
            ),
            'performance_improvement': round(
                comparison['performance'] - baseline['performance'], 2
            ),
            'quality_improvement': round(
                comparison['quality'] - baseline['quality'], 2
            ),
            'baseline_oee_class': baseline['oee_class'],
            'comparison_oee_class': comparison['oee_class'],
        }


# Example usage
if __name__ == "__main__":
    # Create calculator
    calc = OEECalculator()

    # Example: Calculate OEE for a shift
    oee_result = calc.calculate_oee(
        scheduled_time=480,  # 8 hours
        downtime=60,          # 1 hour downtime
        run_time=420,         # 7 hours actual run
        total_units=100,
        good_units=95,
        theoretical_cycle_time=2.5  # 2.5 seconds per unit
    )

    print("OEE Calculation Result:")
    print(f"  Availability: {oee_result.availability}%")
    print(f"  Performance: {oee_result.performance}%")
    print(f"  Quality: {oee_result.quality}%")
    print(f"  OEE: {oee_result.oee}%")
    print(f"  Classification: {calc.get_oee_class(oee_result.oee)}")

    # Get improvement recommendations
    recommendations = calc.get_improvement_recommendations(oee_result)
    print("\nImprovement Recommendations:")
    for component, suggestions in recommendations.items():
        if suggestions:
            print(f"  {component.upper()}:")
            for suggestion in suggestions:
                print(f"    - {suggestion}")

    # Simulate improvements
    improved_result = calc.simulate_improvements(
        oee_result,
        availability_improvement=5.0,  # Improve availability by 5%
        performance_improvement=3.0,    # Improve performance by 3%
        quality_improvement=2.0          # Improve quality by 2%
    )

    print(f"\nWith Improvements:")
    print(f"  Projected OEE: {improved_result.oee}%")
    print(f"  Classification: {calc.get_oee_class(improved_result.oee)}")

    # Real-time tracking example
    tracker = OEETracker(equipment_id="MILL_001")

    # Record some production events
    tracker.record_production_event('run', duration=60, units_produced=50, units_good=48)
    tracker.record_production_event('downtime', duration=10, details={'reason': 'toolchange'})
    tracker.record_production_event('run', duration=50, units_produced=40, units_good=39)

    # Get current shift OEE
    shift_oee = tracker.get_current_shift_oee()
    if shift_oee:
        print(f"\nCurrent Shift OEE for {tracker.equipment_id}: {shift_oee.oee}%")
