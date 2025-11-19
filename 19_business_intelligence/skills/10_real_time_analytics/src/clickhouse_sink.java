package com.analytics.flink;

import org.apache.flink.streaming.api.functions.sink.RichSinkFunction;
import ru.yandex.clickhouse.ClickHouseDataSource;
import java.sql.*;
import java.util.*;

public class ClickHouseSink<T> extends RichSinkFunction<T> {
    private transient Connection connection;
    private transient PreparedStatement statement;
    private final String tableName;
    private final int batchSize = 1000;
    private List<T> buffer = new ArrayList<>();
    
    public ClickHouseSink(String tableName) {
        this.tableName = tableName;
    }
    
    @Override
    public void open(Configuration parameters) throws Exception {
        ClickHouseDataSource dataSource = new ClickHouseDataSource(
            "jdbc:clickhouse://clickhouse:8123/analytics"
        );
        connection = dataSource.getConnection();
    }
    
    @Override
    public void invoke(T value, Context context) throws Exception {
        buffer.add(value);
        if (buffer.size() >= batchSize) {
            flush();
        }
    }
    
    private void flush() throws SQLException {
        if (buffer.isEmpty()) return;
        
        String sql = buildInsertSQL(tableName);
        statement = connection.prepareStatement(sql);
        
        for (T record : buffer) {
            setParameters(statement, record);
            statement.addBatch();
        }
        
        statement.executeBatch();
        buffer.clear();
    }
    
    @Override
    public void close() throws Exception {
        flush();
        if (statement != null) statement.close();
        if (connection != null) connection.close();
    }
}
