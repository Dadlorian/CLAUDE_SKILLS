package com.analytics.flink;

import org.apache.flink.api.common.functions.AggregateFunction;

public class HourlyStatsAggregator 
        implements AggregateFunction<Event, StatsAccumulator, HourlyStats> {
    
    @Override
    public StatsAccumulator createAccumulator() {
        return new StatsAccumulator();
    }
    
    @Override
    public StatsAccumulator add(Event event, StatsAccumulator acc) {
        acc.count++;
        acc.totalRevenue += event.getRevenue() != null ? event.getRevenue() : 0;
        acc.userIds.add(event.getUserId());
        acc.sessionDurations.add(event.getSessionDuration());
        return acc;
    }
    
    @Override
    public HourlyStats getResult(StatsAccumulator acc) {
        return new HourlyStats(
            acc.windowStart,
            acc.eventType,
            acc.country,
            acc.count,
            acc.totalRevenue,
            acc.userIds.size(),
            acc.sessionDurations.stream()
                .mapToLong(Long::longValue)
                .average()
                .orElse(0)
        );
    }
    
    @Override
    public StatsAccumulator merge(StatsAccumulator a, StatsAccumulator b) {
        a.count += b.count;
        a.totalRevenue += b.totalRevenue;
        a.userIds.addAll(b.userIds);
        a.sessionDurations.addAll(b.sessionDurations);
        return a;
    }
}

class StatsAccumulator {
    long windowStart;
    String eventType;
    String country;
    long count = 0;
    double totalRevenue = 0;
    Set<Long> userIds = new HashSet<>();
    List<Long> sessionDurations = new ArrayList<>();
}
