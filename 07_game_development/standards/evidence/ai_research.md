# Game AI Research & Techniques

## Behavior Trees

**Origin**: Halo 2 (Bungie, 2004)
**Popularization**: "Behavior Trees for AI in Games" - Isla, 2005 (GDC)

**Advantages**:
- Modular and reusable
- Visual representation
- Easy to debug
- Scalable complexity

**Industry Adoption**:
- Unreal Engine: Built-in Behavior Tree editor
- Unity: Third-party assets (Behavior Designer, NodeCanvas)
- CryEngine, Lumberyard: Native support

**Key Nodes**:
- **Sequence**: Execute until failure
- **Selector**: Execute until success
- **Parallel**: Execute simultaneously
- **Decorator**: Modify child behavior

**References**:
- Isla: "Handling Complexity in the Halo 2 AI" (GDC 2005)
- Champandard: "Behavior Trees for Next-Gen Game AI" (aiGameDev)

## Utility AI

**Concept**: Score-based decision making

**Formula**:
```
Action Score = Σ (Consideration₁ × Weight₁)
Best Action = argmax(Score)
```

**Advantages**:
- Handles complex decisions
- Smooth transitions
- Tunable via curves
- No explicit state transitions

**Drawbacks**:
- Requires careful tuning
- Can be opaque

**Games**:
- The Sims series
- F.E.A.R. (combined with GOAP)
- Civilization series

**References**:
- Mark & Dill: "Behavioral Mathematics for Game AI" (2010)
- Graham: "An Introduction to Utility Theory" (aiGameDev)

## Goal-Oriented Action Planning (GOAP)

**Origin**: F.E.A.R. (Monolith, 2005)

**Concept**: AI plans sequence of actions to satisfy goals

**Algorithm**: A* search through action space
- **State**: World conditions
- **Actions**: Change state (preconditions → effects)
- **Goal**: Target state

**Advantages**:
- Emergent behavior
- Flexible to level changes
- Handles dynamic environments

**Drawbacks**:
- Computational cost (planning)
- Requires well-defined actions/states

**Games**:
- F.E.A.R.
- Deus Ex: Human Revolution
- Shadow of Mordor (Nemesis System uses GOAP-like planning)

**References**:
- Orkin: "Three States and a Plan: The AI of F.E.A.R." (GDC 2006)
- Orkin: "Applying Goal-Oriented Action Planning to Games" (AI Game Programming Wisdom 2)

## Pathfinding: A* and Beyond

### A* Algorithm
**Invented**: Hart, Nilsson, Raphael, 1968

**Properties**:
- Optimal (finds shortest path)
- Complete (finds path if exists)
- Time complexity: O(b^d) worst case

**Optimizations**:
- **Hierarchical A***: Split into high/low level graphs
- **Jump Point Search**: Skip intermediate nodes (grid only)
- **Theta***: Any-angle pathfinding

### Navigation Meshes (NavMesh)
**Concept**: Polygon mesh defining walkable areas

**Algorithms**:
- **Funnel Algorithm**: Smooth path through portals
- **String Pulling**: Post-process to remove zigzags

**Industry Standard**:
- Unreal: Recast/Detour navigation
- Unity: NavMesh system
- Custom: Recast Navigation (open-source)

**References**:
- Tozour: "Building a Near-Optimal Navigation Mesh" (AI Game Programming Wisdom)
- Recast Navigation: https://github.com/recastnavigation/recastnavigation

### Dynamic Pathfinding

**Techniques**:
- **D* Lite**: Incremental A*, handles dynamic obstacles
- **Flow Fields**: Pre-compute direction field (RTS games)
- **Local Avoidance**: Reciprocal Velocity Obstacles (RVO)

**Games**:
- Supreme Commander: Flow fields for massive unit counts
- Starcraft 2: Hierarchical pathfinding + local avoidance

**References**:
- Koenig: "Fast Replanning for Navigation in Unknown Terrain" (D* Lite)
- Berg: "Reciprocal n-Body Collision Avoidance" (RVO)

## Machine Learning for Game AI

### Reinforcement Learning

