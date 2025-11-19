# Vision Systems Reference Guide

## Machine Vision and 3D Guidance for Industrial Robots

---

## 1. Machine Vision Fundamentals

### System Architecture

```
Light Source → Optics → Image Sensor → Processing Unit → Decision/Output
     ↓                                          ↓
  Lighting               Image Capture      Algorithm      Robot Control
```

### Image Sensor Types

#### Area Scan Cameras

**Characteristics:**
- Standard 2D imaging
- CCD or CMOS sensors
- Resolution: 640x480 to 40+ megapixels
- Frame rates: 30-500+ fps depending on resolution
- Cost: $500-5000 per camera

**Color vs Monochrome:**

| Monochrome | Color |
|-----------|-------|
| Higher sensitivity | Better color differentiation |
| Better for detail | Larger file sizes |
| Lower cost | More processing |
| B&W contrast | RGB or Bayer pattern |

**Popular Manufacturers:**
- Basler (ace2, dart, purest)
- IDS Imaging (uEye, ensenso)
- Cognex (In-Sight)
- SICK (ranger3)
- Keyence (XG series)

#### Line Scan Cameras

**Use Cases:**
- Continuous material inspection (conveyor-based)
- Detecting defects during motion
- High-speed inspection (3000+ feet/minute)
- Web inspection (paper, film, fabric)

**Characteristics:**
- Single line of pixels (typically 2048-8192)
- Requires motion perpendicular to scan line
- Excellent for continuous processes
- High throughput

#### 3D/Depth Cameras

**Two Categories:**

1. **Passive Systems:**
   - Structured Light (stereo)
   - Time-of-Flight
   - Monocular depth estimation (AI-based)

2. **Active Systems:**
   - Structured Light projection
   - Laser triangulation
   - Pulsed Time-of-Flight
   - Phase-shift ToF

### Optical Components

#### Lens Selection

**Focal Length:**
- Shorter focal length (4mm): Wide field of view, less magnification
- Longer focal length (50mm): Narrow FOV, higher magnification
- Standard (16mm): Balanced field and detail

**Working Distance Calculation:**
```
Working Distance = (FOV_Width / Image_Width) × Focal_Length
```

**F-Number (Aperture):**
- F/2.8: Large aperture, more light, shallow depth of field
- F/5.6: Balanced
- F/16: Small aperture, small depth of field, less light

**Depth of Field:**
```
DOF = 2 × (N × Δx × (f + d)) / f²

Where:
N = F-number
Δx = Minimum resolvable spot size
f = Focal length
d = Working distance
```

#### Lighting Strategies

**Backlighting:**
- Light source behind object
- Creates silhouette
- Best for: Shape detection, edge detection
- Advantage: High contrast
- Disadvantage: No surface detail

**Coaxial Lighting:**
- Light along same axis as camera
- Illuminates object surface
- Best for: Surface defects, text reading
- Advantage: Direct illumination
- Disadvantage: Specular reflections

**Ring Lighting:**
- Uniform illumination around lens
- Best for: General-purpose imaging
- Advantage: Even lighting, no shadows
- Disadvantage: Can create reflections on shiny surfaces

**Directional Lighting:**
- Side lighting at angle
- Best for: Texture, depth perception
- Advantage: 3D perception
- Disadvantage: Shadows and contrast depend on angle

**Strobe Lighting:**
- High-intensity brief pulse
- Best for: Fast-moving objects
- Advantage: Freezes motion, high intensity
- Disadvantage: Special synchronization required

**Wavelength Selection:**

| Wavelength | Color | Use Case |
|-----------|-------|----------|
| 380-450 nm | Violet/Blue | Fluorescent materials |
| 450-495 nm | Blue | Low-contrast surfaces |
| 495-570 nm | Green | Standard, eye-safe |
| 570-590 nm | Yellow | Good for most materials |
| 590-620 nm | Red | Heat-resistant, low interference |
| 620+ nm | Infrared | Thermal imaging |

---

## 2. 3D Vision Technologies

### Structured Light Systems

#### Principle of Operation

```
Projector sends known pattern (stripes, checkerboard)
  ↓
Pattern distorts on object surface
  ↓
Camera captures distorted pattern
  ↓
Pattern analysis reveals object geometry
  ↓
3D point cloud generated
```

#### How It Works

**Stripe Pattern Method:**
1. Project horizontal/vertical stripes
2. Analyze phase shift of stripes
3. Calculate depth from phase shift
4. Generate XYZ coordinates

**Checkerboard Method:**
1. Project checkerboard pattern
2. Identify pattern distortion
3. Calculate surface orientation
4. Create 3D surface mesh

