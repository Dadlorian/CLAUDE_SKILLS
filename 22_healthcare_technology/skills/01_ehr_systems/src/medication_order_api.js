/**
 * Medication Order API
 * RESTful API for CPOE medication ordering with CDS integration
 */

const express = require('express');
const router = express.Router();

// Mock database and CDS service
const db = require('../services/database');
const cdsService = require('../services/clinical-decision-support');

/**
 * Create new medication order
 * POST /api/orders/medications
 */
router.post('/medications', async (req, res) => {
  try {
    const {
      patient_id,
      encounter_id,
      medication,
      dose,
      dose_unit,
      route,
      frequency,
      duration,
      indication,
      ordering_provider_id
    } = req.body;

    // Validate required fields
    if (!patient_id || !medication || !dose || !route || !frequency) {
      return res.status(400).json({
        error: 'Missing required fields'
      });
    }

    // Run clinical decision support checks
    const cdsAlerts = await runCDSChecks(patient_id, medication, dose);

    // If critical alerts, block order
    const criticalAlerts = cdsAlerts.filter(a => a.severity === 'critical');
    if (criticalAlerts.length > 0 && !req.body.override_reason) {
      return res.status(422).json({
        error: 'Critical alerts must be resolved',
        alerts: criticalAlerts
      });
    }

    // Create order
    const order = await db.medication_order.create({
      patient_id,
      encounter_id,
      medication_name: medication,
      dose_quantity: dose,
      dose_unit_code: dose_unit,
      route_code: route,
      frequency_code: frequency,
      duration,
      clinical_indication: indication,
      ordering_provider_id,
      order_status_code: 'ACTIVE',
      start_datetime: new Date()
    });

    // Log CDS alerts that were overridden
    if (req.body.override_reason) {
      await db.cds_alert_log.create({
        order_id: order.order_id,
        alerts: cdsAlerts,
        override_reason: req.body.override_reason,
        overridden_by: ordering_provider_id
      });
    }

    res.status(201).json({
      order_id: order.order_id,
      status: 'created',
      alerts: cdsAlerts
    });
  } catch (error) {
    console.error('Error creating medication order:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

/**
 * Run CDS checks for medication order
 */
async function runCDSChecks(patient_id, medication, dose) {
  const alerts = [];

  // Get patient's current medications
  const currentMeds = await db.medication_order.findAll({
    where: { patient_id, order_status_code: 'ACTIVE' }
  });

  // Check drug-drug interactions
  for (const med of currentMeds) {
    const interaction = await cdsService.checkDrugInteraction(medication, med.medication_name);
    if (interaction) {
      alerts.push({
        type: 'drug-drug-interaction',
        severity: interaction.severity,
        message: `${medication} + ${med.medication_name}: ${interaction.description}`,
        recommendation: interaction.recommendation
      });
    }
  }

  // Check drug-allergy interactions
  const allergies = await db.allergy.findAll({
    where: { patient_id, allergy_status_code: 'ACTIVE' }
  });

  for (const allergy of allergies) {
    const allergyCheck = await cdsService.checkDrugAllergy(medication, allergy.allergen_code);
    if (allergyCheck.matches) {
      alerts.push({
        type: 'drug-allergy',
        severity: 'critical',
        message: `Patient allergic to ${allergy.allergen_name}`,
        recommendation: 'Do not administer. Choose alternative medication.'
      });
    }
  }

  // Check dose range
  const doseCheck = await cdsService.checkDoseRange(medication, dose);
  if (!doseCheck.withinRange) {
    alerts.push({
      type: 'dose-range',
      severity: 'warning',
      message: `Dose ${dose} ${doseCheck.unit} outside recommended range`,
      recommendation: `Recommended: ${doseCheck.min}-${doseCheck.max} ${doseCheck.unit}`
    });
  }

  return alerts;
}

/**
 * Get active medication orders for patient
 * GET /api/orders/medications/:patient_id
 */
router.get('/medications/:patient_id', async (req, res) => {
  try {
    const { patient_id } = req.params;

    const orders = await db.medication_order.findAll({
      where: {
        patient_id,
        order_status_code: 'ACTIVE'
      },
      order: [['ordered_datetime', 'DESC']]
    });

    res.json({ orders });
  } catch (error) {
    console.error('Error fetching medication orders:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

/**
 * Discontinue medication order
 * PUT /api/orders/medications/:order_id/discontinue
 */
router.put('/medications/:order_id/discontinue', async (req, res) => {
  try {
    const { order_id } = req.params;
    const { reason, discontinued_by } = req.body;

    await db.medication_order.update(
      {
        order_status_code: 'DISCONTINUED',
        stop_datetime: new Date(),
        discontinue_reason: reason
      },
      { where: { order_id } }
    );

    res.json({ message: 'Order discontinued successfully' });
  } catch (error) {
    console.error('Error discontinuing order:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

module.exports = router;
