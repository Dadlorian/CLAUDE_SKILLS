# Wallet Integration Guide

## MetaMask Integration

### Connect Wallet
```javascript
async function connectWallet() {
  if (!window.ethereum) {
    alert('Please install MetaMask');
    return;
  }

  try {
    const accounts = await window.ethereum.request({
      method: 'eth_requestAccounts'
    });

    const account = accounts[0];
    console.log('Connected:', account);
    return account;
  } catch (error) {
    console.error('Connection failed:', error);
  }
}
```

### Get Network
```javascript
async function getNetwork() {
  const chainId = await window.ethereum.request({ method: 'eth_chainId' });
  console.log('Chain ID:', parseInt(chainId, 16));

  const chainInfo = {
    1: 'Mainnet',
    5: 'Goerli',
    11155111: 'Sepolia',
    137: 'Polygon',
    43114: 'Avalanche',
    42161: 'Arbitrum',
  };

  return chainInfo[parseInt(chainId, 16)];
}
```

### Switch Network
```javascript
async function switchNetwork(chainId) {
  try {
    await window.ethereum.request({
      method: 'wallet_switchEthereumChain',
      params: [{ chainId: `0x${chainId.toString(16)}` }],
    });
  } catch (error) {
    if (error.code === 4902) {
      // Network not added, add it
      await addNetwork(chainId);
    }
  }
}

async function addNetwork(chainId) {
  const networks = {
    137: {
      chainId: '0x89',
      chainName: 'Polygon',
      nativeCurrency: { name: 'MATIC', symbol: 'MATIC', decimals: 18 },
      rpcUrls: ['https://polygon-rpc.com'],
      blockExplorerUrls: ['https://polygonscan.com'],
    },
  };

  await window.ethereum.request({
    method: 'wallet_addEthereumChain',
    params: [networks[chainId]],
  });
}
```

## Send Transactions

### Basic ETH Transfer
```javascript
async function sendETH(recipient, amount) {
  const tx = {
    to: recipient,
    value: ethers.parseEther(amount),
    from: account,
  };

  try {
    const txHash = await window.ethereum.request({
      method: 'eth_sendTransaction',
      params: [tx],
    });

    console.log('Transaction sent:', txHash);
    return txHash;
  } catch (error) {
    console.error('Transaction failed:', error);
  }
}
```

### Contract Interaction
```javascript
const provider = new ethers.BrowserProvider(window.ethereum);
const signer = await provider.getSigner();

const contract = new ethers.Contract(
  CONTRACT_ADDRESS,
  CONTRACT_ABI,
  signer
);

// Call function
const tx = await contract.transfer(recipient, amount);
const receipt = await tx.wait();
```

## Sign Messages

### Personal Sign
```javascript
async function signMessage(message) {
  const accounts = await window.ethereum.request({
    method: 'eth_accounts'
  });

  const signature = await window.ethereum.request({
    method: 'personal_sign',
    params: [message, accounts[0]],
  });

  console.log('Signature:', signature);
  return signature;
}
```

### Sign Typed Data (EIP-712)
```javascript
async function signTypedData(data) {
  const signature = await window.ethereum.request({
    method: 'eth_signTypedData_v4',
    params: [account, JSON.stringify(data)],
  });

  return signature;
}

// Example EIP-712 data
const data = {
  types: {
    EIP712Domain: [
      { name: 'name', type: 'string' },
      { name: 'version', type: 'string' },
      { name: 'chainId', type: 'uint256' },
      { name: 'verifyingContract', type: 'address' },
    ],
    Message: [
      { name: 'to', type: 'address' },
      { name: 'amount', type: 'uint256' },
    ],
  },
  primaryType: 'Message',
  domain: {
    name: 'MyApp',
    version: '1',
    chainId: 1,
    verifyingContract: '0x...',
  },
  message: {
    to: '0x...',
    amount: ethers.parseEther('1'),
  },
};
```

## Event Handling

### Account Changed
```javascript
window.ethereum.on('accountsChanged', (accounts) => {
  if (accounts.length === 0) {
    console.log('Wallet disconnected');
  } else {
    console.log('Account changed:', accounts[0]);
    // Update UI
  }
});
```

### Chain Changed
```javascript
window.ethereum.on('chainChanged', (chainId) => {
  console.log('Network changed:', parseInt(chainId, 16));
  // Refresh app state
  window.location.reload();
});
```

### Disconnect
```javascript
window.ethereum.on('disconnect', (error) => {
  console.log('Disconnected:', error);
  // Handle disconnection
});
```

## Multi-Chain Support

### Check and Switch
```javascript
async function ensureCorrectNetwork(requiredChainId) {
  const currentChainId = parseInt(
    await window.ethereum.request({ method: 'eth_chainId' }),
    16
  );

  if (currentChainId !== requiredChainId) {
    await switchNetwork(requiredChainId);
  }
}
```

## Gas Estimation

### Estimate and Send
```javascript
async function estimateAndSend(contract, method, ...args) {
  try {
    // Estimate gas
    const gasEstimate = await contract.estimateGas[method](...args);

    // Add 20% buffer
    const gasLimit = gasEstimate * BigInt(120) / BigInt(100);

    // Get current gas price
    const gasPrice = await provider.getGasPrice();

    // Send with gas estimation
    const tx = await contract[method](...args, {
      gasLimit,
      gasPrice,
    });

    return await tx.wait();
  } catch (error) {
    console.error('Error:', error);
  }
}
```

## ENS Integration

### Resolve Name
```javascript
async function resolveENS(name) {
  const address = await provider.resolveName(name);
  return address;
}

async function reverseLookup(address) {
  const name = await provider.lookupAddress(address);
  return name;
}
```

## Hardware Wallet Support

### HardHat + Ledger
```javascript
// hardhat.config.js
module.exports = {
  networks: {
    mainnet: {
      url: process.env.INFURA_URL,
      accounts: {
        mnemonic: process.env.MNEMONIC,
      },
    },
  },
};
```

### Web3 with Ledger
```javascript
const LedgerWalletProvider = require('@ledgerhq/web3-subprovider');
const ProviderEngine = require('web3-provider-engine');

const engine = new ProviderEngine();
const ledger = new LedgerWalletProvider({
  networkId: 1,
  accountsOffset: 0,
});

engine.addProvider(ledger);
engine.start();
```

---

**Key Takeaways**:
- MetaMask is most popular wallet
- Support multiple chains
- Handle errors gracefully
- Listen to account/chain changes
- Consider hardware wallets for safety
