# Balancing Game Economy Guide

## Currency Flow

### Sources (Faucets)
- Quest rewards
- Enemy drops
- Daily bonuses
- Achievements

### Sinks (Drains)
- Item purchases
- Upgrades
- Repairs
- Fast-travel

**Balance**: Faucets ≈ Sinks over time

## Pricing Models

### Exponential Scaling
```
Level 1: 100 gold
Level 2: 200 gold
Level 3: 400 gold
Formula: Cost = BaseCost × 2^(Level-1)
```

### Linear Scaling
```
Level 1: 100 gold
Level 2: 150 gold
Level 3: 200 gold
Formula: Cost = BaseCost + (Increment × Level)
```

## Progression Pacing

### Early Game (Hours 0-5)
- Fast progression
- Frequent rewards
- Low complexity

### Mid Game (Hours 5-20)
- Slower progression
- Strategic choices
- Increased complexity

### Late Game (Hours 20+)
- Very slow progression
- Optimization focus
- Max complexity

## Testing Economy

### Metrics to Track
- Currency earned per hour
- Currency spent per hour
- Player wealth over time
- Time to unlock items

### Red Flags
- Negative currency flow
- Excessive grinding required
- Pay-to-win imbalance
- Runaway inflation

## References
- "Game Balance" - Ian Schreiber
- GDC: "Balancing Free-to-Play Games"
