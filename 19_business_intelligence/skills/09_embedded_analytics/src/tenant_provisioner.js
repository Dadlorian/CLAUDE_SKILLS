/**
 * Tenant Provisioning Service
 * Automates new tenant setup with database, BI platform, and RLS
 */
const { Pool } = require('pg');

class TenantProvisioner {
  constructor(config) {
    this.dbPool = new Pool(config.database);
    this.biPlatform = config.biPlatform;
  }

  async provisionTenant(tenant) {
    console.log(`Provisioning tenant: ${tenant.name}`);

    const client = await this.dbPool.connect();

    try {
      await client.query('BEGIN');

      // Create database resources
      await this.createDatabaseResources(client, tenant);

      // Create BI workspace
      const workspace = await this.createBIWorkspace(tenant);

      // Setup RLS
      await this.setupRLS(client, tenant);

      // Create admin user
      await this.createAdminUser(client, tenant);

      await client.query('COMMIT');

      return { success: true, tenantId: tenant.id, workspace };

    } catch (error) {
      await client.query('ROLLBACK');
      console.error('Provisioning failed:', error);
      throw error;
    } finally {
      client.release();
    }
  }

  async createDatabaseResources(client, tenant) {
    await client.query(
      'INSERT INTO tenants (id, name, tier) VALUES ($1, $2, $3)',
      [tenant.id, tenant.name, tenant.tier]
    );
  }

  async setupRLS(client, tenant) {
    const tables = ['sales', 'customers'];

    for (const table of tables) {
      await client.query(`
        ALTER TABLE ${table} ENABLE ROW LEVEL SECURITY;
        CREATE POLICY tenant_${tenant.id}_${table} ON ${table}
          USING (tenant_id = ${tenant.id});
      `);
    }
  }
}

module.exports = TenantProvisioner;
