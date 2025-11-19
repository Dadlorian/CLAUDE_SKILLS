# Cost Optimization for Embedded Analytics

## Overview

Strategies to minimize costs while maintaining performance and user experience in embedded analytics deployments.

## Cost Structure Understanding

### Power BI Embedded Pricing Model

```
Azure Capacity (A SKUs):
- A1: $1/hour (~$730/month)  - Testing/dev
- A2: $2/hour (~$1,460/month) - Small production
- A3: $4/hour (~$2,920/month) - Medium production
- A4: $8/hour (~$5,840/month) - Large production

Optimization: Pause when not in use, scale dynamically
```

### Tableau Pricing Model

```
Per-User Licensing:
- Viewer: $15/user/month
- Explorer: $42/user/month
- Creator: $70/user/month

Embedded Analytics Add-on:
- Custom pricing, typically $1000-$5000/month base
- + usage-based fees

Optimization: Use viewer licenses, limit creators
```

### Looker Pricing Model

```
Platform License: $3,000-$5,000/month base
Per-User: $30-$50/user/month
Data egress charges apply

Optimization: Optimize queries, cache aggressively
```

---

## Cost Optimization Strategies

### 1. Capacity Management (Power BI)

```javascript
class PowerBICapacityManager {
  constructor() {
    this.azureClient = new ComputeManagementClient(credentials, subscriptionId);
    this.usageThreshold = 80; // Pause below 80% utilization
  }

  // Auto-pause during off-hours
  async scheduleCapacityPause() {
    const cron = require('node-cron');

    // Pause at 8 PM EST (when usage drops)
    cron.schedule('0 20 * * *', async () => {
      const usage = await this.getCapacityUsage();

      if (usage < this.usageThreshold) {
        await this.pauseCapacity();
        console.log('Capacity paused due to low usage');
      }
    });

    // Resume at 6 AM EST (before business hours)
    cron.schedule('0 6 * * *', async () => {
      await this.resumeCapacity();
      console.log('Capacity resumed for business hours');
    });
  }

  async pauseCapacity() {
    await this.azureClient.capacities.beginSuspend(
      resourceGroupName,
      capacityName
    );

    await db.analytics.update({
      availability: 'paused',
      paused_at: new Date()
    });
  }

  async resumeCapacity() {
    await this.azureClient.capacities.beginResume(
      resourceGroupName,
      capacityName
    );

    await db.analytics.update({
      availability: 'active',
      resumed_at: new Date()
    });
  }

  // Monitor usage and scale dynamically
  async monitorAndScale() {
    setInterval(async () => {
      const metrics = await this.getCapacityMetrics();

      if (metrics.cpuUsage > 90) {
        await this.scaleUp();
      } else if (metrics.cpuUsage < 30 && this.currentSKU !== 'A1') {
        await this.scaleDown();
      }
    }, 5 * 60 * 1000); // Check every 5 minutes
  }

  async scaleUp() {
    const nextSKU = this.getNextSKU(this.currentSKU);
    console.log(`Scaling up from ${this.currentSKU} to ${nextSKU}`);

    await this.updateCapacitySKU(nextSKU);
    this.currentSKU = nextSKU;
  }

  async scaleDown() {
    const previousSKU = this.getPreviousSKU(this.currentSKU);
    console.log(`Scaling down from ${this.currentSKU} to ${previousSKU}`);

    await this.updateCapacitySKU(previousSKU);
    this.currentSKU = previousSKU;
  }

  getNextSKU(current) {
    const skus = ['A1', 'A2', 'A3', 'A4', 'A5', 'A6'];
    const currentIndex = skus.indexOf(current);
    return skus[Math.min(currentIndex + 1, skus.length - 1)];
  }

  getPreviousSKU(current) {
    const skus = ['A1', 'A2', 'A3', 'A4', 'A5', 'A6'];
    const currentIndex = skus.indexOf(current);
    return skus[Math.max(currentIndex - 1, 0)];
  }
}

// Usage
const capacityManager = new PowerBICapacityManager();
capacityManager.scheduleCapacityPause();
capacityManager.monitorAndScale();
```

### 2. Query Optimization

