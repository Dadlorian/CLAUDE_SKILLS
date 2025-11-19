# Spatial Audio Techniques Reference

## Overview

Spatial audio creates the illusion that sounds originate from specific locations in 3D space, fundamental for immersion in games. This reference covers the mathematical and practical techniques for implementing realistic 3D audio.

## Fundamental Concepts

### Distance Attenuation

**Purpose**: Sounds get quieter as they move farther from the listener.

**Mathematical Models**:

1. **Linear Falloff** (simple but unrealistic):
```
volume = max(0, 1 - (distance / maxDistance))

Example:
maxDistance = 100m
At 0m:   volume = 1.0 (100%)
At 50m:  volume = 0.5 (50%)
At 100m: volume = 0.0 (0%)
```

2. **Inverse Distance** (realistic):
```
volume = referenceDistance / (referenceDistance + rolloff * (distance - referenceDistance))

Example:
referenceDistance = 10m (where volume = 50%)
rolloff = 1.0 (realistic)

At 0m:    volume = 1.0
At 10m:   volume = 0.5
At 30m:   volume = 0.25
At 100m:  volume = 0.09
```

3. **Logarithmic** (game-friendly):
```
volume = 1 / (1 + (distance / referenceDistance) ^ rolloff)

rolloff = 2 (aggressive)
referenceDistance = 5m

At 0m:   volume = 1.0
At 5m:   volume = 0.5
At 10m:  volume = 0.2
At 20m:  volume = 0.06
```

**Implementation**:
```csharp
public float CalculateVolume(float distance)
{
    float referenceDistance = 10f;
    float rolloffFactor = 2f;
    float maxDistance = 100f;

    if (distance >= maxDistance)
        return 0f;

    // Logarithmic rolloff
    float attenuation = 1f / (1f + Mathf.Pow(distance / referenceDistance, rolloffFactor));
    return attenuation;
}
```

### Stereo Panning

**Purpose**: Position sound left/right based on horizontal angle.

**Equal Power Panning**:
```csharp
public void CalculatePan(Vector3 listenerPos, Vector3 listenerForward, Vector3 soundPos,
                         out float leftGain, out float rightGain)
{
    // Calculate angle (-1 = full left, 0 = center, 1 = full right)
    Vector3 toSound = (soundPos - listenerPos).normalized;
    Vector3 listenerRight = Vector3.Cross(Vector3.up, listenerForward);
    float pan = Vector3.Dot(toSound, listenerRight);

    // Equal power panning (preserves total energy)
    float angle = (pan + 1f) * 0.5f * Mathf.PI / 2f;
    leftGain = Mathf.Cos(angle);
    rightGain = Mathf.Sin(angle);
}
```

**Pan Law** (maintain perceived loudness):
```
When panning center (both speakers equal):
- -3dB pan law: 0.707 per speaker (√2 total power)
- -4.5dB pan law: 0.595 per speaker
- -6dB pan law: 0.5 per speaker

Most natural: -3dB (equal power)
```

### HRTF (Head-Related Transfer Function)

**Purpose**: Model how ears perceive direction based on head shape and ear position.

**Key Concepts**:

1. **Interaural Time Difference (ITD)**:
   - Sound arrives at far ear later than near ear
   - Delay range: 0-700 microseconds
   - Primary cue for horizontal localization

2. **Interaural Level Difference (ILD)**:
   - High frequencies blocked by head (head shadow effect)
   - Volume difference between ears
   - Primary cue above 1.5 kHz

3. **Spectral Cues**:
   - Ear shape (pinna) filters frequencies differently by direction
   - Critical for vertical and front/back localization

