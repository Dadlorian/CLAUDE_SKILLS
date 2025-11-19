# Web3 Frontend Development

## Overview
Build decentralized applications (dApps) with modern frontend frameworks, Web3 libraries, and blockchain integration. Master wallet connections, smart contract interactions, and Web3 UX patterns.

## Core Technologies

### 1. Web3 Libraries
- **ethers.js**: Modern, lightweight Ethereum library
- **web3.js**: Original Ethereum JavaScript API
- **wagmi**: React Hooks for Ethereum
- **viem**: TypeScript-first Ethereum library
- **Web3Modal**: Multi-wallet connection library

### 2. Frontend Frameworks
- **React**: Component-based UI library
- **Next.js**: React framework with SSR/SSG
- **Vue.js**: Progressive JavaScript framework
- **Svelte**: Compiler-based framework
- **Solid.js**: Fine-grained reactivity

### 3. State Management
- **Redux/Zustand**: Global state
- **React Query/SWR**: Data fetching and caching
- **Context API**: React context for Web3
- **Jotai/Recoil**: Atomic state management

## Wallet Integration

### 1. MetaMask Connection
```javascript
import { ethers } from 'ethers';

async function connectWallet() {
    if (!window.ethereum) {
        throw new Error('MetaMask not installed');
    }

    const provider = new ethers.BrowserProvider(window.ethereum);
    await provider.send('eth_requestAccounts', []);
    const signer = await provider.getSigner();
    const address = await signer.getAddress();

    return { provider, signer, address };
}
```

### 2. Multi-Wallet Support
```javascript
import { WalletConnect } from '@web3modal/react';
import { CoinbaseWallet } from '@coinbase/wallet-sdk';

const connectors = [
    MetaMask,
    WalletConnect,
    CoinbaseWallet
];
```

### 3. Wallet State Management
```javascript
import { create } from 'zustand';

const useWalletStore = create((set) => ({
    address: null,
    chainId: null,
    connected: false,
    connect: async () => {
        // Connection logic
    },
    disconnect: () => set({ address: null, connected: false })
}));
```

## Smart Contract Interaction

### 1. Reading Contract Data
```javascript
const contract = new ethers.Contract(address, abi, provider);

// Read functions
const balance = await contract.balanceOf(userAddress);
const totalSupply = await contract.totalSupply();
const owner = await contract.owner();
```

### 2. Writing to Contract
```javascript
const contractWithSigner = contract.connect(signer);

// Write functions
const tx = await contractWithSigner.mint(quantity, {
    value: ethers.parseEther('0.1')
});

await tx.wait(); // Wait for confirmation
```

### 3. Event Listening
```javascript
// Listen for events
contract.on('Transfer', (from, to, amount) => {
    console.log(`Transfer: ${from} -> ${to}, Amount: ${amount}`);
});

// Filter past events
const filter = contract.filters.Transfer(userAddress);
const events = await contract.queryFilter(filter);
```

## React Hooks Patterns

### 1. useContract Hook
```javascript
function useContract(address, abi) {
    const { provider, signer } = useWallet();

    return useMemo(() => {
        if (!address || !abi) return null;

        return new ethers.Contract(
            address,
            abi,
            signer || provider
        );
    }, [address, abi, signer, provider]);
}
```

### 2. useContractRead Hook
```javascript
function useContractRead(contract, method, args = []) {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (!contract) return;

        async function fetchData() {
            try {
                const result = await contract[method](...args);
                setData(result);
            } catch (err) {
                setError(err);
            } finally {
                setLoading(false);
            }
        }

        fetchData();
    }, [contract, method, JSON.stringify(args)]);

    return { data, loading, error };
}
```

### 3. useContractWrite Hook
```javascript
function useContractWrite(contract, method) {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const write = async (...args) => {
        setLoading(true);
        setError(null);

        try {
            const tx = await contract[method](...args);
            await tx.wait();
            return tx;
        } catch (err) {
            setError(err);
            throw err;
        } finally {
            setLoading(false);
        }
    };

    return { write, loading, error };
}
```

## IPFS Integration