```sql
-- Expensive query (full table scan)
SELECT
  customer_id,
  SUM(amount) as total_amount
FROM sales
WHERE tenant_id = 123
GROUP BY customer_id;

-- Optimized query (uses indexes, filters early)
SELECT
  customer_id,
  SUM(amount) as total_amount
FROM sales
WHERE tenant_id = 123
  AND date >= CURRENT_DATE - INTERVAL '90 days' -- Only recent data
  AND status = 'completed' -- Filter early
GROUP BY customer_id
HAVING SUM(amount) > 1000; -- Only meaningful results
```

```javascript
// Detect and optimize expensive queries
class QueryOptimizer {
  async analyzeQueryCost(query) {
    const explain = await db.query(`EXPLAIN ANALYZE ${query}`);

    const cost = this.extractCost(explain);
    const duration = this.extractDuration(explain);

    if (cost > 10000 || duration > 5000) {
      console.warn(`Expensive query detected:`, {
        cost,
        duration,
        query: query.substring(0, 100)
      });

      await this.suggestOptimizations(query, explain);
    }

    return { cost, duration };
  }

  async suggestOptimizations(query, explain) {
    const suggestions = [];

    // Check for missing indexes
    if (explain.includes('Seq Scan')) {
      suggestions.push('Add index on frequently filtered columns');
    }

    // Check for large result sets
    if (explain.includes('rows=') && this.extractRowCount(explain) > 100000) {
      suggestions.push('Add LIMIT clause or more specific filters');
    }

    // Check for expensive sorts
    if (explain.includes('Sort')) {
      suggestions.push('Add index on ORDER BY columns');
    }

    console.log('Optimization suggestions:', suggestions);
    return suggestions;
  }
}
```

### 3. Caching to Reduce Compute

```javascript
class CostEffectiveCaching {
  constructor() {
    this.redis = new Redis();
    this.costPerQuery = 0.001; // $0.001 per query
  }

  async executeWithCaching(tenantId, query, params) {
    const cacheKey = this.getCacheKey(tenantId, query, params);

    // Check cache first
    const cached = await this.redis.get(cacheKey);
    if (cached) {
      console.log('Cache hit - saved query cost');
      await this.trackCostSavings(this.costPerQuery);
      return JSON.parse(cached);
    }

    // Execute query and cache
    const result = await db.query(query, params);
    await this.trackCost(this.costPerQuery);

    // Cache with adaptive TTL based on query cost
    const explain = await db.query(`EXPLAIN ${query}`);
    const ttl = this.calculateTTL(explain);

    await this.redis.setex(cacheKey, ttl, JSON.stringify(result.rows));

    return result.rows;
  }

  calculateTTL(explain) {
    const cost = this.extractCost(explain);

    // Expensive queries cached longer
    if (cost > 10000) return 3600;      // 1 hour
    if (cost > 5000) return 1800;       // 30 minutes
    if (cost > 1000) return 600;        // 10 minutes
    return 300;                         // 5 minutes
  }

  async trackCost(amount) {
    await this.redis.incrbyfloat('analytics:cost:total', amount);
    await this.redis.incrbyfloat(
      `analytics:cost:${new Date().toISOString().slice(0, 10)}`,
      amount
    );
  }

  async trackCostSavings(amount) {
    await this.redis.incrbyfloat('analytics:cost:saved', amount);
  }

  async getCostReport(startDate, endDate) {
    const days = this.getDaysBetween(startDate, endDate);
    const costs = [];

    for (const day of days) {
      const cost = await this.redis.get(`analytics:cost:${day}`);
      costs.push({
        date: day,
        cost: parseFloat(cost) || 0
      });
    }

    const totalCost = costs.reduce((sum, day) => sum + day.cost, 0);
    const totalSaved = await this.redis.get('analytics:cost:saved');

    return {
      period: { startDate, endDate },
      totalCost,
      totalSaved: parseFloat(totalSaved) || 0,
      dailyCosts: costs,
      averageDailyCost: totalCost / costs.length
    };
  }
}
```

### 4. Data Reduction Techniques

