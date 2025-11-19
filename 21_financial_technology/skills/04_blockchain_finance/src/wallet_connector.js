/**
 * Wallet Connector - Connect and manage wallets
 */

const { ethers } = require('ethers');

class WalletConnector {
  constructor() {
    this.provider = null;
    this.signer = null;
    this.account = null;
    this.network = null;
  }

  /**
   * Connect MetaMask
   */
  async connectMetaMask() {
    if (!window.ethereum) {
      throw new Error('MetaMask not installed');
    }

    const provider = new ethers.providers.Web3Provider(window.ethereum);
    const accounts = await provider.send('eth_requestAccounts', []);

    this.provider = provider;
    this.signer = provider.getSigner();
    this.account = accounts[0];
    this.network = await provider.getNetwork();

    this.setupEventListeners();

    return {
      account: this.account,
      network: this.network.name,
      chainId: this.network.chainId
    };
  }

  /**
   * Setup wallet event listeners
   */
  setupEventListeners() {
    window.ethereum.on('accountsChanged', (accounts) => {
      if (accounts.length === 0) {
        this.disconnect();
      } else {
        this.account = accounts[0];
        console.log('Account changed:', this.account);
      }
    });

    window.ethereum.on('chainChanged', (chainId) => {
      console.log('Network changed:', parseInt(chainId, 16));
      window.location.reload();
    });
  }

  /**
   * Switch network
   */
  async switchNetwork(chainId) {
    try {
      await window.ethereum.request({
        method: 'wallet_switchEthereumChain',
        params: [{ chainId: `0x${chainId.toString(16)}` }]
      });
    } catch (error) {
      if (error.code === 4902) {
        throw new Error('Network not added to MetaMask');
      }
      throw error;
    }
  }

  /**
   * Sign message
   */
  async signMessage(message) {
    if (!this.signer) {
      throw new Error('Wallet not connected');
    }

    return await this.signer.signMessage(message);
  }

  /**
   * Get balance
   */
  async getBalance() {
    if (!this.provider || !this.account) {
      throw new Error('Wallet not connected');
    }

    const balance = await this.provider.getBalance(this.account);
    return ethers.utils.formatEther(balance);
  }

  /**
   * Disconnect wallet
   */
  disconnect() {
    this.provider = null;
    this.signer = null;
    this.account = null;
    this.network = null;
    console.log('Wallet disconnected');
  }

  /**
   * Check if connected
   */
  isConnected() {
    return this.account !== null;
  }
}

module.exports = WalletConnector;
