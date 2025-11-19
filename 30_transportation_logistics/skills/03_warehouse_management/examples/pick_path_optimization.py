"""
Pick Path Optimization for Warehouse Operations

Implements various picking strategies and path optimization algorithms including:
- S-Shape routing
- Return routing
- Largest gap
- Optimal (TSP-based) routing
- Batch picking optimization
"""

from dataclasses import dataclass, field
from typing import List, Set, Tuple, Dict, Optional
from enum import Enum
import math
from collections import defaultdict


class RoutingStrategy(Enum):
    S_SHAPE = "s_shape"
    RETURN = "return"
    LARGEST_GAP = "largest_gap"
    MIDPOINT = "midpoint"
    OPTIMAL = "optimal"  # TSP-based


@dataclass
class PickLocation:
    """Represents a pick location in the warehouse"""

    location_id: str
    aisle: int
    side: str  # "left" or "right"
    position: float  # Position along aisle (0-100)
    x: float  # Cartesian coordinates for distance calculation
    y: float
    sku: str
    quantity: int = 1

    def __hash__(self):
        return hash(self.location_id)


@dataclass
class PickList:
    """Collection of picks to be completed"""

    order_id: str
    picks: List[PickLocation]
    priority: int = 1


@dataclass
class PickPath:
    """Optimized sequence of pick locations"""

    order_id: str
    sequence: List[PickLocation]
    total_distance: float
    routing_strategy: RoutingStrategy


class WarehouseLayout:
    """Represents warehouse physical layout"""

    def __init__(
        self,
        num_aisles: int,
        aisle_length: float,
        aisle_width: float,
        cross_aisle_spacing: float = 100.0,
    ):
        self.num_aisles = num_aisles
        self.aisle_length = aisle_length
        self.aisle_width = aisle_width
        self.cross_aisle_spacing = cross_aisle_spacing

    def get_coordinates(self, aisle: int, position: float, side: str) -> Tuple[float, float]:
        """Convert aisle/position to x,y coordinates"""
        x = aisle * self.aisle_width
        y = position  # Position along aisle

        # Offset for side of aisle
        if side == "right":
            x += 3.0  # Small offset for right side

        return (x, y)

    def distance_between_points(
        self, point1: Tuple[float, float], point2: Tuple[float, float]
    ) -> float:
        """Calculate rectilinear (Manhattan) distance"""
        x1, y1 = point1
        x2, y2 = point2
        return abs(x2 - x1) + abs(y2 - y1)