```javascript
// Pre-aggregate data to reduce query costs
class DataAggregator {
  async createDailySummaries() {
    // Run nightly to pre-aggregate daily stats
    await db.query(`
      INSERT INTO sales_daily_summary (tenant_id, date, metrics)
      SELECT
        tenant_id,
        DATE(created_at) as date,
        jsonb_build_object(
          'total_amount', SUM(amount),
          'transaction_count', COUNT(*),
          'avg_amount', AVG(amount),
          'max_amount', MAX(amount),
          'unique_customers', COUNT(DISTINCT customer_id)
        ) as metrics
      FROM sales
      WHERE DATE(created_at) = CURRENT_DATE - INTERVAL '1 day'
      GROUP BY tenant_id, DATE(created_at)
      ON CONFLICT (tenant_id, date)
      DO UPDATE SET metrics = EXCLUDED.metrics
    `);

    console.log('Daily summaries created');
  }

  // Use summaries instead of raw data for dashboards
  async getDashboardData(tenantId, startDate, endDate) {
    // If date range > 30 days, use daily summaries
    const daysDiff = this.daysBetween(startDate, endDate);

    if (daysDiff > 30) {
      return await db.query(`
        SELECT
          date,
          (metrics->>'total_amount')::numeric as total_amount,
          (metrics->>'transaction_count')::integer as transaction_count
        FROM sales_daily_summary
        WHERE tenant_id = $1
          AND date BETWEEN $2 AND $3
        ORDER BY date
      `, [tenantId, startDate, endDate]);
    } else {
      // Use raw data for recent/short ranges
      return await db.query(`
        SELECT
          DATE(created_at) as date,
          SUM(amount) as total_amount,
          COUNT(*) as transaction_count
        FROM sales
        WHERE tenant_id = $1
          AND created_at BETWEEN $2 AND $3
        GROUP BY DATE(created_at)
        ORDER BY date
      `, [tenantId, startDate, endDate]);
    }
  }
}

// Schedule nightly aggregation
cron.schedule('0 2 * * *', async () => {
  const aggregator = new DataAggregator();
  await aggregator.createDailySummaries();
});
```

### 5. License Optimization

```javascript
class LicenseOptimizer {
  async optimizeTableauLicenses() {
    // Analyze usage patterns
    const users = await db.query(`
      SELECT
        user_id,
        license_type,
        COUNT(*) as login_count,
        MAX(last_login_at) as last_login
      FROM tableau_users
      GROUP BY user_id, license_type
    `);

    const recommendations = [];

    for (const user of users.rows) {
      // Downgrade inactive Creators
      if (user.license_type === 'Creator' && user.login_count === 0) {
        recommendations.push({
          userId: user.user_id,
          action: 'downgrade',
          from: 'Creator',
          to: 'Viewer',
          monthlySavings: 70 - 15 // $55/month
        });
      }

      // Downgrade rarely used Explorers
      if (user.license_type === 'Explorer' && user.login_count < 3) {
        recommendations.push({
          userId: user.user_id,
          action: 'downgrade',
          from: 'Explorer',
          to: 'Viewer',
          monthlySavings: 42 - 15 // $27/month
        });
      }
    }

    return recommendations;
  }

  async applyRecommendation(recommendation) {
    await tableau.updateUserLicense(
      recommendation.userId,
      recommendation.to
    );

    await db.licenseChanges.insert({
      user_id: recommendation.userId,
      from_license: recommendation.from,
      to_license: recommendation.to,
      monthly_savings: recommendation.monthlySavings,
      changed_at: new Date()
    });
  }

  // Calculate potential savings
  async calculatePotentialSavings() {
    const recommendations = await this.optimizeTableauLicenses();

    const totalMonthlySavings = recommendations.reduce(
      (sum, rec) => sum + rec.monthlySavings,
      0
    );

    const totalAnnualSavings = totalMonthlySavings * 12;

    return {
      monthySavings: totalMonthlySavings,
      annualSavings: totalAnnualSavings,
      affectedUsers: recommendations.length,
      recommendations
    };
  }
}
```

### 6. Infrastructure Cost Optimization