**Concept**: Agent learns from rewards

**Algorithms**:
- **Q-Learning**: Value-based
- **Policy Gradient**: Direct policy optimization
- **PPO** (Proximal Policy Optimization): State-of-art

**Applications**:
- OpenAI Five: Dota 2 (2018)
- AlphaStar: Starcraft 2 (DeepMind, 2019)
- Unity ML-Agents: Training NPC behaviors

**Limitations**:
- Long training times
- Requires simulator
- Unpredictable behavior

**References**:
- Mnih: "Playing Atari with Deep Reinforcement Learning" (2013)
- OpenAI: "Dota 2 with Large Scale Deep Reinforcement Learning" (2019)

### Imitation Learning

**Concept**: Learn from human demonstrations

**Techniques**:
- Behavioral Cloning
- Inverse Reinforcement Learning

**Applications**:
- Forza Motorsport: Drivatars (learn from player)
- FIFA: Player behavior modeling

## Perception Systems

### Vision Cones

**Implementation**:
- Raycast from eyes
- Field of view check (dot product)
- Occlusion testing

### Sensing

**Types**:
- **Sight**: Vision cones, line-of-sight
- **Hearing**: Sound propagation, loudness
- **Touch**: Proximity sensors

**Optimization**:
- Update at lower frequency (10-20 Hz)
- Spatial partitioning for nearby agents
- Event-driven (trigger zones)

**References**:
- Champandard: "Understanding the Second Generation of Behavior Trees" (aiGameDev)

## Crowd Simulation

**Techniques**:
- **Boids**: Flocking behavior (Reynolds, 1987)
  - Separation, Alignment, Cohesion
- **Social Forces**: Helbing model (pedestrians)
- **Velocity Obstacles**: Collision avoidance

**Optimizations**:
- LOD for distant crowds
- Simplified collision for background agents

**Games**:
- Assassin's Creed: Large crowd systems
- Total War: Massive battle simulations

**References**:
- Reynolds: "Flocks, Herds, and Schools: A Distributed Behavioral Model" (1987)
- Berg: "Reciprocal Velocity Obstacles for Real-Time Multi-Agent Navigation" (2008)

## AI Debugging & Visualization

**Techniques**:
- **Debug Draw**: Gizmos for paths, vision, states
- **Logging**: Decision history
- **State Visualization**: Current BT/FSM state
- **Performance Profiling**: AI budget monitoring

**Tools**:
- Unreal: Gameplay Debugger (Apostrophe key)
- Unity: Gizmos, Custom inspectors
- Third-party: Debugging overlays

## Industry Best Practices

**From AAA Studios**:

**Guerrilla Games (Horizon Zero Dawn)**:
- Hybrid AI: BT + utility AI
- Machine learning for animation selection
- GDC Talk: "Creating a Tools Pipeline for Horizon Zero Dawn"

**Bioware (Mass Effect)**:
- Cover system integrated with AI
- Squad command system

**Monolith (F.E.A.R.)**:
- GOAP for emergent behavior
- Dynamic cover selection
- Communication system (AI calls out actions)

## References

### Books
- "Programming Game AI by Example" - Mat Buckland
- "Game AI Pro" series (1-3) - Steve Rabin
- "Behavioral Mathematics for Game AI" - Dave Mark
- "Artificial Intelligence for Games" - Millington & Funge

### Conferences
- **GDC AI Summit**: Annual game AI talks
- **AIIDE** (AI and Interactive Digital Entertainment)
- **IEEE CIG** (Computational Intelligence and Games)

### Online Resources
- AIGameDev.com: Alex Champandard's site
- GameAIPro.com: Open-access book series
- Unity ML-Agents: Reinforcement learning toolkit

### Key Papers
1. Isla: "Handling Complexity in the Halo 2 AI" (GDC 2005)
2. Orkin: "Three States and a Plan: The AI of F.E.A.R." (GDC 2006)
3. Reynolds: "Steering Behaviors For Autonomous Characters" (1999)
4. Mark: "Embracing the Dark Art of Mathematical Modeling in AI" (GDC 2013)

---

**Last Updated**: 2025-11-19
