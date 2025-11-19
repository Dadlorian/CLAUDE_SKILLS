# FMOD Integration Guide for Unity

## Setup

1. Download FMOD Studio and Unity Integration from fmod.com
2. Import FMOD Unity Integration package
3. Window → FMOD → Edit Settings
4. Set Studio Project Path to your .fsproj file

## Basic Implementation

```csharp
using FMODUnity;

public class AudioManager : MonoBehaviour
{
    [EventRef]
    public string musicEvent;

    [EventRef]
    public string footstepEvent;

    private FMOD.Studio.EventInstance musicInstance;

    void Start()
    {
        // Play music
        musicInstance = RuntimeManager.CreateInstance(musicEvent);
        musicInstance.start();
    }

    public void PlayFootstep()
    {
        RuntimeManager.PlayOneShot(footstepEvent, transform.position);
    }

    public void SetMusicParameter(string param, float value)
    {
        musicInstance.setParameterByName(param, value);
    }

    void OnDestroy()
    {
        musicInstance.stop(FMOD.Studio.STOP_MODE.IMMEDIATE);
        musicInstance.release();
    }
}
```

## 3D Audio

```csharp
FMOD.Studio.EventInstance instance = RuntimeManager.CreateInstance("event:/Ambience/Forest");
instance.set3DAttributes(RuntimeUtils.To3DAttributes(transform.position));
instance.start();
```

## References
- FMOD Unity Integration documentation
- FMOD Studio User Manual
