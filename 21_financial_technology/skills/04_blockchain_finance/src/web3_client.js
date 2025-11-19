/**
 * Web3 Client - DeFi Application Client
 * Handles blockchain interactions
 */

const { ethers } = require('ethers');

class Web3Client {
  constructor(rpcUrl) {
    this.provider = new ethers.providers.JsonRpcProvider(rpcUrl);
    this.signer = null;
  }

  /**
   * Connect wallet
   */
  async connectWallet() {
    if (!window.ethereum) {
      throw new Error('MetaMask not installed');
    }

    const accounts = await window.ethereum.request({
      method: 'eth_requestAccounts'
    });

    this.signer = new ethers.providers.Web3Provider(window.ethereum).getSigner();
    return accounts[0];
  }

  /**
   * Get balance
   */
  async getBalance(address) {
    const balance = await this.provider.getBalance(address);
    return ethers.utils.formatEther(balance);
  }

  /**
   * Send transaction
   */
  async sendTransaction(to, amount) {
    const tx = await this.signer.sendTransaction({
      to,
      value: ethers.utils.parseEther(amount)
    });
    return await tx.wait();
  }

  /**
   * Get contract
   */
  getContract(address, abi) {
    return new ethers.Contract(address, abi, this.signer);
  }

  /**
   * Get current network
   */
  async getNetwork() {
    return await this.provider.getNetwork();
  }

  /**
   * Listen to events
   */
  onEvent(contract, eventName, callback) {
    const filter = contract.filters[eventName]();
    contract.on(filter, (...args) => callback(args));
  }
}

module.exports = Web3Client;