#### Specifications

**Typical Performance:**
- Accuracy: ±0.1-0.5mm
- Resolution: 640×480 to 2048×1536 pixels
- Working distance: 100mm-2000mm
- Field of view: 30°-90° typical
- Frame rate: 5-30 fps (full resolution)

**Surface Requirements:**
- Works best on diffuse (matte) surfaces
- Glossy/reflective surfaces problematic
- Texture required for accuracy
- Not suitable for mirrors or transparent objects

**Popular Systems:**
- Photoneo PhoXi 3D Scanner
- Cognex In-Sight 3D
- Basler blaze
- ISRA Vision (formerly Isra)
- Ensenso 3D cameras

#### Advantages
- High accuracy and resolution
- Works in ambient light
- Good for complex geometries
- Established technology
- Many software integrations

#### Disadvantages
- Cannot work on highly reflective surfaces
- Slower frame rate than stereo
- Requires calibrated projector
- Higher cost

### Time-of-Flight (ToF) Cameras

#### Operating Principle

```
Emitter sends light pulse
  ↓
Light reflects from object
  ↓
Sensor measures return time
  ↓
Distance = (Time × Speed_of_Light) / 2
```

#### Specifications

**Performance:**
- Accuracy: ±5-50mm (distance dependent)
- Resolution: 160×120 to 512×512 pixels
- Working range: 0.3m-10m typical
- Frame rate: 30-100 fps
- Field of view: 45°-90°

**Distance Accuracy Formula:**
```
Error = ±(a × Distance² + b × Distance + c) mm

Typical:
Error = ±(0.1×Distance² + 1mm) for 0.5-5m range
```

**Sensor Types:**
- **Pulsed ToF:** Direct time measurement, good for outdoor
- **Continuous Wave:** Modulated light, sensitive to multipath
- **Indirect ToF:** Calculates phase delay

#### Popular Systems
- Microsoft Kinect v2 (discontined but supported)
- Pmdtech ifm O3D
- Basler dart BCON
- RealSense D400 series
- SICK TIM series

#### Advantages
- Fast frame rates
- Works on semi-transparent objects
- Less affected by surface finish
- Compact systems available
- Lower cost than structured light

#### Disadvantages
- Lower resolution than structured light
- Affected by ambient light
- Multipath interference in reflective environments
- Less accurate than structured light

### Stereo Vision

#### Stereo Vision Principle

```
Left Camera ←  Baseline Distance  → Right Camera
    ↓                                    ↓
  Image 1                            Image 2
    ↓                                    ↓
      ← Correspondence Matching →
              (Find same point)
            ↓
      Disparity Calculation
            ↓
      Depth = (Baseline × Focal Length) / Disparity
```

#### Calibration Requirements

**Intrinsic Parameters (per camera):**
- Focal length (f)
- Principal point (cx, cy)
- Distortion coefficients (k1, k2, k3, p1, p2)

**Extrinsic Parameters (camera relationship):**
- Rotation matrix (R)
- Translation vector (T)
- Baseline distance

**Calibration Target:**
- Checkerboard pattern
- Multiple poses (10-20 minimum)
- Covers entire image area

#### Specifications

**Typical Performance:**
- Accuracy: 0.1-2% of working distance
- Baseline: 30-200mm typical
- Working range: 0.3m-10m depending on baseline
- Resolution: Pixel-level (2048×1536 max typical)
- Frame rate: 30-120 fps

**Disparity Range:**
```
Max_Range = (Baseline × Focal_Length) / Min_Disparity
Min_Range = (Baseline × Focal_Length) / Max_Disparity
```

#### Disparity Computation Methods

1. **Block Matching:**
   - Compares small blocks between images
   - Fast but less accurate
   - Typical block size: 5×5 to 31×31 pixels

2. **Semi-Global Matching (SGM):**
   - Computes costs globally
   - Better accuracy, more processing
   - Good balance of speed/accuracy

3. **Graph Cuts:**
   - Sophisticated optimization
   - Higher accuracy
   - Much slower

#### Advantages
- Passive (no light projection needed)
- High resolution possible
- Good accuracy with proper calibration
- Works outdoors
- Large baseline = greater accuracy

#### Disadvantages
- Requires feature-rich surfaces
- Fails on featureless surfaces
- Computationally intensive
- Requires excellent calibration
- Larger camera setup

#### Popular Systems
- Basler stereo cameras
- IDS Ensenso (passive)
- Photoneo devices
- Point Grey (FLIR) Bumblebee
- ZED cameras by Stereolabs

### Laser Triangulation

#### Operating Principle

