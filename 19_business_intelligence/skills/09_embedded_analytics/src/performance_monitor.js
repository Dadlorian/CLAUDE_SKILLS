/**
 * Performance Monitoring for Embedded Analytics
 */
class PerformanceMonitor {
  constructor(db, redis) {
    this.db = db;
    this.redis = redis;
  }

  async collectMetrics() {
    return {
      database: await this.getDatabaseMetrics(),
      cache: await this.getCacheMetrics(),
      queries: await this.getQueryMetrics(),
      embeds: await this.getEmbedMetrics()
    };
  }

  async getDatabaseMetrics() {
    const result = await this.db.query(`
      SELECT
        COUNT(*) FILTER (WHERE state = 'active') as active_connections,
        AVG(EXTRACT(EPOCH FROM (now() - query_start))) as avg_query_time
      FROM pg_stat_activity
      WHERE datname = current_database()
    `);

    return result.rows[0];
  }

  async getCacheMetrics() {
    const info = await this.redis.info('stats');
    const hits = this.parseInfo(info, 'keyspace_hits');
    const misses = this.parseInfo(info, 'keyspace_misses');
    const total = hits + misses;

    return {
      hits,
      misses,
      hitRate: total > 0 ? (hits / total).toFixed(2) : 0,
      memory: this.parseInfo(info, 'used_memory')
    };
  }

  async getSlowQueries() {
    const result = await this.db.query(`
      SELECT
        query,
        calls,
        mean_exec_time,
        max_exec_time
      FROM pg_stat_statements
      WHERE mean_exec_time > 1000
      ORDER BY mean_exec_time DESC
      LIMIT 10
    `);

    return result.rows;
  }

  parseInfo(info, key) {
    const match = info.match(new RegExp(`${key}:(\\d+)`));
    return match ? parseInt(match[1]) : 0;
  }
}

module.exports = PerformanceMonitor;