class PickPathOptimizer:
    """Optimizes pick paths using various routing strategies"""

    def __init__(self, layout: WarehouseLayout):
        self.layout = layout

    def optimize(
        self, pick_list: PickList, strategy: RoutingStrategy = RoutingStrategy.S_SHAPE
    ) -> PickPath:
        """Generate optimized pick path"""

        if strategy == RoutingStrategy.S_SHAPE:
            sequence = self._s_shape_routing(pick_list.picks)
        elif strategy == RoutingStrategy.RETURN:
            sequence = self._return_routing(pick_list.picks)
        elif strategy == RoutingStrategy.LARGEST_GAP:
            sequence = self._largest_gap_routing(pick_list.picks)
        elif strategy == RoutingStrategy.MIDPOINT:
            sequence = self._midpoint_routing(pick_list.picks)
        elif strategy == RoutingStrategy.OPTIMAL:
            sequence = self._optimal_routing(pick_list.picks)
        else:
            sequence = pick_list.picks

        # Calculate total distance
        total_distance = self._calculate_path_distance(sequence)

        return PickPath(
            order_id=pick_list.order_id,
            sequence=sequence,
            total_distance=total_distance,
            routing_strategy=strategy,
        )

    def _s_shape_routing(self, picks: List[PickLocation]) -> List[PickLocation]:
        """
        S-Shape: Traverse aisles completely in serpentine pattern.
        Best for dense picking (many picks per aisle).
        """
        # Group picks by aisle
        aisle_picks = defaultdict(list)
        for pick in picks:
            aisle_picks[pick.aisle].append(pick)

        # Sort each aisle's picks by position
        for aisle in aisle_picks:
            aisle_picks[aisle].sort(key=lambda p: p.position)

        # Create sequence by traversing aisles
        sequence = []
        aisles_to_visit = sorted(aisle_picks.keys())

        direction = 1  # 1 = forward, -1 = backward
        for aisle in aisles_to_visit:
            picks_in_aisle = aisle_picks[aisle]

            if direction == -1:
                picks_in_aisle.reverse()

            sequence.extend(picks_in_aisle)
            direction *= -1  # Alternate direction

        return sequence

    def _return_routing(self, picks: List[PickLocation]) -> List[PickLocation]:
        """
        Return: Enter aisle, pick, return to front. Repeat for each aisle.
        Best for sparse picking (few picks per aisle).
        """
        # Group picks by aisle
        aisle_picks = defaultdict(list)
        for pick in picks:
            aisle_picks[pick.aisle].append(pick)

        # Sort each aisle's picks by position
        for aisle in aisle_picks:
            aisle_picks[aisle].sort(key=lambda p: p.position)

        # Create sequence by visiting each aisle and returning
        sequence = []
        aisles_to_visit = sorted(aisle_picks.keys())

        for aisle in aisles_to_visit:
            picks_in_aisle = aisle_picks[aisle]
            sequence.extend(picks_in_aisle)

        return sequence

    def _largest_gap_routing(self, picks: List[PickLocation]) -> List[PickLocation]:
        """
        Largest Gap: Skip aisles where no picks exist, or where gap between picks is large.
        Hybrid approach - more efficient than S-shape for medium density.
        """
        # Group picks by aisle
        aisle_picks = defaultdict(list)
        for pick in picks:
            aisle_picks[pick.aisle].append(pick)

        # Sort each aisle's picks by position
        for aisle in aisle_picks:
            aisle_picks[aisle].sort(key=lambda p: p.position)

        sequence = []
        aisles_to_visit = sorted(aisle_picks.keys())

        direction = 1  # 1 = forward, -1 = backward

        for aisle in aisles_to_visit:
            picks_in_aisle = aisle_picks[aisle]

            if direction == -1:
                picks_in_aisle.reverse()

            # Check if we should traverse entire aisle or skip middle
            if len(picks_in_aisle) == 0:
                continue
            elif len(picks_in_aisle) == 1:
                # Single pick - just enter and return
                sequence.append(picks_in_aisle[0])
                # Don't alternate direction for return routing
            elif len(picks_in_aisle) == 2:
                # Two picks - check gap
                gap = abs(picks_in_aisle[1].position - picks_in_aisle[0].position)
                if gap > self.layout.aisle_length * 0.6:
                    # Large gap - do return routing
                    sequence.extend(picks_in_aisle)
                else:
                    # Small gap - traverse
                    sequence.extend(picks_in_aisle)
                    direction *= -1
            else:
                # Multiple picks - find largest gap
                largest_gap = 0
                gap_index = -1

                for i in range(len(picks_in_aisle) - 1):
                    gap = abs(
                        picks_in_aisle[i + 1].position - picks_in_aisle[i].position
                    )
                    if gap > largest_gap:
                        largest_gap = gap
                        gap_index = i

                # If largest gap is significant, split picks
                if largest_gap > self.layout.aisle_length * 0.4:
                    # Return routing for this aisle
                    sequence.extend(picks_in_aisle)
                else:
                    # Traverse entire aisle
                    sequence.extend(picks_in_aisle)
                    direction *= -1

        return sequence

    def _midpoint_routing(self, picks: List[PickLocation]) -> List[PickLocation]:
        """
        Midpoint: Enter aisle only to midpoint if all picks are before midpoint,
        otherwise traverse entire aisle.
        """
        aisle_picks = defaultdict(list)
        for pick in picks:
            aisle_picks[pick.aisle].append(pick)

        for aisle in aisle_picks:
            aisle_picks[aisle].sort(key=lambda p: p.position)

        sequence = []
        aisles_to_visit = sorted(aisle_picks.keys())
        direction = 1

        midpoint = self.layout.aisle_length / 2

        for aisle in aisles_to_visit:
            picks_in_aisle = aisle_picks[aisle]

            if direction == -1:
                picks_in_aisle.reverse()

            # Check if all picks are before midpoint
            max_position = max(p.position for p in picks_in_aisle)
            min_position = min(p.position for p in picks_in_aisle)

            if max_position < midpoint:
                # All picks in first half - return routing
                sequence.extend(picks_in_aisle)
            elif min_position > midpoint:
                # All picks in second half - enter from other end and return
                sequence.extend(picks_in_aisle)
            else:
                # Picks span midpoint - traverse entire aisle
                sequence.extend(picks_in_aisle)
                direction *= -1

        return sequence

    def _optimal_routing(self, picks: List[PickLocation]) -> List[PickLocation]:
        """
        Optimal: Use TSP-like optimization for true optimal path.
        Computationally expensive but best for complex layouts.
        """
        if len(picks) <= 1:
            return picks

        # Use nearest neighbor heuristic + 2-opt improvement
        unvisited = set(picks)
        current = picks[0]
        sequence = [current]
        unvisited.remove(current)

        # Nearest neighbor construction
        while unvisited:
            nearest = min(
                unvisited,
                key=lambda p: self.layout.distance_between_points(
                    (current.x, current.y), (p.x, p.y)
                ),
            )
            sequence.append(nearest)
            unvisited.remove(nearest)
            current = nearest

        # 2-opt improvement
        improved = True
        while improved:
            improved = False
            for i in range(1, len(sequence) - 2):
                for j in range(i + 1, len(sequence)):
                    if j - i == 1:
                        continue

                    # Calculate current distance
                    current_dist = (
                        self.layout.distance_between_points(
                            (sequence[i - 1].x, sequence[i - 1].y),
                            (sequence[i].x, sequence[i].y),
                        )
                        + self.layout.distance_between_points(
                            (sequence[j - 1].x, sequence[j - 1].y),
                            (sequence[j].x, sequence[j].y),
                        )
                    )

                    # Calculate new distance if we reverse segment
                    new_dist = (
                        self.layout.distance_between_points(
                            (sequence[i - 1].x, sequence[i - 1].y),
                            (sequence[j - 1].x, sequence[j - 1].y),
                        )
                        + self.layout.distance_between_points(
                            (sequence[i].x, sequence[i].y),
                            (sequence[j].x, sequence[j].y),
                        )
                    )

                    if new_dist < current_dist:
                        # Reverse segment
                        sequence[i:j] = reversed(sequence[i:j])
                        improved = True

        return sequence

    def _calculate_path_distance(self, sequence: List[PickLocation]) -> float:
        """Calculate total travel distance for pick sequence"""
        if not sequence:
            return 0.0

        total = 0.0

        # Start from shipping (0, 0)
        prev_point = (0.0, 0.0)

        for pick in sequence:
            current_point = (pick.x, pick.y)
            total += self.layout.distance_between_points(prev_point, current_point)
            prev_point = current_point

        # Return to shipping
        total += self.layout.distance_between_points(prev_point, (0.0, 0.0))

        return total

    def compare_strategies(self, pick_list: PickList) -> Dict[str, PickPath]:
        """Compare all routing strategies for a pick list"""
        results = {}

        for strategy in RoutingStrategy:
            path = self.optimize(pick_list, strategy)
            results[strategy.value] = path

        return results