```
Laser projects line/dot on object
        ↓
Camera observes dot position
        ↓
Offset from zero position → Distance calculation
        ↓
XYZ coordinates generated
```

#### Geometric Calculation

```
Distance = Baseline × tan(θ_offset)

Where θ_offset = arctan(Pixel_Offset × tan(FOV/2) / (Image_Width/2))
```

#### Specifications

**Typical Performance:**
- Accuracy: ±0.05-0.5mm
- Working distance: 50mm-5000mm
- Stand-off distance: Typically 100-500mm
- Spot size: 0.5-10mm depending on configuration
- Frame rate: 100-1000 Hz possible

**Laser Classification:**
- Class 1: Safe for direct eye exposure
- Class 2/3A: Not safe for direct eye exposure
- Class 3B/4: Requires special handling

#### Scanning Patterns

**Line Laser:**
- Projects laser line onto object
- Camera sees full line
- Sweeping motion builds 3D profile
- Best for: Edges, discontinuities

**Point/Dot Laser:**
- Projects single point
- High-frequency sampling possible
- Requires scanning motion
- Best for: Precision measurements

#### Advantages
- Excellent accuracy (±0.05mm possible)
- Works on reflective surfaces
- Very fast acquisition
- Clear edge detection
- Minimal processing needed

#### Disadvantages
- Laser safety considerations
- Reflections on shiny surfaces problematic
- Requires controlled lighting
- Moving parts for full 3D (if using point laser)
- Higher cost for precision systems

#### Popular Systems
- Sick LMS/TIM2D laser scanners
- ISRA 3D cameras
- Cognex 3D vision
- Basler laser triangulation
- Keyence LJ series

---

## 3. Vision System Integration with Robots

### Hand-Eye Calibration

#### Camera-on-Wrist Configuration

```
Calibration Equation:
TCP_pose = Camera_pose × Object_T_Camera^(-1)

Or equivalently:
Object_pose = Camera_pose_in_world × Object_T_camera
```

#### Fixed Camera Configuration

```
Calibration Equation:
Object_pose_in_robot = Calibration_Matrix × Object_pose_in_image

Where Calibration_Matrix is 4×4 homogeneous transformation
```

#### Calibration Procedures

**Single-Point Calibration (Minimum):**
1. Manually position gripper at known world point
2. Capture image, identify object
3. Record gripper position and image coordinates
4. Calculate transformation matrix

**Multi-Point Calibration (Recommended):**
1. Position gripper at 5-10 known positions
2. Capture images at each location
3. Solve for best-fit transformation
4. Minimize error using least-squares optimization

#### Calibration Quality Metrics

```
Mean Absolute Error (MAE):
MAE = Σ|measured_position - predicted_position| / N

Reprojection Error:
Reprojection_Error = √(Σ(dx² + dy²)) / N
```

**Good Calibration:**
- Reprojection error < 1 pixel
- Measured position error < 1-2mm

### Vision-Guided Pick & Place Workflow

#### Complete Process Flow

```
1. Image Acquisition
   ↓
2. Preprocessing (ROI, contrast enhancement)
   ↓
3. Feature Detection (blob analysis, edges, contours)
   ↓
4. Part Localization (centroid, orientation)
   ↓
5. Pose Estimation (position + rotation)
   ↓
6. Coordinate Transformation
   (Image → Robot frame)
   ↓
7. Grasp Point Calculation
   (Account for gripper offset)
   ↓
8. Collision-Free Path Planning
   ↓
9. Motion Execution
   ↓
10. Grasp Verification (optional)
```

#### Code Example (Pseudocode)

```python
# Acquisition
image = capture_image(camera)

# Preprocessing
image_processed = enhance_contrast(image)
roi = crop_roi(image_processed)

# Detection
blobs = find_blobs(roi, min_area=100)

# Localization
for blob in blobs:
    centroid = blob.centroid()
    orientation = blob.orientation()

    # Transformation
    world_x, world_y = image_to_world(
        centroid.x, centroid.y,
        calibration_matrix
    )

    # Grasp point adjustment
    grasp_x = world_x + gripper_offset_x
    grasp_y = world_y + gripper_offset_y
    grasp_angle = orientation

    # Planning
    approach_pose = calculate_approach(grasp_x, grasp_y, grasp_angle)

    # Execution
    robot.move_to(approach_pose)
    robot.move_to(grasp_pose)
    robot.grasp()
    robot.move_to(delivery_pose)
    robot.release()
```

### 3D Vision-Guided Robot Motion

#### 3D Point Cloud Processing

