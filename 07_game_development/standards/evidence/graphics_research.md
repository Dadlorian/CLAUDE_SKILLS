# Graphics Research & Techniques

## Physically Based Rendering (PBR)

### Industry Standard: Disney/Unreal Model

**Key Papers**:
- "Physically Based Shading at Disney" - Burley, 2012 (SIGGRAPH)
- "Real Shading in Unreal Engine 4" - Karis, 2013 (SIGGRAPH)

**Properties**:
- Base Color (Albedo)
- Metallic
- Roughness
- Normal
- Ambient Occlusion

**BRDF**: Cook-Torrance microfacet model
- **D**: GGX/Trowbridge-Reitz (Normal Distribution)
- **F**: Schlick's Fresnel approximation
- **G**: Smith's shadowing-masking function

**Energy Conservation**: Ensures diffuse + specular ≤ 1

### Adoption
- Unity: Standard Shader (2014+)
- Unreal: Default material model (UE4+)
- Godot: PBR materials (3.0+)

## Real-Time Global Illumination

### Techniques

**1. Lightmap Baking**
- Offline pre-computation
- Fast runtime, no dynamic lighting
- **Tools**: Unity Lightmapper, Unreal Lightmass

**2. Light Probes**
- Spherical harmonics for indirect lighting
- Used by Unity, Unreal

**3. Voxel Cone Tracing** (SVOGI)
- Real-time GI approximation
- Used in: CryEngine, NVIDIA VXGI

**4. Screen-Space GI (SSGI)**
- Approximate GI from screen-space depth
- Fast but limited to visible surfaces

**5. Ray-Traced GI (RTGI)**
- Hardware ray tracing (RTX)
- Highest quality, expensive
- Used in: Unreal Engine 5 (Lumen with ray tracing)

**6. Lumen (UE5)**
- Software + hardware ray tracing
- Distance fields for geometry
- Screen traces for near surfaces
- Real-time, dynamic GI

**Research**:
- "Voxel Cone Tracing" - Crassin et al., 2011
- "Real-Time Global Illumination using Precomputed Light Field Probes" - McGuire et al., 2017

## Nanite (Unreal Engine 5)

**Concept**: Virtualized geometry

**Key Techniques**:
- **Cluster Rendering**: Meshes divided into clusters (~128 triangles)
- **LOD Streaming**: Automatic LOD selection
- **Software Rasterization**: GPU compute for visibility
- **Virtual Shadow Maps**: Efficient shadows for high-poly geometry

**Papers**:
- Epic Games: "A Deep Dive into Nanite Virtualized Geometry" (SIGGRAPH 2021)

**Performance**:
- Billions of triangles at 60fps
- No manual LOD creation needed
- Limitations: No skinned meshes, no WPO

## Temporal Anti-Aliasing (TAA)

**Concept**: Accumulate samples over multiple frames

**Benefits**:
- High quality at low cost
- Reduces temporal aliasing
- Works with deferred rendering

**Drawbacks**:
- Ghosting on fast motion
- Requires motion vectors

**Papers**:
- "Temporal Reprojection Anti-Aliasing in INSIDE" - Pedersen, 2016 (GDC)
- "High Quality Temporal Supersampling" - Karis, 2014

**Adoption**: Standard in AAA games (Unreal, Unity HDRP)

## Ray Tracing

### Real-Time Ray Tracing (RTX)

**Techniques**:
- **Ray-traced Reflections**: Accurate mirror reflections
- **Ray-traced Shadows**: Soft shadows, contact hardening
- **Ray-traced GI**: Path tracing for indirect light
- **Ray-traced AO**: Accurate ambient occlusion

**API Support**:
- DirectX Raytracing (DXR)
- Vulkan Ray Tracing
- OptiX (NVIDIA)

**Denoising**: Required for real-time
- Spatial filtering
- Temporal accumulation
- AI denoisers (NVIDIA DLSS, Intel OIDN)

**Papers**:
- "Real-Time Ray Tracing" - Parker et al., 2010
- "Hybrid Rendering for Real-Time Ray Tracing" - Wyman et al., 2019

## Upscaling Techniques

### DLSS (Deep Learning Super Sampling) - NVIDIA
- AI-based upscaling
- Trains on high-res images
- 2-4x performance boost with quality retention

### FSR (FidelityFX Super Resolution) - AMD
- Spatial upscaling (FSR 1.0)
- Temporal upscaling (FSR 2.0+)
- Open-source, platform-agnostic

### TSR (Temporal Super Resolution) - Unreal Engine
- Similar to FSR 2.0
- Integrated into UE5

**Performance Impact**:
- 4K rendered at 1080p → 3-4x FPS boost

## Virtual Shadow Maps (UE5)

**Concept**: High-resolution shadow maps for Nanite

**Techniques**:
- Page-based allocation
- Cached shadow data
- Clipmap structure for directional lights

**Benefits**:
- High detail shadows
- No shadow acne
- Scalable performance

## References

### Books
- "Real-Time Rendering" (4th Ed) - Akenine-Möller, Haines, Hoffman
- "Physically Based Rendering" - Pharr, Jakob, Humphreys
- "GPU Gems" series (1-3)
- "GPU Pro" series (1-7)

### Conferences
- **SIGGRAPH**: Premier graphics research
- **GDC**: Game graphics talks
- **HPG**: High-Performance Graphics

### Online Resources
- NVIDIA Developer: Ray tracing, DLSS guides
- Epic Developer Community: Unreal rendering
- Unity Blog: HDRP, URP updates
- Advances in Real-Time Rendering (SIGGRAPH course)

### Key Papers (Must-Read)
1. Cook-Torrance: "A Reflectance Model for Computer Graphics" (1982)
2. Burley: "Physically Based Shading at Disney" (2012)
3. Karis: "Real Shading in Unreal Engine 4" (2013)
4. Crassin: "Interactive Indirect Illumination Using Voxel Cone Tracing" (2011)

---

**Last Updated**: 2025-11-19
