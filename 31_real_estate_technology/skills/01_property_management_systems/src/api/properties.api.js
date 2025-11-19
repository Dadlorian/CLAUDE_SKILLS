/**
 * Properties API Routes
 * RESTful endpoints for property management
 * Framework: Express.js
 */

const express = require('express');
const router = express.Router();
const { Property, Unit, Lease } = require('../models');
const { authenticate, authorize } = require('../middleware/auth');
const { validateProperty } = require('../middleware/validation');
const { paginate } = require('../utils/pagination');

/**
 * @route   GET /api/properties
 * @desc    List all properties with filtering and pagination
 * @access  Private
 */
router.get('/', authenticate, async (req, res) => {
  try {
    const {
      page = 1,
      limit = 20,
      status,
      property_type,
      city,
      state,
      sort = 'property_name',
      order = 'asc'
    } = req.query;

    // Build filter criteria
    const where = {};
    if (status) where.status = status;
    if (property_type) where.propertyType = property_type;
    if (city) where.city = city;
    if (state) where.state = state;

    // Execute query with pagination
    const { rows: properties, count } = await Property.findAndCountAll({
      where,
      limit: parseInt(limit),
      offset: (parseInt(page) - 1) * parseInt(limit),
      order: [[sort, order.toUpperCase()]],
      attributes: {
        exclude: ['legalDescription'] // Exclude large text fields from list
      }
    });

    // Calculate occupancy for each property
    const propertiesWithMetrics = await Promise.all(
      properties.map(async (property) => {
        const occupancyRate = await property.getOccupancyRate();
        const monthlyRevenue = await property.getMonthlyRevenue();

        return {
          ...property.toJSON(),
          occupancyRate: parseFloat(occupancyRate.toFixed(2)),
          monthlyRevenue: parseFloat(monthlyRevenue.toFixed(2))
        };
      })
    );

    res.json({
      data: propertiesWithMetrics,
      pagination: paginate(count, parseInt(page), parseInt(limit))
    });
  } catch (error) {
    console.error('Error fetching properties:', error);
    res.status(500).json({ error: 'Failed to fetch properties' });
  }
});

/**
 * @route   GET /api/properties/:id
 * @desc    Get property details by ID
 * @access  Private
 */
router.get('/:id', authenticate, async (req, res) => {
  try {
    const property = await Property.findByPk(req.params.id, {
      include: [
        {
          model: Unit,
          as: 'units',
          attributes: ['id', 'unitNumber', 'unitType', 'unitStatus', 'currentRent']
        },
        {
          model: require('../models/User'),
          as: 'manager',
          attributes: ['id', 'firstName', 'lastName', 'email', 'phone']
        }
      ]
    });

    if (!property) {
      return res.status(404).json({ error: 'Property not found' });
    }

    // Add computed metrics
    const occupancyRate = await property.getOccupancyRate();
    const monthlyRevenue = await property.getMonthlyRevenue();
    const activeLeases = await property.getActiveLeases();

    const response = {
      ...property.toJSON(),
      metrics: {
        occupancyRate: parseFloat(occupancyRate.toFixed(2)),
        monthlyRevenue: parseFloat(monthlyRevenue.toFixed(2)),
        activeLeaseCount: activeLeases.length,
        totalUnits: property.units.length,
        occupiedUnits: property.units.filter(u => u.unitStatus === 'occupied').length,
        vacantUnits: property.units.filter(u => u.unitStatus === 'vacant').length
      }
    };

    res.json(response);
  } catch (error) {
    console.error('Error fetching property:', error);
    res.status(500).json({ error: 'Failed to fetch property' });
  }
});

/**
 * @route   POST /api/properties
 * @desc    Create a new property
 * @access  Private (Admin, Portfolio Manager)
 */
router.post('/',
  authenticate,
  authorize(['admin', 'portfolio_manager']),
  validateProperty,
  async (req, res) => {
    try {
      const property = await Property.create({
        ...req.body,
        managerId: req.body.managerId || req.user.id
      });

      // Log activity
      await require('../services/audit').logActivity({
        userId: req.user.id,
        action: 'property.created',
        resourceType: 'property',
        resourceId: property.id,
        details: { propertyName: property.propertyName }
      });

      res.status(201).json(property);
    } catch (error) {
      console.error('Error creating property:', error);

      if (error.name === 'SequelizeValidationError') {
        return res.status(400).json({
          error: 'Validation failed',
          details: error.errors.map(e => ({
            field: e.path,
            message: e.message
          }))
        });
      }

      res.status(500).json({ error: 'Failed to create property' });
    }
  }
);

/**
 * @route   PUT /api/properties/:id
 * @desc    Update property
 * @access  Private (Admin, Portfolio Manager, Property Manager)
 */
