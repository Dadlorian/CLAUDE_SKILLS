# Network Optimization Reference

## Bandwidth Reduction

### Delta Compression
- Only send changed values
- Bit flags for what changed
- **Savings**: 50-80% bandwidth

### Quantization
```csharp
// Position: 3 floats (12 bytes) → 3 shorts (6 bytes)
short QuantizePosition(float value, float min, float max)
{
    float normalized = (value - min) / (max - min);
    return (short)(normalized * 65535);
}
```

### Dead Reckoning
- Predict movement client-side
- Only send corrections
- **Savings**: 60-90% for predictable movement

## Update Rate Optimization

### Variable Update Rates
- **Important objects**: 20-60 Hz
- **Distant objects**: 5-10 Hz
- **Static objects**: On change only

### Interest Management
- Only send nearby entities
- Area-based relevancy
- **Savings**: Scales with player count

## Packet Optimization

### Batching
- Combine multiple messages per packet
- Reduce header overhead

### Reliability Levels
- **Reliable Ordered**: Important state changes
- **Unreliable**: Position updates (can drop)
- **Unreliable Sequenced**: Latest state only

## Target Budgets
- **Per Client**: 50-200 Kbps
- **Mobile**: 30-100 Kbps
- **Packet Size**: 500-1200 bytes
