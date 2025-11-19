# 3D Audio Reference

## Spatialization

### Basics
```csharp
AudioSource source = GetComponent<AudioSource>();
source.spatialBlend = 1.0f; // 0 = 2D, 1 = 3D
source.minDistance = 1f;
source.maxDistance = 100f;
source.rolloffMode = AudioRolloffMode.Logarithmic;
```

### Distance Attenuation Curves
- **Linear**: Constant decrease
- **Logarithmic**: Realistic (default)
- **Custom**: Full control via curve

## Occlusion & Obstruction

### Simple Implementation
```csharp
void UpdateOcclusion(AudioSource source, Vector3 listener)
{
    if (Physics.Linecast(source.transform.position, listener, out RaycastHit hit))
    {
        // Occluded
        source.volume = 0.3f;
        AudioLowPassFilter filter = source.GetComponent<AudioLowPassFilter>();
        filter.cutoffFrequency = 1000f; // Muffle high frequencies
    }
    else
    {
        // Clear
        source.volume = 1.0f;
    }
}
```

## Reverb Zones

```csharp
AudioReverbZone zone = gameObject.AddComponent<AudioReverbZone>();
zone.minDistance = 5f;
zone.maxDistance = 20f;
zone.reverbPreset = AudioReverbPreset.Cave;
```

## Doppler Effect
```csharp
source.dopplerLevel = 1.0f; // 0 = off, 1 = realistic
```

## HRTF (Head-Related Transfer Function)
- Simulates ear shape/position
- Improved vertical positioning
- Platform-specific (enable in audio settings)
