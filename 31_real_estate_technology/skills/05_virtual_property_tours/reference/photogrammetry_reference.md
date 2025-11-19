# Photogrammetry Reference

Comprehensive guide to photogrammetry for real estate virtual tours, 3D modeling, and digital twins.

## Introduction to Photogrammetry

**Photogrammetry** is the science of making measurements and creating 3D models from photographs. In real estate, it's used to create:
- Interactive 3D property models
- Accurate measurements and floor plans
- Virtual staging environments
- Digital twins for property management
- Marketing materials and flythrough videos

### Advantages Over Traditional Methods
- **Cost-effective**: Uses standard DSLR or smartphone cameras
- **Flexible**: Can capture any property size or complexity
- **Detailed**: Captures textures and fine details automatically
- **Scalable**: From single rooms to entire buildings
- **Versatile Output**: Multiple formats for various applications

## Capture Requirements

### Photo Overlap
- **Minimum Overlap**: 60% between consecutive photos
- **Recommended Overlap**: 70-80% for best results
- **Critical Overlap**: 85-90% for complex geometry (corners, edges, details)
- **Side Overlap**: 60-70% between rows in grid patterns

**Why Overlap Matters:**
- Ensures sufficient feature matching between images
- Creates redundancy for robust 3D reconstruction
- Enables accurate depth estimation
- Prevents gaps in final model

### Shooting Patterns

#### Room Interior Capture
- **Pattern**: Circular orbit around room center
- **Positions**: 20-40 positions in 2-3 concentric circles
- **Heights**: Low (3-4 ft), mid (5-6 ft), high (7-8 ft)
- **Photo Count**: 100-300 photos per room
- **Special Attention**: Corners, ceiling details, floor transitions

#### Exterior Building Capture
- **Pattern**: Grid or orbital pattern around building
- **Positions**: Every 5-10 feet depending on building size
- **Heights**: Ground level, elevated (ladder or drone if permitted)
- **Photo Count**: 300-800 photos for typical house
- **Coverage**: All facades, roof (drone), architectural details

#### Object Close-up Capture
- **Pattern**: Spherical orbit around object
- **Positions**: 15-30 degree increments
- **Distances**: Maintain consistent distance
- **Photo Count**: 40-100 photos per object
- **Focus**: Uniform lighting, avoid shadows

### Camera Settings

#### Recommended Equipment
- **Camera**:
  - Entry: Modern smartphone (iPhone 13+, Samsung S21+)
  - Mid: DSLR/Mirrorless (24MP+, Sony A7, Canon R6, Nikon Z)
  - Pro: Full-frame DSLR (45MP+, Sony A7R, Canon 5DS R)
- **Lens**:
  - Wide angle 16-35mm for interiors
  - Standard 35-50mm for exteriors
  - Avoid fisheye (excessive distortion)

#### Camera Settings
- **Mode**: Manual or Aperture Priority
- **Aperture**: f/8 to f/11 for maximum depth of field
- **ISO**: Lowest possible (100-400) to minimize noise
- **Shutter Speed**: 1/60s minimum (use tripod if slower)
- **Focus**: Manual focus on hyperfocal distance
- **White Balance**: Locked/consistent throughout shoot
- **RAW Format**: Preferred for post-processing flexibility

### Lighting Considerations

#### Natural Light
- **Best Time**: Overcast days (even, diffuse lighting)
- **Avoid**: Direct harsh sunlight (creates strong shadows)
- **Indoor**: Open curtains/blinds for consistent ambient light
- **Time of Day**: Mid-morning or mid-afternoon (avoid extreme angles)

#### Artificial Light
- **Interior**: Turn on all lights for consistent illumination
- **Flash**: Avoid on-camera flash (creates hotspots and shadows)
- **Supplemental**: Use softbox or bounce flash if needed
- **Consistency**: Same lighting for all photos in a set

#### Post-Processing for Lighting
- **Bracketing**: Not recommended (confuses feature matching)
- **HDR**: Process before photogrammetry if necessary
- **Exposure Correction**: Minor adjustments acceptable
- **Color Grading**: Avoid significant changes

## Processing Software

### RealityCapture
- **Developer**: Epic Games (Capturing Reality)
- **Pricing**: PPI (Pay-Per-Input) $10/month or subscription $3,750/year
- **Speed**: Fastest processing (GPU-accelerated)
- **Quality**: Excellent mesh quality
- **Max Photos**: Unlimited (tested with 100,000+ photos)
- **OS**: Windows only
- **Best For**: Professional workflows, large projects, time-sensitive deliverables

