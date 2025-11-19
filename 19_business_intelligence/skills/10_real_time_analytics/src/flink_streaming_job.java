/**
 * Flink Streaming Job for Real-Time Analytics
 * Processes events from Kafka and writes aggregates to ClickHouse
 */
package com.analytics.flink;

import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.windowing.time.Time;
import org.apache.flink.streaming.api.windowing.assigners.TumblingEventTimeWindows;
import org.apache.flink.api.common.eventtime.WatermarkStrategy;
import java.time.Duration;

public class RealTimeAnalytics {
    public static void main(String[] args) throws Exception {
        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
        
        // Configure environment
        env.enableCheckpointing(60000);
        env.setParallelism(16);
        
        // Read from Kafka
        DataStream<Event> events = env
            .addSource(new FlinkKafkaConsumer<>("events", new EventSchema(), kafkaProps))
            .assignTimestampsAndWatermarks(
                WatermarkStrategy.<Event>forBoundedOutOfOrderness(Duration.ofMinutes(5))
                    .withTimestampAssigner((event, timestamp) -> event.getTimestamp())
            );
        
        // Window aggregations
        DataStream<HourlyStats> hourlyStats = events
            .keyBy(event -> event.getEventType())
            .window(TumblingEventTimeWindows.of(Time.hours(1)))
            .aggregate(new HourlyStatsAggregator());
        
        // Write to ClickHouse
        hourlyStats.addSink(new ClickHouseSink<>("hourly_stats"));
        
        env.execute("Real-Time Analytics");
    }
}
