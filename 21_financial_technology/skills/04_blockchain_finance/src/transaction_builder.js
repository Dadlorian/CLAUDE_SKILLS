/**
 * Transaction Builder - Build and execute complex transactions
 */

const { ethers } = require('ethers');

class TransactionBuilder {
  constructor(signer) {
    this.signer = signer;
    this.transactions = [];
  }

  /**
   * Add transaction
   */
  addTransaction(contract, method, args, options = {}) {
    this.transactions.push({
      contract,
      method,
      args,
      options
    });
    return this;
  }

  /**
   * Execute all transactions
   */
  async execute() {
    const results = [];

    for (const tx of this.transactions) {
      console.log(`Executing ${tx.method}...`);

      try {
        const result = await tx.contract[tx.method](...tx.args, tx.options);
        const receipt = await result.wait();

        results.push({
          success: true,
          hash: receipt.transactionHash,
          gasUsed: receipt.gasUsed.toString()
        });

        console.log(`✓ ${tx.method} executed`);
      } catch (error) {
        results.push({
          success: false,
          error: error.message
        });

        console.error(`✗ ${tx.method} failed: ${error.message}`);
      }
    }

    return results;
  }

  /**
   * Estimate gas
   */
  async estimateGas() {
    const estimates = [];

    for (const tx of this.transactions) {
      try {
        const gasEstimate = await tx.contract.estimateGas[tx.method](...tx.args);
        estimates.push({
          method: tx.method,
          gasEstimate: gasEstimate.toString()
        });
      } catch (error) {
        console.error(`Gas estimation failed for ${tx.method}`);
      }
    }

    return estimates;
  }

  /**
   * Clear transactions
   */
  clear() {
    this.transactions = [];
    return this;
  }
}

module.exports = TransactionBuilder;
