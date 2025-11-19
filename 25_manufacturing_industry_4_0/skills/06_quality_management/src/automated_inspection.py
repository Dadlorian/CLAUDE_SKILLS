"""
Automated Computer Vision Inspection Module

This module provides tools for automated optical inspection (AOI)
and computer vision-based dimensional inspection in manufacturing.

Author: Quality Engineering
License: MIT
"""

import numpy as np
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict
from enum import Enum
import logging


class DefectType(Enum):
    """Types of defects detected in inspection"""
    SURFACE_SCRATCH = "Surface Scratch"
    SOLDER_BRIDGE = "Solder Bridge"
    COLD_SOLDER = "Cold Solder Joint"
    MISSING_COMPONENT = "Missing Component"
    COMPONENT_MISALIGNMENT = "Component Misalignment"
    COLOR_MISMATCH = "Color Mismatch"
    DIMENSIONAL_OUT_OF_SPEC = "Dimension Out of Spec"
    INCOMPLETE_FILL = "Incomplete Fill"
    VOID_OR_INCLUSION = "Void/Inclusion"
    CONNECTOR_SEATING = "Connector Not Fully Seated"
    NO_DEFECT = "No Defect"


class InspectionResult(Enum):
    """Inspection result classification"""
    PASS = "PASS"
    FAIL_HIGH_CONFIDENCE = "FAIL_HIGH_CONFIDENCE"
    FAIL_LOW_CONFIDENCE = "FAIL_LOW_CONFIDENCE"
    MANUAL_REVIEW = "MANUAL_REVIEW"


@dataclass
class InspectionImage:
    """Container for inspection image data"""
    image_id: str
    image_array: np.ndarray
    timestamp: str
    location: str
    production_line: str
    part_id: str

    @property
    def image_shape(self) -> Tuple:
        """Get image shape (height, width, channels)"""
        return self.image_array.shape

    @property
    def pixel_count(self) -> int:
        """Total number of pixels"""
        return np.prod(self.image_shape[:2])


@dataclass
class DetectionResult:
    """Result of defect detection"""
    defect_type: DefectType
    confidence: float  # 0-1 scale
    location: Tuple[int, int]  # (x, y) coordinates
    region: Optional[Tuple[int, int, int, int]] = None  # (x1, y1, x2, y2) bounding box
    severity: int = 1  # 1-10 scale


class CalibrationData:
    """Camera calibration and scaling information"""

    def __init__(self, pixels_per_mm: float, lens_distortion: Optional[np.ndarray] = None):
        """
        Initialize calibration data

        Args:
            pixels_per_mm: Conversion factor from pixels to millimeters
            lens_distortion: Distortion coefficients (k1, k2, p1, p2, k3)
        """
        self.pixels_per_mm = pixels_per_mm
        self.lens_distortion = lens_distortion or np.array([0, 0, 0, 0, 0])

    def pixel_to_mm(self, pixel_distance: float) -> float:
        """Convert pixel distance to millimeters"""
        return pixel_distance / self.pixels_per_mm

    def mm_to_pixel(self, mm_distance: float) -> float:
        """Convert millimeter distance to pixels"""
        return mm_distance * self.pixels_per_mm