**Key Features:**
- GPU-accelerated processing (CUDA required)
- Automatic alignment and registration
- High-density mesh generation
- Texture baking and optimization
- Unlimited resolution output
- Command-line batch processing

**Typical Processing Times:**
- Small room (100 photos): 10-20 minutes
- House exterior (500 photos): 1-2 hours
- Large building (2000 photos): 4-8 hours
- (With RTX 3090 GPU, 64GB RAM)

### Agisoft Metashape (formerly PhotoScan)
- **Developer**: Agisoft LLC
- **Pricing**: Standard $179, Professional $3,499 (perpetual license)
- **Quality**: Industry standard, excellent accuracy
- **Accuracy**: Sub-centimeter with ground control points
- **Max Photos**: ~50,000 practical limit
- **OS**: Windows, macOS, Linux
- **Best For**: Surveying, mapping, cultural heritage, scientific applications

**Key Features:**
- Dense point cloud generation
- 4D time series processing
- Ground control point integration
- Orthomosaic and DEM generation
- Coordinate system support
- Accuracy assessment tools

**Typical Processing Times:**
- Room (200 photos): 30-45 minutes
- House (600 photos): 2-4 hours
- Site (3000 photos): 12-24 hours
- (With high-quality settings)

### Meshroom
- **Developer**: AliceVision (Open-Source)
- **Pricing**: Free
- **Quality**: Good, improving rapidly
- **Interface**: Node-based processing graph
- **OS**: Windows, Linux (macOS experimental)
- **Best For**: Learning, small projects, budget-conscious users

**Key Features:**
- Completely free and open-source
- Node-based workflow editor
- HDR texture generation
- Integration with Blender
- Active community development

**Limitations:**
- Slower than commercial options
- Requires CUDA-capable NVIDIA GPU
- Less automated than alternatives
- Smaller maximum project size

### Additional Tools
- **3DF Zephyr**: User-friendly, affordable alternative ($149-$3,200)
- **Pix4D**: Specialized for drone mapping ($350/month)
- **COLMAP**: Open-source, research-grade
- **Regard3D**: Free, simple interface
- **Autodesk ReCap Photo**: Cloud-based, subscription

## Detailed Workflow

### 1. Pre-Capture Planning
- Scout property and identify key areas
- Plan shooting positions and patterns
- Check lighting conditions and time of day
- Clear obstacles and stage property
- Charge batteries and clear memory cards

### 2. Photo Capture (2-4 hours for typical house)
- Set up camera with consistent settings
- Follow planned shooting pattern
- Maintain consistent overlap
- Verify photos as you shoot
- Capture additional detail shots
- Document with notes/sketches

### 3. Data Import and Organization
- Transfer photos to computer
- Organize by room/area
- Backup originals (critical!)
- Verify photo count and quality
- Remove blurry or problematic images

### 4. Photo Alignment (Structure from Motion)
- Import photos to software
- Detect and match features across images
- Estimate camera positions and orientations
- Generate sparse point cloud
- Review alignment quality
- **Time**: 10-30 minutes for 300 photos

### 5. Dense Point Cloud Generation
- Calculate depth maps for all images
- Merge depth maps into dense cloud
- Filter noise and outliers
- Set desired quality level (high/ultra)
- **Time**: 30-120 minutes
- **Output**: Point cloud with millions of points

### 6. Mesh Generation
- Convert point cloud to polygonal mesh
- Choose mesh resolution (faces/triangles)
- Apply smoothing and hole filling
- Optimize topology
- **Time**: 15-45 minutes
- **Output**: 3D mesh (typically 1-10 million triangles)

### 7. Texture Generation
- Unwrap mesh (create UV coordinates)
- Project photos onto mesh surface
- Blend textures from multiple photos
- Optimize texture resolution (2K, 4K, 8K)
- **Time**: 10-30 minutes
- **Output**: Textured 3D model

### 8. Model Optimization and Export
- Decimate mesh for web use (reduce polygons)
- Compress textures
- Export in target format
- Test in target application
- **Time**: 10-20 minutes

### Total Processing Time
- **Quick**: 1-2 hours (low settings, small room)
- **Standard**: 3-6 hours (medium settings, house)
- **High Quality**: 12-24 hours (high settings, large building)

