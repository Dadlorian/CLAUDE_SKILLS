"""
Production Tracking Module
Real-time tracking of production orders, work orders, and manufacturing KPIs.
Includes OEE calculation, cycle time tracking, and production analytics.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Tuple
from collections import defaultdict, deque

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WorkOrderStatus(Enum):
    """Work order status enumeration."""
    NOT_STARTED = "not_started"
    READY = "ready"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class EquipmentState(Enum):
    """Equipment operational state."""
    RUNNING = "running"
    IDLE = "idle"
    SETUP = "setup"
    CHANGEOVER = "changeover"
    PLANNED_DOWNTIME = "planned_downtime"
    UNPLANNED_DOWNTIME = "unplanned_downtime"


@dataclass
class TimeWindow:
    """Represents a time window with start and end."""
    start: datetime
    end: datetime

    @property
    def duration(self) -> timedelta:
        """Get duration of window."""
        return self.end - self.start

    @property
    def duration_minutes(self) -> float:
        """Get duration in minutes."""
        return self.duration.total_seconds() / 60

    def overlaps(self, other: 'TimeWindow') -> bool:
        """Check if this window overlaps with another."""
        return not (self.end <= other.start or self.start >= other.end)

    def intersect(self, other: 'TimeWindow') -> Optional['TimeWindow']:
        """Get intersection of two windows."""
        start = max(self.start, other.start)
        end = min(self.end, other.end)
        if start < end:
            return TimeWindow(start, end)
        return None


@dataclass
class ProductionEvent:
    """Production event record."""
    timestamp: datetime
    equipment_id: str
    event_type: str  # "start", "stop", "pause", "resume", "quality_check", "defect"
    value: Optional[float] = None
    unit: Optional[str] = None
    details: Dict = field(default_factory=dict)


@dataclass
class WorkOrderExecution:
    """Work order execution tracking."""
    work_order_id: str
    product_id: str
    equipment_id: str
    target_quantity: int
    scheduled_window: TimeWindow

    # Execution data
    status: WorkOrderStatus = WorkOrderStatus.NOT_STARTED
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    good_units: int = 0
    defect_units: int = 0
    scrap_units: int = 0
    events: List[ProductionEvent] = field(default_factory=list)

    @property
    def total_units(self) -> int:
        """Total units produced."""
        return self.good_units + self.defect_units

    @property
    def actual_quantity(self) -> int:
        """Quantity produced (good + defect)."""
        return self.total_units

    @property
    def yield_percentage(self) -> float:
        """Calculate yield percentage."""
        if self.total_units == 0:
            return 0.0
        return (self.good_units / self.total_units) * 100

    @property
    def is_complete(self) -> bool:
        """Check if work order is complete."""
        return self.status in [
            WorkOrderStatus.COMPLETED,
            WorkOrderStatus.FAILED,
            WorkOrderStatus.CANCELLED
        ]

    @property
    def actual_window(self) -> Optional[TimeWindow]:
        """Get actual execution window."""
        if self.actual_start and self.actual_end:
            return TimeWindow(self.actual_start, self.actual_end)
        return None

    @property
    def scheduled_duration_minutes(self) -> float:
        """Get scheduled duration in minutes."""
        return self.scheduled_window.duration_minutes

    @property
    def actual_duration_minutes(self) -> Optional[float]:
        """Get actual duration in minutes."""
        window = self.actual_window
        return window.duration_minutes if window else None

    @property
    def schedule_variance_minutes(self) -> Optional[float]:
        """Get schedule variance (actual - scheduled)."""
        actual = self.actual_duration_minutes
        if actual is None:
            return None
        return actual - self.scheduled_duration_minutes

    def record_event(self, event: ProductionEvent) -> None:
        """Record a production event."""
        self.events.append(event)
        logger.info(f"Event recorded for {self.work_order_id}: {event.event_type}")

    def start_execution(self, timestamp: datetime) -> None:
        """Start work order execution."""
        self.actual_start = timestamp
        self.status = WorkOrderStatus.IN_PROGRESS
        logger.info(f"Work order started: {self.work_order_id}")

    def complete(self, timestamp: datetime) -> None:
        """Complete work order."""
        self.actual_end = timestamp
        self.status = WorkOrderStatus.COMPLETED
        logger.info(f"Work order completed: {self.work_order_id} "
                   f"(Good: {self.good_units}, Defect: {self.defect_units})")

    def fail(self, timestamp: datetime, reason: str) -> None:
        """Mark work order as failed."""
        self.actual_end = timestamp
        self.status = WorkOrderStatus.FAILED
        logger.error(f"Work order failed: {self.work_order_id} - {reason}")


class EquipmentTracker:
    """Track equipment state and downtime."""

    def __init__(self, equipment_id: str):
        """Initialize equipment tracker.

        Args:
            equipment_id: Equipment identifier
        """
        self.equipment_id = equipment_id
        self.current_state = EquipmentState.IDLE
        self.state_start = datetime.utcnow()
        self.state_history: List[Tuple[EquipmentState, TimeWindow]] = []
        self.downtime_events: List[Tuple[str, TimeWindow]] = []  # (reason, window)

    def change_state(self, new_state: EquipmentState, timestamp: datetime) -> None:
        """Change equipment state.

        Args:
            new_state: New equipment state
            timestamp: Time of state change
        """
        if new_state == self.current_state:
            return

        # Record previous state
        window = TimeWindow(self.state_start, timestamp)
        self.state_history.append((self.current_state, window))

        # Update current state
        self.current_state = new_state
        self.state_start = timestamp

        logger.info(f"{self.equipment_id}: State changed to {new_state.value}")

    def record_downtime(self, reason: str, window: TimeWindow) -> None:
        """Record downtime event.

        Args:
            reason: Reason for downtime
            window: Time window of downtime
        """
        self.downtime_events.append((reason, window))
        logger.warning(f"{self.equipment_id}: Downtime - {reason} ({window.duration_minutes:.1f} min)")

    def get_state_duration(self, state: EquipmentState) -> timedelta:
        """Get total duration in specific state.

        Args:
            state: Equipment state

        Returns:
            Total duration in that state
        """
        total = timedelta()
        for recorded_state, window in self.state_history:
            if recorded_state == state:
                total += window.duration

        # Include current state if still in it
        if self.current_state == state:
            total += datetime.utcnow() - self.state_start

        return total

    def get_availability_window(self, window: TimeWindow) -> float:
        """Calculate availability percentage for time window.

        Args:
            window: Time window to analyze

        Returns:
            Availability percentage (0-100)
        """
        total_time = window.duration_minutes
        downtime_minutes = 0

        for reason, dt_window in self.downtime_events:
            intersection = window.intersect(dt_window)
            if intersection:
                downtime_minutes += intersection.duration_minutes

        if total_time == 0:
            return 100.0

        return ((total_time - downtime_minutes) / total_time) * 100


class ProductionAnalytics:
    """Calculate production KPIs and analytics."""

    def __init__(self, window_size: int = 24):
        """Initialize analytics calculator.

        Args:
            window_size: Lookback window in hours
        """
        self.window_size = window_size
        self.work_orders: Dict[str, WorkOrderExecution] = {}
        self.equipment_trackers: Dict[str, EquipmentTracker] = {}

    def register_work_order(self, execution: WorkOrderExecution) -> None:
        """Register work order for tracking.

        Args:
            execution: WorkOrderExecution to track
        """
        self.work_orders[execution.work_order_id] = execution
        logger.info(f"Work order registered: {execution.work_order_id}")

    def register_equipment(self, equipment_id: str) -> EquipmentTracker:
        """Register equipment for tracking.

        Args:
            equipment_id: Equipment identifier

        Returns:
            EquipmentTracker instance
        """
        if equipment_id not in self.equipment_trackers:
            tracker = EquipmentTracker(equipment_id)
            self.equipment_trackers[equipment_id] = tracker
            logger.info(f"Equipment registered: {equipment_id}")
        return self.equipment_trackers[equipment_id]

    def get_equipment_oee(self, equipment_id: str, window: TimeWindow) -> float:
        """Calculate OEE for equipment.

        Overall Equipment Effectiveness (OEE) = Availability × Performance × Quality

        Args:
            equipment_id: Equipment identifier
            window: Time window for calculation

        Returns:
            OEE percentage (0-100)
        """
        # Availability
        tracker = self.equipment_trackers.get(equipment_id)
        if not tracker:
            return 0.0

        availability = tracker.get_availability_window(window) / 100

        # Performance (actual output vs. theoretical)
        performance = self._calculate_performance(equipment_id, window)

        # Quality (good units vs. total)
        quality = self._calculate_quality(equipment_id, window)

        oee = (availability * performance * quality) * 100
        return max(0, min(100, oee))  # Clamp to 0-100

    def _calculate_performance(self, equipment_id: str, window: TimeWindow) -> float:
        """Calculate performance component of OEE.

        Performance = (Theoretical Cycle Time × Total Output) / Running Time

        Args:
            equipment_id: Equipment identifier
            window: Time window

        Returns:
            Performance ratio (0-1)
        """
        # Find work orders for this equipment in the window
        relevant_orders = [
            wo for wo in self.work_orders.values()
            if wo.equipment_id == equipment_id and wo.actual_window and
            wo.actual_window.overlaps(window)
        ]

        if not relevant_orders:
            return 0.8  # Default assumption

        total_good_units = sum(wo.good_units for wo in relevant_orders)
        total_units = sum(wo.total_units for wo in relevant_orders)

        if total_units == 0:
            return 0.0

        # Assume 10 minutes per unit as theoretical cycle time
        theoretical_time_minutes = total_units * 10
        actual_running_time = sum(
            wo.actual_duration_minutes or 0 for wo in relevant_orders
        )

        if actual_running_time == 0:
            return 0.0

        performance = min(1.0, theoretical_time_minutes / actual_running_time)
        return performance

    def _calculate_quality(self, equipment_id: str, window: TimeWindow) -> float:
        """Calculate quality component of OEE.

        Quality = Good Units / Total Units

        Args:
            equipment_id: Equipment identifier
            window: Time window

        Returns:
            Quality ratio (0-1)
        """
        relevant_orders = [
            wo for wo in self.work_orders.values()
            if wo.equipment_id == equipment_id and wo.actual_window and
            wo.actual_window.overlaps(window)
        ]

        total_good = sum(wo.good_units for wo in relevant_orders)
        total_units = sum(wo.total_units for wo in relevant_orders)

        if total_units == 0:
            return 1.0

        return total_good / total_units

    def calculate_cycle_time_stats(
        self,
        equipment_id: str,
        window: Optional[TimeWindow] = None
    ) -> Dict[str, float]:
        """Calculate cycle time statistics.

        Args:
            equipment_id: Equipment identifier
            window: Optional time window (default: last 24 hours)

        Returns:
            Dictionary with cycle time metrics
        """
        if not window:
            now = datetime.utcnow()
            window = TimeWindow(now - timedelta(hours=24), now)

        relevant_orders = [
            wo for wo in self.work_orders.values()
            if wo.equipment_id == equipment_id and wo.actual_window and
            wo.actual_window.overlaps(window) and wo.is_complete
        ]

        if not relevant_orders:
            return {
                'avg_cycle_time': 0.0,
                'min_cycle_time': 0.0,
                'max_cycle_time': 0.0,
                'stddev_cycle_time': 0.0,
                'count': 0
            }

        cycle_times = [wo.actual_duration_minutes or 0 for wo in relevant_orders]

        avg = sum(cycle_times) / len(cycle_times)
        min_ct = min(cycle_times)
        max_ct = max(cycle_times)

        # Calculate standard deviation
        variance = sum((ct - avg) ** 2 for ct in cycle_times) / len(cycle_times)
        stddev = variance ** 0.5

        return {
            'avg_cycle_time': avg,
            'min_cycle_time': min_ct,
            'max_cycle_time': max_ct,
            'stddev_cycle_time': stddev,
            'count': len(cycle_times)
        }

    def calculate_yield_stats(
        self,
        equipment_id: Optional[str] = None,
        product_id: Optional[str] = None,
        window: Optional[TimeWindow] = None
    ) -> Dict[str, float]:
        """Calculate yield statistics.

        Args:
            equipment_id: Optional equipment filter
            product_id: Optional product filter
            window: Optional time window

        Returns:
            Dictionary with yield metrics
        """
        if not window:
            now = datetime.utcnow()
            window = TimeWindow(now - timedelta(hours=24), now)

        # Filter work orders
        filtered_orders = self.work_orders.values()

        if equipment_id:
            filtered_orders = [wo for wo in filtered_orders if wo.equipment_id == equipment_id]
        if product_id:
            filtered_orders = [wo for wo in filtered_orders if wo.product_id == product_id]

        relevant_orders = [
            wo for wo in filtered_orders
            if wo.actual_window and wo.actual_window.overlaps(window) and wo.is_complete
        ]

        if not relevant_orders:
            return {
                'avg_yield': 0.0,
                'total_good_units': 0,
                'total_units': 0,
                'total_defects': 0,
                'defect_rate': 0.0,
                'count': 0
            }

        total_good = sum(wo.good_units for wo in relevant_orders)
        total_units = sum(wo.total_units for wo in relevant_orders)
        total_defects = sum(wo.defect_units for wo in relevant_orders)

        if total_units == 0:
            avg_yield = 0.0
            defect_rate = 0.0
        else:
            avg_yield = (total_good / total_units) * 100
            defect_rate = (total_defects / total_units) * 100

        return {
            'avg_yield': avg_yield,
            'total_good_units': total_good,
            'total_units': total_units,
            'total_defects': total_defects,
            'defect_rate': defect_rate,
            'count': len(relevant_orders)
        }

    def get_on_time_delivery_percentage(self, window: Optional[TimeWindow] = None) -> float:
        """Calculate on-time delivery percentage.

        Args:
            window: Optional time window

        Returns:
            Percentage of orders completed on time
        """
        if not window:
            now = datetime.utcnow()
            window = TimeWindow(now - timedelta(hours=24), now)

        relevant_orders = [
            wo for wo in self.work_orders.values()
            if wo.scheduled_window.overlaps(window) and wo.is_complete
        ]

        if not relevant_orders:
            return 100.0

        on_time = sum(
            1 for wo in relevant_orders
            if wo.actual_end and wo.actual_end <= wo.scheduled_window.end
        )

        return (on_time / len(relevant_orders)) * 100

    def get_production_summary(self, window: Optional[TimeWindow] = None) -> Dict:
        """Get production summary for period.

        Args:
            window: Optional time window

        Returns:
            Summary dictionary with key metrics
        """
        if not window:
            now = datetime.utcnow()
            window = TimeWindow(now - timedelta(hours=24), now)

        relevant_orders = [
            wo for wo in self.work_orders.values()
            if wo.scheduled_window.overlaps(window)
        ]

        completed_orders = [wo for wo in relevant_orders if wo.is_complete]

        return {
            'period': {
                'start': window.start.isoformat(),
                'end': window.end.isoformat(),
                'duration_hours': window.duration.total_seconds() / 3600
            },
            'orders': {
                'total': len(relevant_orders),
                'completed': len(completed_orders),
                'in_progress': len([wo for wo in relevant_orders if wo.status == WorkOrderStatus.IN_PROGRESS]),
                'failed': len([wo for wo in relevant_orders if wo.status == WorkOrderStatus.FAILED])
            },
            'production': {
                'total_units_targeted': sum(wo.target_quantity for wo in relevant_orders),
                'total_units_produced': sum(wo.total_units for wo in completed_orders),
                'total_good_units': sum(wo.good_units for wo in completed_orders),
                'total_defects': sum(wo.defect_units for wo in completed_orders),
                'overall_yield': (
                    sum(wo.good_units for wo in completed_orders) /
                    sum(wo.total_units for wo in completed_orders) * 100
                    if sum(wo.total_units for wo in completed_orders) > 0 else 0.0
                )
            },
            'schedule': {
                'on_time_percentage': self.get_on_time_delivery_percentage(window)
            }
        }


# ==================== Example Usage ====================

def main():
    """Example usage of production tracking."""

    # Create analytics instance
    analytics = ProductionAnalytics()

    # Register equipment
    equipment = analytics.register_equipment("Line1-Machine1")

    # Create work order
    now = datetime.utcnow()
    scheduled_window = TimeWindow(now, now + timedelta(hours=2))

    execution = WorkOrderExecution(
        work_order_id="WO-2024-001",
        product_id="Widget-A",
        equipment_id="Line1-Machine1",
        target_quantity=500,
        scheduled_window=scheduled_window
    )

    analytics.register_work_order(execution)

    # Simulate execution
    execution.start_execution(now + timedelta(minutes=5))

    # Record production events
    execution.record_event(ProductionEvent(
        timestamp=now + timedelta(minutes=30),
        equipment_id="Line1-Machine1",
        event_type="quality_check",
        value=0.95,
        unit="pass_rate"
    ))

    # Complete work order
    execution.good_units = 475
    execution.defect_units = 25
    execution.complete(now + timedelta(hours=2, minutes=10))

    # Record equipment downtime
    equipment.change_state(EquipmentState.UNPLANNED_DOWNTIME, now + timedelta(hours=1))
    equipment.record_downtime(
        "Jam in discharge",
        TimeWindow(now + timedelta(hours=1), now + timedelta(hours=1, minutes=15))
    )
    equipment.change_state(EquipmentState.RUNNING, now + timedelta(hours=1, minutes=15))

    # Calculate metrics
    oee = analytics.get_equipment_oee("Line1-Machine1", scheduled_window)
    yield_stats = analytics.calculate_yield_stats("Line1-Machine1", window=scheduled_window)
    cycle_stats = analytics.calculate_cycle_time_stats("Line1-Machine1", window=scheduled_window)
    otd = analytics.get_on_time_delivery_percentage(scheduled_window)
    summary = analytics.get_production_summary(scheduled_window)

    # Print results
    print(f"\n=== Production Analytics ===")
    print(f"OEE: {oee:.1f}%")
    print(f"\nYield Stats:")
    print(f"  Average Yield: {yield_stats['avg_yield']:.1f}%")
    print(f"  Total Units: {yield_stats['total_units']}")
    print(f"  Good Units: {yield_stats['total_good_units']}")
    print(f"  Defect Rate: {yield_stats['defect_rate']:.1f}%")
    print(f"\nCycle Time Stats:")
    print(f"  Average: {cycle_stats['avg_cycle_time']:.1f} minutes")
    print(f"  Min: {cycle_stats['min_cycle_time']:.1f} minutes")
    print(f"  Max: {cycle_stats['max_cycle_time']:.1f} minutes")
    print(f"\nOn-Time Delivery: {otd:.1f}%")
    print(f"\nProduction Summary:")
    print(f"  Orders Completed: {summary['orders']['completed']}/{summary['orders']['total']}")
    print(f"  Overall Yield: {summary['production']['overall_yield']:.1f}%")


if __name__ == "__main__":
    main()