### 1. Upload to IPFS
```javascript
import { create } from 'ipfs-http-client';

const client = create({ url: 'https://ipfs.infura.io:5001' });

async function uploadToIPFS(file) {
    const added = await client.add(file);
    return `ipfs://${added.path}`;
}
```

### 2. Fetch from IPFS
```javascript
function useIPFS(uri) {
    const [data, setData] = useState(null);

    useEffect(() => {
        if (!uri) return;

        const ipfsHash = uri.replace('ipfs://', '');
        const url = `https://ipfs.io/ipfs/${ipfsHash}`;

        fetch(url)
            .then(res => res.json())
            .then(setData);
    }, [uri]);

    return data;
}
```

## Transaction Management

### 1. Transaction Status
```javascript
function useTransaction(hash) {
    const [status, setStatus] = useState('pending');
    const provider = useProvider();

    useEffect(() => {
        if (!hash) return;

        async function checkStatus() {
            const receipt = await provider.getTransactionReceipt(hash);

            if (receipt) {
                setStatus(receipt.status === 1 ? 'success' : 'failed');
            }
        }

        checkStatus();
    }, [hash]);

    return status;
}
```

### 2. Gas Estimation
```javascript
async function estimateGas(contract, method, args) {
    const gasEstimate = await contract[method].estimateGas(...args);
    const gasPrice = await provider.getFeeData();

    return {
        gasLimit: gasEstimate,
        maxFeePerGas: gasPrice.maxFeePerGas,
        maxPriorityFeePerGas: gasPrice.maxPriorityFeePerGas
    };
}
```

## Error Handling

### 1. User-Friendly Errors
```javascript
function parseError(error) {
    if (error.code === 4001) {
        return 'Transaction rejected by user';
    }

    if (error.code === 'INSUFFICIENT_FUNDS') {
        return 'Insufficient funds for transaction';
    }

    if (error.data?.message) {
        return error.data.message;
    }

    return 'Transaction failed. Please try again.';
}
```

### 2. Error Boundaries
```javascript
class Web3ErrorBoundary extends React.Component {
    state = { hasError: false };

    static getDerivedStateFromError(error) {
        return { hasError: true };
    }

    render() {
        if (this.state.hasError) {
            return <ErrorFallback />;
        }

        return this.props.children;
    }
}
```

## UI/UX Best Practices

### 1. Loading States
```javascript
function MintButton() {
    const { write, loading } = useContractWrite(contract, 'mint');

    return (
        <button disabled={loading} onClick={() => write(1)}>
            {loading ? 'Minting...' : 'Mint NFT'}
        </button>
    );
}
```

### 2. Network Detection
```javascript
function NetworkCheck() {
    const { chainId } = useWallet();
    const expectedChainId = 1; // Mainnet

    if (chainId !== expectedChainId) {
        return <NetworkSwitcher expectedChainId={expectedChainId} />;
    }

    return <App />;
}
```

### 3. Balance Display
```javascript
function formatBalance(balance, decimals = 18) {
    const formatted = ethers.formatUnits(balance, decimals);
    return parseFloat(formatted).toFixed(4);
}
```

## Testing

### 1. Unit Tests
```javascript
import { render, screen } from '@testing-library/react';
import { WalletButton } from './WalletButton';

test('renders connect button', () => {
    render(<WalletButton />);
    expect(screen.getByText('Connect Wallet')).toBeInTheDocument();
});
```

### 2. Contract Mocking
```javascript
import { MockProvider } from '@wagmi/core/mock';

const mockContract = {
    balanceOf: jest.fn().mockResolvedValue('1000'),
    mint: jest.fn().mockResolvedValue({ hash: '0x123' })
};
```

## Performance Optimization

### 1. Caching
```javascript
import { useQuery } from '@tanstack/react-query';

function useTokenBalance(address) {
    return useQuery({
        queryKey: ['balance', address],
        queryFn: () => contract.balanceOf(address),
        staleTime: 60000 // 1 minute
    });
}
```

### 2. Batch Requests
```javascript
async function batchRead(contract, calls) {
    const promises = calls.map(({ method, args }) =>
        contract[method](...args)
    );

    return Promise.all(promises);
}
```

## Resources

### Documentation
- ethers.js docs
- wagmi docs
- RainbowKit
- Web3Modal
- WalletConnect

### Tools
- Hardhat
- Remix
- Tenderly
- Alchemy
- Infura

## Conclusion

Web3 frontend development requires mastery of both traditional web development and blockchain-specific patterns. Focus on user experience, error handling, and performance for successful dApps.
