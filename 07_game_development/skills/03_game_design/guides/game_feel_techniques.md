# Game Feel Techniques

## Definition
"Game feel" = tactile sensations and emotions from interaction

## Techniques

### 1. Input Response Time
- **Target**: < 100ms from input to visual feedback
- **Ideal**: < 50ms for competitive games

### 2. Animation
- **Squash & Stretch**: Exaggerate movement
- **Anticipation**: Wind-up before action
- **Follow-through**: Overshoot then settle

### 3. Camera Effects
```csharp
// Screen shake on impact
void ScreenShake(float intensity, float duration)
{
    StartCoroutine(ShakeCoroutine(intensity, duration));
}

IEnumerator ShakeCoroutine(float intensity, float duration)
{
    Vector3 originalPos = transform.position;
    float elapsed = 0f;

    while (elapsed < duration)
    {
        float x = Random.Range(-1f, 1f) * intensity;
        float y = Random.Range(-1f, 1f) * intensity;

        transform.position = originalPos + new Vector3(x, y, 0);
        elapsed += Time.deltaTime;
        yield return null;
    }

    transform.position = originalPos;
}
```

### 4. Particle Effects
- Spawn on: Jump, land, hit, collect
- Match action intensity
- Short lifetime (0.2-0.5s)

### 5. Sound Effects
- Layer multiple sounds
- Pitch variation (±10%)
- Spatial audio for directionality

### 6. Hit Stop / Freeze Frames
```csharp
void HitStop(float duration)
{
    Time.timeScale = 0;
    StartCoroutine(ResumeTime(duration));
}

IEnumerator ResumeTime(float delay)
{
    yield return new WaitForSecondsRealtime(delay);
    Time.timeScale = 1;
}
```

### 7. Controller Rumble
```csharp
Gamepad.current.SetMotorSpeeds(0.5f, 0.5f);
```

## "Juice" Checklist
✅ Screen shake on significant events
✅ Particle effects on actions
✅ Sound effects with variation
✅ Responsive animations (< 100ms)
✅ Visual feedback on button press
✅ Satisfying hit sounds
✅ Camera follow with smoothing

## References
- "Game Feel" - Steve Swink
- "Juice It or Lose It" - Martin Jonasson & Petri Purho (GDC)
- Vlambeer: nuclear throne game feel
