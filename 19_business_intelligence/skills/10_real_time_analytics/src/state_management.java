package com.analytics.flink;

import org.apache.flink.api.common.state.*;

public class StatefulProcessor extends KeyedProcessFunction<String, Event, UserMetrics> {
    private transient MapState<String, Long> productCounts;
    private transient ListState<Event> recentEvents;
    
    @Override
    public void open(Configuration config) {
        // Map state for product counts
        MapStateDescriptor<String, Long> mapDescriptor = 
            new MapStateDescriptor<>("products", String.class, Long.class);
        productCounts = getRuntimeContext().getMapState(mapDescriptor);
        
        // List state for recent events
        ListStateDescriptor<Event> listDescriptor = 
            new ListStateDescriptor<>("recent", Event.class);
        recentEvents = getRuntimeContext().getListState(listDescriptor);
    }
    
    @Override
    public void processElement(Event event, Context ctx, Collector<UserMetrics> out) 
            throws Exception {
        // Update product counts
        String product = event.getProductId();
        Long count = productCounts.get(product);
        productCounts.put(product, count == null ? 1L : count + 1);
        
        // Add to recent events
        recentEvents.add(event);
    }
}
