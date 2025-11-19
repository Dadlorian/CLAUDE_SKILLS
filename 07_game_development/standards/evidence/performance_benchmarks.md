# Game Performance Benchmarks - Industry Standards

## Frame Rate Targets by Platform

### Console (PlayStation 5, Xbox Series X)
- **Target**: 60 FPS (16.67ms per frame)
- **Acceptable**: 30 FPS locked (33.33ms) for visually complex games
- **Premium**: 120 FPS (8.33ms) for competitive games

**References**:
- Naughty Dog: "The Last of Us Part II" (30fps locked, native 4K)
- Insomniac Games: "Spider-Man: Miles Morales" (60fps performance mode)
- id Software: "Doom Eternal" (120fps on Series X)

### PC
- **Minimum**: 30 FPS (33.33ms)
- **Target**: 60 FPS (16.67ms)
- **Competitive**: 144+ FPS (6.94ms or less)
- **Scalable**: Must support wide range of hardware

**References**:
- Valve: CS:GO targets 300+ FPS for competitive play
- Epic: Fortnite scalable from 30fps (low-end) to 240fps (competitive)

### Mobile (iOS/Android)
- **Low-End**: 30 FPS (33.33ms)
- **Mid-Range**: 60 FPS (16.67ms)
- **High-End**: 120 FPS (8.33ms) on supported devices

**Battery Targets**:
- **< 15% drain per hour** for casual games
- **< 25% drain per hour** for intensive games

**References**:
- Unity "Optimize for Mobile Performance" guidelines
- Apple "Optimizing Performance" (WWDC)

### VR
- **Minimum**: 72 FPS (13.89ms) - Quest 2
- **Target**: 90 FPS (11.11ms) - PC VR, Quest 3
- **Premium**: 120 FPS (8.33ms) - PSVR2, Index

**Critical**: VR requires locked framerate to prevent motion sickness

**References**:
- Oculus Developer Center: Performance Guidelines
- Valve Index: Framerate targets

---

## Frame Time Budgets (60 FPS = 16.67ms)

### AAA Console/PC Game
- **Game Logic**: 8-10ms (48-60%)
- **Rendering**: 4-6ms (24-36%)
- **Physics**: 1-2ms (6-12%)
- **Audio**: 0.5-1ms (3-6%)
- **Other/Margin**: 1-2ms (6-12%)

**Source**: GDC talks from Naughty Dog, Insomniac, Epic

### Mobile Game
- **Game Logic**: 6-8ms (36-48%)
- **Rendering**: 6-8ms (36-48%)
- **Physics**: 0.5-1ms (3-6%)
- **Audio**: 0.5-1ms (3-6%)
- **Other/Margin**: 1-2ms (6-12%)

**Source**: Unity "Mobile Optimization Guide"

### Competitive Multiplayer (120 FPS = 8.33ms)
- **Game Logic**: 3-4ms
- **Rendering**: 3-4ms
- **Physics**: 0.5ms
- **Networking**: 0.5ms
- **Other/Margin**: 0.5-1ms

**Source**: Riot Games "League of Legends Performance"

---

## Rendering Budgets

### Draw Calls
| Platform | Target | Maximum |
|----------|--------|---------|
| Mobile (Low) | < 300 | < 500 |
| Mobile (High) | < 500 | < 1000 |
| Console | < 1500 | < 3000 |
| PC (Mid) | < 2000 | < 5000 |
| PC (High) | < 3000 | < 10000 |

**References**:
- Unity: "Optimizing Graphics Rendering in Unity Games"
- Epic: Unreal Engine Performance Guidelines

### Triangles (On-Screen, per frame)
| Platform | Target | Maximum |
|----------|--------|---------|
| Mobile (Low) | 50k | 100k |
| Mobile (High) | 100k | 500k |
| Console | 1M | 5M |
| PC | 1M | 10M+ |

**Note**: With Nanite (UE5), triangle counts are virtualized

### Texture Memory
| Platform | Budget |
|----------|--------|
| Mobile (Low) | 200-500 MB |
| Mobile (High) | 500 MB - 1 GB |
| Console | 2-4 GB |
| PC (Low) | 1-2 GB |
| PC (Mid) | 2-4 GB |
| PC (High) | 4-8 GB |

**References**:
- Arm: "Mali GPU Best Practices"
- NVIDIA: "GPU Memory Best Practices"

---

## CPU Benchmarks

### Physics (PhysX, Havok)
- **Rigidbodies (Active)**: < 500 for 60fps
- **Collision Checks/Frame**: < 10,000
- **Ragdolls (Active)**: < 20
- **Physics Timestep**: 1/60s (0.0166s) or 1/120s

**Source**: NVIDIA PhysX documentation

