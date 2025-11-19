# Lighting Techniques Reference

## Light Types

### Directional Light
- Simulates sun
- Infinite distance
- Parallel rays
- **Use**: Outdoor scenes

### Point Light
- Emits in all directions
- Has range/falloff
- **Use**: Lamps, fires

### Spot Light
- Cone-shaped emission
- Has range and angle
- **Use**: Flashlights, stage lights

### Area Light
- Emits from surface
- Soft shadows
- **Use**: Windows, panels

## Shadow Techniques

### Shadow Mapping
- Render depth from light
- Compare with scene depth
- **Issues**: Shadow acne, peter panning

### Cascaded Shadow Maps (CSM)
- Multiple shadow maps at different distances
- Better quality for large scenes

### Ray-Traced Shadows
- Physically accurate
- Expensive but high quality

## Global Illumination

### Baked Lightmaps
- Pre-computed offline
- Fast runtime, static only

### Light Probes
- Sample lighting at points
- Interpolate for dynamic objects

### Real-Time GI
- Screen-space techniques
- Voxel cone tracing
- Ray tracing
