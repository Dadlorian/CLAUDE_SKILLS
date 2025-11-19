# Shader Optimization Quick Reference

## Performance Targets

### Mobile
- **Vertex Shader**: < 200 instructions
- **Fragment Shader**: < 300 instructions
- **Texture Samples**: < 4 per fragment

### Console/PC
- **Vertex Shader**: < 500 instructions
- **Fragment Shader**: < 1000 instructions
- **Texture Samples**: < 8 per fragment

## Optimization Techniques

### 1. Move Work to Vertex Shader
Fragment shader runs per-pixel (expensive), vertex shader runs per-vertex (cheaper)

❌ **Bad** (fragment):
```hlsl
float3 worldPos = mul(unity_ObjectToWorld, input.vertex);
float3 normal = normalize(mul((float3x3)unity_ObjectToWorld, input.normal));
```

✅ **Good** (vertex):
```hlsl
output.worldPos = mul(unity_ObjectToWorld, input.vertex);
output.worldNormal = normalize(mul((float3x3)unity_ObjectToWorld, input.normal));
```

### 2. Use Half Precision
```hlsl
// Use half instead of float when possible (mobile)
half3 color = half3(1, 0, 0);
half alpha = 0.5h;
```

### 3. Avoid Conditionals
❌ **Bad**:
```hlsl
if (value > 0.5)
    result = a;
else
    result = b;
```

✅ **Good**:
```hlsl
result = lerp(b, a, step(0.5, value));
```

### 4. Minimize Texture Samples
Texture sampling is expensive

❌ **Bad**:
```hlsl
float4 tex1 = tex2D(_Tex, uv);
float4 tex2 = tex2D(_Tex, uv + 0.01);
float4 tex3 = tex2D(_Tex, uv + 0.02);
```

### 5. Use LOD Shaders
Different shader complexity for different distances

```hlsl
// LOD 0: Full PBR
// LOD 1: Simplified lighting
// LOD 2: Unlit
```

### 6. Combine Operations
❌ **Bad**:
```hlsl
float3 a = normalize(v1);
float3 b = normalize(v2);
float3 c = normalize(v3);
```

✅ **Good**:
```hlsl
// Combine normalizations if vectors are similar
```

## Profiling

### Unity
- Frame Debugger → Shader Complexity view
- Stats window: Shader time

### Unreal
- Shader Complexity view mode (Alt+8)
- Console: `profilegpu`

### RenderDoc
- Shader instruction count
- ALU/TEX balance

## Mobile Shader Variants

```hlsl
#pragma shader_feature _NORMALMAP
#pragma shader_feature _METALLICGLOSSMAP
#pragma shader_feature _EMISSION

// Only include features you need
```

## References
- "GPU Gems" series
- "Optimizing Mobile Shader Performance" - Arm
- "Shader Optimization" - NVIDIA