### AI
- **Agents w/ Pathfinding**: < 100 for 60fps
- **Behavior Tree Ticks**: 10-20 per second per agent
- **NavMesh Size**: < 5MB for fast queries

**Source**: Unreal Engine AI Performance Guide

### Animation
- **Skinned Meshes**: < 50 on screen
- **Bones per Character**: < 100
- **Animation Layers**: < 5 active simultaneously

**Source**: Unity Animation Performance

---

## Network Performance

### Latency Targets
- **< 50ms**: Excellent (feels local)
- **50-100ms**: Good (playable for most genres)
- **100-150ms**: Acceptable (noticeable but okay)
- **> 150ms**: Poor (frustrating experience)

### Tick Rates
| Genre | Client Tick Rate | Server Tick Rate |
|-------|------------------|------------------|
| FPS (Competitive) | 60-128 Hz | 60-128 Hz |
| FPS (Casual) | 30-60 Hz | 30-60 Hz |
| MOBA | 30 Hz | 30 Hz |
| Battle Royale | 20-60 Hz | 20-60 Hz |
| MMO | 10-20 Hz | 10-20 Hz |

**Sources**:
- Valve: CS:GO 128-tick servers
- Epic: Fortnite 30Hz servers (increased to 60Hz in endgame)
- Riot: League of Legends 30Hz

### Bandwidth
- **Per Client Target**: 50-200 Kbps
- **Maximum Burst**: 500 Kbps
- **Mobile Target**: 30-100 Kbps

**Source**: Gaffer on Games, Unreal Replication Graph

---

## Memory Benchmarks

### Total Memory Budget
| Platform | Available RAM | Typical Game Budget |
|----------|---------------|---------------------|
| Mobile (Low) | 2 GB | 800 MB - 1 GB |
| Mobile (High) | 6-12 GB | 2-4 GB |
| PS5/Xbox Series X | 16 GB | 10-12 GB |
| PC (Low) | 8 GB | 4-6 GB |
| PC (Mid) | 16 GB | 8-12 GB |
| PC (High) | 32 GB+ | 16+ GB |

### Asset Breakdown
**Mobile Game** (1 GB total):
- Textures: 400 MB (40%)
- Meshes: 150 MB (15%)
- Audio: 200 MB (20%)
- Code/Scripts: 100 MB (10%)
- Other: 150 MB (15%)

**Console Game** (10 GB total):
- Textures: 4 GB (40%)
- Meshes: 2 GB (20%)
- Audio: 1.5 GB (15%)
- Animation: 1 GB (10%)
- Code: 500 MB (5%)
- Other: 1 GB (10%)

**Source**: Industry best practices (GDC talks)

---

## Load Time Targets

### Initial Load
- **Mobile**: < 5 seconds
- **Console**: < 15 seconds
- **PC**: < 20 seconds

### Level Streaming
- **Seamless (open world)**: 0 seconds (preload)
- **Behind loading screen**: < 5 seconds
- **Fast travel**: < 10 seconds

**References**:
- Insomniac: Spider-Man fast travel (< 1 second with SSD)
- Epic: Fortnite level streaming

---

## Audio Performance

### Voice Count
| Platform | Simultaneous Voices |
|----------|---------------------|
| Mobile | < 32 |
| Console/PC | < 64-128 |

### Memory
- **Mobile**: < 50 MB
- **Console/PC**: < 200 MB

### CPU
- **Target**: < 1ms per frame
- **Middleware (FMOD/Wwise)**: Handles optimization

**Source**: FMOD/Wwise performance guidelines

---

## Battery Consumption (Mobile)

### Targets
- **Casual Game**: < 15% drain per hour
- **Mid-Core**: < 20% drain per hour
- **High-End/Competitive**: < 30% drain per hour

### Thermal Targets
- **Sustained**: Device temp < 42°C
- **Peak**: Device temp < 45°C (brief)

**Source**: Apple "Energy Efficiency Guide for iOS Apps"

---

## References

### Industry Sources
- **GDC Vault**: Performance talks from AAA studios
- **Unity Blog**: "Optimizing Mobile Games"
- **Unreal Documentation**: Performance Guidelines
- **NVIDIA Developer**: GPU optimization guides
- **Arm Developer**: Mobile GPU guides

### Specific Studios
- **Naughty Dog**: Engine architecture (GDC talks)
- **Insomniac Games**: 60fps techniques
- **id Software**: DOOM performance (GDC 2016)
- **Epic Games**: Fortnite optimization
- **Riot Games**: League of Legends performance

### Academic
- "Real-Time Rendering" (4th Ed) - Performance chapters
- "Game Engine Architecture" - Jason Gregory
- SIGGRAPH papers on real-time graphics

---

**Last Updated**: 2025-11-19
**Based On**: Current-gen consoles (PS5, Xbox Series X), Unity 2022 LTS, Unreal Engine 5.3
