# Level Design Guide

## Overview

Level design is the art of creating spaces that guide, challenge, and delight players. Great levels teach without tutorials, create memorable moments, and support varied playstyles. This guide covers principles and practical techniques for crafting engaging game spaces.

## Core Principles

### 1. The Three Cs

**Camera** - How the player sees the world
- Fixed camera (classic RE, strategy games)
- Follow camera (most 3D games)
- First-person (immersive, limited awareness)
- Top-down (tactics, strategy)

**Character** - How the player moves
- Movement speed and acceleration
- Jump height and distance
- Special abilities (dash, wall-run, grapple)

**Controls** - How the player interacts
- Button mapping and responsiveness
- Context-sensitive actions
- Input buffering

**Design levels FOR your specific 3Cs** - A level perfect for Mario wouldn't work for Dark Souls.

### 2. Flow and Pacing

**Energy Curve**: Alternate intensity throughout the level

```
Combat → Exploration → Puzzle → Boss Fight → Safe Zone → Repeat
High   → Low        → Medium → Very High  → Recovery  → ...
```

**Pacing Principles**:
- Never sustain max intensity >5 minutes (player fatigue)
- Recovery sections should have environmental storytelling or loot
- Major story beats after intense sequences (player is engaged)
- End on high note (final encounter memorable)

### 3. The Rule of Threes

Introduce concepts three times for mastery:
1. **Teach**: Safe environment, no pressure
2. **Test**: Challenging context requiring application
3. **Twist**: Combine with other mechanics or increase difficulty

**Example - Portal**:
1. Teach: Simple portal placement on flat walls
2. Test: Portal placement while moving/under time pressure
3. Twist: Portals + momentum + turrets

### 4. Visual Language and Readability

Players should instantly understand:
- **Where they can go** (accessible paths vs decoration)
- **What they can interact with** (consistent visual style for interactive objects)
- **Where threats are** (enemy silhouettes, color coding)
- **Where safety is** (lighting, openness, music cues)

**Techniques**:
- **Color coding**: Green = health, Red = danger, Blue = mana/shields
- **Lighting**: Bright areas draw attention, shadows hide secrets
- **Contrast**: Important elements should visually "pop"
- **Texture differentiation**: Smooth = safe, sharp = dangerous

## Level Architecture Patterns

### 1. Linear Levels

**Structure**: A → B → C → Goal

**Pros**:
- Tight pacing control
- Easy difficulty curve management
- Clear narrative progression
- Lower development cost

**Cons**:
- Limited player agency
- Low replayability
- Can feel restrictive

**Best For**: Story-driven games, action set pieces, tutorials

**Examples**: Half-Life 2, The Last of Us, Call of Duty campaigns

### 2. Hub-and-Spoke

**Structure**: Central hub with branching paths that return

```
     Level 2
       |
Hub ━━━┿━━━ Level 3
       |
     Level 1
```

**Pros**:
- Player choice in order
- Familiar central space (orientation)
- Controlled complexity
- Easy to gate content

**Cons**:
- Can feel fragmented
- Backtracking through hub
- Less environmental variety

**Best For**: RPGs, action-adventures, mission-based games