router.put('/:id',
  authenticate,
  authorize(['admin', 'portfolio_manager', 'property_manager']),
  validateProperty,
  async (req, res) => {
    try {
      const property = await Property.findByPk(req.params.id);

      if (!property) {
        return res.status(404).json({ error: 'Property not found' });
      }

      // Check authorization - property managers can only edit their properties
      if (req.user.role === 'property_manager' &&
          property.managerId !== req.user.id) {
        return res.status(403).json({ error: 'Not authorized to edit this property' });
      }

      await property.update(req.body);

      // Log activity
      await require('../services/audit').logActivity({
        userId: req.user.id,
        action: 'property.updated',
        resourceType: 'property',
        resourceId: property.id,
        details: { changes: req.body }
      });

      res.json(property);
    } catch (error) {
      console.error('Error updating property:', error);

      if (error.name === 'SequelizeValidationError') {
        return res.status(400).json({
          error: 'Validation failed',
          details: error.errors.map(e => ({
            field: e.path,
            message: e.message
          }))
        });
      }

      res.status(500).json({ error: 'Failed to update property' });
    }
  }
);

/**
 * @route   DELETE /api/properties/:id
 * @desc    Delete property (soft delete)
 * @access  Private (Admin only)
 */
router.delete('/:id',
  authenticate,
  authorize(['admin']),
  async (req, res) => {
    try {
      const property = await Property.findByPk(req.params.id);

      if (!property) {
        return res.status(404).json({ error: 'Property not found' });
      }

      // Check if property has active leases
      const activeLeases = await property.getActiveLeases();
      if (activeLeases.length > 0) {
        return res.status(400).json({
          error: 'Cannot delete property with active leases',
          activeLeaseCount: activeLeases.length
        });
      }

      // Soft delete (set status to inactive)
      await property.update({ status: 'inactive' });

      // Log activity
      await require('../services/audit').logActivity({
        userId: req.user.id,
        action: 'property.deleted',
        resourceType: 'property',
        resourceId: property.id
      });

      res.status(204).send();
    } catch (error) {
      console.error('Error deleting property:', error);
      res.status(500).json({ error: 'Failed to delete property' });
    }
  }
);

/**
 * @route   GET /api/properties/:id/units
 * @desc    Get all units for a property
 * @access  Private
 */
router.get('/:id/units', authenticate, async (req, res) => {
  try {
    const { status, unit_type, available_by } = req.query;

    const where = { propertyId: req.params.id };
    if (status) where.unitStatus = status;
    if (unit_type) where.unitType = unit_type;
    if (available_by) {
      where.availabilityDate = {
        [require('sequelize').Op.lte]: new Date(available_by)
      };
    }

    const units = await Unit.findAll({
      where,
      order: [['unitNumber', 'ASC']]
    });

    res.json({ data: units });
  } catch (error) {
    console.error('Error fetching units:', error);
    res.status(500).json({ error: 'Failed to fetch units' });
  }
});

/**
 * @route   GET /api/properties/:id/financial-summary
 * @desc    Get financial summary for a property
 * @access  Private (Admin, Portfolio Manager, Property Manager)
 */
router.get('/:id/financial-summary',
  authenticate,
  authorize(['admin', 'portfolio_manager', 'property_manager']),
  async (req, res) => {
    try {
      const { start_date, end_date } = req.query;

      if (!start_date || !end_date) {
        return res.status(400).json({
          error: 'start_date and end_date are required'
        });
      }

      const financialService = require('../services/financial');
      const summary = await financialService.getPropertyFinancialSummary(
        req.params.id,
        new Date(start_date),
        new Date(end_date)
      );

      res.json(summary);
    } catch (error) {
      console.error('Error generating financial summary:', error);
      res.status(500).json({ error: 'Failed to generate financial summary' });
    }
  }
);

/**
 * @route   GET /api/properties/:id/rent-roll
 * @desc    Get rent roll for a property
 * @access  Private (Admin, Portfolio Manager, Property Manager)
 */
router.get('/:id/rent-roll',
  authenticate,
  authorize(['admin', 'portfolio_manager', 'property_manager']),
  async (req, res) => {
    try {
      const { as_of_date } = req.query;

      const reportService = require('../services/reports');
      const rentRoll = await reportService.generateRentRoll(
        req.params.id,
        as_of_date ? new Date(as_of_date) : new Date()
      );

      res.json(rentRoll);
    } catch (error) {
      console.error('Error generating rent roll:', error);
      res.status(500).json({ error: 'Failed to generate rent roll' });
    }
  }
);

/**
 * @route   GET /api/properties/search
 * @desc    Search properties
 * @access  Private
 */
router.get('/search', authenticate, async (req, res) => {
  try {
    const properties = await Property.search(req.query);
    res.json({ data: properties });
  } catch (error) {
    console.error('Error searching properties:', error);
    res.status(500).json({ error: 'Search failed' });
  }
});

module.exports = router;
