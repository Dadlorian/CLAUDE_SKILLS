package com.analytics.flink;

import org.apache.flink.api.common.state.*;
import org.apache.flink.streaming.api.functions.KeyedProcessFunction;
import org.apache.flink.util.Collector;

public class DeduplicationFunction extends KeyedProcessFunction<String, Event, Event> {
    private transient ValueState<Boolean> seenState;
    
    @Override
    public void open(Configuration parameters) {
        StateTtlConfig ttlConfig = StateTtlConfig
            .newBuilder(Time.hours(24))
            .setUpdateType(StateTtlConfig.UpdateType.OnCreateAndWrite)
            .setStateVisibility(StateTtlConfig.StateVisibility.NeverReturnExpired)
            .cleanupIncrementally(10, true)
            .build();
        
        ValueStateDescriptor<Boolean> descriptor = 
            new ValueStateDescriptor<>("seen", Boolean.class);
        descriptor.enableTimeToLive(ttlConfig);
        
        seenState = getRuntimeContext().getState(descriptor);
    }
    
    @Override
    public void processElement(Event event, Context ctx, Collector<Event> out) 
            throws Exception {
        Boolean seen = seenState.value();
        
        if (seen == null || !seen) {
            seenState.update(true);
            out.collect(event);
        } else {
            // Duplicate detected, increment metric
            getRuntimeContext().getMetricGroup()
                .counter("duplicates").inc();
        }
    }
}
