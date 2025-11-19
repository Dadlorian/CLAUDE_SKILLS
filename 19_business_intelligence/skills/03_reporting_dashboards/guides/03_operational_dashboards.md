# Operational Dashboards - Complete Implementation Guide

## Overview

Operational dashboards enable real-time or near-real-time monitoring of business operations. They answer: "Is everything running smoothly? What needs immediate attention?"

**Key Characteristics**:
- Real-time or frequently updated (minutes/hours)
- Alert-driven design
- 10-15 metrics
- Exception highlighting
- Action-oriented
- Used by managers and frontline staff

---

## Core Principles

### 1. Exception-First Design

**Normal operations → Gray/subtle**
**Exceptions → Bright/prominent**

Users should instantly see what needs attention.

### 2. Status Indicators

Use traffic light metaphor (carefully):
- ✓ Green: Operating within normal parameters
- ⚠ Orange: Warning - approaching thresholds
- 🔴 Red: Critical - immediate action required

**Accessibility**: Always include icon + text, not just color.

### 3. Actionable Information

Every alert should answer:
- What is the problem?
- How severe?
- What action to take?

---

## Dashboard Structure

### Layout Pattern: The Waterfall

```
┌─────────────────────────────────────────┐
│ 🔴 CRITICAL ALERTS (if any)             │ ← Top priority
├─────────────────────────────────────────┤
│ HIGH-PRIORITY METRICS                   │ ← Key indicators
├─────────────────────────────────────────┤
│ MONITORING CHARTS                       │ ← Trends/patterns
├─────────────────────────────────────────┤
│ DETAILED BREAKDOWNS                     │ ← Drill-down
└─────────────────────────────────────────┘
```

### Example: Operations Center Dashboard

```
┌────────────────────────────────────────────┐
│ Operations Dashboard        🔴 2 ALERTS    │
│                             [⟳ Live]       │
├────────────────────────────────────────────┤
│                                            │
│ ⚠ ACTIVE ALERTS                            │
│ ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓ │
│ ┃ 🔴 Server CPU >90% (Last 10 min)      ┃ │
│ ┃ Action: Auto-scaling triggered        ┃ │
│ ┃ [View Details] [Acknowledge]          ┃ │
│ ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ │
│ ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓ │
│ ┃ 🟠 API response time >500ms           ┃ │
│ ┃ Action: Monitor, may need optimization ┃│
│ ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ │
│                                            │
│ STATUS OVERVIEW                            │
│ ┌─────────┬─────────┬─────────┬─────────┐│
│ │ Uptime  │Response │Requests │ Errors  ││
│ │ ✓       │ ⚠       │         │ ✓       ││
│ │ 99.98%  │ 543ms   │ 12.5K/s │ 0.3%    ││
│ │ Target: │ Target: │ Current │ Target: ││
│ │ >99.9%  │ <500ms  │ 15K/s   │ <1.0%   ││
│ └─────────┴─────────┴─────────┴─────────┘│
│                                            │
│ REAL-TIME MONITORING                       │
│ ┌──────────────────┬──────────────────┐  │
│ │ Response Time    │ Error Rate       │  │
│ │ (Last Hour)      │ (Last Hour)      │  │
│ │ [Live chart]     │ [Live chart]     │  │
│ └──────────────────┴──────────────────┘  │
│                                            │
│ ┌──────────────────┬──────────────────┐  │
│ │ Traffic by       │ Top Errors       │  │
│ │ Endpoint         │                  │  │
│ │ [Bar chart]      │ [Table]          │  │
│ └──────────────────┴──────────────────┘  │
│                                            │
│ Last updated: 3 seconds ago [Pause]        │
└────────────────────────────────────────────┘
```

---

## Use Case Examples

### 1. IT Operations Dashboard

**Metrics**:
- System uptime %
- API response time (p95, p99)
- Error rate %
- Active users
- Server CPU/memory utilization
- Network throughput
- Queue depth
- Failed jobs

