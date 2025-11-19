#!/usr/bin/env node

/**
 * Complete Quickstart Example: Payment Processing
 *
 * This example demonstrates:
 * - API authentication
 * - Creating a charge
 * - Handling responses
 * - Error handling
 *
 * Prerequisites:
 * - Node.js 14+
 * - npm install axios dotenv
 */

const axios = require('axios');
require('dotenv').config();

// Configuration
const API_KEY = process.env.API_KEY || 'sk_live_YOUR_KEY_HERE';
const API_BASE_URL = 'https://api.example.com/v1';

// Initialize API client with authentication
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Authorization': `Bearer ${API_KEY}`,
    'Content-Type': 'application/json'
  }
});

/**
 * Create a charge
 *
 * @param {number} amount - Amount in cents (e.g., 2000 = $20.00)
 * @param {string} currency - Currency code (usd, eur, gbp, etc.)
 * @param {string} description - Charge description
 * @returns {Promise<Object>} Charge response
 */
async function createCharge(amount, currency = 'usd', description = 'Test charge') {
  try {
    console.log('Creating charge...');
    console.log(`Amount: $${(amount / 100).toFixed(2)} ${currency.toUpperCase()}`);

    const response = await apiClient.post('/charges', {
      amount,
      currency,
      description
    });

    console.log('\n✅ Charge created successfully!');
    console.log(`Charge ID: ${response.data.id}`);
    console.log(`Status: ${response.data.status}`);
    console.log(`Amount: ${response.data.amount} ${response.data.currency}`);

    return response.data;

  } catch (error) {
    console.error('\n❌ Error creating charge:');

    // Handle different error types
    if (error.response) {
      // Server responded with error status
      console.error(`Status: ${error.response.status}`);
      console.error(`Error: ${error.response.data.error?.message}`);

      // Specific error handling
      switch (error.response.status) {
        case 401:
          console.error('Check your API key');
          break;
        case 400:
          console.error('Invalid parameters. Check amount, currency, etc.');
          break;
        case 429:
          console.error('Rate limited. Wait before retrying.');
          break;
      }
    } else if (error.request) {
      // Request made but no response
      console.error('No response from server. Check your internet connection.');
    } else {
      // Error in request setup
      console.error(error.message);
    }

    throw error;
  }
}

/**
 * Retrieve a charge
 *
 * @param {string} chargeId - The charge ID to retrieve
 * @returns {Promise<Object>} Charge details
 */
async function getCharge(chargeId) {
  try {
    const response = await apiClient.get(`/charges/${chargeId}`);
    return response.data;
  } catch (error) {
    console.error(`Failed to retrieve charge ${chargeId}:`, error.message);
    throw error;
  }
}

/**
 * Refund a charge
 *
 * @param {string} chargeId - The charge ID to refund
 * @returns {Promise<Object>} Refund response
 */
async function refundCharge(chargeId) {
  try {
    console.log(`Refunding charge ${chargeId}...`);

    const response = await apiClient.post(`/charges/${chargeId}/refund`);

    console.log('✅ Refund processed');
    console.log(`Refund ID: ${response.data.refund_id}`);

    return response.data;
  } catch (error) {
    console.error('Failed to refund charge:', error.message);
    throw error;
  }
}

/**
 * Main execution
 */
async function main() {
  try {
    // Create a test charge
    const charge = await createCharge(2000, 'usd', 'Test payment');

    // Retrieve the charge
    console.log('\nRetrieving charge details...');
    const retrieved = await getCharge(charge.id);
    console.log(`Retrieved status: ${retrieved.status}`);

    // Uncomment to test refund
    // await refundCharge(charge.id);

  } catch (error) {
    process.exit(1);
  }
}

// Run if executed directly
if (require.main === module) {
  main();
}

module.exports = {
  createCharge,
  getCharge,
  refundCharge,
  apiClient
};
