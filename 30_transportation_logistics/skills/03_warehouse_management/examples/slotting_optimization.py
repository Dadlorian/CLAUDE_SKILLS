"""
Warehouse Slotting Optimization

Production-ready implementation of slotting algorithms to optimize product placement
in warehouse locations based on velocity, cube utilization, and operational efficiency.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
import numpy as np
from collections import defaultdict
import heapq


class StorageType(Enum):
    FLOOR = "floor"
    PALLET_RACK = "pallet_rack"
    FLOW_RACK = "flow_rack"
    SHELVING = "shelving"
    CASE_FLOW = "case_flow"
    EACH_PICK = "each_pick"


class ProductCategory(Enum):
    A_MOVER = "a"  # Top 20% velocity
    B_MOVER = "b"  # Middle 30%
    C_MOVER = "c"  # Bottom 50%


@dataclass
class Product:
    sku: str
    description: str
    length: float  # inches
    width: float
    height: float
    weight: float  # lbs
    picks_per_day: float  # average daily pick lines
    picks_per_line: float = 1.0  # units per pick
    case_quantity: int = 1
    requires_refrigeration: bool = False
    hazmat: bool = False
    category: Optional[ProductCategory] = None

    @property
    def cube(self) -> float:
        """Cubic feet"""
        return (self.length * self.width * self.height) / 1728.0

    @property
    def velocity_score(self) -> float:
        """Picks per day (higher = faster moving)"""
        return self.picks_per_day


@dataclass
class Location:
    location_id: str
    aisle: int
    bay: int
    level: int  # 1 = floor, higher = elevated
    length: float
    width: float
    height: float
    storage_type: StorageType
    zone: str  # e.g., "ambient", "refrigerated", "hazmat"
    distance_from_shipping: float  # feet
    current_sku: Optional[str] = None
    priority_score: float = field(default=0.0, init=False)

    @property
    def cube(self) -> float:
        """Cubic feet"""
        return (self.length * self.width * self.height) / 1728.0

    @property
    def is_golden_zone(self) -> bool:
        """Waist-height, near shipping (best locations)"""
        return self.level in [2, 3] and self.distance_from_shipping < 100

    @property
    def accessibility_score(self) -> float:
        """Higher score = more accessible (lower = better)"""
        # Prefer waist height (level 2-3), penalize high/low
        level_penalty = abs(self.level - 2.5) * 10

        # Penalize distance from shipping
        distance_penalty = self.distance_from_shipping

        return level_penalty + distance_penalty


@dataclass
class SlottingRecommendation:
    sku: str
    from_location: Optional[str]
    to_location: str
    reason: str
    expected_improvement: float  # % reduction in travel or improvement in picks
    priority: int = 1  # 1 = high, 3 = low


class SlottingOptimizer:
    """
    Optimizes warehouse slotting using velocity-based placement and profitability index.
    """

    def __init__(self, products: List[Product], locations: List[Location]):
        self.products = products
        self.locations = locations
        self.product_map = {p.sku: p for p in products}
        self.location_map = {l.location_id: l for l in locations}

        # Calculate ABC categories
        self._categorize_products()

    def _categorize_products(self):
        """Classify products into A/B/C categories using velocity"""
        sorted_products = sorted(
            self.products, key=lambda p: p.velocity_score, reverse=True
        )

        total_picks = sum(p.picks_per_day for p in sorted_products)
        cumulative_picks = 0

        for product in sorted_products:
            cumulative_picks += product.picks_per_day
            cumulative_pct = cumulative_picks / total_picks

            if cumulative_pct <= 0.20:
                product.category = ProductCategory.A_MOVER
            elif cumulative_pct <= 0.50:
                product.category = ProductCategory.B_MOVER
            else:
                product.category = ProductCategory.C_MOVER

    def optimize(self) -> List[SlottingRecommendation]:
        """
        Generate slotting recommendations using profitability index method.
        """
        recommendations = []

        # Calculate profitability index for each product-location pair
        assignments = []

        for product in self.products:
            compatible_locations = self._get_compatible_locations(product)

            for location in compatible_locations:
                if location.current_sku == product.sku:
                    # Already in this location
                    continue

                profitability_index = self._calculate_profitability_index(
                    product, location
                )

                assignments.append(
                    {
                        "sku": product.sku,
                        "location": location.location_id,
                        "index": profitability_index,
                        "product": product,
                        "location_obj": location,
                    }
                )

        # Sort by profitability index (highest first)
        assignments.sort(key=lambda x: x["index"], reverse=True)

        # Assign products to locations (greedy)
        assigned_products = set()
        assigned_locations = set()

        for assignment in assignments:
            sku = assignment["sku"]
            location_id = assignment["location"]

            if sku in assigned_products or location_id in assigned_locations:
                continue

            product = assignment["product"]
            location = assignment["location_obj"]
            current_location = self._get_current_location(sku)

            if current_location:
                # Calculate improvement
                current_score = self._calculate_profitability_index(
                    product, current_location
                )
                new_score = assignment["index"]
                improvement = ((new_score - current_score) / current_score * 100) if current_score > 0 else 100

                if improvement > 5:  # Only recommend if >5% improvement
                    recommendations.append(
                        SlottingRecommendation(
                            sku=sku,
                            from_location=current_location.location_id,
                            to_location=location_id,
                            reason=f"Move from {current_location.location_id} to {location_id}",
                            expected_improvement=improvement,
                            priority=self._get_priority(product),
                        )
                    )
            else:
                # New slotting
                recommendations.append(
                    SlottingRecommendation(
                        sku=sku,
                        from_location=None,
                        to_location=location_id,
                        reason=f"Initial slotting to {location_id}",
                        expected_improvement=100.0,
                        priority=self._get_priority(product),
                    )
                )

            assigned_products.add(sku)
            assigned_locations.add(location_id)

        return sorted(recommendations, key=lambda r: (r.priority, -r.expected_improvement))

    def _calculate_profitability_index(
        self, product: Product, location: Location
    ) -> float:
        """
        Profitability Index = (Picks × Cube) / (Travel Distance × Slot Size)

        Higher index = better match
        """
        # Velocity component
        picks = product.velocity_score

        # Cube utilization component
        cube_utilization = product.cube / location.cube if location.cube > 0 else 0

        # Accessibility component (lower distance = higher score)
        travel_factor = 1.0 / (1.0 + location.distance_from_shipping / 100.0)

        # Golden zone bonus
        golden_zone_bonus = 1.5 if location.is_golden_zone else 1.0

        # Combine factors
        index = (
            picks * cube_utilization * travel_factor * golden_zone_bonus
        )

        return index

    def _get_compatible_locations(self, product: Product) -> List[Location]:
        """Find locations that can physically fit the product"""
        compatible = []

        for location in self.locations:
            # Check size fit
            if (
                product.length > location.length
                or product.width > location.width
                or product.height > location.height
            ):
                continue

            # Check zone compatibility
            if product.requires_refrigeration and location.zone != "refrigerated":
                continue

            if product.hazmat and location.zone != "hazmat":
                continue

            compatible.append(location)

        return compatible

    def _get_current_location(self, sku: str) -> Optional[Location]:
        """Find current location of SKU"""
        for location in self.locations:
            if location.current_sku == sku:
                return location
        return None

    def _get_priority(self, product: Product) -> int:
        """Determine priority of slotting change (1=high, 3=low)"""
        if product.category == ProductCategory.A_MOVER:
            return 1
        elif product.category == ProductCategory.B_MOVER:
            return 2
        else:
            return 3

    def analyze_current_slotting(self) -> Dict:
        """Analyze current slotting efficiency"""
        total_picks = 0
        total_travel = 0
        golden_zone_picks = 0
        category_stats = defaultdict(lambda: {"picks": 0, "in_golden": 0})

        for location in self.locations:
            if location.current_sku:
                product = self.product_map.get(location.current_sku)
                if product:
                    picks = product.picks_per_day
                    travel = picks * location.distance_from_shipping

                    total_picks += picks
                    total_travel += travel

                    if location.is_golden_zone:
                        golden_zone_picks += picks

                    cat = product.category.value if product.category else "unknown"
                    category_stats[cat]["picks"] += picks
                    if location.is_golden_zone:
                        category_stats[cat]["in_golden"] += picks

        avg_travel_per_pick = total_travel / total_picks if total_picks > 0 else 0
        golden_zone_pct = (
            (golden_zone_picks / total_picks * 100) if total_picks > 0 else 0
        )

        return {
            "total_picks_per_day": total_picks,
            "total_travel_feet_per_day": total_travel,
            "avg_travel_per_pick": avg_travel_per_pick,
            "golden_zone_pick_percentage": golden_zone_pct,
            "category_stats": dict(category_stats),
        }


class DynamicSlottingEngine:
    """
    Real-time slotting adjustments based on changing velocity patterns.
    """

    def __init__(self, optimizer: SlottingOptimizer):
        self.optimizer = optimizer
        self.velocity_history = defaultdict(list)

    def update_velocity(self, sku: str, picks_today: int):
        """Track daily picks for trending analysis"""
        self.velocity_history[sku].append(picks_today)

        # Keep last 30 days
        if len(self.velocity_history[sku]) > 30:
            self.velocity_history[sku].pop(0)

    def detect_velocity_changes(self) -> List[Tuple[str, str, float]]:
        """
        Detect products with significant velocity changes.
        Returns list of (sku, change_type, change_pct)
        """
        changes = []

        for sku, history in self.velocity_history.items():
            if len(history) < 14:  # Need at least 2 weeks
                continue

            # Compare recent week to previous week
            recent_avg = np.mean(history[-7:])
            previous_avg = np.mean(history[-14:-7])

            if previous_avg == 0:
                continue

            change_pct = ((recent_avg - previous_avg) / previous_avg) * 100

            if abs(change_pct) > 30:  # >30% change
                change_type = "increase" if change_pct > 0 else "decrease"
                changes.append((sku, change_type, change_pct))

        return changes

    def recommend_reallocations(
        self, velocity_changes: List[Tuple[str, str, float]]
    ) -> List[SlottingRecommendation]:
        """Generate recommendations based on velocity changes"""
        recommendations = []

        for sku, change_type, change_pct in velocity_changes:
            product = self.optimizer.product_map.get(sku)
            if not product:
                continue

            current_location = self.optimizer._get_current_location(sku)
            if not current_location:
                continue

            if change_type == "increase":
                # Moving up in velocity - find better location
                better_locations = [
                    loc
                    for loc in self.optimizer._get_compatible_locations(product)
                    if loc.accessibility_score < current_location.accessibility_score
                ]

                if better_locations:
                    best_location = min(
                        better_locations, key=lambda l: l.accessibility_score
                    )

                    recommendations.append(
                        SlottingRecommendation(
                            sku=sku,
                            from_location=current_location.location_id,
                            to_location=best_location.location_id,
                            reason=f"Velocity increased {change_pct:.1f}%, move to more accessible location",
                            expected_improvement=change_pct / 2,  # Estimate
                            priority=1,
                        )
                    )

        return recommendations


# ============================================================================
# Example Usage
# ============================================================================

def example_usage():
    # Define products
    products = [
        Product("SKU001", "Fast Mover A", 12, 12, 8, 5, picks_per_day=50),
        Product("SKU002", "Fast Mover B", 18, 18, 12, 10, picks_per_day=45),
        Product("SKU003", "Medium Mover", 24, 18, 12, 15, picks_per_day=15),
        Product("SKU004", "Slow Mover A", 12, 12, 6, 3, picks_per_day=2),
        Product("SKU005", "Slow Mover B", 18, 12, 8, 8, picks_per_day=1),
        Product(
            "SKU006",
            "Refrigerated Fast",
            12,
            12,
            10,
            6,
            picks_per_day=30,
            requires_refrigeration=True,
        ),
    ]

    # Define locations
    locations = [
        Location("A01-01-02", 1, 1, 2, 48, 40, 48, StorageType.PALLET_RACK, "ambient", 20),
        Location("A01-02-02", 1, 2, 2, 48, 40, 48, StorageType.PALLET_RACK, "ambient", 25),
        Location("A01-03-03", 1, 3, 3, 48, 40, 48, StorageType.PALLET_RACK, "ambient", 30),
        Location("A02-01-01", 2, 1, 1, 48, 40, 72, StorageType.FLOOR, "ambient", 50),
        Location("A02-02-05", 2, 2, 5, 24, 24, 24, StorageType.SHELVING, "ambient", 55),
        Location("R01-01-02", 10, 1, 2, 48, 40, 48, StorageType.PALLET_RACK, "refrigerated", 100),
    ]

    # Create optimizer
    optimizer = SlottingOptimizer(products, locations)

    # Analyze current state (before optimization)
    print("=== Current Slotting Analysis ===")
    current_stats = optimizer.analyze_current_slotting()
    print(f"Total picks/day: {current_stats['total_picks_per_day']:.0f}")
    print(f"Avg travel/pick: {current_stats['avg_travel_per_pick']:.1f} feet")
    print(f"Golden zone %: {current_stats['golden_zone_pick_percentage']:.1f}%")

    # Generate recommendations
    print("\n=== Slotting Recommendations ===")
    recommendations = optimizer.optimize()

    for i, rec in enumerate(recommendations[:10], 1):  # Top 10
        print(f"\n{i}. SKU: {rec.sku} (Priority {rec.priority})")
        if rec.from_location:
            print(f"   Move from: {rec.from_location} → {rec.to_location}")
        else:
            print(f"   Initial slot: {rec.to_location}")
        print(f"   Expected improvement: {rec.expected_improvement:.1f}%")
        print(f"   Reason: {rec.reason}")

    # Dynamic slotting example
    print("\n=== Dynamic Slotting (Velocity Changes) ===")
    dynamic_engine = DynamicSlottingEngine(optimizer)

    # Simulate velocity tracking
    dynamic_engine.update_velocity("SKU001", 50)
    dynamic_engine.update_velocity("SKU001", 52)
    # ... simulate 14 days ...
    for day in range(14):
        dynamic_engine.update_velocity("SKU001", 50 + day)  # Increasing trend

    # Detect changes
    velocity_changes = dynamic_engine.detect_velocity_changes()
    print(f"Detected {len(velocity_changes)} velocity changes")

    for sku, change_type, change_pct in velocity_changes:
        print(f"  {sku}: {change_type} by {change_pct:.1f}%")

    # Get reallocation recommendations
    reallocations = dynamic_engine.recommend_reallocations(velocity_changes)
    print(f"\nGenerated {len(reallocations)} reallocation recommendations")


if __name__ == "__main__":
    example_usage()
