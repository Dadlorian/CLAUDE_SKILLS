# Web3 Development Guide

## Frontend Setup with ethers.js

### Install & Initialize
```bash
npm install ethers
npm install react-ethers  # if using React
npm install web3-react   # alternative: Web3 integration library
```

### Connect Wallet
```javascript
import { ethers } from 'ethers';

async function connectWallet() {
  // Check if MetaMask is installed
  if (!window.ethereum) {
    alert('Please install MetaMask');
    return;
  }

  try {
    // Request access to user's wallet
    const accounts = await window.ethereum.request({
      method: 'eth_requestAccounts'
    });

    const account = accounts[0];
    console.log('Connected:', account);

    // Get provider
    const provider = new ethers.BrowserProvider(window.ethereum);
    const signer = await provider.getSigner();

    return { account, provider, signer };
  } catch (error) {
    console.error('Connection failed:', error);
  }
}
```

### Interact with Contract
```javascript
const CONTRACT_ADDRESS = '0x...';
const CONTRACT_ABI = [...];

async function interactWithContract(signer) {
  const contract = new ethers.Contract(
    CONTRACT_ADDRESS,
    CONTRACT_ABI,
    signer
  );

  // Read function (no gas)
  const balance = await contract.balanceOf(userAddress);
  console.log('Balance:', ethers.formatEther(balance));

  // Write function (needs transaction)
  const tx = await contract.transfer(recipient, amount);
  console.log('Transaction:', tx.hash);

  // Wait for confirmation
  const receipt = await tx.wait();
  console.log('Confirmed in block:', receipt.blockNumber);
}
```

## React Integration

### Setup with ethers.js
```javascript
import React, { useState, useEffect } from 'react';
import { ethers } from 'ethers';

function App() {
  const [account, setAccount] = useState(null);
  const [provider, setProvider] = useState(null);
  const [balance, setBalance] = useState(null);

  useEffect(() => {
    initializeWeb3();
  }, []);

  async function initializeWeb3() {
    if (!window.ethereum) return;

    const provider = new ethers.BrowserProvider(window.ethereum);
    setProvider(provider);

    try {
      const accounts = await window.ethereum.request({
        method: 'eth_requestAccounts'
      });

      if (accounts.length > 0) {
        setAccount(accounts[0]);
        const balance = await provider.getBalance(accounts[0]);
        setBalance(ethers.formatEther(balance));
      }
    } catch (error) {
      console.error('Failed to connect:', error);
    }
  }

  return (
    <div>
      {account ? (
        <div>
          <p>Connected: {account.substring(0, 6)}...</p>
          <p>Balance: {balance} ETH</p>
        </div>
      ) : (
        <button onClick={initializeWeb3}>Connect Wallet</button>
      )}
    </div>
  );
}

export default App;
```

### Transaction Handling
```javascript
async function sendTransaction(to, amount) {
  const signer = provider.getSigner();

  try {
    const tx = await signer.sendTransaction({
      to,
      value: ethers.parseEther(amount),
    });

    setTxHash(tx.hash);
    setStatus('pending');

    const receipt = await tx.wait();

    if (receipt.status === 1) {
      setStatus('success');
    } else {
      setStatus('failed');
    }
  } catch (error) {
    setStatus('error');
    setError(error.message);
  }
}
```

## Contract Interaction Patterns

### ERC20 Token Operations
```javascript
const ERC20_ABI = [
  'function balanceOf(address owner) view returns (uint256)',
  'function transfer(address to, uint256 amount) returns (bool)',
  'function approve(address spender, uint256 amount) returns (bool)',
  'function allowance(address owner, address spender) view returns (uint256)',
];

async function transferToken(tokenAddress, recipient, amount) {
  const contract = new ethers.Contract(tokenAddress, ERC20_ABI, signer);

  const tx = await contract.transfer(recipient, amount);
  return await tx.wait();
}

async function approveToken(tokenAddress, spender, amount) {
  const contract = new ethers.Contract(tokenAddress, ERC20_ABI, signer);

  const tx = await contract.approve(spender, amount);
  return await tx.wait();
}
```

### Multi-Call Pattern
```javascript
const MULTICALL_ABI = [
  'function aggregate(tuple(address,bytes)[] calls) view returns (uint256, bytes[])',
];

async function multiCall(calls) {
  const multicall = new ethers.Contract(
    MULTICALL_ADDRESS,
    MULTICALL_ABI,
    provider
  );

  const [blockNumber, results] = await multicall.aggregate(calls);
  return results;
}
```

## Handling Wallet Events

### Listen to Account Changes
```javascript
window.ethereum.on('accountsChanged', (accounts) => {
  if (accounts.length === 0) {
    setAccount(null);
  } else {
    setAccount(accounts[0]);
  }
});
```

### Listen to Network Changes
```javascript
window.ethereum.on('chainChanged', (chainId) => {
  console.log('Network changed to:', parseInt(chainId, 16));
  // Refresh application state
  window.location.reload();
});
```