**Examples**: Dark Souls (Firelink Shrine), Mario 64 (Peach's Castle), Destiny (Tower)

### 3. Open World

**Structure**: Fully interconnected space with minimal loading

**Pros**:
- Maximum player freedom
- Emergent gameplay
- High replayability
- Exploration rewards

**Cons**:
- Difficult pacing control
- Can lack focus
- High development cost
- Easy to get lost

**Best For**: Sandbox games, exploration-focused titles

**Examples**: Breath of the Wild, Skyrim, Red Dead Redemption 2

### 4. Metroidvania

**Structure**: Interconnected with ability-gated progression

**Pros**:
- Rewarding exploration
- Meaningful progression
- High replayability
- Interconnected world building

**Cons**:
- Complex to design
- Can be confusing
- Requires excellent map systems

**Best For**: Exploration platformers, action-adventures

**Examples**: Hollow Knight, Metroid Dread, Symphony of the Night

## Design Techniques

### Composition and Framing

**Leading Lines**: Use geometry to guide player attention
- Hallways, roads, fences
- Light shafts, particle trails
- Aligned architectural elements

**Rule of Thirds**: Place important elements at intersection points
```
┌─────┬─────┬─────┐
│     │     │     │
├─────X─────X─────┤  ← Place objectives at X
│     │     │     │
├─────X─────X─────┤
│     │     │     │
└─────┴─────┴─────┘
```

**Vistas**: Reward players with breathtaking views
- After difficult sections
- At high points
- When entering new areas
- Shows distant goals (creates anticipation)

### Teaching Through Design

**Environmental Tutorialization**: Let the space teach mechanics

**Example - Teaching "Look Up"**:
```
Step 1: Ceiling collapse blocks forward path (forces looking up)
Step 2: Objective visible above (now they know to look up)
Step 3: Enemies attack from above (learned behavior applied)
```

**Safe Practice Spaces**:
- Low-stakes areas to experiment
- No enemies or timers
- Optional challenges that hint at later requirements
- Health/ammo nearby to encourage trying mechanics

### Landmarks and Wayfinding

**Verticality and Orientation**:
- Tall structures visible from distance (navigation aids)
- Distinct visual themes per area (instant recognition)
- Skybox changes signal area transitions
- Audio cues (music, ambient sound) aid orientation

**Breadcrumbing**:
- String of small rewards leading to larger goal
- Ammo/health pickups showing the path
- Environmental clues (footprints, blood trails)
- Distant lights or sounds

**The Invisible Hand**:
Players should FEEL like they're choosing the path, even when guided:
- Make desired path slightly brighter
- Place enemies in undesired directions (indirect blocking)
- Use attractive landmarks in desired direction
- Ensure "wrong" paths dead-end quickly with small reward

### Secrets and Discovery

**Types of Secrets**:
1. **Obvious Hidden** (90% find): Visual hint obvious on inspection
2. **Obscure Hidden** (40% find): Requires careful observation
3. **Expert Hidden** (10% find): Requires specific knowledge or ability

**Reward Tiers**:
- **Obvious**: Minor rewards (health, ammo)
- **Obscure**: Significant rewards (upgrades, collectibles)
- **Expert**: Major rewards or Easter eggs (unique items, lore)

**Telegraphing Secrets**:
- Different wall texture (breakable wall)
- Suspicious geometry (extra space implies hidden room)
- Audio cues (different sound when walking over secret)
- Environmental clues (cracks, vines, discoloration)

## Specific Level Types

### Combat Arenas

**Design Goals**:
- Clear enemy entry points
- Cover variety (high, low, destructible)
- Flanking routes
- Environmental hazards as options
- Health/ammo at edges (risk/reward)

**Layout Patterns**:
```
Figure-8: Creates rotation and flow
    ┌───┐
  ╱       ╲
 │    X    │  ← Central objective
  ╲       ╱
    └───┘

Triangle: 3 points of interest
      △
     ╱ ╲
    ╱   ╲
   △─────△

Multi-level: Verticality creates dynamics
  [High Ground]
       │
  [Mid Level]
       │
  [Low Ground]
```

**Encounter Design**:
1. **Initial Contact**: Players engage from cover
2. **Escalation**: Reinforcements or tougher enemies
3. **Twist**: Environmental change or special enemy
4. **Resolution**: Last enemies with low threat

### Puzzle Rooms

**Core Design**:
- Clear goal (exit door, pressure plate, etc.)
- Visible elements (no hidden solutions)
- Multiple approaches OR clear intended solution
- Undo mechanisms (don't lock players out of solutions)

**Difficulty Scaling**:
- **Easy**: 1 mechanic, 2-3 steps
- **Medium**: 2 mechanics combined, 4-5 steps
- **Hard**: 3+ mechanics, multi-stage, 6+ steps

**Feedback Systems**:
- Visual: Parts of puzzle light up when correct
- Audio: Confirmatory sounds for correct actions
- Progress indicators: "2/3 switches activated"

### Stealth Sections

**Essential Elements**:
- **Clear sightlines**: Player can see enemy patrol routes
- **Cover variety**: Hiding spots distributed evenly
- **Distraction tools**: Ways to manipulate enemy position
- **Failure recovery**: Combat is possible but harder (not instant death)

**Enemy Patrol Design**:
```
Good Patrol:
- Predictable routes
- Clear gaps in coverage
- Overlapping patrols create timing challenge
- Facing direction clear from silhouette

Bad Patrol:
- Random movement
- No gaps (impossible to pass)
- Unfair sightlines (seeing through walls)
```

### Boss Arenas

**Structure**:
1. **Opening**: Grand entrance, size established
2. **Phase 1**: Learn boss patterns (30-40% health)
3. **Phase 2**: New attacks, increased speed (30-40% health)
4. **Phase 3**: Desperation moves, environmental changes (final 30%)

**Arena Features**:
- Size: Large enough to dodge but not so big you lose boss
- Healing items: At edges (risky to retrieve mid-fight)
- Cover: Minimal (encourages learning patterns, not hiding)
- Environmental hazards: Optional bonus damage opportunities
- Verticality: Only if boss has vertical attacks

**Fairness Principles**:
- Telegraphed attacks (wind-up animations, audio cues)
- Dodge windows (reaction time <500ms for most players)
- Checkpoint before arena (no long walk back)
- Visible health bar (players can track progress)

## Environmental Storytelling

### Show, Don't Tell

**Implicit Narrative**:
- Skeleton with weapon = died fighting
- Broken barricade = defenses failed
- Empty beds with personal items = hasty evacuation
- Graffiti and notes = resident perspectives

**Lighting as Mood**:
- Warm lighting = safe, welcoming
- Cool lighting = danger, alien
- Flickering lights = unstable, failing systems
- Darkness = unknown threats

### World Building Through Space

**Environmental Consistency**:
- If area is a hospital, needs: beds, medical equipment, signs, supplies
- If area is abandoned, needs: dust, decay, scattered items, blocked paths
- If area is lived-in, needs: personal effects, variety, organized chaos

**Scale and Realism**:
- Doorways should fit character + margin
- Stairs should have realistic rise and run
- Rooms should be proportional to function
- Impossible spaces break immersion (unless intentional)

## Technical Considerations

### Performance Optimization

**Occlusion and LOD**:
- Use occluders to hide unrendered geometry
- Level-of-detail models for distant objects
- Draw call batching for repeated assets
- Frustum culling for off-screen objects

**Streaming and Loading**:
- Load zones hidden by corridors or doors
- Elevators as disguised loading screens
- Streaming radius around player position
- Pre-load adjacent areas

### Collision and Navmesh

**Player Collision**:
- Capsule collision prevents catching on geometry
- Smooth collision edges (avoid 90° corners)
- Invisible collision to simplify complex shapes
- Stairs as ramps for smooth movement

**AI Navmesh**:
- Cover points marked for AI
- Jump/climb points explicitly defined
- Pathing lanes to prevent clustering
- Off-mesh links for special movement

### Lighting Strategy

**Three-Point Lighting** (for important areas):
1. **Key Light**: Primary light source (sun, lamp)
2. **Fill Light**: Softer light to reduce harsh shadows
3. **Rim Light**: Separates subject from background

**Performance**:
- Baked lighting for static geometry
- Dynamic lights reserved for important elements
- Light probes for dynamic object lighting
- Shadow distance limits

## Playtesting and Iteration

### Metrics to Track

**Movement Heatmaps**:
- Where do players go?
- Where do they get stuck?
- Which paths are ignored?

**Death Locations**:
- Unfair difficulty spikes?
- Unclear hazards?
- Poor telegraphing?

**Completion Times**:
- Faster than expected = too easy or sequence break
- Slower than expected = confusing or too hard

### Observation Techniques

**Silent Observation**:
- Don't help or guide players
- Note when they hesitate (confusion point)
- Note when they backtrack (wrong path taken)
- Note their facial expressions (frustration, joy)

**Think-Aloud Protocol**:
- Ask players to vocalize their thoughts
- Reveals decision-making process
- Identifies unclear objectives
- Shows emotional responses

**Post-Play Interviews**:
- "What was your favorite moment?"
- "Where did you get frustrated?"
- "Did you understand how to [mechanic]?"
- "Would you play this level again?"

### Common Issues and Solutions

| Problem | Symptom | Solution |
|---------|---------|----------|
| Players get lost | Excessive backtracking | Add landmarks, lighting cues, breadcrumbs |
| Players skip intended path | Sequence breaking | Block shortcuts, incentivize intended path |
| Players miss objective | Wandering without direction | Increase visibility, add UI marker, improve signposting |
| Section feels too long | Frustration, speedrunning | Add checkpoint, reduce enemy count, shorten path |
| Section feels too short | Underwhelming payoff | Add encounter, expand space, increase challenge |
| Difficulty spike | Deaths cluster at one location | Add health pickup, reduce enemy count, improve telegraphing |

## Advanced Techniques

### Negative Space

**Definition**: Empty space that gives meaning to filled space.

- Combat arenas need space to dodge
- Puzzle rooms need space to think
- Platforming needs space to see next platform
- Don't fill every square meter with detail

### Rhythm and Tempo

**Visual Rhythm**:
- Repeat architectural elements to create pattern
- Break pattern to draw attention to important elements

**Gameplay Tempo**:
- Fast sections: narrow corridors, close enemies, tight timing
- Slow sections: open spaces, distant enemies, exploration

### Emergent Design

**Systems-Driven Spaces**:
- Place tools (explosives, physics objects)
- Create challenges (enemies, obstacles)
- Let players solve creatively

**Example**:
- Explosive barrels + high ground + enemies below = Player can shoot barrel OR push it off ledge

### The Ken Levine Method

1. **Establish Rules**: What can the player do here?
2. **Set Up Expectation**: Show intended interaction
3. **Subvert Expectation**: Twist the rule in unexpected way
4. **Payoff**: Reward clever thinking

**Example - BioShock**:
1. Rule: Water conducts electricity
2. Expectation: Enemies in water can be shocked
3. Subversion: Player standing in water gets shocked too
4. Payoff: Player must think about positioning

## Level Design Workflow

### Pre-Production

1. **Define Goals**: What should this level accomplish?
   - Story beats
   - Mechanics introduced
   - Pacing role in overall game

2. **Paper Design**: Sketch top-down layout
   - Major paths
   - Key encounters
   - Checkpoints and saves

3. **Reference Gathering**: Collect visual inspiration
   - Architecture styles
   - Lighting moods
   - Color palettes

### Production

1. **Blockout/Graybox**: Basic geometry, no art
   - Test flow and pacing
   - Verify metrics (jump distances, sightlines)
   - Playtest for fun

2. **First Pass Art**: Basic materials and lighting
   - Establish visual hierarchy
   - Test readability
   - Identify performance issues

3. **Gameplay Implementation**: Add enemies, puzzles, scripted events
   - Playtest each encounter
   - Balance difficulty
   - Ensure variety

4. **Polish Pass**: Final art, lighting, effects
   - Particle effects
   - Ambient audio
   - Detail props

### Post-Production

1. **Optimization**: Hit performance targets
2. **Bug Fixing**: Resolve collision, AI, scripting issues
3. **Final Playtesting**: Fresh eyes on complete level
4. **Iteration**: Small tweaks based on final feedback

## Case Studies

### Case Study 1: Portal - Test Chamber 17

**Design Goal**: Teach momentum-based portal puzzles

**Structure**:
1. High platform with button
2. Deep pit with angled surface
3. Exit platform at medium height

**Teaching**:
1. Player presses button, sees exit open but too high to reach
2. Pit with angled surface suggests "falling"
3. Player must: fall through portal, gain speed, exit portal with upward momentum
4. First true "thinking with portals" moment

**Why It Works**:
- All elements visible from start
- No time pressure
- Failure is safe (respawn)
- "Aha!" moment is earned

### Case Study 2: Dark Souls - Undead Burg

**Design Goal**: Teach caution and observation

**Structure**: Linear path with branching shortcuts

**Teaching**:
1. Narrow bridge with single enemy (spacing matters)
2. Tower with ambush (always check corners)
3. Bonfire behind illusory wall (secrets exist)
4. Dragon on bridge (some threats can't be fought yet)

**Why It Works**:
- Each lesson builds on previous
- Shortcuts reward exploration
- Clear checkpoints after difficult sections
- Feels dangerous but fair

### Case Study 3: Half-Life 2 - Ravenholm

**Design Goal**: Introduce Gravity Gun as primary weapon

**Structure**: Dark, claustrophobic town with physics objects everywhere

**Teaching**:
1. Ammo scarce (encourages Gravity Gun)
2. Saw blades and explosive barrels everywhere
3. Enemies vulnerable to physics damage
4. Set pieces showcase creative kills

**Why It Works**:
- Context forces using new tool
- Immediate satisfying feedback (sawblade bisection)
- Dark atmosphere creates tension
- Memorable setpieces (spinning blade trap)

## Conclusion

Great level design is invisible - players feel guided without noticing the design. Levels should:

1. **Teach clearly** without explicit tutorials
2. **Challenge fairly** with balanced difficulty
3. **Pace deliberately** with intensity variation
4. **Reward exploration** with secrets and lore
5. **Support playstyles** with multiple approaches

The best levels are built through iteration. Playtest early, playtest often, and don't be precious about cutting or changing sections that don't work.

Key takeaways:
- Design for your specific game's mechanics (3Cs)
- Use environmental storytelling over exposition
- Create clear visual language and readability
- Balance player freedom with guided experiences
- Test with fresh players, not just your team

Level design is where all disciplines intersect - art, programming, sound, and narrative. Master it, and you create the spaces players remember long after finishing the game.
