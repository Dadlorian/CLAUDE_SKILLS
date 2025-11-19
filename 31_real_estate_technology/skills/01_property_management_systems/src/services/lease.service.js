/**
 * Lease Service
 * Business logic for lease management
 */

const { Lease, Unit, Tenant, Ledger } = require('../models');
const { Op } = require('sequelize');
const moment = require('moment');

class LeaseService {
  /**
   * Create a new lease
   */
  async createLease(leaseData, tenantIds) {
    const transaction = await Lease.sequelize.transaction();

    try {
      // Validate unit is available
      const unit = await Unit.findByPk(leaseData.unitId);
      if (!unit) {
        throw new Error('Unit not found');
      }

      if (unit.unitStatus !== 'vacant') {
        throw new Error('Unit is not available');
      }

      // Check for overlapping leases
      const overlapping = await this.checkOverlappingLeases(
        leaseData.unitId,
        leaseData.startDate,
        leaseData.endDate
      );

      if (overlapping) {
        throw new Error('Overlapping lease exists for this unit and date range');
      }

      // Create lease
      const lease = await Lease.create({
        ...leaseData,
        leaseNumber: await this.generateLeaseNumber(),
        leaseStatus: 'pending'
      }, { transaction });

      // Add tenants
      await lease.addTenants(tenantIds, { transaction });

      // Update unit status
      await unit.update({
        unitStatus: 'leased',
        leaseStatus: 'pending',
        availabilityDate: null
      }, { transaction });

      // Generate initial charges
      await this.generateInitialCharges(lease.id, { transaction });

      await transaction.commit();

      // Return lease with associations
      return await Lease.findByPk(lease.id, {
        include: [
          { model: Unit, as: 'unit' },
          { model: Tenant, as: 'tenants' }
        ]
      });
    } catch (error) {
      await transaction.rollback();
      throw error;
    }
  }

  /**
   * Generate unique lease number
   */
  async generateLeaseNumber() {
    const year = new Date().getFullYear();
    const count = await Lease.count({
      where: {
        createdAt: {
          [Op.gte]: new Date(`${year}-01-01`),
          [Op.lt]: new Date(`${year + 1}-01-01`)
        }
      }
    });

    return `L-${year}-${String(count + 1).padStart(6, '0')}`;
  }

  /**
   * Check for overlapping leases
   */
  async checkOverlappingLeases(unitId, startDate, endDate) {
    const overlapping = await Lease.findOne({
      where: {
        unitId,
        leaseStatus: {
          [Op.in]: ['pending', 'active']
        },
        startDate: { [Op.lte]: endDate },
        endDate: { [Op.gte]: startDate }
      }
    });

    return overlapping !== null;
  }

  /**
   * Generate initial charges for new lease
   */
  async generateInitialCharges(leaseId, options = {}) {
    const lease = await Lease.findByPk(leaseId);

    const charges = [];

    // Pro-rated first month rent if mid-month move-in
    const moveInDate = moment(lease.moveInDate);
    const firstDayOfMonth = moveInDate.clone().startOf('month');

    if (!moveInDate.isSame(firstDayOfMonth, 'day')) {
      const daysInMonth = moveInDate.daysInMonth();
      const daysOccupied = daysInMonth - moveInDate.date() + 1;
      const proRatedRent = (lease.totalMonthlyRent / daysInMonth) * daysOccupied;

      charges.push({
        leaseId,
        transactionDate: moveInDate.toDate(),
        transactionType: 'charge',
        chargeCode: 'RENT',
        amount: parseFloat(proRatedRent.toFixed(2)),
        description: `Pro-rated rent for ${moveInDate.format('MMMM YYYY')}`
      });
    } else {
      // Full month rent
      charges.push({
        leaseId,
        transactionDate: moveInDate.toDate(),
        transactionType: 'charge',
        chargeCode: 'RENT',
        amount: lease.totalMonthlyRent,
        description: `Rent for ${moveInDate.format('MMMM YYYY')}`
      });
    }

    // Security deposit
    if (lease.securityDeposit > 0) {
      charges.push({
        leaseId,
        transactionDate: moveInDate.toDate(),
        transactionType: 'charge',
        chargeCode: 'DEPOSIT',
        amount: lease.securityDeposit,
        description: 'Security deposit'
      });
    }

    // Pet deposit
    if (lease.petDeposit > 0) {
      charges.push({
        leaseId,
        transactionDate: moveInDate.toDate(),
        transactionType: 'charge',
        chargeCode: 'PET_DEPOSIT',
        amount: lease.petDeposit,
        description: 'Pet deposit'
      });
    }

    // Create all charges
    await Ledger.bulkCreate(charges, options);

    return charges;
  }