## Error Handling Best Practices

### Transaction Errors
```javascript
async function safeTransaction(fn) {
  try {
    const result = await fn();
    return { success: true, data: result };
  } catch (error) {
    if (error.code === 'ACTION_REJECTED') {
      return { success: false, error: 'Transaction rejected by user' };
    }

    if (error.code === 'CALL_EXCEPTION') {
      return { success: false, error: 'Contract call failed: ' + error.reason };
    }

    if (error.code === 'NETWORK_ERROR') {
      return { success: false, error: 'Network error, check RPC provider' };
    }

    return { success: false, error: error.message };
  }
}
```

### Gas Estimation
```javascript
async function estimateAndSend(contract, method, ...args) {
  try {
    // Estimate gas
    const gasEstimate = await contract.estimateGas[method](...args);

    // Add 20% buffer
    const gasLimit = gasEstimate.mul(120).div(100);

    // Send transaction
    const tx = await contract[method](...args, { gasLimit });

    return await tx.wait();
  } catch (error) {
    if (error.reason === 'insufficient funds') {
      throw new Error('Insufficient funds for gas');
    }

    throw error;
  }
}
```

## Displaying Data

### Format Numbers
```javascript
function formatValue(value, decimals = 18, displayDecimals = 4) {
  const formatted = ethers.formatUnits(value, decimals);
  return parseFloat(formatted).toFixed(displayDecimals);
}

// Usage
const balance = await contract.balanceOf(userAddress);
console.log(formatValue(balance)); // e.g., "1.2345"
```

### Format Addresses
```javascript
function shortenAddress(address) {
  return `${address.substring(0, 6)}...${address.substring(address.length - 4)}`;
}

// Usage
<p>{shortenAddress('0x1234567890123456789012345678901234567890')}</p>
// Output: 0x1234...7890
```

## Testing Web3 Code

### Unit Tests
```javascript
const { expect } = require('chai');
const { ethers } = require('hardhat');

describe('Web3 Integration', () => {
  it('should connect to contract', async () => {
    const [signer] = await ethers.getSigners();

    const contract = new ethers.Contract(
      CONTRACT_ADDRESS,
      CONTRACT_ABI,
      signer
    );

    const result = await contract.someFunction();
    expect(result).to.not.be.undefined;
  });

  it('should send transaction', async () => {
    const [signer] = await ethers.getSigners();

    const contract = new ethers.Contract(
      CONTRACT_ADDRESS,
      CONTRACT_ABI,
      signer
    );

    const tx = await contract.transfer(recipient, amount);
    const receipt = await tx.wait();

    expect(receipt.status).to.equal(1);
  });
});
```

## Building dApps

### Basic dApp Structure
```
dapp/
├── public/
├── src/
│   ├── components/
│   │   ├── WalletConnect.jsx
│   │   ├── TransactionForm.jsx
│   │   └── BalanceDisplay.jsx
│   ├── hooks/
│   │   ├── useWeb3.js
│   │   ├── useContract.js
│   │   └── useBalance.js
│   ├── utils/
│   │   ├── contract.js
│   │   ├── formatting.js
│   │   └── constants.js
│   ├── App.jsx
│   └── index.js
├── .env
└── package.json
```

### Custom Hook Example
```javascript
// hooks/useContract.js
import { useState, useEffect } from 'react';
import { ethers } from 'ethers';

export function useContract(address, abi, provider) {
  const [contract, setContract] = useState(null);

  useEffect(() => {
    if (provider && address && abi) {
      const signer = provider.getSigner();
      const instance = new ethers.Contract(address, abi, signer);
      setContract(instance);
    }
  }, [address, abi, provider]);

  return contract;
}
```

## Deployment

### Deploy to Vercel
```bash
npm run build
vercel

# Set environment variables in Vercel dashboard
# REACT_APP_INFURA_KEY
# REACT_APP_CONTRACT_ADDRESS
```

### Secure Sensitive Data
```
# .env.local (never commit)
REACT_APP_INFURA_KEY=xxxx
REACT_APP_ETHERSCAN_API_KEY=xxxx

# Access in code
const INFURA_KEY = process.env.REACT_APP_INFURA_KEY;
```

## Performance Optimization

### Caching
```javascript
const cache = {};

async function getCachedData(key, fetchFn, ttl = 60000) {
  const now = Date.now();

  if (cache[key] && now - cache[key].timestamp < ttl) {
    return cache[key].data;
  }

  const data = await fetchFn();
  cache[key] = { data, timestamp: now };

  return data;
}
```

### Debouncing User Input
```javascript
function useDebounce(value, delay) {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => clearTimeout(handler);
  }, [value, delay]);

  return debouncedValue;
}
```

---

**Key Takeaways**:
- Use ethers.js for Web3 interaction
- Connect wallet via window.ethereum
- Handle errors gracefully
- Format numbers and addresses for display
- Test code thoroughly
- Secure sensitive data
- Optimize performance
