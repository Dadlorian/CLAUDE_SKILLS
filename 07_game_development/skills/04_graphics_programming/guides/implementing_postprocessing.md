# Implementing Post-Processing Effects

## Common Effects

### Bloom
**Purpose**: Glow on bright areas
```hlsl
float3 Bloom(Texture2D tex, float2 uv, float threshold)
{
    float3 color = tex.Sample(sampler, uv).rgb;
    float brightness = dot(color, float3(0.2126, 0.7152, 0.0722));

    if (brightness > threshold)
        return color * (brightness - threshold);
    return 0;
}
```

### Chromatic Aberration
**Purpose**: RGB channel separation (lens distortion)
```hlsl
float3 ChromaticAberration(Texture2D tex, float2 uv, float amount)
{
    float2 direction = uv - 0.5;
    float r = tex.Sample(sampler, uv + direction * amount * 0.01).r;
    float g = tex.Sample(sampler, uv).g;
    float b = tex.Sample(sampler, uv - direction * amount * 0.01).b;
    return float3(r, g, b);
}
```

### Vignette
**Purpose**: Darken edges
```hlsl
float Vignette(float2 uv, float intensity)
{
    float2 center = uv - 0.5;
    float dist = length(center);
    return 1.0 - (dist * intensity);
}
```

### Color Grading
**Purpose**: Adjust color mood
```hlsl
float3 ColorGrade(float3 color, float saturation, float contrast)
{
    // Saturation
    float luma = dot(color, float3(0.2126, 0.7152, 0.0722));
    color = lerp(luma, color, saturation);

    // Contrast
    color = (color - 0.5) * contrast + 0.5;

    return saturate(color);
}
```

## Unity URP Post-Processing

```csharp
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

Volume volume = GetComponent<Volume>();
if (volume.profile.TryGet<Bloom>(out var bloom))
{
    bloom.intensity.value = 1.5f;
    bloom.threshold.value = 1.0f;
}
```

## Performance
- Post-processing is expensive (runs per-pixel)
- Use at appropriate resolution
- Combine effects when possible
- Optimize shader instructions