**Basic HRTF Implementation**:
```csharp
public struct HRTFOutput
{
    public float leftDelay;    // Microseconds
    public float rightDelay;
    public float leftGain;
    public float rightGain;
    public float lowPassFilter; // For distance/occlusion
}

public HRTFOutput CalculateHRTF(Vector3 listenerPos, Vector3 listenerForward, Vector3 soundPos)
{
    Vector3 toSound = (soundPos - listenerPos).normalized;

    // Calculate horizontal angle
    Vector3 listenerRight = Vector3.Cross(Vector3.up, listenerForward);
    float azimuth = Mathf.Atan2(Vector3.Dot(toSound, listenerRight),
                                 Vector3.Dot(toSound, listenerForward));

    // Calculate elevation angle
    float elevation = Mathf.Asin(toSound.y);

    HRTFOutput output = new HRTFOutput();

    // Interaural time difference (ITD)
    float headRadius = 0.0875f; // Average human head radius in meters
    float speedOfSound = 343f;   // m/s
    output.leftDelay = (headRadius / speedOfSound) * (azimuth + Mathf.Sin(azimuth));
    output.rightDelay = (headRadius / speedOfSound) * (-azimuth + Mathf.Sin(-azimuth));

    // Interaural level difference (ILD)
    // Head shadow effect is frequency-dependent (simplified here)
    float shadowAttenuation = 1f - Mathf.Abs(azimuth) / Mathf.PI;
    if (azimuth < 0) // Sound to the left
    {
        output.leftGain = 1f;
        output.rightGain = shadowAttenuation;
    }
    else // Sound to the right
    {
        output.leftGain = shadowAttenuation;
        output.rightGain = 1f;
    }

    return output;
}
```

## Advanced Spatialization

### Doppler Effect

**Purpose**: Frequency shift when sound source moves relative to listener.

**Formula**:
```
observedFrequency = emittedFrequency × (speedOfSound + observerVelocity) / (speedOfSound + sourceVelocity)

Approaching: sourceVelocity is negative → higher pitch
Receding: sourceVelocity is positive → lower pitch
```

**Implementation**:
```csharp
public float CalculateDopplerShift(Vector3 listenerPos, Vector3 listenerVelocity,
                                   Vector3 soundPos, Vector3 soundVelocity)
{
    const float speedOfSound = 343f; // m/s at 20°C

    Vector3 toSound = soundPos - listenerPos;
    float distance = toSound.magnitude;

    if (distance < 0.01f)
        return 1f; // No shift at zero distance

    Vector3 direction = toSound / distance;

    // Velocity components along line between listener and source
    float observerVel = Vector3.Dot(listenerVelocity, direction);
    float sourceVel = Vector3.Dot(soundVelocity, direction);

    // Doppler equation
    float dopplerFactor = (speedOfSound + observerVel) / (speedOfSound + sourceVel);

    // Clamp to reasonable range to avoid artifacts
    return Mathf.Clamp(dopplerFactor, 0.5f, 2f);
}
```

### Occlusion and Obstruction

**Occlusion**: Sound completely blocked by geometry
**Obstruction**: Sound partially blocked (e.g., around corner)

**Techniques**:

1. **Raycast-Based**:
```csharp
public float CalculateOcclusion(Vector3 listenerPos, Vector3 soundPos)
{
    Vector3 direction = soundPos - listenerPos;
    float distance = direction.magnitude;

    RaycastHit hit;
    if (Physics.Raycast(listenerPos, direction.normalized, out hit, distance))
    {
        // Sound is occluded
        float occlusionAmount = CalculateMaterialOcclusion(hit.collider);
        return occlusionAmount;
    }

    return 0f; // No occlusion
}

private float CalculateMaterialOcclusion(Collider collider)
{
    // Material-based occlusion values (0 = no occlusion, 1 = fully occluded)
    switch (collider.tag)
    {
        case "Wood":     return 0.3f;
        case "Concrete": return 0.7f;
        case "Metal":    return 0.8f;
        case "Glass":    return 0.2f;
        default:         return 0.5f;
    }
}
```

2. **Volume-Based**:
```csharp
public float CalculateObstruction(Vector3 listenerPos, Vector3 soundPos)
{
    // Cast multiple rays in a cone
    int rayCount = 8;
    int hitCount = 0;

    Vector3 direction = (soundPos - listenerPos).normalized;
    float distance = Vector3.Distance(listenerPos, soundPos);

    for (int i = 0; i < rayCount; i++)
    {
        float angle = (i / (float)rayCount) * 360f;
        Vector3 offset = Quaternion.Euler(0, angle, 0) * Vector3.right * 0.5f;
        Vector3 rayOrigin = listenerPos + offset;

        if (Physics.Raycast(rayOrigin, direction, distance))
        {
            hitCount++;
        }
    }

    return hitCount / (float)rayCount; // 0 = clear, 1 = fully obstructed
}
```

