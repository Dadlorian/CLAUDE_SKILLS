# Analytics Integration Guide

## Unity Analytics

### Setup
```csharp
using UnityEngine.Analytics;

// Enable: Window → General → Services → Analytics

// Custom event
Analytics.CustomEvent("level_complete", new Dictionary<string, object>
{
    { "level_name", "Forest_1" },
    { "time_seconds", 125.5f },
    { "deaths", 3 }
});

// Economy event
Analytics.Transaction("item_purchase", 9.99m, "USD", new Dictionary<string, object>
{
    { "item_id", "sword_legendary" },
    { "item_type", "weapon" }
});
```

## GameAnalytics

### Setup
```csharp
using GameAnalyticsSDK;

void Start()
{
    GameAnalytics.Initialize();
}

// Progression events
GameAnalytics.NewProgressionEvent(
    GAProgressionStatus.Start,
    "World01",
    "Level01"
);

GameAnalytics.NewProgressionEvent(
    GAProgressionStatus.Complete,
    "World01",
    "Level01",
    score: 1250
);

// Design events (custom)
GameAnalytics.NewDesignEvent("Player:Death", deaths);
GameAnalytics.NewDesignEvent("Enemy:Killed:Zombie", 1);

// Resource events (economy)
GameAnalytics.NewResourceEvent(
    GAResourceFlowType.Source,
    "Gold",
    100,
    "Quest",
    "CompletedQuest_01"
);
```

## Firebase Analytics (Mobile)

### Unity
```csharp
using Firebase.Analytics;

void Start()
{
    FirebaseAnalytics.SetAnalyticsCollectionEnabled(true);
}

// Log event
FirebaseAnalytics.LogEvent("level_start", "level_name", "Forest_1");

// Log event with multiple parameters
FirebaseAnalytics.LogEvent("purchase",
    new Parameter("item_id", "sword"),
    new Parameter("currency", "USD"),
    new Parameter("value", 9.99)
);

// User properties
FirebaseAnalytics.SetUserProperty("player_level", "25");
```

## Key Metrics to Track

### Engagement
```csharp
// Session start/end
Analytics.CustomEvent("session_start");

// Play time
Analytics.CustomEvent("session_end", new Dictionary<string, object>
{
    { "duration_minutes", playTime }
});

// Daily Active Users (DAU)
// Monthly Active Users (MAU)
```

### Retention
```csharp
// Day 1, 7, 30 retention
// Tracked automatically by most analytics platforms

// Cohort analysis: Track groups by install date
```

### Monetization
```csharp
// Revenue per user
// Conversion rate (free → paying)
// Average Revenue Per Paying User (ARPPU)

Analytics.Transaction("iap_purchase", 4.99m, "USD", new Dictionary<string, object>
{
    { "item_id", "coin_pack_medium" },
    { "quantity", 500 }
});
```

### Progression
```csharp
// Level completion rate
Analytics.CustomEvent("level_complete", new Dictionary<string, object>
{
    { "level_id", levelId },
    { "attempts", attempts },
    { "time_spent", timeSpent }
});

// Funnel analysis: Tutorial → Level 1 → Level 2 → etc.
```

### User Behavior
```csharp
// Feature usage
Analytics.CustomEvent("feature_used", new Dictionary<string, object>
{
    { "feature_name", "inventory" },
    { "duration_seconds", 45 }
});

// Difficulty spikes (where players quit)
Analytics.CustomEvent("player_quit", new Dictionary<string, object>
{
    { "level_id", levelId },
    { "progress_percent", progressPercent }
});
```

## Event Taxonomy

### Naming Convention
```
category:action:label

Examples:
- player:death:fall_damage
- enemy:killed:zombie
- ui:button_clicked:settings
- economy:purchase:health_potion
```

### Event Limits
- **Unity Analytics**: 100 custom events
- **GameAnalytics**: Unlimited events
- **Firebase**: 500 distinct events

## Privacy Compliance

### GDPR (Europe)
```csharp
// Request user consent
if (userConsentedToAnalytics)
{
    Analytics.SetAnalyticsEnabled(true);
}
else
{
    Analytics.SetAnalyticsEnabled(false);
}
```

### COPPA (Children < 13)
```csharp
// Disable personalized ads and data collection
```

## Best Practices
✅ Track key user journey milestones
✅ Measure what you'll act on
✅ Don't over-track (performance impact)
✅ Respect user privacy (opt-out)
✅ Consistent naming convention
✅ Regular dashboard review

## Dashboard Setup

### KPIs to Monitor
1. **DAU / MAU**: Daily/Monthly Active Users
2. **Retention**: D1, D7, D30
3. **Session Length**: Average play time
4. **Conversion Rate**: Free → Paid
5. **Churn Rate**: % leaving the game