class BatchPickOptimizer:
    """Optimize batch picking assignments"""

    def __init__(self, max_orders_per_batch: int = 5):
        self.max_orders_per_batch = max_orders_per_batch

    def create_batches(self, orders: List[PickList]) -> List[List[PickList]]:
        """Group orders into batches based on aisle overlap"""
        if not orders:
            return []

        # Sort orders by number of picks (largest first)
        sorted_orders = sorted(orders, key=lambda o: len(o.picks), reverse=True)

        batches = []
        current_batch = []
        current_batch_aisles = set()

        for order in sorted_orders:
            order_aisles = set(pick.aisle for pick in order.picks)

            # Check if adding this order to current batch makes sense
            overlap = len(current_batch_aisles & order_aisles)
            overlap_ratio = (
                overlap / len(order_aisles) if order_aisles else 0
            )

            if (
                len(current_batch) < self.max_orders_per_batch
                and (overlap_ratio > 0.3 or len(current_batch) == 0)
            ):
                # Add to current batch
                current_batch.append(order)
                current_batch_aisles.update(order_aisles)
            else:
                # Start new batch
                if current_batch:
                    batches.append(current_batch)

                current_batch = [order]
                current_batch_aisles = order_aisles

        # Add last batch
        if current_batch:
            batches.append(current_batch)

        return batches