**Audio Filtering** for occlusion:
```csharp
public void ApplyOcclusionFilter(AudioSource source, float occlusion)
{
    // Apply low-pass filter
    AudioLowPassFilter filter = source.GetComponent<AudioLowPassFilter>();
    if (filter == null)
        filter = source.gameObject.AddComponent<AudioLowPassFilter>();

    // Map occlusion to cutoff frequency
    // 0 occlusion = 22000 Hz (no filter)
    // 1 occlusion = 500 Hz (heavily muffled)
    float cutoffFrequency = Mathf.Lerp(22000f, 500f, occlusion);
    filter.cutoffFrequency = cutoffFrequency;

    // Reduce volume with occlusion
    source.volume = Mathf.Lerp(1f, 0.3f, occlusion);
}
```

### Reverb and Acoustic Spaces

**Purpose**: Model reflections and room acoustics.

**Reverb Parameters**:
```csharp
public struct ReverbSettings
{
    public float roomSize;        // 0-100 (cubic meters)
    public float decayTime;       // 0.1-20 seconds
    public float earlyReflections; // 0-1
    public float lateReflections;  // 0-1
    public float diffusion;        // 0-1 (how scattered reflections are)
    public float damping;          // 0-1 (high frequency absorption)
}

// Presets
public static ReverbSettings SmallRoom = new ReverbSettings
{
    roomSize = 10f,
    decayTime = 0.3f,
    earlyReflections = 0.7f,
    lateReflections = 0.3f,
    diffusion = 0.5f,
    damping = 0.8f
};

public static ReverbSettings Cathedral = new ReverbSettings
{
    roomSize = 1000f,
    decayTime = 8f,
    earlyReflections = 0.5f,
    lateReflections = 0.9f,
    diffusion = 0.9f,
    damping = 0.2f
};

public static ReverbSettings Cave = new ReverbSettings
{
    roomSize = 500f,
    decayTime = 5f,
    earlyReflections = 0.4f,
    lateReflections = 0.8f,
    diffusion = 0.6f,
    damping = 0.4f
};
```

**Dynamic Reverb Zones**:
```csharp
public class ReverbZone : MonoBehaviour
{
    public ReverbSettings settings;
    private AudioReverbFilter reverbFilter;

    void Start()
    {
        reverbFilter = Camera.main.GetComponent<AudioReverbFilter>();
        if (reverbFilter == null)
            reverbFilter = Camera.main.gameObject.AddComponent<AudioReverbFilter>();
    }

    void OnTriggerEnter(Collider other)
    {
        if (other.CompareTag("Player"))
        {
            ApplyReverbSettings();
        }
    }

    void ApplyReverbSettings()
    {
        reverbFilter.reverbPreset = AudioReverbPreset.User;
        reverbFilter.room = ConvertRoomSize(settings.roomSize);
        reverbFilter.decayTime = settings.decayTime;
        reverbFilter.reflectionsLevel = ConvertToDecibels(settings.earlyReflections);
        reverbFilter.reverbLevel = ConvertToDecibels(settings.lateReflections);
        reverbFilter.diffusion = settings.diffusion * 100f;
        reverbFilter.hfReference = 5000f * (1f - settings.damping);
    }

    float ConvertRoomSize(float size)
    {
        // Convert room size to reverb room parameter (-10000 to 0)
        return Mathf.Lerp(-10000f, 0f, Mathf.Clamp01(size / 100f));
    }

    float ConvertToDecibels(float linear)
    {
        // Convert 0-1 to decibels (-10000 to 1000)
        if (linear <= 0f)
            return -10000f;
        return Mathf.Lerp(-10000f, 1000f, linear);
    }
}
```

## Optimization Techniques

### Spatial Partitioning for Audio

**Purpose**: Only process audio for nearby sounds.

**Grid-Based Culling**:
```csharp
public class AudioSpatialGrid
{
    private Dictionary<Vector2Int, List<AudioSource>> grid;
    private float cellSize = 50f;

    public void RegisterSound(AudioSource source)
    {
        Vector2Int cell = GetCell(source.transform.position);
        if (!grid.ContainsKey(cell))
            grid[cell] = new List<AudioSource>();

        grid[cell].Add(source);
    }

    public List<AudioSource> GetNearby(Vector3 listenerPos, float radius)
    {
        List<AudioSource> nearby = new List<AudioSource>();
        Vector2Int centerCell = GetCell(listenerPos);
        int cellRadius = Mathf.CeilToInt(radius / cellSize);

        for (int x = -cellRadius; x <= cellRadius; x++)
        {
            for (int z = -cellRadius; z <= cellRadius; z++)
            {
                Vector2Int cell = new Vector2Int(centerCell.x + x, centerCell.y + z);
                if (grid.ContainsKey(cell))
                {
                    foreach (var source in grid[cell])
                    {
                        if (Vector3.Distance(listenerPos, source.transform.position) <= radius)
                        {
                            nearby.Add(source);
                        }
                    }
                }
            }
        }

        return nearby;
    }

    Vector2Int GetCell(Vector3 position)
    {
        return new Vector2Int(
            Mathf.FloorToInt(position.x / cellSize),
            Mathf.FloorToInt(position.z / cellSize)
        );
    }
}
```