  /**
   * Renew lease
   */
  async renewLease(leaseId, renewalData) {
    const transaction = await Lease.sequelize.transaction();

    try {
      const currentLease = await Lease.findByPk(leaseId, {
        include: [{ model: Tenant, as: 'tenants' }]
      });

      if (!currentLease) {
        throw new Error('Lease not found');
      }

      if (currentLease.leaseStatus !== 'active') {
        throw new Error('Only active leases can be renewed');
      }

      // Create new lease
      const newLease = await Lease.create({
        unitId: currentLease.unitId,
        propertyId: currentLease.propertyId,
        leaseType: renewalData.leaseType || currentLease.leaseType,
        startDate: renewalData.startDate,
        endDate: renewalData.endDate,
        baseRent: renewalData.baseRent,
        petRent: renewalData.petRent || currentLease.petRent,
        parkingRent: renewalData.parkingRent || currentLease.parkingRent,
        totalMonthlyRent: renewalData.totalMonthlyRent,
        securityDeposit: currentLease.securityDeposit,
        petDeposit: currentLease.petDeposit,
        leaseTermMonths: renewalData.leaseTermMonths,
        rentDueDay: currentLease.rentDueDay,
        lateFeeAmount: currentLease.lateFeeAmount,
        lateFeeGraceDays: currentLease.lateFeeGraceDays,
        previousLeaseId: currentLease.id,
        renewalCount: currentLease.renewalCount + 1,
        leaseStatus: 'pending',
        leaseNumber: await this.generateLeaseNumber()
      }, { transaction });

      // Copy tenants to new lease
      const tenantIds = currentLease.tenants.map(t => t.id);
      await newLease.addTenants(tenantIds, { transaction });

      // Update current lease
      await currentLease.update({
        leaseStatus: 'renewed',
        endDate: renewalData.startDate // End on new lease start date
      }, { transaction });

      await transaction.commit();

      return await Lease.findByPk(newLease.id, {
        include: [
          { model: Unit, as: 'unit' },
          { model: Tenant, as: 'tenants' }
        ]
      });
    } catch (error) {
      await transaction.rollback();
      throw error;
    }
  }

  /**
   * Terminate lease
   */
  async terminateLease(leaseId, terminationData) {
    const transaction = await Lease.sequelize.transaction();

    try {
      const lease = await Lease.findByPk(leaseId);

      if (!lease) {
        throw new Error('Lease not found');
      }

      if (lease.leaseStatus !== 'active') {
        throw new Error('Only active leases can be terminated');
      }

      // Update lease
      await lease.update({
        leaseStatus: 'terminated',
        noticeDate: terminationData.noticeDate,
        moveOutDate: terminationData.moveOutDate,
        terminationReason: terminationData.reason,
        earlyTermination: terminationData.earlyTermination || false
      }, { transaction });

      // Update unit
      const unit = await Unit.findByPk(lease.unitId);
      await unit.update({
        unitStatus: 'vacant',
        leaseStatus: 'vacant',
        availabilityDate: terminationData.moveOutDate
      }, { transaction });

      // If early termination, apply fee
      if (terminationData.earlyTermination && terminationData.terminationFee) {
        await Ledger.create({
          leaseId,
          transactionDate: new Date(),
          transactionType: 'charge',
          chargeCode: 'TERM_FEE',
          amount: terminationData.terminationFee,
          description: 'Early termination fee'
        }, { transaction });
      }

      await transaction.commit();

      return await Lease.findByPk(leaseId);
    } catch (error) {
      await transaction.rollback();
      throw error;
    }
  }

  /**
   * Get leases expiring soon
   */
  async getExpiring Leases(daysAhead = 90) {
    const targetDate = moment().add(daysAhead, 'days').toDate();

    return await Lease.findAll({
      where: {
        leaseStatus: 'active',
        endDate: {
          [Op.lte]: targetDate,
          [Op.gte]: new Date()
        }
      },
      include: [
        { model: Unit, as: 'unit' },
        { model: Tenant, as: 'tenants' }
      ],
      order: [['endDate', 'ASC']]
    });
  }

  /**
   * Calculate lease financials
   */
  async getLeaseFinancials(leaseId) {
    const ledger = await Ledger.findAll({
      where: { leaseId },
      order: [['transactionDate', 'ASC']]
    });

    const financials = {
      totalCharges: 0,
      totalPayments: 0,
      currentBalance: 0,
      securityDepositHeld: 0,
      totalRentCharged: 0,
      totalRentPaid: 0,
      lateFees: 0,
      otherCharges: 0
    };

    ledger.forEach(entry => {
      const amount = parseFloat(entry.amount);

      if (entry.transactionType === 'charge') {
        financials.totalCharges += amount;

        if (entry.chargeCode === 'RENT') {
          financials.totalRentCharged += amount;
        } else if (entry.chargeCode === 'LATE') {
          financials.lateFees += amount;
        } else if (entry.chargeCode === 'DEPOSIT') {
          financials.securityDepositHeld += amount;
        } else {
          financials.otherCharges += amount;
        }
      } else if (entry.transactionType === 'payment') {
        financials.totalPayments += Math.abs(amount);
        if (entry.appliedTo === 'RENT') {
          financials.totalRentPaid += Math.abs(amount);
        }
      }
    });

    financials.currentBalance = financials.totalCharges - financials.totalPayments;

    return financials;
  }

  /**
   * Process monthly rent charges
   */
  async processMonthlyRentCharges(date = new Date()) {
    const activeLeases = await Lease.findAll({
      where: {
        leaseStatus: 'active',
        startDate: { [Op.lte]: date },
        endDate: { [Op.gte]: date }
      }
    });

    const charges = [];

    for (const lease of activeLeases) {
      const chargeDate = moment(date).date(lease.rentDueDay).toDate();

      // Check if charge already exists for this month
      const existingCharge = await Ledger.findOne({
        where: {
          leaseId: lease.id,
          chargeCode: 'RENT',
          transactionDate: {
            [Op.gte]: moment(chargeDate).startOf('month').toDate(),
            [Op.lte]: moment(chargeDate).endOf('month').toDate()
          }
        }
      });

      if (!existingCharge) {
        charges.push({
          leaseId: lease.id,
          transactionDate: chargeDate,
          transactionType: 'charge',
          chargeCode: 'RENT',
          amount: lease.totalMonthlyRent,
          description: `Rent for ${moment(chargeDate).format('MMMM YYYY')}`,
          autoGenerated: true
        });
      }
    }

    if (charges.length > 0) {
      await Ledger.bulkCreate(charges);
    }

    return {
      processed: charges.length,
      totalAmount: charges.reduce((sum, c) => sum + c.amount, 0)
    };
  }
}

module.exports = new LeaseService();