**Alert Thresholds**:
```
Uptime:
  ✓ Green: >99.9%
  ⚠ Orange: 99.5-99.9%
  🔴 Red: <99.5%

Response Time (p95):
  ✓ Green: <200ms
  ⚠ Orange: 200-500ms
  🔴 Red: >500ms

Error Rate:
  ✓ Green: <0.5%
  ⚠ Orange: 0.5-1.0%
  🔴 Red: >1.0%
```

### 2. Customer Support Dashboard

**Metrics**:
- Open tickets (by priority)
- First response time
- Resolution time
- CSAT score
- SLA compliance %
- Tickets by category
- Agent performance
- Queue depth

**Real-Time Features**:
- Live ticket count
- Aging tickets (>24h, >48h)
- Unassigned tickets
- SLA violations

### 3. Manufacturing Operations

**Metrics**:
- Production output (units/hour)
- Defect rate %
- Equipment OEE (Overall Equipment Effectiveness)
- Downtime minutes
- Inventory levels
- WIP (Work in Progress)
- On-time delivery %
- Safety incidents

### 4. E-commerce Operations

**Metrics**:
- Current visitors
- Orders per hour
- Conversion rate
- Average order value
- Cart abandonment rate
- Inventory alerts (low stock)
- Fulfillment status
- Payment failures

---

## Real-Time Update Strategies

### Pattern 1: Auto-Refresh

```javascript
// Refresh every 30 seconds
setInterval(() => {
  refreshDashboard();
}, 30000);
```

**Best Practices**:
- User control (pause/resume)
- Show countdown to next refresh
- Don't interrupt user interaction
- Smooth transitions (no jarring updates)

**UI**:
```
Last updated: 15 seconds ago
[Next update in: 15s] [⏸ Pause]
```

### Pattern 2: WebSocket Live Updates

```javascript
// Real-time updates via WebSocket
socket.on('metric-update', (data) => {
  updateMetric(data);
});
```

**Best For**:
- Mission-critical monitoring
- High-frequency changes
- Need sub-second updates

**UI**:
```
🔴 LIVE
Last update: Just now
```

### Pattern 3: Polling with Smart Intervals

```javascript
// Poll critical metrics frequently, others less so
pollCriticalMetrics(10000);  // 10 seconds
pollStandardMetrics(60000);  // 1 minute
pollDetailedReports(300000); // 5 minutes
```

---

## Alert Design

### Alert Components

Every alert should have:

1. **Severity** (Visual indicator)
   - 🔴 Red: Critical
   - 🟠 Orange: Warning
   - 🔵 Blue: Info

2. **Metric & Value**
   - What metric is alerting
   - Current value
   - Threshold crossed

3. **Context**
   - When did this start?
   - How much above/below threshold?
   - Historical context

4. **Action**
   - What should user do?
   - Who should be notified?
   - Automatic remediation?

### Alert Template

```
┌─────────────────────────────────────────┐
│ 🔴 CRITICAL ALERT                       │
├─────────────────────────────────────────┤
│ Metric: API Response Time (p95)         │
│ Current: 850ms                          │
│ Threshold: >500ms (Critical)            │
│                                         │
│ Duration: Last 15 minutes               │
│ Trend: [chart showing spike]            │
│                                         │
│ RECOMMENDED ACTIONS:                    │
│ 1. Check database connection pool      │
│ 2. Review recent deployments           │
│ 3. Escalate to on-call engineer        │
│                                         │
│ [Acknowledge] [Escalate] [View Details]│
└─────────────────────────────────────────┘
```

### Alert Grouping

**Problem**: 50 related alerts flood dashboard

**Solution**: Group related alerts

```
🔴 DATABASE ISSUES (5 alerts)
├─ Connection pool exhausted
├─ Query timeout on orders table
├─ Replication lag >60s
├─ Disk space <10% on primary
└─ Slow query detected

[Expand All] [Group Actions]
```

---

## Performance Considerations

### Challenge: Real-time = Heavy load

**Optimization Strategies**:

1. **Incremental Updates**
   ```
   Don't re-query everything
   Only update changed metrics
   ```

2. **Caching**
   ```
   Cache static reference data
   Cache aggregated metrics
   Invalidate on data change
   ```