# ============================================================================
# Example Usage
# ============================================================================


def example_usage():
    # Create warehouse layout
    layout = WarehouseLayout(
        num_aisles=10, aisle_length=200.0, aisle_width=15.0, cross_aisle_spacing=50.0
    )

    # Create sample pick locations
    picks = [
        PickLocation("A01-L-10", 1, "left", 10, *layout.get_coordinates(1, 10, "left"), "SKU001"),
        PickLocation("A01-R-25", 1, "right", 25, *layout.get_coordinates(1, 25, "right"), "SKU002"),
        PickLocation("A02-L-50", 2, "left", 50, *layout.get_coordinates(2, 50, "left"), "SKU003"),
        PickLocation("A03-R-75", 3, "right", 75, *layout.get_coordinates(3, 75, "right"), "SKU004"),
        PickLocation("A03-L-120", 3, "left", 120, *layout.get_coordinates(3, 120, "left"), "SKU005"),
        PickLocation("A05-R-30", 5, "right", 30, *layout.get_coordinates(5, 30, "right"), "SKU006"),
        PickLocation("A05-L-180", 5, "left", 180, *layout.get_coordinates(5, 180, "left"), "SKU007"),
        PickLocation("A07-R-90", 7, "right", 90, *layout.get_coordinates(7, 90, "right"), "SKU008"),
    ]

    pick_list = PickList(order_id="ORDER-001", picks=picks, priority=1)

    # Create optimizer
    optimizer = PickPathOptimizer(layout)

    # Compare all strategies
    print("=== Pick Path Strategy Comparison ===")
    print(f"Order: {pick_list.order_id}")
    print(f"Number of picks: {len(pick_list.picks)}")
    print()

    results = optimizer.compare_strategies(pick_list)

    for strategy_name, path in sorted(
        results.items(), key=lambda x: x[1].total_distance
    ):
        print(f"{strategy_name.upper():20s}: {path.total_distance:8.1f} feet")

    # Show detailed path for best strategy
    best_strategy = min(results.items(), key=lambda x: x[1].total_distance)
    best_path = best_strategy[1]

    print(f"\n=== Best Strategy: {best_strategy[0].upper()} ===")
    print("Pick sequence:")
    for i, pick in enumerate(best_path.sequence, 1):
        print(f"  {i}. {pick.location_id} (Aisle {pick.aisle}, Position {pick.position:.0f})")

    # Batch picking example
    print("\n=== Batch Picking Optimization ===")

    # Create multiple orders
    orders = [
        PickList("ORDER-001", picks[:3]),
        PickList("ORDER-002", picks[3:5]),
        PickList("ORDER-003", picks[5:]),
        PickList(
            "ORDER-004",
            [
                PickLocation("A01-L-15", 1, "left", 15, *layout.get_coordinates(1, 15, "left"), "SKU009"),
                PickLocation("A02-R-40", 2, "right", 40, *layout.get_coordinates(2, 40, "right"), "SKU010"),
            ],
        ),
    ]

    batch_optimizer = BatchPickOptimizer(max_orders_per_batch=3)
    batches = batch_optimizer.create_batches(orders)

    print(f"Created {len(batches)} batches from {len(orders)} orders:")
    for i, batch in enumerate(batches, 1):
        order_ids = [order.order_id for order in batch]
        total_picks = sum(len(order.picks) for order in batch)
        print(f"  Batch {i}: {order_ids} ({total_picks} total picks)")


if __name__ == "__main__":
    example_usage()