```javascript
class InfrastructureCostManager {
  // Use spot instances for non-critical BI workloads
  async useSpotInstances() {
    // For self-hosted BI platforms (Tableau Server, Metabase, Superset)
    const ec2 = new AWS.EC2();

    const params = {
      InstanceType: 't3.2xlarge',
      SpotPrice: '0.25', // Max price willing to pay
      InstanceCount: 1,
      LaunchSpecification: {
        ImageId: 'ami-12345678',
        KeyName: 'analytics-key',
        SecurityGroupIds: ['sg-12345678'],
        SubnetId: 'subnet-12345678',
        UserData: Buffer.from(this.getStartupScript()).toString('base64')
      }
    };

    const result = await ec2.requestSpotInstances(params).promise();
    console.log('Spot instance requested:', result.SpotInstanceRequestId);

    // Can save 60-90% vs on-demand
  }

  // Use reserved instances for baseline capacity
  async reserveBaselineCapacity() {
    // Reserve instances for predictable baseline load
    const pricing = {
      onDemand: 0.42, // $/hour
      reserved1Year: 0.28, // $/hour with 1-year commitment
      reserved3Year: 0.18  // $/hour with 3-year commitment
    };

    const baselineHoursPerMonth = 730; // 24/7
    const monthlySavings = (pricing.onDemand - pricing.reserved3Year) * baselineHoursPerMonth;

    console.log(`Monthly savings with 3-year reserved: $${monthlySavings}`);
    return monthlySavings;
  }

  // Right-size instances based on actual usage
  async rightsizeInstances() {
    const cloudwatch = new AWS.CloudWatch();

    // Get CPU utilization for last 30 days
    const cpuMetrics = await cloudwatch.getMetricStatistics({
      Namespace: 'AWS/EC2',
      MetricName: 'CPUUtilization',
      Dimensions: [{ Name: 'InstanceId', Value: instanceId }],
      StartTime: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000),
      EndTime: new Date(),
      Period: 3600,
      Statistics: ['Average', 'Maximum']
    }).promise();

    const avgCPU = this.calculateAverage(cpuMetrics.Datapoints);
    const maxCPU = Math.max(...cpuMetrics.Datapoints.map(d => d.Maximum));

    if (avgCPU < 20 && maxCPU < 40) {
      console.log('Instance is oversized, recommend downsizing');
      return {
        recommendation: 'downsize',
        currentType: 't3.2xlarge',
        recommendedType: 't3.xlarge',
        monthlySavings: 200 // Approximate
      };
    }

    return { recommendation: 'no_change' };
  }
}
```

### 7. Data Transfer Cost Optimization

```javascript
class DataTransferOptimizer {
  // Minimize cross-region data transfer
  async optimizeDataLocation() {
    // Co-locate database and BI platform in same region
    const recommendations = [];

    const dbRegion = 'us-east-1';
    const biRegion = 'us-west-2'; // Different region!

    if (dbRegion !== biRegion) {
      recommendations.push({
        issue: 'Cross-region data transfer',
        cost: 'est. $1000/month for 10TB',
        solution: `Move BI platform to ${dbRegion}`,
        savings: 'est. $900/month (10x reduction)'
      });
    }

    return recommendations;
  }

  // Use CloudFront/CDN to cache dashboard images
  async useCDNForImages() {
    // Dashboard images can be expensive to regenerate
    // Cache in CloudFront to reduce origin requests

    const cloudfront = new AWS.CloudFront();

    await cloudfront.createDistribution({
      DistributionConfig: {
        Origins: {
          Quantity: 1,
          Items: [{
            Id: 'bi-platform-origin',
            DomainName: 'tableau.example.com',
            CustomOriginConfig: {
              HTTPPort: 80,
              HTTPSPort: 443,
              OriginProtocolPolicy: 'https-only'
            }
          }]
        },
        DefaultCacheBehavior: {
          TargetOriginId: 'bi-platform-origin',
          ViewerProtocolPolicy: 'redirect-to-https',
          AllowedMethods: {
            Quantity: 2,
            Items: ['GET', 'HEAD']
          },
          CachedMethods: {
            Quantity: 2,
            Items: ['GET', 'HEAD']
          },
          DefaultTTL: 86400, // 24 hours
          MaxTTL: 31536000   // 1 year
        },
        Enabled: true
      }
    }).promise();

    console.log('CDN configured, reducing origin requests by ~80%');
  }

  // Compress data before transfer
  async enableCompression() {
    // Enable gzip/brotli compression
    const express = require('express');
    const compression = require('compression');

    const app = express();

    app.use(compression({
      level: 6,
      threshold: 1024,
      filter: (req, res) => {
        // Compress analytics API responses
        return req.path.startsWith('/api/analytics');
      }
    }));

    // Can reduce bandwidth by 70-90%
  }
}
```

