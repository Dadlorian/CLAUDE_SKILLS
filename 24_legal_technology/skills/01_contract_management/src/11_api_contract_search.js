/**
 * API Contract Search - RESTful API for searching and retrieving contracts
 * Express.js implementation
 */

const express = require('express');
const router = express.Router();

class ContractSearchAPI {
  constructor(database) {
    this.db = database;
    this.setupRoutes();
  }

  setupRoutes() {
    // Search contracts
    router.get('/api/contracts/search', this.searchContracts.bind(this));

    // Get contract by ID
    router.get('/api/contracts/:id', this.getContractById.bind(this));

    // Get contracts by metadata
    router.get('/api/contracts/metadata/query', this.searchByMetadata.bind(this));

    // Get high-risk contracts
    router.get('/api/contracts/risk/high', this.getHighRiskContracts.bind(this));

    // Get expiring contracts
    router.get('/api/contracts/expiring', this.getExpiringContracts.bind(this));

    // Get contracts by party
    router.get('/api/parties/:partyId/contracts', this.getContractsByParty.bind(this));
  }

  async searchContracts(req, res) {
    try {
      const { q, type, status, limit = 20, offset = 0 } = req.query;

      let query = {};

      if (q) {
        // Full-text search
        query.$text = { $search: q };
      }

      if (type) {
        query.contract_type = type;
      }

      if (status) {
        query.status = status;
      }

      const contracts = await this.db.find(query)
        .limit(parseInt(limit))
        .skip(parseInt(offset));

      const total = await this.db.countDocuments(query);

      return res.json({
        success: true,
        data: contracts,
        pagination: {
          total,
          limit: parseInt(limit),
          offset: parseInt(offset),
          hasMore: offset + limit < total
        }
      });
    } catch (error) {
      return res.status(500).json({
        success: false,
        error: error.message
      });
    }
  }

  async getContractById(req, res) {
    try {
      const { id } = req.params;

      const contract = await this.db.findById(id);

      if (!contract) {
        return res.status(404).json({
          success: false,
          error: 'Contract not found'
        });
      }

      return res.json({
        success: true,
        data: contract
      });
    } catch (error) {
      return res.status(500).json({
        success: false,
        error: error.message
      });
    }
  }

  async searchByMetadata(req, res) {
    try {
      const { parties, minValue, maxValue, effectiveDate, expirationDate } = req.query;

      let query = {};

      if (parties) {
        query.parties = { $in: parties.split(',') };
      }

      if (minValue || maxValue) {
        query.contract_value = {};
        if (minValue) query.contract_value.$gte = parseFloat(minValue);
        if (maxValue) query.contract_value.$lte = parseFloat(maxValue);
      }

      if (effectiveDate) {
        query.effective_date = { $gte: new Date(effectiveDate) };
      }

      if (expirationDate) {
        query.expiration_date = { $lte: new Date(expirationDate) };
      }

      const contracts = await this.db.find(query);

      return res.json({
        success: true,
        data: contracts,
        count: contracts.length
      });
    } catch (error) {
      return res.status(500).json({
        success: false,
        error: error.message
      });
    }
  }

  async getHighRiskContracts(req, res) {
    try {
      const { limit = 20 } = req.query;

      const contracts = await this.db.find({
        risk_level: { $in: ['HIGH', 'CRITICAL'] }
      })
        .sort({ risk_score: -1 })
        .limit(parseInt(limit));

      return res.json({
        success: true,
        data: contracts
      });
    } catch (error) {
      return res.status(500).json({
        success: false,
        error: error.message
      });
    }
  }

  async getExpiringContracts(req, res) {
    try {
      const { days = 90 } = req.query;

      const today = new Date();
      const futureDate = new Date(today.getTime() + days * 24 * 60 * 60 * 1000);

      const contracts = await this.db.find({
        expiration_date: {
          $gte: today,
          $lte: futureDate
        },
        status: { $ne: 'EXPIRED' }
      })
        .sort({ expiration_date: 1 });

      return res.json({
        success: true,
        data: contracts,
        daysWindow: days
      });
    } catch (error) {
      return res.status(500).json({
        success: false,
        error: error.message
      });
    }
  }

  async getContractsByParty(req, res) {
    try {
      const { partyId } = req.params;
      const { role = 'any' } = req.query;

      let query = {};

      if (role === 'primary') {
        query.primary_party_id = partyId;
      } else if (role === 'counterparty') {
        query.counterparty_id = partyId;
      } else {
        query.$or = [
          { primary_party_id: partyId },
          { counterparty_id: partyId }
        ];
      }

      const contracts = await this.db.find(query);

      return res.json({
        success: true,
        data: contracts,
        party_id: partyId
      });
    } catch (error) {
      return res.status(500).json({
        success: false,
        error: error.message
      });
    }
  }

  getRouter() {
    return router;
  }
}

module.exports = ContractSearchAPI;

// Example usage
if (require.main === module) {
  const app = express();
  const contractAPI = new ContractSearchAPI({} /* database instance */);

  app.use(contractAPI.getRouter());
  app.listen(3000, () => console.log('API running on port 3000'));
}