class EdgeDetector:
    """Edge detection algorithms for dimensional measurement"""

    @staticmethod
    def canny_edge_detection(image: np.ndarray, low_threshold: int = 50,
                            high_threshold: int = 150) -> np.ndarray:
        """
        Simplified Canny edge detection

        Args:
            image: Input image (grayscale)
            low_threshold: Lower threshold for edge detection
            high_threshold: Upper threshold for edge detection

        Returns:
            Binary edge map
        """
        if len(image.shape) == 3:
            # Convert color to grayscale
            image = np.dot(image[..., :3], [0.299, 0.587, 0.114])

        # Simple Sobel-based edge detection
        # Sobel X kernel
        kernel_x = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=float)
        # Sobel Y kernel
        kernel_y = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]], dtype=float)

        # Approximate gradient calculation
        edges = np.zeros_like(image, dtype=float)

        for i in range(1, image.shape[0] - 1):
            for j in range(1, image.shape[1] - 1):
                region = image[i-1:i+2, j-1:j+2].astype(float)
                gx = np.sum(region * kernel_x)
                gy = np.sum(region * kernel_y)
                edges[i, j] = np.sqrt(gx**2 + gy**2)

        # Threshold
        edges = (edges > low_threshold).astype(int)
        return edges

    @staticmethod
    def detect_lines(edges: np.ndarray, min_length: int = 10) -> List[Tuple]:
        """
        Simple line detection from edges

        Args:
            edges: Binary edge map
            min_length: Minimum line length in pixels

        Returns:
            List of line segments as ((x1,y1), (x2,y2))
        """
        lines = []
        visited = np.zeros_like(edges)

        # Find connected edge pixels
        for i in range(edges.shape[0]):
            for j in range(edges.shape[1]):
                if edges[i, j] > 0 and visited[i, j] == 0:
                    # Trace connected component
                    line_points = []
                    stack = [(i, j)]

                    while stack:
                        y, x = stack.pop()
                        if y < 0 or y >= edges.shape[0] or x < 0 or x >= edges.shape[1]:
                            continue
                        if visited[y, x] > 0 or edges[y, x] == 0:
                            continue

                        visited[y, x] = 1
                        line_points.append((x, y))

                        # Check neighbors
                        for dy in [-1, 0, 1]:
                            for dx in [-1, 0, 1]:
                                stack.append((y + dy, x + dx))

                    if len(line_points) >= min_length:
                        # Find endpoints
                        line_points = np.array(line_points)
                        p1 = line_points[0]
                        p2 = line_points[-1]
                        lines.append((p1, p2))

        return lines

    @staticmethod
    def detect_circles(edges: np.ndarray, radius_range: Tuple[int, int] = (10, 100)
                       ) -> List[Tuple[int, int, int]]:
        """
        Simple circle detection using Hough transform approximation

        Args:
            edges: Binary edge map
            radius_range: (min_radius, max_radius) in pixels

        Returns:
            List of (center_x, center_y, radius) tuples
        """
        circles = []
        min_r, max_r = radius_range

        # For each possible radius
        for r in range(min_r, max_r):
            # Accumulator array for circle centers
            accumulator = np.zeros((edges.shape[0], edges.shape[1]))

            # For each edge pixel, vote for circle center
            edge_pixels = np.where(edges > 0)
            for y, x in zip(edge_pixels[0], edge_pixels[1]):
                # Circle equation: (x-cx)^2 + (y-cy)^2 = r^2
                # Try all angles
                for angle in np.linspace(0, 2*np.pi, 36):
                    cx = int(x - r * np.cos(angle))
                    cy = int(y - r * np.sin(angle))

                    if 0 <= cx < accumulator.shape[1] and 0 <= cy < accumulator.shape[0]:
                        accumulator[cy, cx] += 1

            # Find peaks in accumulator
            threshold = 10
            peaks = np.where(accumulator > threshold)
            for cy, cx in zip(peaks[0], peaks[1]):
                circles.append((cx, cy, r))

        return circles


class DimensionalInspector:
    """Vision-based dimensional measurement and inspection"""

    def __init__(self, calibration: CalibrationData):
        """
        Initialize inspector

        Args:
            calibration: CalibrationData object
        """
        self.calibration = calibration
        self.edge_detector = EdgeDetector()

    def measure_hole_diameter(self, image: np.ndarray) -> Optional[Tuple[float, Tuple[int, int]]]:
        """
        Measure hole diameter from image

        Args:
            image: Image array containing hole

        Returns:
            (diameter_mm, center_coordinates) or None if not detected
        """
        # Detect edges
        edges = self.edge_detector.canny_edge_detection(image)

        # Detect circles
        circles = self.edge_detector.detect_circles(edges)

        if not circles:
            return None

        # Use largest circle
        circles.sort(key=lambda c: c[2], reverse=True)
        cx, cy, radius_pixels = circles[0]

        # Convert to mm
        diameter_mm = self.calibration.pixel_to_mm(radius_pixels * 2)

        return diameter_mm, (cx, cy)

    def measure_feature_distance(self, image: np.ndarray) -> Optional[float]:
        """
        Measure distance between two features (e.g., slot width)

        Args:
            image: Image array

        Returns:
            Distance in mm or None
        """
        edges = self.edge_detector.canny_edge_detection(image)
        lines = self.edge_detector.detect_lines(edges)

        if len(lines) < 2:
            return None

        # Find two parallel lines
        line1, line2 = lines[0], lines[1]

        # Calculate distance between lines
        # Distance = |ax + by + c| / sqrt(a^2 + b^2)
        # Simplified: use perpendicular distance
        (x1, y1), _ = line1
        (x2, y2), _ = line2

        distance_pixels = abs(x2 - x1)
        distance_mm = self.calibration.pixel_to_mm(distance_pixels)

        return distance_mm

    def check_part_presence(self, image: np.ndarray, threshold: float = 0.3) -> bool:
        """
        Check if part is present in field of view

        Args:
            image: Image array
            threshold: Fraction of image that must be filled

        Returns:
            True if part detected
        """
        if len(image.shape) == 3:
            # Convert to grayscale
            image = np.dot(image[..., :3], [0.299, 0.587, 0.114])

        # Simple presence check: non-background pixels
        background_level = 200  # Assuming bright background
        part_pixels = np.sum(image < background_level)
        total_pixels = image.size

        return (part_pixels / total_pixels) > threshold