## Output Formats and Uses

### OBJ (Wavefront Object)
- **Use**: Universal 3D interchange format
- **Support**: All 3D software
- **Contents**: Geometry (.obj) + Materials (.mtl) + Textures (.jpg/.png)
- **Best For**: Import to 3D modeling software, offline viewing
- **Limitations**: No animation, scene hierarchy, or advanced materials

### FBX (Filmbox)
- **Use**: Game engines, animation software
- **Support**: Unity, Unreal Engine, Blender, Maya, 3ds Max
- **Contents**: Geometry, materials, textures, animation data
- **Best For**: Interactive experiences, virtual staging, games
- **Features**: Supports bones, animation, cameras, lights

### glTF/GLB (GL Transmission Format)
- **Use**: Web 3D and AR applications
- **Support**: Three.js, Babylon.js, WebGL, AR platforms
- **GLB**: Binary single-file version
- **File Size**: Optimized for web delivery
- **Best For**: Website embedding, web AR, mobile AR
- **Modern Standard**: Industry standard for web 3D

### USD/USDZ (Universal Scene Description)
- **Use**: Apple ecosystem AR
- **Support**: iOS AR Quick Look, macOS
- **Best For**: iPhone/iPad AR experiences
- **Features**: Advanced materials, animation, physics
- **Platform**: Primary format for Apple AR

### PLY (Polygon File Format)
- **Use**: Point cloud and mesh storage
- **Support**: Research software, CloudCompare, MeshLab
- **Best For**: Point cloud analysis, scientific visualization
- **Features**: Stores vertex colors, normals, texture coordinates

### E57
- **Use**: Point cloud archival standard
- **Support**: Industry standard for laser scanning
- **Best For**: Long-term archival, surveying data exchange
- **Features**: Lossless compression, metadata

## Quality Optimization Tips

### Improving Reconstruction Quality
- Shoot more photos (better redundancy)
- Improve lighting consistency
- Use higher resolution camera
- Ensure sharp focus throughout
- Capture from more angles
- Add scale references or markers

### Reducing Processing Time
- Use GPU acceleration (critical)
- Reduce photo resolution (resize to 4000px max)
- Process in stages (room by room)
- Use medium quality settings
- Optimize alignment before dense cloud

### Achieving Web-Ready Models
- Target poly count: 50K-500K triangles
- Texture resolution: 2K-4K max
- Use texture atlasing
- Apply mesh decimation
- Compress textures (JPEG for web)
- Test on target devices

## Common Issues and Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| Holes in model | Insufficient coverage | Capture more photos of problem areas |
| Misalignment | Repetitive textures | Add unique markers or objects |
| Blurry textures | Out of focus photos | Use smaller aperture, check focus |
| Noisy point cloud | High ISO, poor lighting | Use better lighting, lower ISO |
| Slow processing | Insufficient GPU/RAM | Reduce photo count/resolution, upgrade hardware |
| Distorted geometry | Moving objects | Remove photos with people, vehicles |
| Color inconsistency | Auto white balance | Lock white balance during capture |

## Real Estate Applications

### Property Marketing
- Interactive 3D tours embedded on listing sites
- Social media 3D posts (Facebook 3D photos)
- Virtual open houses
- Flythrough videos for YouTube/Instagram

### Measurement and Documentation
- Accurate floor plans and elevations
- Volume calculations for renovations
- As-built documentation
- Insurance documentation

### Virtual Staging
- Import model to 3D software
- Add furniture and decor
- Render photorealistic images
- Show multiple design options

### Digital Twins
- Baseline property condition
- Track changes over time
- Facility management
- Renovation planning

## Cost Analysis

### Equipment Investment
- **Entry Level** ($500-1,500): Smartphone + basic software
- **Mid Range** ($2,500-5,000): DSLR camera + Metashape Standard
- **Professional** ($8,000-15,000): High-end camera + RealityCapture + processing workstation

### Per-Property Cost
- **Time**: 2-6 hours on-site, 3-8 hours processing
- **Labor**: $200-800 depending on property size
- **Software**: $10-50 per project (PPI model)
- **Total**: $300-1,200 per property

### Return on Investment
- Increased property engagement (+40-60%)
- Faster sales (average 31% faster)
- Higher selling prices (average 5-9% premium for premium listings)
- Reduced showing costs
- Competitive differentiation
