# FMOD Integration Guide for Unity

## Overview

FMOD Studio is the industry-leading audio middleware for games. It provides a powerful event-based system that separates audio design from code, allowing sound designers to iterate independently while giving programmers a simple API. This guide covers comprehensive integration patterns for Unity.

## Installation and Setup

### Step 1: Download and Install

1. **FMOD Studio**: Download from [fmod.com](https://www.fmod.com/download)
   - Install FMOD Studio (authoring tool)
   - Version 2.02+ recommended

2. **Unity Integration Plugin**:
   - Download Unity Integration package from FMOD downloads
   - Import into Unity: Assets → Import Package → Custom Package
   - Select downloaded .unitypackage

### Step 2: Configure Settings

1. Open FMOD Settings:
   - **Window → FMOD → Edit Settings**

2. Configure paths:
   - **Studio Project Path**: Point to your `.fsproj` file
   - **Build Path**: Where FMOD builds banks (usually `Assets/StreamingAssets`)
   - **Platform Settings**: Configure per-platform audio settings

3. Import banks:
   - FMOD → Refresh Banks (or set Auto-build)
   - Verify banks appear in StreamingAssets folder

### Step 3: Project Structure

Recommended FMOD Studio project organization:
```
MyProject.fsproj
├── Events/
│   ├── Music/
│   ├── SFX/
│   │   ├── Player/
│   │   ├── Enemies/
│   │   └── Environment/
│   └── Ambience/
├── Parameters/
├── Snapshots/
└── Banks/
    ├── Master.bank
    ├── SFX.bank
    └── Music.bank
```

## Core Integration Patterns

### Pattern 1: Simple One-Shot Sounds

For sounds that play once and automatically clean up (UI, impacts, pickups):

```csharp
using FMODUnity;
using UnityEngine;

public class SimpleAudio : MonoBehaviour
{
    [EventRef]
    public string impactSound = "event:/SFX/Impact";

    public void PlayImpact()
    {
        // Plays at world origin, no spatial audio
        RuntimeManager.PlayOneShot(impactSound);
    }

    public void PlayImpactAt(Vector3 position)
    {
        // Plays at specific world position
        RuntimeManager.PlayOneShot(impactSound, position);
    }

    public void OnCollisionEnter(Collision collision)
    {
        // Play sound at collision point
        RuntimeManager.PlayOneShot(impactSound, collision.contacts[0].point);
    }
}
```

### Pattern 2: Persistent Event Instances

For sounds that need control (looping, parameters, stopping):

```csharp
using FMODUnity;
using FMOD.Studio;
using UnityEngine;

public class EngineSound : MonoBehaviour
{
    [EventRef]
    public string engineEvent = "event:/SFX/Engine";

    private EventInstance engineInstance;
    private bool isInitialized = false;

    void Start()
    {
        InitializeEngineSound();
    }

    void InitializeEngineSound()
    {
        // Create instance
        engineInstance = RuntimeManager.CreateInstance(engineEvent);

        // Attach to this GameObject for 3D positioning
        RuntimeManager.AttachInstanceToGameObject(engineInstance, transform);

        // Start playback
        engineInstance.start();

        isInitialized = true;
    }

    void Update()
    {
        if (!isInitialized) return;

        // Update engine sound based on speed
        float speed = GetComponent<Rigidbody>().velocity.magnitude;
        engineInstance.setParameterByName("Speed", speed);
    }

    void OnDestroy()
    {
        // Proper cleanup
        if (isInitialized)
        {
            engineInstance.stop(STOP_MODE.ALLOWFADEOUT);
            engineInstance.release();
        }
    }
}
```

### Pattern 3: Music System with Parameters

```csharp
using FMODUnity;
using FMOD.Studio;
using UnityEngine;

public class MusicManager : MonoBehaviour
{
    public static MusicManager Instance { get; private set; }

    [EventRef]
    public string musicEvent = "event:/Music/GameplayMusic";

    private EventInstance musicInstance;

    void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
            InitializeMusic();
        }
        else
        {
            Destroy(gameObject);
        }
    }

    void InitializeMusic()
    {
        musicInstance = RuntimeManager.CreateInstance(musicEvent);
        musicInstance.start();
    }

    public void SetIntensity(float intensity)
    {
        // Intensity: 0 (calm) to 1 (combat)
        musicInstance.setParameterByName("Intensity", intensity);
    }

    public void SetMusicState(string stateName)
    {
        // Change music state (Exploration, Combat, Boss)
        musicInstance.setParameterByName("MusicState", GetStateValue(stateName));
    }

    private float GetStateValue(string state)
    {
        return state switch
        {
            "Exploration" => 0f,
            "Combat" => 1f,
            "Boss" => 2f,
            _ => 0f
        };
    }

    public void StopMusic(bool immediate = false)
    {
        STOP_MODE mode = immediate ? STOP_MODE.IMMEDIATE : STOP_MODE.ALLOWFADEOUT;
        musicInstance.stop(mode);
    }

    void OnDestroy()
    {
        musicInstance.stop(STOP_MODE.IMMEDIATE);
        musicInstance.release();
    }
}
```

### Pattern 4: Footstep System with Surface Detection

```csharp
using FMODUnity;
using UnityEngine;

public class FootstepController : MonoBehaviour
{
    [EventRef]
    public string footstepEvent = "event:/SFX/Player/Footstep";

    private float stepInterval = 0.5f;
    private float stepTimer = 0f;

    void Update()
    {
        // Detect if moving
        float speed = GetComponent<CharacterController>().velocity.magnitude;

        if (speed > 0.1f)
        {
            stepTimer += Time.deltaTime;

            if (stepTimer >= stepInterval)
            {
                PlayFootstep();
                stepTimer = 0f;

                // Adjust interval based on speed
                stepInterval = Mathf.Lerp(0.6f, 0.3f, speed / 10f);
            }
        }
    }

    void PlayFootstep()
    {
        // Detect surface type
        RaycastHit hit;
        if (Physics.Raycast(transform.position, Vector3.down, out hit, 2f))
        {
            string surfaceType = GetSurfaceType(hit.collider);

            // Create event instance
            EventInstance footstep = RuntimeManager.CreateInstance(footstepEvent);

            // Set surface parameter
            footstep.setParameterByName("Surface", GetSurfaceValue(surfaceType));

            // Play at foot position
            footstep.set3DAttributes(RuntimeUtils.To3DAttributes(hit.point));
            footstep.start();

            // Auto-cleanup
            footstep.release();
        }
    }

    private string GetSurfaceType(Collider collider)
    {
        // Check for SurfaceType component
        SurfaceType surface = collider.GetComponent<SurfaceType>();
        if (surface != null)
            return surface.surfaceTypeName;

        // Fallback: detect by tag
        return collider.tag switch
        {
            "Metal" => "Metal",
            "Wood" => "Wood",
            "Concrete" => "Concrete",
            _ => "Default"
        };
    }

    private float GetSurfaceValue(string surfaceType)
    {
        return surfaceType switch
        {
            "Grass" => 0f,
            "Concrete" => 1f,
            "Metal" => 2f,
            "Wood" => 3f,
            "Water" => 4f,
            _ => 0f
        };
    }
}

// Helper component for surface marking
public class SurfaceType : MonoBehaviour
{
    public string surfaceTypeName = "Default";
}
```

## Advanced Techniques

### Dynamic Occlusion and Obstruction

```csharp
using FMODUnity;
using FMOD.Studio;
using UnityEngine;

public class AudioOcclusionManager : MonoBehaviour
{
    [EventRef]
    public string ambientSound = "event:/Ambience/Outdoor";

    private EventInstance soundInstance;
    private Transform listenerTransform;

    void Start()
    {
        soundInstance = RuntimeManager.CreateInstance(ambientSound);
        soundInstance.set3DAttributes(RuntimeUtils.To3DAttributes(transform.position));
        soundInstance.start();

        // Get listener (usually main camera)
        listenerTransform = Camera.main.transform;
    }

    void Update()
    {
        CalculateOcclusion();
    }

    void CalculateOcclusion()
    {
        Vector3 directionToListener = listenerTransform.position - transform.position;
        float distance = directionToListener.magnitude;

        // Raycast to check for obstacles
        RaycastHit hit;
        if (Physics.Raycast(transform.position, directionToListener.normalized, out hit, distance))
        {
            if (hit.collider.gameObject != listenerTransform.gameObject)
            {
                // There's an obstacle
                float occlusionAmount = CalculateOcclusionAmount(hit);
                soundInstance.setParameterByName("Occlusion", occlusionAmount);
            }
            else
            {
                // Clear line of sight
                soundInstance.setParameterByName("Occlusion", 0f);
            }
        }
    }

    float CalculateOcclusionAmount(RaycastHit hit)
    {
        // Different materials occlude differently
        string tag = hit.collider.tag;

        return tag switch
        {
            "ThinWall" => 0.3f,
            "ThickWall" => 0.8f,
            "Metal" => 0.9f,
            _ => 0.5f
        };
    }

    void OnDestroy()
    {
        soundInstance.stop(STOP_MODE.IMMEDIATE);
        soundInstance.release();
    }
}
```

### Reverb Zone System

```csharp
using FMODUnity;
using UnityEngine;

public class ReverbZone : MonoBehaviour
{
    public string reverbPreset = "Cathedral";

    private void OnTriggerEnter(Collider other)
    {
        if (other.CompareTag("Player"))
        {
            ApplyReverb();
        }
    }

    private void OnTriggerExit(Collider other)
    {
        if (other.CompareTag("Player"))
        {
            ClearReverb();
        }
    }

    void ApplyReverb()
    {
        // Set global reverb parameter
        RuntimeManager.StudioSystem.setParameterByName("GlobalReverb", GetReverbValue());
    }

    void ClearReverb()
    {
        RuntimeManager.StudioSystem.setParameterByName("GlobalReverb", 0f);
    }

    float GetReverbValue()
    {
        return reverbPreset switch
        {
            "Small Room" => 1f,
            "Cathedral" => 2f,
            "Cave" => 3f,
            "Outdoor" => 0f,
            _ => 0f
        };
    }
}
```

### Snapshot Mixing (Dynamic Ducking)

```csharp
using FMODUnity;
using FMOD.Studio;
using UnityEngine;

public class DialogueSystem : MonoBehaviour
{
    [EventRef]
    public string dialogueEvent = "event:/Dialogue/NPC";

    private EventInstance dialogueInstance;
    private Snapshot dialogueSnapshot;

    void Start()
    {
        // Load dialogue snapshot (defined in FMOD Studio)
        dialogueSnapshot = RuntimeManager.StudioSystem.getEvent("snapshot:/DialogueDuck");
    }

    public void PlayDialogue(string dialogueKey)
    {
        // Create dialogue instance
        dialogueInstance = RuntimeManager.CreateInstance(dialogueEvent);

        // Set dialogue variant parameter
        dialogueInstance.setParameterByName("DialogueID", GetDialogueID(dialogueKey));

        // Start snapshot (ducks music and ambient)
        dialogueSnapshot.start();

        // Play dialogue
        dialogueInstance.start();

        // Schedule cleanup when dialogue ends
        StartCoroutine(WaitForDialogueEnd());
    }

    System.Collections.IEnumerator WaitForDialogueEnd()
    {
        PLAYBACK_STATE state;

        do
        {
            dialogueInstance.getPlaybackState(out state);
            yield return null;
        } while (state != PLAYBACK_STATE.STOPPED);

        // Stop snapshot (restore volume)
        dialogueSnapshot.stop(STOP_MODE.ALLOWFADEOUT);

        // Cleanup
        dialogueInstance.release();
    }

    int GetDialogueID(string key)
    {
        // Convert dialogue key to ID
        // This would typically be a lookup table
        return key.GetHashCode();
    }
}
```

## Performance Optimization

### Voice Pooling

```csharp
using FMODUnity;
using FMOD.Studio;
using UnityEngine;
using System.Collections.Generic;

public class AudioPool : MonoBehaviour
{
    public static AudioPool Instance { get; private set; }

    [EventRef]
    public List<string> preloadedEvents;

    private Dictionary<string, Queue<EventInstance>> eventPools;

    void Awake()
    {
        Instance = this;
        eventPools = new Dictionary<string, Queue<EventInstance>>();

        // Preload event instances
        foreach (string eventPath in preloadedEvents)
        {
            CreatePool(eventPath, poolSize: 10);
        }
    }

    void CreatePool(string eventPath, int poolSize)
    {
        Queue<EventInstance> pool = new Queue<EventInstance>();

        for (int i = 0; i < poolSize; i++)
        {
            EventInstance instance = RuntimeManager.CreateInstance(eventPath);
            pool.Enqueue(instance);
        }

        eventPools[eventPath] = pool;
    }

    public EventInstance GetInstance(string eventPath)
    {
        if (eventPools.ContainsKey(eventPath) && eventPools[eventPath].Count > 0)
        {
            return eventPools[eventPath].Dequeue();
        }

        // Create new instance if pool empty
        return RuntimeManager.CreateInstance(eventPath);
    }

    public void ReturnInstance(string eventPath, EventInstance instance)
    {
        // Reset instance
        instance.stop(STOP_MODE.IMMEDIATE);

        // Return to pool
        if (eventPools.ContainsKey(eventPath))
        {
            eventPools[eventPath].Enqueue(instance);
        }
        else
        {
            instance.release();
        }
    }
}
```

### Streaming vs Memory Loading

```csharp
// In FMOD Studio:
// - Set small sounds (< 200KB) to "Decompress into memory"
// - Set music/ambience to "Streaming"
// - Configure in Bank settings

// Unity side: Verify streaming settings
public class AudioMemoryManager : MonoBehaviour
{
    void Start()
    {
        // Get memory usage info
        FMOD.Studio.MEMORY_USAGE memUsage;
        RuntimeManager.StudioSystem.getMemoryUsage(out memUsage);

        Debug.Log($"Sample data memory: {memUsage.sampledata / 1024f} KB");
        Debug.Log($"Stream buffer memory: {memUsage.streamdata / 1024f} KB");
    }
}
```

## Common Patterns and Best Practices

### Centralized Audio Manager

```csharp
using FMODUnity;
using FMOD.Studio;
using UnityEngine;
using System.Collections.Generic;

public class GameAudioManager : MonoBehaviour
{
    public static GameAudioManager Instance { get; private set; }

    // Global parameters
    private const string PARAM_MASTER_VOLUME = "MasterVolume";
    private const string PARAM_MUSIC_VOLUME = "MusicVolume";
    private const string PARAM_SFX_VOLUME = "SFXVolume";

    // Active instances tracking
    private Dictionary<string, EventInstance> activeInstances;

    void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
            Initialize();
        }
        else
        {
            Destroy(gameObject);
        }
    }

    void Initialize()
    {
        activeInstances = new Dictionary<string, EventInstance>();

        // Load default volumes from PlayerPrefs
        SetMasterVolume(PlayerPrefs.GetFloat("MasterVolume", 1f));
        SetMusicVolume(PlayerPrefs.GetFloat("MusicVolume", 1f));
        SetSFXVolume(PlayerPrefs.GetFloat("SFXVolume", 1f));
    }

    public void SetMasterVolume(float volume)
    {
        Bus masterBus = RuntimeManager.GetBus("bus:/");
        masterBus.setVolume(volume);
        PlayerPrefs.SetFloat("MasterVolume", volume);
    }

    public void SetMusicVolume(float volume)
    {
        Bus musicBus = RuntimeManager.GetBus("bus:/Music");
        musicBus.setVolume(volume);
        PlayerPrefs.SetFloat("MusicVolume", volume);
    }

    public void SetSFXVolume(float volume)
    {
        Bus sfxBus = RuntimeManager.GetBus("bus:/SFX");
        sfxBus.setVolume(volume);
        PlayerPrefs.SetFloat("SFXVolume", volume);
    }

    public void PlayOneShotAt(string eventPath, Vector3 position)
    {
        RuntimeManager.PlayOneShot(eventPath, position);
    }

    public EventInstance CreateAndTrack(string eventPath, string identifier)
    {
        EventInstance instance = RuntimeManager.CreateInstance(eventPath);
        activeInstances[identifier] = instance;
        return instance;
    }

    public void StopAndRelease(string identifier, bool immediate = false)
    {
        if (activeInstances.ContainsKey(identifier))
        {
            STOP_MODE mode = immediate ? STOP_MODE.IMMEDIATE : STOP_MODE.ALLOWFADEOUT;
            activeInstances[identifier].stop(mode);
            activeInstances[identifier].release();
            activeInstances.Remove(identifier);
        }
    }

    public void StopAllSounds()
    {
        foreach (var kvp in activeInstances)
        {
            kvp.Value.stop(STOP_MODE.IMMEDIATE);
            kvp.Value.release();
        }
        activeInstances.Clear();
    }

    void OnDestroy()
    {
        StopAllSounds();
    }
}
```

## Debugging and Testing

### Audio Debug Overlay

```csharp
using FMODUnity;
using FMOD.Studio;
using UnityEngine;

public class AudioDebugger : MonoBehaviour
{
    private bool showDebug = false;

    void Update()
    {
        if (Input.GetKeyDown(KeyCode.F8))
        {
            showDebug = !showDebug;
        }
    }

    void OnGUI()
    {
        if (!showDebug) return;

        GUILayout.BeginArea(new Rect(10, 10, 400, 600));
        GUILayout.Label("=== Audio Debug ===");

        // Memory usage
        FMOD.Studio.MEMORY_USAGE memUsage;
        RuntimeManager.StudioSystem.getMemoryUsage(out memUsage);

        GUILayout.Label($"Sample Memory: {memUsage.sampledata / 1024f:F2} KB");
        GUILayout.Label($"Stream Memory: {memUsage.streamdata / 1024f:F2} KB");

        // CPU usage
        FMOD.Studio.CPU_USAGE cpuUsage;
        RuntimeManager.CoreSystem.getCPUUsage(out cpuUsage);

        GUILayout.Label($"DSP CPU: {cpuUsage.dsp:F2}%");
        GUILayout.Label($"Stream CPU: {cpuUsage.stream:F2}%");
        GUILayout.Label($"Update CPU: {cpuUsage.update:F2}%");

        // Channel count
        int channels, realchannels;
        RuntimeManager.CoreSystem.getChannelsPlaying(out channels, out realchannels);

        GUILayout.Label($"Channels Playing: {channels} (Real: {realchannels})");

        GUILayout.EndArea();
    }
}
```

## Common Issues and Solutions

### Issue 1: Events Not Playing

**Symptoms**: No sound when triggering events

**Solutions**:
1. Verify banks are built: FMOD → Refresh Banks
2. Check event path is correct (use [EventRef] attribute)
3. Ensure banks are in StreamingAssets folder
4. Verify FMOD initialization: Check for errors in Console

### Issue 2: Stuttering Audio

**Symptoms**: Choppy, interrupted playback

**Solutions**:
1. Increase buffer size: Edit Settings → Buffer Length
2. Reduce voice count: Check channel count in profiler
3. Use streaming for large files
4. Enable asynchronous bank loading

### Issue 3: Memory Leaks

**Symptoms**: Memory usage increases over time

**Solutions**:
1. Always call `release()` on EventInstances
2. Use `stop()` before `release()`
3. Don't create new instances every frame
4. Use object pooling for frequently-played sounds

### Issue 4: 3D Audio Not Working

**Symptoms**: Sounds don't spatialize correctly

**Solutions**:
1. Set event to 3D in FMOD Studio
2. Call `set3DAttributes()` or use `AttachInstanceToGameObject()`
3. Verify listener position (usually camera)
4. Check min/max distance settings in FMOD Studio

## Production Checklist

Before shipping:

- [ ] All banks are properly built and included
- [ ] Streaming sounds are correctly configured
- [ ] Memory usage is within target (< 100MB typically)
- [ ] CPU usage is acceptable (< 5% for audio)
- [ ] All EventInstances are properly released
- [ ] Volume settings are saved/loaded
- [ ] Audio works on all target platforms
- [ ] Localization is implemented (if needed)
- [ ] Subtitles sync with dialogue (if applicable)
- [ ] Audio doesn't cut out under load

## Platform-Specific Considerations

### Mobile Optimization
```csharp
#if UNITY_ANDROID || UNITY_IOS
void Start()
{
    // Use lower sample rate on mobile
    RuntimeManager.StudioSystem.setAdvancedSettings(new FMOD.Studio.ADVANCEDSETTINGS
    {
        studioupdateperiod = 20 // Update every 20ms instead of 16ms
    });
}
#endif
```

### Console Optimization
```csharp
#if UNITY_PS5 || UNITY_XBOXONE
void Start()
{
    // Take advantage of hardware acceleration
    RuntimeManager.CoreSystem.setDSPBufferSize(512, 4);
}
#endif
```

## Conclusion

FMOD Studio provides powerful audio tools that scale from simple sound effects to complex adaptive music systems. Key principles:

1. **Use event-based architecture** - Separate audio design from code
2. **Leverage parameters** - Connect game state to audio dynamically
3. **Manage resources** - Properly create, use, and release instances
4. **Optimize performance** - Stream large files, pool instances, monitor CPU/memory
5. **Test thoroughly** - Profile on target hardware, test edge cases

The integration patterns in this guide cover 90% of game audio needs. For advanced topics (procedural audio, advanced spatialization), consult the FMOD Studio documentation and community forums.

## References
- [FMOD Studio Documentation](https://fmod.com/docs)
- [FMOD Unity Integration Documentation](https://fmod.com/docs/2.02/unity/)
- [FMOD Community Forum](https://qa.fmod.com/)
- [FMOD API Reference](https://fmod.com/docs/2.02/api/)