class DefectDetector:
    """Machine learning based defect detection"""

    def __init__(self, confidence_threshold: float = 0.85):
        """
        Initialize defect detector

        Args:
            confidence_threshold: Minimum confidence for FAIL_HIGH_CONFIDENCE
        """
        self.confidence_threshold = confidence_threshold
        self.logger = logging.getLogger(__name__)

    def detect_solder_bridge(self, image: np.ndarray) -> List[DetectionResult]:
        """
        Detect solder bridge defects

        Solder bridges are unwanted solder connections between traces.

        Args:
            image: Image array

        Returns:
            List of DetectionResult objects
        """
        detections = []

        # Simplified detection: look for large continuous solder regions
        if len(image.shape) == 3:
            # Extract solder region (typically shiny/bright)
            solder_mask = image[:, :, 2] > image[:, :, 0]  # More blue/silver
        else:
            solder_mask = image > 100

        # Find connected regions
        labeled_array = self._label_connected_components(solder_mask)

        for region_id in np.unique(labeled_array):
            if region_id == 0:
                continue

            region = (labeled_array == region_id)
            region_size = np.sum(region)

            # Bridges are typically large connected regions
            if region_size > 500:  # Pixels
                points = np.where(region)
                center_y, center_x = np.mean(points[0]), np.mean(points[1])

                detections.append(DetectionResult(
                    defect_type=DefectType.SOLDER_BRIDGE,
                    confidence=0.92,  # High confidence for obvious bridges
                    location=(int(center_x), int(center_y)),
                    severity=8  # High severity
                ))

        return detections

    def detect_missing_component(self, image: np.ndarray, template: Optional[np.ndarray] = None
                                 ) -> List[DetectionResult]:
        """
        Detect missing component

        Args:
            image: Image array
            template: Template image of expected component (optional)

        Returns:
            List of DetectionResult objects
        """
        detections = []

        # Check if expected region is empty
        if len(image.shape) == 3:
            grayscale = np.dot(image[..., :3], [0.299, 0.587, 0.114])
        else:
            grayscale = image

        # Simple check: if region is uniform background
        if np.std(grayscale) < 10:  # Very low variation = empty
            detections.append(DetectionResult(
                defect_type=DefectType.MISSING_COMPONENT,
                confidence=0.95,
                location=(image.shape[1] // 2, image.shape[0] // 2),
                severity=9  # Critical
            ))

        return detections

    def detect_color_mismatch(self, image: np.ndarray, reference_color: Tuple[int, int, int]
                              ) -> List[DetectionResult]:
        """
        Detect color mismatch defects

        Args:
            image: Image array (RGB)
            reference_color: Expected RGB color

        Returns:
            List of DetectionResult objects
        """
        detections = []

        if len(image.shape) != 3 or image.shape[2] < 3:
            return detections

        # Calculate color distance
        color_diff = np.sqrt(np.sum((image[:, :, :3] - reference_color) ** 2, axis=2))

        # Flag regions with significant color mismatch
        threshold = 50
        mismatch_regions = np.where(color_diff > threshold)

        if len(mismatch_regions[0]) > 100:  # Significant area
            center_y = int(np.mean(mismatch_regions[0]))
            center_x = int(np.mean(mismatch_regions[1]))

            detections.append(DetectionResult(
                defect_type=DefectType.COLOR_MISMATCH,
                confidence=0.78,
                location=(center_x, center_y),
                severity=2  # Low severity (cosmetic)
            ))

        return detections

    def detect_dimensional_defect(self, measurement: float, spec_lower: float,
                                  spec_upper: float) -> Optional[DetectionResult]:
        """
        Detect dimensional out-of-spec

        Args:
            measurement: Measured dimension
            spec_lower: Lower specification limit
            spec_upper: Upper specification limit

        Returns:
            DetectionResult or None
        """
        if measurement < spec_lower or measurement > spec_upper:
            severity = 5
            if abs(measurement - spec_lower) < 0.05 or abs(measurement - spec_upper) < 0.05:
                severity = 3  # Near limit
            else:
                severity = 7  # Way out

            return DetectionResult(
                defect_type=DefectType.DIMENSIONAL_OUT_OF_SPEC,
                confidence=0.99,
                location=(0, 0),  # Whole part
                severity=severity
            )

        return None

    @staticmethod
    def _label_connected_components(binary_array: np.ndarray) -> np.ndarray:
        """
        Simple connected component labeling

        Args:
            binary_array: Binary array (0 and 1)

        Returns:
            Labeled array
        """
        labeled = np.zeros_like(binary_array)
        label = 0

        for i in range(binary_array.shape[0]):
            for j in range(binary_array.shape[1]):
                if binary_array[i, j] > 0 and labeled[i, j] == 0:
                    label += 1
                    # Flood fill
                    stack = [(i, j)]
                    while stack:
                        y, x = stack.pop()
                        if y < 0 or y >= labeled.shape[0] or x < 0 or x >= labeled.shape[1]:
                            continue
                        if labeled[y, x] > 0 or binary_array[y, x] == 0:
                            continue

                        labeled[y, x] = label

                        for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                            stack.append((y + dy, x + dx))

        return labeled


class InspectionSystem:
    """Complete automated inspection system"""

    def __init__(self, calibration: CalibrationData, confidence_threshold: float = 0.85):
        """
        Initialize inspection system

        Args:
            calibration: CalibrationData object
            confidence_threshold: Minimum confidence threshold
        """
        self.calibration = calibration
        self.dimensional_inspector = DimensionalInspector(calibration)
        self.defect_detector = DefectDetector(confidence_threshold)
        self.confidence_threshold = confidence_threshold

        self.inspection_results = []

    def inspect_part(self, image: InspectionImage) -> InspectionResult:
        """
        Perform complete inspection of a part

        Args:
            image: InspectionImage object

        Returns:
            InspectionResult (PASS, FAIL_HIGH_CONFIDENCE, FAIL_LOW_CONFIDENCE, MANUAL_REVIEW)
        """
        defects = []

        # Detect defects
        defects.extend(self.defect_detector.detect_solder_bridge(image.image_array))
        defects.extend(self.defect_detector.detect_missing_component(image.image_array))

        # Categorize results
        high_confidence_defects = [d for d in defects if d.confidence >= self.confidence_threshold]
        low_confidence_defects = [d for d in defects if d.confidence < self.confidence_threshold]

        # Determine result
        if high_confidence_defects:
            result = InspectionResult.FAIL_HIGH_CONFIDENCE
        elif low_confidence_defects:
            result = InspectionResult.FAIL_LOW_CONFIDENCE
        else:
            result = InspectionResult.PASS

        # Log results
        log_entry = {
            "image_id": image.image_id,
            "result": result,
            "defects": defects,
            "high_confidence": high_confidence_defects,
            "low_confidence": low_confidence_defects
        }
        self.inspection_results.append(log_entry)

        return result

    def get_statistics(self) -> Dict:
        """Get inspection statistics"""
        if not self.inspection_results:
            return {}

        pass_count = sum(1 for r in self.inspection_results if r['result'] == InspectionResult.PASS)
        fail_high = sum(1 for r in self.inspection_results
                       if r['result'] == InspectionResult.FAIL_HIGH_CONFIDENCE)
        fail_low = sum(1 for r in self.inspection_results
                      if r['result'] == InspectionResult.FAIL_LOW_CONFIDENCE)
        manual = sum(1 for r in self.inspection_results if r['result'] == InspectionResult.MANUAL_REVIEW)

        total = len(self.inspection_results)

        return {
            "total_parts_inspected": total,
            "pass_count": pass_count,
            "fail_high_confidence": fail_high,
            "fail_low_confidence": fail_low,
            "manual_review": manual,
            "pass_rate": pass_count / total * 100 if total > 0 else 0,
            "defect_rate": (fail_high + fail_low) / total * 100 if total > 0 else 0
        }


# Example usage
if __name__ == "__main__":
    print("Automated Inspection System - Example Usage")
    print("=" * 60)

    # Create calibration
    calibration = CalibrationData(pixels_per_mm=40)  # 40 pixels = 1 mm

    # Create inspection system
    inspection_system = InspectionSystem(calibration, confidence_threshold=0.85)

    # Simulate inspection of 100 parts
    np.random.seed(42)
    for i in range(100):
        # Simulate image
        image_array = np.random.randint(0, 256, (480, 640, 3), dtype=np.uint8)

        # 95% good parts, 5% defective
        if np.random.random() < 0.05:
            # Add simulated defect
            image_array[100:150, 100:150] = [50, 50, 50]  # Dark region = defect

        image = InspectionImage(
            image_id=f"IMG_001_{i:03d}",
            image_array=image_array,
            timestamp=f"2024-01-01T{i:02d}:00:00",
            location="Station_1",
            production_line="Line_1",
            part_id=f"PART_{i:04d}"
        )

        result = inspection_system.inspect_part(image)

    # Get statistics
    stats = inspection_system.get_statistics()
    print(f"Parts Inspected: {stats['total_parts_inspected']}")
    print(f"Pass Rate: {stats['pass_rate']:.1f}%")
    print(f"Defect Rate: {stats['defect_rate']:.1f}%")
    print(f"  - High Confidence Failures: {stats['fail_high_confidence']}")
    print(f"  - Low Confidence Failures: {stats['fail_low_confidence']}")
    print(f"  - Manual Review Required: {stats['manual_review']}")
