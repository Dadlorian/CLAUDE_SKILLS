/**
 * Event Listener - Listen to smart contract events
 */

const { ethers } = require('ethers');

class EventListener {
  constructor(provider) {
    this.provider = provider;
    this.listeners = [];
  }

  /**
   * Listen to contract events
   */
  onContractEvent(contract, eventName, callback, fromBlock = 'latest') {
    const filter = contract.filters[eventName]();

    contract.on(filter, (...args) => {
      const event = args[args.length - 1];
      console.log(`Event ${eventName}:`, {
        blockNumber: event.blockNumber,
        transactionHash: event.transactionHash,
        args: args.slice(0, -1)
      });

      callback(args.slice(0, -1));
    });

    this.listeners.push({ contract, filter });
  }

  /**
   * Listen to transfers
   */
  onTransfer(contract, callback) {
    const filter = contract.filters.Transfer();

    contract.on(filter, (from, to, value, event) => {
      console.log(`Transfer: ${from} → ${to} (${ethers.utils.formatEther(value)})`);
      callback({ from, to, value });
    });
  }

  /**
   * Listen to swaps
   */
  onSwap(contract, callback) {
    const filter = contract.filters.Swap();

    contract.on(filter, (sender, amount0In, amount1In, amount0Out, amount1Out, to, event) => {
      console.log(`Swap detected at block ${event.blockNumber}`);
      callback({ sender, amount0In, amount1In, amount0Out, amount1Out, to });
    });
  }

  /**
   * Stop listening to all events
   */
  removeAllListeners() {
    for (const listener of this.listeners) {
      listener.contract.removeAllListeners(listener.filter);
    }

    this.listeners = [];
  }
}

module.exports = EventListener;