3. **Efficient Queries**
   ```sql
   -- ❌ Bad: Full table scan every refresh
   SELECT COUNT(*) FROM orders;

   -- ✓ Good: Incremental since last check
   SELECT COUNT(*) FROM orders
   WHERE created_at > :last_check_time;
   ```

4. **Pre-aggregation**
   ```
   Aggregate data in background job
   Dashboard queries pre-aggregated tables
   Much faster than real-time aggregation
   ```

---

## Mobile Considerations

**Challenge**: Operations staff often mobile

**Mobile Layout**:
```
┌──────────────────┐
│ ☰ Operations     │
│ 🔴 2 Alerts      │
├──────────────────┤
│                  │
│ CRITICAL         │
│ 🔴 CPU >90%      │
│ [Details ▾]      │
│                  │
├──────────────────┤
│                  │
│ STATUS           │
│ Uptime:  ✓ 99.9% │
│ Errors:  ⚠ 0.6%  │
│ Response: ✓ 234ms│
│                  │
├──────────────────┤
│                  │
│ [View All ▾]     │
│                  │
└──────────────────┘
```

**Features**:
- Alerts first (most important)
- Simplified metrics (top 5-7)
- Click to expand details
- Push notifications for critical alerts
- Offline mode with last known state

---

## Testing Checklist

### Functional Testing
- [ ] All metrics display correctly
- [ ] Alerts trigger at correct thresholds
- [ ] Real-time updates working
- [ ] Drill-downs functional
- [ ] Filters apply correctly

### Performance Testing
- [ ] Load time <3 seconds
- [ ] Updates don't block UI
- [ ] Handles concurrent users
- [ ] No memory leaks (long sessions)
- [ ] Mobile performance acceptable

### Alert Testing
- [ ] Alerts visible and prominent
- [ ] Alert severity correct
- [ ] Actions clear and functional
- [ ] Alert history accessible
- [ ] Notifications sent (if configured)

### Usability Testing
- [ ] 5-second test: Can identify issues quickly
- [ ] Action test: Clear what to do for each alert
- [ ] Mobile test: Works on operator's device

---

## Common Patterns

### Pattern 1: SLA Monitoring

```
Support SLA Compliance - Today

First Response Time:
Target: <1 hour
Actual: 47 minutes ✓
Compliance: 94% (47/50 tickets)

┌─────────────────────────────┐
│ SLA Status                  │
├─────────────────────────────┤
│ ✓ Met:       47 (94%)       │
│ ⚠ At Risk:    2 (4%)        │
│ 🔴 Breached:  1 (2%)        │
└─────────────────────────────┘

[View At-Risk Tickets]
```

### Pattern 2: Queue Monitoring

```
Processing Queues

┌───────────┬──────┬────────┬──────┐
│ Queue     │ Depth│ Oldest │Status│
├───────────┼──────┼────────┼──────┤
│ Email     │ 23   │  5min  │ ✓    │
│ Reports   │ 145  │ 45min  │ ⚠    │
│ Exports   │ 1,234│ 3hrs   │ 🔴   │
│ Webhooks  │ 8    │  2min  │ ✓    │
└───────────┴──────┴────────┴──────┘

Action: Exports queue backed up - scaling workers
```

### Pattern 3: Real-Time Metrics

```
┌─────────────────────────────┐
│ LIVE METRICS                │
│ Updates every 5 seconds     │
├─────────────────────────────┤
│                             │
│ Current Active Users: 2,345 │
│ [Live sparkline ━━━╱╱╱]    │
│                             │
│ Requests/Second: 127        │
│ [Live sparkline ━━━━━━]    │
│                             │
│ Response Time: 234ms        │
│ [Live sparkline ━━━━━▲]    │
│                             │
└─────────────────────────────┘
```

---

## References

- Stephen Few: "Information Dashboard Design" - Chapter 5: Operational Dashboards
- Lean Manufacturing: Andon Board concepts
- ITIL: Service Operation Management
- DevOps Handbook: Monitoring and Observability
