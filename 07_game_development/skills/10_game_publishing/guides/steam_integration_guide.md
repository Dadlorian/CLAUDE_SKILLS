# Steam Integration Guide

## Steamworks SDK Setup

1. Register app at partner.steamgames.com
2. Download Steamworks SDK
3. For Unity: Use Steamworks.NET package

## Basic Integration

```csharp
using Steamworks;

public class SteamManager : MonoBehaviour
{
    void Start()
    {
        if (!SteamAPI.Init())
        {
            Debug.LogError("Steam API failed to initialize");
            return;
        }

        string playerName = SteamFriends.GetPersonaName();
        Debug.Log($"Logged in as: {playerName}");
    }

    void OnDestroy()
    {
        SteamAPI.Shutdown();
    }
}
```

## Achievements

```csharp
public void UnlockAchievement(string achievementID)
{
    SteamUserStats.SetAchievement(achievementID);
    SteamUserStats.StoreStats();
}
```

## Cloud Saves

```csharp
public void SaveToCloud(string filename, byte[] data)
{
    SteamRemoteStorage.FileWrite(filename, data, data.Length);
}

public byte[] LoadFromCloud(string filename)
{
    int size = SteamRemoteStorage.GetFileSize(filename);
    byte[] data = new byte[size];
    SteamRemoteStorage.FileRead(filename, data, size);
    return data;
}
```

## References
- Steamworks Documentation
- Steamworks.NET on GitHub