### Level of Detail (LOD) for Audio

**Purpose**: Reduce processing for distant sounds.

```csharp
public enum AudioLOD
{
    High,    // Full 3D spatialization, occlusion, reverb
    Medium,  // Basic spatialization, no occlusion
    Low,     // Simple distance attenuation
    Virtual  // Not rendered, but tracked
}

public class AudioLODSystem : MonoBehaviour
{
    public float highLODDistance = 20f;
    public float mediumLODDistance = 50f;
    public float lowLODDistance = 100f;

    private AudioSource audioSource;
    private Transform listener;

    void Start()
    {
        audioSource = GetComponent<AudioSource>();
        listener = Camera.main.transform;
    }

    void Update()
    {
        float distance = Vector3.Distance(transform.position, listener.position);
        AudioLOD lod = DetermineLOD(distance);
        ApplyLOD(lod);
    }

    AudioLOD DetermineLOD(float distance)
    {
        if (distance <= highLODDistance)
            return AudioLOD.High;
        else if (distance <= mediumLODDistance)
            return AudioLOD.Medium;
        else if (distance <= lowLODDistance)
            return AudioLOD.Low;
        else
            return AudioLOD.Virtual;
    }

    void ApplyLOD(AudioLOD lod)
    {
        switch (lod)
        {
            case AudioLOD.High:
                audioSource.spatialBlend = 1f;
                audioSource.reverbZoneMix = 1f;
                // Enable occlusion calculation
                break;

            case AudioLOD.Medium:
                audioSource.spatialBlend = 1f;
                audioSource.reverbZoneMix = 0.5f;
                // Disable occlusion
                break;

            case AudioLOD.Low:
                audioSource.spatialBlend = 1f;
                audioSource.reverbZoneMix = 0f;
                // Simple distance attenuation only
                break;

            case AudioLOD.Virtual:
                // Don't render audio, but keep tracking position
                audioSource.volume = 0f;
                break;
        }
    }
}
```

## Ambisonic Audio

**Purpose**: Full-sphere surround sound (360° horizontal + vertical).

**Ambisonic Formats**:
- **First Order (FOA)**: 4 channels (W, X, Y, Z)
- **Higher Order (HOA)**: More channels = better resolution

**Use Cases**:
- VR audio (head tracking requires full-sphere)
- 360° videos
- Immersive installations

**Implementation** (conceptual):
```csharp
public struct AmbisonicChannels
{
    public float W; // Omnidirectional (pressure)
    public float X; // Front-back
    public float Y; // Left-right
    public float Z; // Up-down
}

public AmbisonicChannels EncodeToAmbisonic(Vector3 soundDirection, float soundLevel)
{
    AmbisonicChannels channels = new AmbisonicChannels();

    // W channel (omnidirectional)
    channels.W = soundLevel * 0.707f; // √2/2 normalization

    // X, Y, Z directional channels
    channels.X = soundLevel * soundDirection.z;  // Front-back
    channels.Y = soundLevel * soundDirection.x;  // Left-right
    channels.Z = soundLevel * soundDirection.y;  // Up-down

    return channels;
}

public void DecodeAmbisonicToStereo(AmbisonicChannels ambisonic, float azimuth,
                                     out float left, out float right)
{
    // Decode to stereo based on listener head rotation
    float cos_az = Mathf.Cos(azimuth);
    float sin_az = Mathf.Sin(azimuth);

    // Left channel
    left = ambisonic.W + (ambisonic.X * sin_az * 0.707f) - (ambisonic.Y * cos_az * 0.707f);

    // Right channel
    right = ambisonic.W + (ambisonic.X * sin_az * 0.707f) + (ambisonic.Y * cos_az * 0.707f);
}
```

## Platform-Specific Techniques

