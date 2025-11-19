# Dynamic Music Systems Guide

## Layered Music

### Concept
Multiple stems play simultaneously, volume adjusted based on game state

### Implementation
```csharp
using UnityEngine;

public class LayeredMusicSystem : MonoBehaviour
{
    [SerializeField] private AudioSource drums;
    [SerializeField] private AudioSource bass;
    [SerializeField] private AudioSource melody;
    [SerializeField] private AudioSource choir;

    [SerializeField] private float fadeSpeed = 2f;

    private float drumsVolume = 0f;
    private float bassVolume = 0f;
    private float melodyVolume = 0f;
    private float choirVolume = 0f;

    void Start()
    {
        // Start all layers, volume at 0
        drums.Play();
        bass.Play();
        melody.Play();
        choir.Play();

        drums.volume = 0;
        bass.volume = 0;
        melody.volume = 0;
        choir.volume = 0;
    }

    void Update()
    {
        // Smoothly adjust volumes
        drums.volume = Mathf.Lerp(drums.volume, drumsVolume, Time.deltaTime * fadeSpeed);
        bass.volume = Mathf.Lerp(bass.volume, bassVolume, Time.deltaTime * fadeSpeed);
        melody.volume = Mathf.Lerp(melody.volume, melodyVolume, Time.deltaTime * fadeSpeed);
        choir.volume = Mathf.Lerp(choir.volume, choirVolume, Time.deltaTime * fadeSpeed);
    }

    public void SetIntensity(float intensity)
    {
        // intensity 0-1
        drumsVolume = intensity > 0.2f ? 1f : 0f;
        bassVolume = intensity > 0.4f ? 1f : 0f;
        melodyVolume = intensity > 0.6f ? 1f : 0f;
        choirVolume = intensity > 0.8f ? 1f : 0f;
    }
}
```

## Horizontal Resequencing

### Concept
Switch between different musical phrases

### FMOD Implementation
```
1. Create Music Track
2. Add Tempo (120 BPM)
3. Add Transition Markers (every 4 beats)
4. Create Parameter (Intensity)
5. Add Transition Timelines for each intensity level
6. Set Transition Quantization (Next Bar)
```

## Vertical Remixing

### Concept
Crossfade between different arrangements

```csharp
public void TransitionToIntenseMusic()
{
    StartCoroutine(CrossfadeMusic(calmMusic, intenseMusic, 2f));
}

IEnumerator CrossfadeMusic(AudioSource from, AudioSource to, float duration)
{
    to.Play();
    to.volume = 0;

    float elapsed = 0;
    while (elapsed < duration)
    {
        elapsed += Time.deltaTime;
        float t = elapsed / duration;

        from.volume = Mathf.Lerp(1f, 0f, t);
        to.volume = Mathf.Lerp(0f, 1f, t);

        yield return null;
    }

    from.Stop();
}
```

## Stinger Events

### Concept
Short musical hits for events (victory, death, pickup)

```csharp
public void PlayStinger(AudioClip stinger)
{
    // Duck main music
    musicSource.volume = 0.3f;

    // Play stinger
    AudioSource.PlayClipAtPoint(stinger, Camera.main.transform.position);

    // Restore music volume
    StartCoroutine(RestoreMusicVolume(stinger.length));
}

IEnumerator RestoreMusicVolume(float delay)
{
    yield return new WaitForSeconds(delay);

    while (musicSource.volume < 1f)
    {
        musicSource.volume += Time.deltaTime * 2f;
        yield return null;
    }
}
```

## Best Practices
✅ Keep all stems tempo-synced
✅ Use transition markers (on beat)
✅ Subtle volume changes (avoid jarring)
✅ Test emotional impact
✅ Mix for clarity (EQ separation)

## Tools
- **FMOD**: Industry standard
- **Wwise**: AAA audio middleware
- **Unity**: Basic layering possible