**Typical Workflow:**
1. **Acquisition:** 3D camera captures point cloud
2. **Filtering:** Remove outliers and noise
3. **Segmentation:** Identify individual objects
4. **Feature Extraction:** Compute centroids and orientations
5. **Pose Estimation:** Calculate 6-DOF position and orientation
6. **Planning:** Generate collision-free path
7. **Execution:** Move robot to grasp point

#### Point Cloud Libraries

**Popular Frameworks:**
- **PCL (Point Cloud Library):** Open-source, C++, extensive algorithms
- **Open3D:** Python-based, user-friendly
- **ROS PointCloud2:** ROS integration, standardized format

**Key Algorithms:**
- RANSAC (plane detection)
- ICP (Iterative Closest Point)
- Voxel Grid Downsampling (noise reduction)
- Statistical Outlier Removal

#### 3D Object Pose Estimation

**Methods:**

1. **Centroid-Based:**
   - Calculate center of mass
   - Assumes symmetric objects
   - Fast but limited

2. **PCA (Principal Component Analysis):**
   - Find major axes
   - Works for elongated objects
   - Better orientation estimation

3. **Template Matching:**
   - Compare to known models
   - Works for specific object types
   - Computationally intensive

4. **ML-Based (Deep Learning):**
   - Train neural network on examples
   - Most robust for complex shapes
   - Requires training data

---

## 4. Advanced Vision Applications

### Defect Detection

**Surface Inspection Methods:**

1. **Edge Detection:**
   ```
   Edges indicate: Cracks, discontinuities, missing features
   ```

2. **Texture Analysis:**
   ```
   Statistical methods identify surface finish quality
   Algorithms: Gabor filters, LBP (Local Binary Patterns)
   ```

3. **Color Analysis:**
   ```
   Deviation from expected color = possible defects
   Methods: Color histogram matching, color threshold
   ```

### Bin Picking

**Typical Workflow:**

```
1. Capture 3D image of bin
2. Segment individual parts
3. Estimate part poses
4. Plan grasp point (handle-aware if possible)
5. Check for collisions with other parts
6. Plan approach/retreat paths
7. Execute pick
8. Verify successful grasp
9. Update bin contents for next pick
```

**Challenges:**
- Part occlusion (parts hiding each other)
- Deformable objects (cloth, foam)
- Reflective/transparent materials
- Dense random piling
- Texture similarity between parts

**Solutions:**
- Multi-view imaging
- Shake the bin to loosen parts
- Specialized gripper with force feedback
- Machine learning for complex cases

### Assembly Verification

**Quality Checks:**

1. **Presence Verification:**
   - Component count check
   - All required parts present

2. **Position Verification:**
   - Component within tolerance
   - Correct orientation
   - Proper gaps/spacing

3. **Dimensional Check:**
   - Size verification
   - Gap measurement
   - Alignment check

**Implementation:**
- Vision systems at key assembly points
- Pass/fail decision for reject line
- Statistical tracking for trending

---

## 5. Vision System Specification Checklist

### When Selecting a Vision System

**Application Requirements:**
- [ ] What is the target object size? (mm)
- [ ] What is the working distance? (mm)
- [ ] What resolution is required? (pixels)
- [ ] What is the cycle time requirement? (ms)
- [ ] What accuracy is needed? (±mm)
- [ ] What surface properties? (reflective, matte, transparent)
- [ ] What lighting conditions? (controlled, variable ambient)
- [ ] What environmental temperature range? (°C)

**Performance Specifications:**
- [ ] Frame rate requirement (fps)
- [ ] 2D or 3D imaging?
- [ ] Color or monochrome?
- [ ] Field of view (°)
- [ ] Depth of field (mm)
- [ ] Processing speed requirement (ms)

**Integration Specifications:**
- [ ] Robot brand compatibility
- [ ] Communication protocol (Ethernet, PROFIBUS, EtherCAT)
- [ ] Mounting location (on wrist, fixed)
- [ ] Cable routing and length
- [ ] Power requirements (24VDC typical)

**Environmental Considerations:**
- [ ] Ambient light level (lux)
- [ ] Temperature stability needed? (±°C)
- [ ] Dust/moisture protection (IP rating)
- [ ] Vibration isolation required?
- [ ] Cleanroom compatible?

---

## 6. Vision System Maintenance

**Recommended Schedule:**

**Weekly:**
- Clean camera lens with appropriate lens tissue
- Check for dust on lighting
- Verify calibration accuracy

**Monthly:**
- Full system calibration check
- Review image quality and contrast
- Check camera mounting security

**Quarterly:**
- Deep cleaning of all optics
- Software update check
- Performance trending analysis

**Annually:**
- Professional calibration verification
- Lighting intensity check
- Complete system overhaul if needed