### Windows Sonic / Dolby Atmos

**Features**:
- OS-level spatial audio
- Headphone virtualization of surround sound
- Works with any game using standard Windows audio

**Integration**:
```csharp
// Unity automatically uses Windows Sonic if enabled
// Ensure AudioSettings are configured for 3D

AudioConfiguration config = AudioSettings.GetConfiguration();
config.speakerMode = AudioSpeakerMode.Stereo; // Spatial audio virtualizes to stereo
AudioSettings.Reset(config);
```

### PlayStation Tempest 3D Audio

**Features**:
- Hardware-accelerated HRTF
- Up to hundreds of sound sources
- Custom HRTF profiles per user

**Integration** (pseudocode):
```csharp
// PS5 SDK specific
SceAudio3dObjectHandle obj = CreateAudio3dObject();
SetAudio3dObjectPosition(obj, position);
SetAudio3dObjectVolume(obj, volume);
PlayAudio3dObject(obj, audioData);
```

### Xbox Spatial Audio

**Features**:
- Project Acoustics (geometric audio propagation)
- HRTF built into platform
- Dolby Atmos support

## Best Practices

### Performance Guidelines

**Target Metrics**:
- Audio CPU budget: 5-10% of frame time
- Max simultaneous voices: 64-128 (depends on platform)
- Occlusion raycasts: Max 1 per sound per frame (or amortize over multiple frames)

**Optimization Checklist**:
- [ ] Use spatial partitioning (only process nearby sounds)
- [ ] Implement audio LOD (reduce quality for distant sounds)
- [ ] Pool audio sources (reuse instead of creating/destroying)
- [ ] Limit occlusion raycasts (only on important sounds)
- [ ] Use middleware (FMOD, Wwise) for optimized processing
- [ ] Stream large audio files (music, ambience)
- [ ] Compress audio appropriately (balance quality and size)

### Quality Guidelines

**3D Audio Checklist**:
- [ ] Clear left/right panning (stereo separation)
- [ ] Distance attenuation feels natural (not too abrupt)
- [ ] Doppler effect is subtle (not distracting)
- [ ] Occlusion is believable (muffled through walls)
- [ ] Reverb matches environment (cathedral vs small room)
- [ ] HRTF improves localization (especially vertical)
- [ ] No audio popping or clicking (smooth transitions)

### Testing Methodology

**Spatial Audio Test Scenarios**:
1. **Horizontal Localization**: Sound moves left-right, player closes eyes, points to sound
2. **Vertical Localization**: Sound moves up-down, player identifies direction
3. **Distance Perception**: Sound moves closer/farther, player estimates distance
4. **Occlusion**: Sound behind wall vs open space, player identifies muffling
5. **Reverb**: Different room types, player identifies environment

**Tools**:
- Audio profilers (Unity Profiler, FMOD Profiler)
- Visual debuggers (draw audio sources, occlusion rays)
- Headphone testing (critical for HRTF)
- Surround speaker testing (5.1, 7.1 setups)

## Common Pitfalls

### Mistake 1: Over-Aggressive Distance Attenuation

**Problem**: Sounds disappear too quickly as player moves away.

**Solution**: Use realistic rolloff curves; test at various distances.

### Mistake 2: No Occlusion

**Problem**: Sounds heard clearly through walls.

**Solution**: Implement basic raycast occlusion at minimum.

### Mistake 3: Constant Reverb

**Problem**: Same reverb everywhere breaks immersion.

**Solution**: Use reverb zones; different spaces have different acoustics.

### Mistake 4: Ignoring Vertical Localization

**Problem**: Sounds above/below player feel like they're on same plane.

**Solution**: Use HRTF or ensure vertical panning is implemented.

### Mistake 5: CPU-Intensive Occlusion Every Frame

**Problem**: Raycasting occlusion for every sound every frame tanks performance.

**Solution**: Amortize over multiple frames; only check important sounds frequently.

## Conclusion

Great spatial audio requires:
1. **Realistic distance attenuation** - Sounds fade naturally
2. **Accurate panning** - Clear left/right/vertical positioning
3. **Occlusion and reverb** - Environment affects sound
4. **Performance optimization** - Doesn't tank frame rate
5. **Platform integration** - Use hardware acceleration when available

The techniques in this reference cover the fundamentals and advanced topics for production-quality 3D audio in games. Always test with headphones and surround speakers to ensure localization works correctly.
