#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Industrial Robot Vision System Integration
Real-time image processing and robot guidance

Compatible with:
- Universal Robots collaborative robots
- ABB, KUKA, FANUC industrial robots
- Standard USB cameras, Basler, IDS, Cognex systems

Date: 2025
"""

import cv2
import numpy as np
import time
from dataclasses import dataclass
from typing import Tuple, List, Optional
import threading
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ======================================================================
# DATA STRUCTURES
# ======================================================================

@dataclass
class CalibrationMatrix:
    """Stores camera-to-robot coordinate transformation"""
    matrix: np.ndarray  # 4x4 homogeneous transformation matrix
    camera_matrix: np.ndarray  # Camera intrinsics
    distortion_coeffs: np.ndarray  # Lens distortion coefficients

    def transform_point(self, image_point: Tuple[int, int]) -> Tuple[float, float]:
        """Transform image coordinates to robot coordinates"""
        # Convert to homogeneous coordinates
        point_homogeneous = np.array([[image_point[0]],
                                      [image_point[1]],
                                      [1.0]])

        # Apply transformation
        robot_point = self.matrix @ point_homogeneous

        return float(robot_point[0, 0]), float(robot_point[1, 0])


@dataclass
class DetectedPart:
    """Represents a detected part in image"""
    centroid_x: float
    centroid_y: float
    width: float
    height: float
    angle: float  # Rotation in degrees
    area: float
    confidence: float  # 0-1 confidence score
    contour: np.ndarray  # Contour points


@dataclass
class RobotPose:
    """Robot tool pose (position + orientation)"""
    x: float  # mm
    y: float  # mm
    z: float  # mm
    rx: float  # radians (roll)
    ry: float  # radians (pitch)
    rz: float  # radians (yaw)

    def to_list(self) -> List[float]:
        """Convert to list format for robot"""
        return [self.x/1000.0, self.y/1000.0, self.z/1000.0,  # Convert mm to m
                self.rx, self.ry, self.rz]


# ======================================================================
# SECTION 1: CAMERA INTERFACE
# ======================================================================

class CameraInterface:
    """Handles camera acquisition and preprocessing"""

    def __init__(self, camera_id: int = 0, width: int = 640, height: int = 480):
        """
        Initialize camera interface

        Args:
            camera_id: Camera device ID (0 for default camera)
            width: Frame width in pixels
            height: Frame height in pixels
        """
        self.camera_id = camera_id
        self.width = width
        self.height = height
        self.cap = None
        self.frame = None
        self.is_running = False
        self.frame_lock = threading.Lock()

    def open(self) -> bool:
        """Open camera device"""
        try:
            self.cap = cv2.VideoCapture(self.camera_id)

            # Set camera properties
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            self.cap.set(cv2.CAP_PROP_FPS, 30)

            # Verify camera opened
            if not self.cap.isOpened():
                logger.error(f"Failed to open camera {self.camera_id}")
                return False

            logger.info(f"Camera {self.camera_id} opened successfully")
            return True

        except Exception as e:
            logger.error(f"Camera initialization error: {e}")
            return False

    def start_continuous_capture(self):
        """Start continuous frame capture in background thread"""
        if not self.cap or not self.cap.isOpened():
            logger.error("Camera not opened")
            return

        self.is_running = True
        capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        capture_thread.start()

    def _capture_loop(self):
        """Background thread for continuous capture"""
        while self.is_running:
            ret, frame = self.cap.read()

            if ret:
                with self.frame_lock:
                    self.frame = frame
            else:
                logger.warning("Failed to capture frame")

            time.sleep(0.01)  # Limit to ~100 FPS

    def get_frame(self) -> Optional[np.ndarray]:
        """Get latest captured frame"""
        with self.frame_lock:
            return self.frame.copy() if self.frame is not None else None

    def capture_single_frame(self) -> Optional[np.ndarray]:
        """Capture single frame"""
        if not self.cap or not self.cap.isOpened():
            return None

        ret, frame = self.cap.read()
        return frame if ret else None

    def close(self):
        """Close camera"""
        self.is_running = False
        if self.cap:
            self.cap.release()
        logger.info("Camera closed")


# ======================================================================
# SECTION 2: IMAGE PROCESSING AND PART DETECTION
# ======================================================================

class PartDetector:
    """Detects parts in images using computer vision"""

    def __init__(self, min_area: int = 100, max_area: int = 50000):
        """
        Initialize part detector

        Args:
            min_area: Minimum contour area (pixels²)
            max_area: Maximum contour area (pixels²)
        """
        self.min_area = min_area
        self.max_area = max_area
        self.debug_mode = False

    def detect_parts(self, image: np.ndarray, threshold_value: int = 127) -> List[DetectedPart]:
        """
        Detect parts in image using contour analysis

        Args:
            image: Input image (BGR or grayscale)
            threshold_value: Binary threshold (0-255)

        Returns:
            List of detected parts
        """
        if image is None:
            logger.error("Input image is None")
            return []

        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        # Apply threshold to create binary image
        _, binary = cv2.threshold(gray, threshold_value, 255, cv2.THRESH_BINARY)

        # Morphological operations to clean up image
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)

        # Find contours
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        detected_parts = []

        for contour in contours:
            area = cv2.contourArea(contour)

            # Filter by area
            if area < self.min_area or area > self.max_area:
                continue

            # Calculate properties
            M = cv2.moments(contour)
            if M["m00"] == 0:
                continue

            # Centroid
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])

            # Fit ellipse to get orientation
            if len(contour) >= 5:
                ellipse = cv2.fitEllipse(contour)
                (ex, ey), (ewidth, eheight), angle = ellipse
            else:
                angle = 0.0
                ewidth = eheight = 0

            # Bounding rectangle
            x, y, w, h = cv2.boundingRect(contour)

            # Create detected part
            part = DetectedPart(
                centroid_x=float(cx),
                centroid_y=float(cy),
                width=float(w),
                height=float(h),
                angle=angle,
                area=float(area),
                confidence=min(1.0, area / 10000.0),  # Simple confidence metric
                contour=contour
            )

            detected_parts.append(part)

        logger.info(f"Detected {len(detected_parts)} parts")
        return detected_parts

    def detect_color_parts(self, image: np.ndarray,
                          lower_color: Tuple[int, int, int],
                          upper_color: Tuple[int, int, int]) -> List[DetectedPart]:
        """
        Detect parts by color range

        Args:
            image: Input BGR image
            lower_color: Lower HSV threshold (H, S, V)
            upper_color: Upper HSV threshold (H, S, V)

        Returns:
            List of detected parts matching color range
        """
        # Convert BGR to HSV
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # Create mask for color range
        lower = np.array(lower_color)
        upper = np.array(upper_color)
        mask = cv2.inRange(hsv, lower, upper)

        # Find contours in mask
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        detected_parts = []

        for contour in contours:
            area = cv2.contourArea(contour)

            if area < self.min_area or area > self.max_area:
                continue

            M = cv2.moments(contour)
            if M["m00"] == 0:
                continue

            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])

            if len(contour) >= 5:
                ellipse = cv2.fitEllipse(contour)
                (_, _), (_, _), angle = ellipse
            else:
                angle = 0.0

            x, y, w, h = cv2.boundingRect(contour)

            part = DetectedPart(
                centroid_x=float(cx),
                centroid_y=float(cy),
                width=float(w),
                height=float(h),
                angle=angle,
                area=float(area),
                confidence=min(1.0, area / 10000.0),
                contour=contour
            )

            detected_parts.append(part)

        return detected_parts


# ======================================================================
# SECTION 3: CALIBRATION AND COORDINATE TRANSFORMATION
# ======================================================================

class CameraCalibration:
    """Handles camera calibration and coordinate transformations"""

    def __init__(self):
        """Initialize calibration"""
        self.calibration_matrix = None
        self.camera_matrix = None
        self.distortion_coeffs = None

    def calibrate_hand_eye_single_point(self,
                                       image_point: Tuple[int, int],
                                       robot_position: RobotPose) -> np.ndarray:
        """
        Simple single-point hand-eye calibration

        Requires: Known robot position with camera on wrist

        Args:
            image_point: Point in image (x, y)
            robot_position: Corresponding robot TCP pose

        Returns:
            Calibration transformation matrix (4x4)
        """
        # This is a simplified single-point calibration
        # Real implementation would use multiple points and least-squares fitting

        # Create transformation matrix
        # Image pixel to robot millimeters scaling
        # This example assumes: 1 pixel = 0.5 mm at working distance

        pixels_to_mm = 0.5

        # Center point (typically image center)
        image_center_x = 320
        image_center_y = 240

        # Offset from image center
        offset_x = (image_point[0] - image_center_x) * pixels_to_mm
        offset_y = (image_point[1] - image_center_y) * pixels_to_mm

        # Create 4x4 transformation matrix
        T = np.eye(4)
        T[0, 3] = robot_position.x + offset_x  # X position
        T[1, 3] = robot_position.y + offset_y  # Y position
        T[2, 3] = robot_position.z             # Z position

        logger.info(f"Calibrated with single point: {image_point}")

        return T

    def calibrate_hand_eye_multi_point(self,
                                       image_points: List[Tuple[int, int]],
                                       robot_positions: List[RobotPose]) -> np.ndarray:
        """
        Multi-point hand-eye calibration using least squares

        Args:
            image_points: List of image points
            robot_positions: Corresponding robot positions

        Returns:
            Optimal calibration transformation matrix
        """
        if len(image_points) != len(robot_positions):
            raise ValueError("Image points and robot positions must have same length")

        if len(image_points) < 4:
            raise ValueError("Need at least 4 calibration points")

        # Collect source and destination points
        src_points = np.array(image_points, dtype=np.float32)
        dst_points = np.array([[p.x, p.y] for p in robot_positions], dtype=np.float32)

        # Find affine transformation (or homography for 2D to 2D)
        # Using perspective transform for better accuracy
        if len(src_points) >= 4:
            # Use first 4 points for homography
            H = cv2.getPerspectiveTransform(
                src_points[:4].reshape(4, 1, 2),
                dst_points[:4].reshape(4, 1, 2)
            )

            # Create 4x4 matrix from 3x3 homography
            T = np.eye(4)
            T[:3, :3] = H

        else:
            # Fall back to affine
            M = cv2.getAffineTransform(
                src_points[:3].reshape(3, 1, 2),
                dst_points[:3].reshape(3, 1, 2)
            )

            T = np.eye(4)
            T[:2, :] = M

        # Calculate reprojection error
        error = self._calculate_reprojection_error(src_points, dst_points, T)
        logger.info(f"Calibration reprojection error: {error:.3f} pixels")

        return T

    @staticmethod
    def _calculate_reprojection_error(src: np.ndarray, dst: np.ndarray,
                                      T: np.ndarray) -> float:
        """Calculate calibration error"""
        errors = []
        for i in range(len(src)):
            src_h = np.array([src[i][0], src[i][1], 1.0])
            dst_h = np.array([dst[i][0], dst[i][1], 1.0])

            projected = T @ src_h
            projected = projected[:2] / projected[2] if projected[2] != 0 else projected[:2]

            error = np.linalg.norm(projected - dst[i])
            errors.append(error)

        return np.mean(errors)


# ======================================================================
# SECTION 4: 3D VISION AND POINT CLOUD PROCESSING
# ======================================================================

class PointCloudProcessor:
    """Process 3D point clouds from depth cameras"""

    def __init__(self):
        """Initialize processor"""
        self.points = None
        self.colors = None

    def load_point_cloud_from_depth(self, depth_image: np.ndarray,
                                   camera_matrix: np.ndarray,
                                   depth_scale: float = 1.0) -> np.ndarray:
        """
        Convert depth image to 3D point cloud

        Args:
            depth_image: Depth image (dtype: uint16, millimeters)
            camera_matrix: Camera intrinsic matrix (3x3)
            depth_scale: Scaling factor from pixel value to meters

        Returns:
            Point cloud (Nx3)
        """
        h, w = depth_image.shape

        # Create mesh grid
        x, y = np.meshgrid(np.arange(w), np.arange(h))

        # Get focal length and principal point from camera matrix
        fx = camera_matrix[0, 0]
        fy = camera_matrix[1, 1]
        cx = camera_matrix[0, 2]
        cy = camera_matrix[1, 2]

        # Convert to 3D
        z = depth_image * depth_scale
        x = (x - cx) * z / fx
        y = (y - cy) * z / fy

        # Flatten and stack
        points = np.stack([x.flatten(), y.flatten(), z.flatten()], axis=1)

        # Remove invalid points (zero depth)
        valid = points[:, 2] > 0
        points = points[valid]

        self.points = points
        logger.info(f"Loaded point cloud with {len(points)} points")

        return points

    def filter_outliers(self, points: np.ndarray,
                       radius: float = 0.01,
                       min_neighbors: int = 10) -> np.ndarray:
        """
        Remove outliers using statistical filtering

        Args:
            points: Point cloud (Nx3)
            radius: Neighborhood radius (meters)
            min_neighbors: Minimum neighbors to keep point

        Returns:
            Filtered point cloud
        """
        from scipy.spatial import KDTree

        tree = KDTree(points)

        # Find neighbors for each point
        valid_indices = []
        for i, point in enumerate(points):
            neighbors = tree.query_ball_point(point, radius)
            if len(neighbors) >= min_neighbors:
                valid_indices.append(i)

        filtered = points[valid_indices]
        logger.info(f"Filtered cloud: {len(points)} → {len(filtered)} points")

        return filtered

    def detect_plane_ransac(self, points: np.ndarray,
                           threshold: float = 0.01,
                           iterations: int = 1000) -> Tuple[np.ndarray, np.ndarray]:
        """
        Detect planar surface using RANSAC

        Args:
            points: Point cloud (Nx3)
            threshold: Distance threshold for inliers (meters)
            iterations: RANSAC iterations

        Returns:
            Plane normal vector (3,) and inlier points
        """
        best_normal = None
        best_inliers = None
        max_inliers = 0

        for _ in range(iterations):
            # Sample 3 random points
            sample_indices = np.random.choice(len(points), 3, replace=False)
            p1, p2, p3 = points[sample_indices]

            # Compute plane normal
            v1 = p2 - p1
            v2 = p3 - p1
            normal = np.cross(v1, v2)

            if np.linalg.norm(normal) < 1e-6:
                continue

            normal = normal / np.linalg.norm(normal)

            # Count inliers
            distances = np.abs(np.dot(points - p1, normal))
            inliers = distances < threshold
            num_inliers = np.sum(inliers)

            if num_inliers > max_inliers:
                max_inliers = num_inliers
                best_normal = normal
                best_inliers = inliers

        inlier_points = points[best_inliers]
        logger.info(f"Found plane with {max_inliers} inliers")

        return best_normal, inlier_points


# ======================================================================
# SECTION 5: VISION-GUIDED ROBOT OPERATION
# ======================================================================

class VisionGuidedRobot:
    """Main class for vision-guided robot operations"""

    def __init__(self, camera_device: int = 0, calibration_file: Optional[str] = None):
        """
        Initialize vision-guided robot system

        Args:
            camera_device: Camera device ID
            calibration_file: Path to saved calibration (if available)
        """
        self.camera = CameraInterface(camera_device)
        self.detector = PartDetector()
        self.calibration = CameraCalibration()
        self.calibration_matrix = None

        if calibration_file and self._load_calibration(calibration_file):
            logger.info(f"Loaded calibration from {calibration_file}")

    def initialize(self) -> bool:
        """Initialize all systems"""
        if not self.camera.open():
            return False

        self.camera.start_continuous_capture()
        logger.info("Vision system initialized")
        return True

    def capture_and_detect(self) -> List[DetectedPart]:
        """Capture image and detect parts"""
        frame = self.camera.get_frame()

        if frame is None:
            logger.warning("Failed to get frame")
            return []

        parts = self.detector.detect_parts(frame)
        return parts

    def detect_best_part(self) -> Optional[DetectedPart]:
        """Detect and return highest confidence part"""
        parts = self.capture_and_detect()

        if not parts:
            return None

        # Sort by confidence
        best_part = max(parts, key=lambda p: p.confidence)

        logger.info(f"Best part: confidence={best_part.confidence:.2f}, "
                   f"position=({best_part.centroid_x:.0f}, {best_part.centroid_y:.0f})")

        return best_part

    def part_to_robot_pose(self, part: DetectedPart,
                          grasp_height: float = 50.0) -> RobotPose:
        """
        Convert detected part to robot grasp pose

        Args:
            part: Detected part from vision
            grasp_height: Height above part (mm)

        Returns:
            Robot pose for grasping
        """
        if self.calibration_matrix is None:
            logger.error("Calibration not loaded")
            return None

        # Transform image coordinates to robot coordinates
        x, y = self.calibration.calibrate_hand_eye_single_point(
            (int(part.centroid_x), int(part.centroid_y)),
            RobotPose(x=0, y=0, z=0, rx=0, ry=0, rz=0)
        )

        # Create grasp pose
        grasp_angle = np.deg2rad(part.angle)

        pose = RobotPose(
            x=x,
            y=y,
            z=grasp_height,
            rx=0.0,
            ry=np.pi,  # 180 degree pitch (vertical approach)
            rz=grasp_angle
        )

        logger.info(f"Grasp pose: x={pose.x:.1f}, y={pose.y:.1f}, "
                   f"z={pose.z:.1f}, angle={np.rad2deg(grasp_angle):.1f}°")

        return pose

    def _load_calibration(self, filename: str) -> bool:
        """Load calibration from file"""
        try:
            import pickle
            with open(filename, 'rb') as f:
                self.calibration_matrix = pickle.load(f)
            return True
        except Exception as e:
            logger.error(f"Failed to load calibration: {e}")
            return False

    def save_calibration(self, filename: str):
        """Save calibration to file"""
        try:
            import pickle
            with open(filename, 'wb') as f:
                pickle.dump(self.calibration_matrix, f)
            logger.info(f"Calibration saved to {filename}")
        except Exception as e:
            logger.error(f"Failed to save calibration: {e}")

    def shutdown(self):
        """Shutdown vision system"""
        self.camera.close()
        logger.info("Vision system shutdown")


# ======================================================================
# SECTION 6: EXAMPLE USAGE
# ======================================================================

def example_pick_and_place():
    """
    Example: Vision-guided pick and place
    Detects parts and generates robot grasp commands
    """

    # Initialize vision system
    vision = VisionGuidedRobot(camera_device=0)

    if not vision.initialize():
        logger.error("Failed to initialize vision system")
        return

    logger.info("Vision system ready - starting pick and place cycle")

    try:
        # Main loop
        for cycle in range(10):  # 10 cycles
            logger.info(f"=== Cycle {cycle + 1} ===")

            # Capture and detect
            time.sleep(0.5)  # Wait for image stabilization

            part = vision.detect_best_part()

            if part is None:
                logger.warning("No parts detected")
                continue

            # Generate grasp pose
            grasp_pose = vision.part_to_robot_pose(part, grasp_height=50)

            logger.info(f"Robot should move to: {grasp_pose.to_list()}")

            # In real application, would send command to robot:
            # robot.movej(grasp_pose.to_list(), a=0.5, v=0.5)
            # robot.set_digital_out(1, True)  # Close gripper
            # etc...

            time.sleep(2.0)  # Simulate cycle time

    finally:
        vision.shutdown()


def example_calibration():
    """
    Example: Perform hand-eye calibration
    """

    logger.info("Starting calibration procedure...")

    # Create calibration system
    calibration = CameraCalibration()

    # Simulate calibration points
    # In real use: would move robot to known positions and record image coordinates
    image_points = [
        (100, 100),
        (200, 100),
        (100, 200),
        (200, 200),
        (300, 150)
    ]

    robot_positions = [
        RobotPose(x=0, y=0, z=100, rx=0, ry=np.pi, rz=0),
        RobotPose(x=100, y=0, z=100, rx=0, ry=np.pi, rz=0),
        RobotPose(x=0, y=100, z=100, rx=0, ry=np.pi, rz=0),
        RobotPose(x=100, y=100, z=100, rx=0, ry=np.pi, rz=0),
        RobotPose(x=150, y=50, z=100, rx=0, ry=np.pi, rz=0),
    ]

    # Perform calibration
    calibration_matrix = calibration.calibrate_hand_eye_multi_point(
        image_points, robot_positions
    )

    logger.info(f"Calibration matrix:\n{calibration_matrix}")


if __name__ == "__main__":
    # Run example
    example_pick_and_place()
    # example_calibration()