---

## Cost Monitoring Dashboard

```javascript
class CostMonitoringDashboard {
  async generateCostReport() {
    const report = {
      // Infrastructure costs
      infrastructure: {
        compute: await this.getComputeCosts(),
        storage: await this.getStorageCosts(),
        network: await this.getNetworkCosts()
      },

      // License costs
      licenses: {
        tableau: await this.getTableauLicenseCosts(),
        powerbi: await this.getPowerBICosts(),
        total: 0
      },

      // Per-tenant breakdown
      tenants: await this.getPerTenantCosts(),

      // Optimization opportunities
      optimizations: await this.getOptimizationOpportunities(),

      // Projections
      projections: await this.projectCosts()
    };

    report.licenses.total =
      report.licenses.tableau + report.licenses.powerbi;

    report.total =
      report.infrastructure.compute +
      report.infrastructure.storage +
      report.infrastructure.network +
      report.licenses.total;

    return report;
  }

  async getOptimizationOpportunities() {
    const opportunities = [];

    // License optimization
    const licenseOpt = await new LicenseOptimizer().calculatePotentialSavings();
    if (licenseOpt.annualSavings > 0) {
      opportunities.push({
        category: 'licenses',
        opportunity: 'Downgrade unused licenses',
        annualSavings: licenseOpt.annualSavings,
        effort: 'low'
      });
    }

    // Capacity optimization (Power BI)
    opportunities.push({
      category: 'compute',
      opportunity: 'Auto-pause Power BI capacity during off-hours',
      annualSavings: 2920 * 0.5 * 12, // 50% uptime reduction
      effort: 'medium'
    });

    // Caching optimization
    const cacheStats = await this.getCacheStats();
    if (cacheStats.hitRate < 0.7) {
      opportunities.push({
        category: 'compute',
        opportunity: 'Improve cache hit rate',
        annualSavings: 5000, // Estimated
        effort: 'medium'
      });
    }

    return opportunities.sort((a, b) => b.annualSavings - a.annualSavings);
  }

  async projectCosts() {
    const current = await this.getCurrentMonthCost();
    const growth = 0.15; // 15% monthly growth assumption

    const projections = [];

    for (let month = 1; month <= 12; month++) {
      projections.push({
        month,
        projected: current * Math.pow(1 + growth, month),
        optimized: current * Math.pow(1 + growth * 0.7, month) // With optimization
      });
    }

    return projections;
  }
}
```

---

## Cost Optimization Checklist

### Compute
- [ ] Auto-pause/scale capacity during off-hours
- [ ] Use spot/preemptible instances where possible
- [ ] Right-size instances based on actual usage
- [ ] Use reserved instances for baseline load
- [ ] Monitor and optimize query performance
- [ ] Implement aggressive caching

### Licenses
- [ ] Regular license audits (quarterly)
- [ ] Downgrade unused/inactive users
- [ ] Use viewer licenses where possible
- [ ] Negotiate volume discounts
- [ ] Consider open-source alternatives

### Data
- [ ] Pre-aggregate data where possible
- [ ] Archive old data to cheaper storage
- [ ] Implement data retention policies
- [ ] Use columnar storage formats
- [ ] Compress data at rest

### Network
- [ ] Co-locate database and BI platform
- [ ] Use CDN for static assets
- [ ] Enable compression
- [ ] Minimize data transfer
- [ ] Regional deployment strategy

### Monitoring
- [ ] Track costs per tenant
- [ ] Set up cost alerts
- [ ] Monthly cost reviews
- [ ] Identify optimization opportunities
- [ ] Project future costs
- [ ] Regular cost/benefit analysis
