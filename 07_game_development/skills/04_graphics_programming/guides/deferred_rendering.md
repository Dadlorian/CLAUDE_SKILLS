# Deferred Rendering Guide

## Forward vs Deferred

### Forward Rendering
- Each object rendered with all lights
- Cost: Objects × Lights
- Good for: Few lights, transparent objects

### Deferred Rendering
- Render geometry to G-Buffer first
- Apply lighting as post-process
- Cost: Objects + Lights
- Good for: Many lights, opaque scenes

## G-Buffer Layout

**Render Targets**:
1. **RT0**: Albedo (RGB) + Metallic (A)
2. **RT1**: Normal (RGB) + Roughness (A)
3. **RT2**: Emission (RGB) + AO (A)
4. **Depth**: Depth/Stencil buffer

## Implementation

### Geometry Pass
```hlsl
struct GBufferOutput
{
    float4 Albedo : SV_Target0;
    float4 Normal : SV_Target1;
    float4 Emission : SV_Target2;
};

GBufferOutput PS_GBuffer(VertexOutput input)
{
    GBufferOutput output;

    output.Albedo = float4(albedo, metallic);
    output.Normal = float4(normal * 0.5 + 0.5, roughness);
    output.Emission = float4(emission, ao);

    return output;
}
```

### Lighting Pass
```hlsl
float4 PS_Lighting(VertexOutput input) : SV_Target
{
    // Sample G-Buffer
    float4 albedoMetal = GBuffer0.Sample(sampler, input.uv);
    float4 normalRough = GBuffer1.Sample(sampler, input.uv);

    float3 albedo = albedoMetal.rgb;
    float metallic = albedoMetal.a;
    float3 normal = normalRough.rgb * 2.0 - 1.0;
    float roughness = normalRough.a;

    // Reconstruct world position from depth
    float depth = DepthBuffer.Sample(sampler, input.uv);
    float3 worldPos = ReconstructWorldPos(input.uv, depth);

    // Apply lighting (PBR, etc.)
    float3 lighting = CalculateLighting(worldPos, normal, albedo, metallic, roughness);

    return float4(lighting, 1.0);
}
```

## Advantages
✅ Constant cost per light
✅ Efficient with many lights
✅ Easy post-processing

## Disadvantages
❌ No MSAA (use TAA instead)
❌ No transparency
❌ Higher memory bandwidth
❌ No material variation

## Unity Implementation
- Rendering Path: Deferred
- Automatically handles G-Buffer

## Unreal Implementation
- Default rendering path
- Can view G-Buffer: Show → Visualize → Buffer Visualization
