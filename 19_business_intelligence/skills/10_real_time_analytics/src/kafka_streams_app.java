package com.analytics.streams;

import org.apache.kafka.streams.*;
import org.apache.kafka.streams.kstream.*;
import java.time.Duration;

public class KafkaStreamsAnalytics {
    public static void main(String[] args) {
        StreamsBuilder builder = new StreamsBuilder();
        
        KStream<String, Event> events = builder.stream("events");
        
        // Windowed aggregation
        KTable<Windowed<String>, Long> counts = events
            .groupBy((key, event) -> event.getEventType())
            .windowedBy(TimeWindows.of(Duration.ofMinutes(5)))
            .count();
        
        counts.toStream().to("event-counts");
        
        KafkaStreams streams = new KafkaStreams(builder.build(), getConfig());
        streams.start();
    }
}
