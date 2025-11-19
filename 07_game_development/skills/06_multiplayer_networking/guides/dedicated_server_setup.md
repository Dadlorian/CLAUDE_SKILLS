# Dedicated Server Setup Guide

## Unity + Mirror

### Headless Build
```csharp
// Build Settings
- Platform: Linux
- Server Build: Checked
- Target: Headless

// Conditional compilation
#if UNITY_SERVER
    // Server-only code
#else
    // Client code
#endif
```

### Running Server
```bash
./MyGame.x86_64 -batchmode -nographics -logFile server.log
```

### Network Manager
```csharp
public class MyNetworkManager : NetworkManager
{
    public override void Start()
    {
        base.Start();

        if (IsHeadless())
        {
            StartServer();
        }
    }

    bool IsHeadless()
    {
        return SystemInfo.graphicsDeviceType == GraphicsDeviceType.Null;
    }
}
```

## Unreal Dedicated Server

### Build Configuration
- Project Settings → Packaging
- Build Configuration: Shipping
- Cook only maps you need

### Command Line
```bash
UE4Server.exe MyProject -log -port=7777
```

### Code Separation
```cpp
if (GetNetMode() == NM_DedicatedServer)
{
    // Server-only logic
}
else
{
    // Client logic (rendering, input, etc.)
}
```

## Hosting Options

### Cloud Providers
- **AWS GameLift**: Auto-scaling, matchmaking
- **Google Cloud**: Compute Engine + Agones (Kubernetes)
- **Azure PlayFab**: Multiplayer services
- **Digital Ocean**: Simple droplets

### Bare Metal
- **OVH**: Dedicated servers
- **Hetzner**: Affordable dedicated servers

## Server Configuration

### Tick Rate
```
20 Hz: MMO, casual games
30 Hz: Standard multiplayer
60 Hz: Competitive FPS
120 Hz: Esports
```

### Performance
- Headless (no rendering): 90% less CPU
- Multithreading for multiple game instances
- Monitor: CPU, RAM, network bandwidth

### Security
- ✅ Input validation (prevent exploits)
- ✅ Rate limiting (prevent DDoS)
- ✅ Encryption (TLS/SSL)
- ✅ Anti-cheat integration

## Matchmaking
- **Skill-based**: Rank/MMR matching
- **Region-based**: Low latency
- **Party support**: Friends play together
- **Backfill**: Join in-progress matches

## Costs
**Example** (100 CCU):
- 5 servers × $0.10/hr = $0.50/hr
- $360/month for 24/7 operation
- Add bandwidth costs
