# Implementing Achievements Guide

## Steam Achievements

### Setup (Steamworks)
1. Steamworks Partner → Your App → Stats & Achievements
2. Create achievement (ID, name, description, icon)

### Implementation
```csharp
using Steamworks;

public class AchievementManager : MonoBehaviour
{
    void Start()
    {
        if (!SteamManager.Initialized)
            return;

        // Check if already unlocked
        bool unlocked;
        SteamUserStats.GetAchievement("ACH_FIRST_KILL", out unlocked);

        if (unlocked)
            Debug.Log("Already unlocked!");
    }

    public void UnlockAchievement(string achievementID)
    {
        SteamUserStats.SetAchievement(achievementID);
        SteamUserStats.StoreStats(); // Upload to Steam
    }

    public void ClearAchievement(string achievementID)
    {
        SteamUserStats.ClearAchievement(achievementID);
        SteamUserStats.StoreStats();
    }

    // Progress achievements (e.g., kill 100 enemies)
    public void SetProgress(string statID, int value)
    {
        SteamUserStats.SetStat(statID, value);
        SteamUserStats.StoreStats();
    }
}

// Usage
public class GameManager : MonoBehaviour
{
    private AchievementManager achievements;

    void OnEnemyKilled()
    {
        achievements.UnlockAchievement("ACH_FIRST_KILL");
    }
}
```

## Xbox Achievements

### Setup
```cpp
// Xbox Game Development Kit
auto asyncBlock = std::make_unique<XAsyncBlock>();
asyncBlock->queue = queue;
asyncBlock->context = this;
asyncBlock->callback = [](XAsyncBlock* asyncBlock)
{
    // Achievement unlocked
};

XblAchievementsUpdateAchievementAsync(
    xboxLiveContext,
    xboxUserId,
    "AchievementId",
    100, // Progress percentage
    asyncBlock.get()
);
```

## PlayStation Trophies

### Setup
```cpp
// PlayStation SDK
sceNpTrophyUnlockTrophy(
    context,
    handle,
    trophyId,
    &platinumId
);
```

## Google Play Achievements

### Unity
```csharp
using GooglePlayGames;

PlayGamesPlatform.Activate();

// Unlock
Social.ReportProgress("ACHIEVEMENT_ID", 100.0, (bool success) =>
{
    if (success)
        Debug.Log("Achievement unlocked!");
});

// Incremental
PlayGamesPlatform.Instance.IncrementAchievement("ACHIEVEMENT_ID", 1, null);

// Show UI
Social.ShowAchievementsUI();
```

## iOS Game Center

### Unity
```csharp
using UnityEngine.SocialPlatforms;
using UnityEngine.SocialPlatforms.GameCenter;

Social.localUser.Authenticate((bool success) =>
{
    if (success)
    {
        Social.ReportProgress("achievement_id", 100.0, (bool result) =>
        {
            Debug.Log("Achievement unlocked!");
        });
    }
});

// Show achievements
Social.ShowAchievementsUI();
```

## Achievement Design

### Types
1. **Story**: Complete chapter, beat boss
2. **Skill**: Speedrun, no damage, perfect score
3. **Collection**: Find all items, max level
4. **Challenge**: Self-imposed difficulty
5. **Easter Egg**: Hidden, secret

### Best Practices
✅ Visible progress (0-100%)
✅ Clear requirements
✅ Achievable but challenging
✅ Diverse (casual + hardcore)
✅ No missable achievements (frustrating)
✅ Instant feedback (toast notification)

### Metrics
- **Completion rate**: % of players unlocking
- **Time to unlock**: How long it takes
- **Rarity**: Makes players feel special

## Common Pitfalls
❌ Too many achievements (overwhelming)
❌ Grindy achievements (100,000 kills)
❌ Missable achievements (one chance only)
❌ Broken/unobtainable achievements
❌ Spoiler achievements (reveal plot)
