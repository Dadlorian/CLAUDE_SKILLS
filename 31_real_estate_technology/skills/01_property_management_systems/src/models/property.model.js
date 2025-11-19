/**
 * Property Data Model
 * Represents a property in the PMS system
 * Framework: Sequelize ORM with PostgreSQL
 */

const { Model, DataTypes } = require('sequelize');

class Property extends Model {
  static init(sequelize) {
    return super.init({
      id: {
        type: DataTypes.UUID,
        defaultValue: DataTypes.UUIDV4,
        primaryKey: true
      },
      propertyName: {
        type: DataTypes.STRING(255),
        allowNull: false,
        field: 'property_name'
      },
      propertyType: {
        type: DataTypes.ENUM('multifamily', 'commercial', 'mixed_use', 'industrial', 'single_family'),
        allowNull: false,
        field: 'property_type'
      },
      streetAddress: {
        type: DataTypes.STRING(255),
        allowNull: false,
        field: 'street_address'
      },
      city: {
        type: DataTypes.STRING(100),
        allowNull: false
      },
      state: {
        type: DataTypes.CHAR(2),
        allowNull: false
      },
      postalCode: {
        type: DataTypes.STRING(10),
        allowNull: false,
        field: 'postal_code'
      },
      country: {
        type: DataTypes.CHAR(2),
        defaultValue: 'US'
      },
      latitude: {
        type: DataTypes.DECIMAL(10, 8)
      },
      longitude: {
        type: DataTypes.DECIMAL(11, 8)
      },
      yearBuilt: {
        type: DataTypes.INTEGER,
        field: 'year_built',
        validate: {
          min: 1800,
          max: new Date().getFullYear() + 5
        }
      },
      totalUnits: {
        type: DataTypes.INTEGER,
        allowNull: false,
        field: 'total_units',
        validate: {
          min: 1
        }
      },
      totalSquareFeet: {
        type: DataTypes.DECIMAL(10, 2),
        field: 'total_square_feet'
      },
      lotSizeAcres: {
        type: DataTypes.DECIMAL(8, 4),
        field: 'lot_size_acres'
      },
      parkingSpaces: {
        type: DataTypes.INTEGER,
        field: 'parking_spaces',
        defaultValue: 0
      },
      taxIdNumber: {
        type: DataTypes.STRING(50),
        field: 'tax_id_number'
      },
      legalDescription: {
        type: DataTypes.TEXT,
        field: 'legal_description'
      },
      acquisitionDate: {
        type: DataTypes.DATEONLY,
        field: 'acquisition_date'
      },
      acquisitionPrice: {
        type: DataTypes.DECIMAL(15, 2),
        field: 'acquisition_price'
      },
      currentValue: {
        type: DataTypes.DECIMAL(15, 2),
        field: 'current_value'
      },
      status: {
        type: DataTypes.ENUM('active', 'inactive', 'under_construction', 'sold'),
        defaultValue: 'active'
      },
      portfolioId: {
        type: DataTypes.UUID,
        field: 'portfolio_id',
        references: {
          model: 'portfolios',
          key: 'id'
        }
      },
      amenities: {
        type: DataTypes.JSONB,
        defaultValue: []
      },
      managerId: {
        type: DataTypes.UUID,
        field: 'manager_id',
        references: {
          model: 'users',
          key: 'id'
        }
      }
    }, {
      sequelize,
      tableName: 'properties',
      underscored: true,
      timestamps: true,
      indexes: [
        { fields: ['status'] },
        { fields: ['property_type'] },
        { fields: ['city', 'state'] },
        { fields: ['portfolio_id'] },
        { fields: ['manager_id'] }
      ]
    });
  }

  static associate(models) {
    // Property has many Units
    this.hasMany(models.Unit, {
      foreignKey: 'propertyId',
      as: 'units'
    });

    // Property has many Buildings
    this.hasMany(models.Building, {
      foreignKey: 'propertyId',
      as: 'buildings'
    });

    // Property has many Leases
    this.hasMany(models.Lease, {
      foreignKey: 'propertyId',
      as: 'leases'
    });

    // Property belongs to Portfolio
    this.belongsTo(models.Portfolio, {
      foreignKey: 'portfolioId',
      as: 'portfolio'
    });

    // Property has one Manager (User)
    this.belongsTo(models.User, {
      foreignKey: 'managerId',
      as: 'manager'
    });

    // Property has many Owners (through junction)
    this.belongsToMany(models.Owner, {
      through: 'property_owners',
      foreignKey: 'propertyId',
      otherKey: 'ownerId',
      as: 'owners'
    });
  }

  // Instance Methods

  /**
   * Get full address as formatted string
   */
  getFullAddress() {
    return `${this.streetAddress}, ${this.city}, ${this.state} ${this.postalCode}`;
  }

  /**
   * Calculate current occupancy rate
   */
  async getOccupancyRate() {
    const units = await this.getUnits();
    if (units.length === 0) return 0;

    const occupied = units.filter(u => u.unitStatus === 'occupied').length;
    return (occupied / units.length) * 100;
  }

  /**
   * Get active leases
   */
  async getActiveLeases() {
    const Lease = this.sequelize.models.Lease;
    return await Lease.findAll({
      where: {
        propertyId: this.id,
        leaseStatus: 'active'
      }
    });
  }

  /**
   * Calculate monthly revenue
   */
  async getMonthlyRevenue() {
    const leases = await this.getActiveLeases();
    return leases.reduce((sum, lease) => sum + parseFloat(lease.totalMonthlyRent), 0);
  }

  /**
   * Get available units
   */
  async getAvailableUnits(moveInDate = new Date()) {
    const Unit = this.sequelize.models.Unit;
    return await Unit.findAll({
      where: {
        propertyId: this.id,
        unitStatus: 'vacant',
        availabilityDate: {
          [this.sequelize.Op.lte]: moveInDate
        }
      }
    });
  }

  // Class Methods

  /**
   * Find properties by city and state
   */
  static async findByLocation(city, state) {
    return await this.findAll({
      where: { city, state, status: 'active' }
    });
  }

  /**
   * Get portfolio summary
   */
  static async getPortfolioSummary(portfolioId) {
    const properties = await this.findAll({
      where: { portfolioId, status: 'active' },
      include: [{ model: this.sequelize.models.Unit, as: 'units' }]
    });

    const summary = {
      totalProperties: properties.length,
      totalUnits: 0,
      occupiedUnits: 0,
      totalSquareFeet: 0,
      averageOccupancy: 0
    };

    properties.forEach(property => {
      summary.totalUnits += property.units.length;
      summary.occupiedUnits += property.units.filter(
        u => u.unitStatus === 'occupied'
      ).length;
      summary.totalSquareFeet += parseFloat(property.totalSquareFeet || 0);
    });

    summary.averageOccupancy = summary.totalUnits > 0
      ? (summary.occupiedUnits / summary.totalUnits) * 100
      : 0;

    return summary;
  }

  /**
   * Search properties
   */
  static async search(filters = {}) {
    const where = {};

    if (filters.city) where.city = filters.city;
    if (filters.state) where.state = filters.state;
    if (filters.propertyType) where.propertyType = filters.propertyType;
    if (filters.status) where.status = filters.status;

    if (filters.minUnits) {
      where.totalUnits = { [this.sequelize.Op.gte]: filters.minUnits };
    }
    if (filters.maxUnits) {
      where.totalUnits = {
        ...where.totalUnits,
        [this.sequelize.Op.lte]: filters.maxUnits
      };
    }

    return await this.findAll({
      where,
      order: [['propertyName', 'ASC']]
    });
  }
}

module.exports = Property;
