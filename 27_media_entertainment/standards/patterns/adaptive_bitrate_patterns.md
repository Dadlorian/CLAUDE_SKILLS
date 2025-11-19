# Adaptive Bitrate Streaming Patterns

## Pattern 1: Throughput-Based ABR

**Description**: Select bitrate based on measured network throughput

**Algorithm**:
```
1. Measure download speed for each segment
2. Calculate exponential weighted moving average (EWMA)
3. Select bitrate = 0.8 × measured_throughput
4. Adjust based on buffer level
```

**Pros**: Simple, responsive to network changes
**Cons**: Can oscillate in variable networks

## Pattern 2: Buffer-Based ABR

**Description**: Select bitrate based on playback buffer level

**Algorithm**:
```
if buffer < 10s:
    select lowest bitrate (safe mode)
elif buffer < 30s:
    maintain current bitrate
else:
    try next higher bitrate
```

**Pros**: Smooth playback, fewer rebuffers
**Cons**: Slower to adapt to improved bandwidth

## Pattern 3: Hybrid ABR (Netflix Pattern)

**Description**: Combine throughput + buffer + quality

**Algorithm**:
```
throughput_score = measured_throughput × 0.8
buffer_multiplier = min(1.2, buffer_level / 30)
quality_target = throughput_score × buffer_multiplier

select bitrate closest to quality_target
apply smoothing to prevent oscillation
```

**Pros**: Best quality with minimal rebuffering
**Cons**: More complex implementation

## Implementation Example

```javascript
class AdaptiveBitrateController {
  constructor() {
    this.throughput = null;
    this.bufferLevel = 0;
    this.currentBitrate = null;
  }

  selectBitrate(availableBitrates, segmentBytes, downloadTime, bufferLevel) {
    // Update throughput (EWMA)
    const instantThroughput = (segmentBytes * 8) / downloadTime;
    this.throughput = this.throughput 
      ? 0.8 * this.throughput + 0.2 * instantThroughput
      : instantThroughput;

    this.bufferLevel = bufferLevel;

    // Calculate safe throughput (80% of measured)
    const safeThroughput = this.throughput * 0.8;

    // Buffer-based adjustment
    let targetBitrate;
    if (bufferLevel < 10) {
      targetBitrate = safeThroughput * 0.7; // Conservative
    } else if (bufferLevel > 30) {
      targetBitrate = safeThroughput * 1.0; // Aggressive
    } else {
      targetBitrate = safeThroughput * 0.85; // Moderate
    }

    // Select best matching bitrate
    const selectedBitrate = availableBitrates
      .filter(br => br <= targetBitrate)
      .sort((a, b) => b - a)[0] || availableBitrates[0];

    // Apply smoothing
    if (this.shouldSwitch(selectedBitrate, bufferLevel)) {
      this.currentBitrate = selectedBitrate;
    }

    return this.currentBitrate;
  }

  shouldSwitch(newBitrate, bufferLevel) {
    // Don't switch if buffer is low
    if (bufferLevel < 5 && newBitrate > this.currentBitrate) {
      return false;
    }

    // Require 30% improvement for upshift
    if (newBitrate > this.currentBitrate) {
      return newBitrate / this.currentBitrate > 1.3;
    }

    // Always allow downshift
    return true;
  }
}
```

**Version**: 1.0
