# Web3 Frontend Integration Template

Modern Web3 frontend development patterns using the latest libraries and best practices.

## Tech Stack (2024+)

- **React** / Next.js
- **viem**: Type-safe, lightweight Ethereum library
- **wagmi**: React Hooks for Ethereum
- **RainbowKit** / **ConnectKit**: Wallet connection UI
- **TanStack Query**: Data fetching and caching
- **TypeScript**: Type safety

## Project Setup

```bash
npm create next-app@latest my-dapp
cd my-dapp
npm install viem wagmi @rainbow-me/rainbowkit @tanstack/react-query
```

## Configuration

### wagmi Configuration

```typescript
// config/wagmi.ts
import { getDefaultConfig } from '@rainbow-me/rainbowkit';
import { mainnet, polygon, optimism, arbitrum, sepolia } from 'wagmi/chains';

export const config = getDefaultConfig({
  appName: 'My DApp',
  projectId: process.env.NEXT_PUBLIC_WALLETCONNECT_PROJECT_ID!,
  chains: [mainnet, polygon, optimism, arbitrum, sepolia],
  ssr: true, // Enable server-side rendering
});
```

### App Provider Setup

```typescript
// app/providers.tsx
'use client';

import '@rainbow-me/rainbowkit/styles.css';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { WagmiProvider } from 'wagmi';
import { RainbowKitProvider } from '@rainbow-me/rainbowkit';
import { config } from '@/config/wagmi';

const queryClient = new QueryClient();

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <WagmiProvider config={config}>
      <QueryClientProvider client={queryClient}>
        <RainbowKitProvider>
          {children}
        </RainbowKitProvider>
      </QueryClientProvider>
    </WagmiProvider>
  );
}
```

```typescript
// app/layout.tsx
import { Providers } from './providers';

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
```

## Wallet Connection

```typescript
// components/ConnectButton.tsx
import { ConnectButton } from '@rainbow-me/rainbowkit';

export function WalletConnect() {
  return (
    <ConnectButton
      accountStatus="address"
      chainStatus="icon"
      showBalance={true}
    />
  );
}
```

## Reading Contract Data

```typescript
// components/TokenBalance.tsx
import { useAccount, useContractRead } from 'wagmi';
import { formatUnits } from 'viem';
import { ERC20_ABI } from '@/abis/erc20';

export function TokenBalance({ tokenAddress }: { tokenAddress: `0x${string}` }) {
  const { address } = useAccount();

  // Read token balance
  const { data: balance, isLoading, isError } = useContractRead({
    address: tokenAddress,
    abi: ERC20_ABI,
    functionName: 'balanceOf',
    args: address ? [address] : undefined,
    enabled: !!address, // Only run if connected
    watch: true, // Auto-refresh on new blocks
  });

  // Read token decimals
  const { data: decimals } = useContractRead({
    address: tokenAddress,
    abi: ERC20_ABI,
    functionName: 'decimals',
  });

  // Read token symbol
  const { data: symbol } = useContractRead({
    address: tokenAddress,
    abi: ERC20_ABI,
    functionName: 'symbol',
  });

  if (!address) return <div>Connect wallet to see balance</div>;
  if (isLoading) return <div>Loading...</div>;
  if (isError) return <div>Error loading balance</div>;

  const formattedBalance = balance && decimals
    ? formatUnits(balance, decimals)
    : '0';

  return (
    <div>
      Balance: {formattedBalance} {symbol}
    </div>
  );
}
```

## Writing to Contracts

```typescript
// components/TokenTransfer.tsx
import { useState } from 'react';
import { useContractWrite, useWaitForTransaction } from 'wagmi';
import { parseUnits } from 'viem';
import { ERC20_ABI } from '@/abis/erc20';

export function TokenTransfer({ tokenAddress }: { tokenAddress: `0x${string}` }) {
  const [recipient, setRecipient] = useState('');
  const [amount, setAmount] = useState('');

  const {
    data: txData,
    write: transfer,
    isLoading: isWriting,
    error: writeError,
  } = useContractWrite({
    address: tokenAddress,
    abi: ERC20_ABI,
    functionName: 'transfer',
  });

  const {
    isLoading: isTxLoading,
    isSuccess: isTxSuccess,
  } = useWaitForTransaction({
    hash: txData?.hash,
  });

  const handleTransfer = async () => {
    if (!recipient || !amount) return;

    try {
      await transfer({
        args: [recipient as `0x${string}`, parseUnits(amount, 18)],
      });
    } catch (error) {
      console.error('Transfer failed:', error);
    }
  };

  return (
    <div className="space-y-4">
      <input
        type="text"
        placeholder="Recipient address"
        value={recipient}
        onChange={(e) => setRecipient(e.target.value)}
        className="w-full p-2 border rounded"
      />
      <input
        type="number"
        placeholder="Amount"
        value={amount}
        onChange={(e) => setAmount(e.target.value)}
        className="w-full p-2 border rounded"
      />
      <button
        onClick={handleTransfer}
        disabled={isWriting || isTxLoading || !recipient || !amount}
        className="w-full px-4 py-2 bg-blue-500 text-white rounded disabled:opacity-50"
      >
        {isWriting || isTxLoading ? 'Transferring...' : 'Transfer'}
      </button>

      {writeError && (
        <div className="text-red-500">
          Error: {writeError.message}
        </div>
      )}

      {isTxSuccess && (
        <div className="text-green-500">
          Transfer successful! Tx: {txData?.hash}
        </div>
      )}
    </div>
  );
}
```

## Advanced: Custom Hooks

```typescript
// hooks/useTokenData.ts
import { useContractReads } from 'wagmi';
import { ERC20_ABI } from '@/abis/erc20';

export function useTokenData(tokenAddress: `0x${string}`) {
  const { data, isLoading, isError } = useContractReads({
    contracts: [
      {
        address: tokenAddress,
        abi: ERC20_ABI,
        functionName: 'name',
      },
      {
        address: tokenAddress,
        abi: ERC20_ABI,
        functionName: 'symbol',
      },
      {
        address: tokenAddress,
        abi: ERC20_ABI,
        functionName: 'decimals',
      },
      {
        address: tokenAddress,
        abi: ERC20_ABI,
        functionName: 'totalSupply',
      },
    ],
    watch: true,
  });

  return {
    name: data?.[0]?.result as string,
    symbol: data?.[1]?.result as string,
    decimals: data?.[2]?.result as number,
    totalSupply: data?.[3]?.result as bigint,
    isLoading,
    isError,
  };
}
```

```typescript
// Usage
function TokenInfo({ tokenAddress }: { tokenAddress: `0x${string}` }) {
  const { name, symbol, decimals, totalSupply, isLoading } = useTokenData(tokenAddress);

  if (isLoading) return <div>Loading...</div>;

  return (
    <div>
      <h2>{name} ({symbol})</h2>
      <p>Decimals: {decimals}</p>
      <p>Total Supply: {totalSupply?.toString()}</p>
    </div>
  );
}
```

## Transaction Management

```typescript
// components/TransactionButton.tsx
import { useState } from 'react';
import { useContractWrite, useWaitForTransaction, usePublicClient } from 'wagmi';
import { parseEther } from 'viem';

export function TransactionButton({ contractAddress, abi, functionName, args, value }) {
  const [status, setStatus] = useState<'idle' | 'estimating' | 'signing' | 'pending' | 'success' | 'error'>('idle');
  const [errorMessage, setErrorMessage] = useState('');

  const publicClient = usePublicClient();

  const {
    data: txData,
    write,
    isLoading: isWriting,
  } = useContractWrite({
    address: contractAddress,
    abi,
    functionName,
  });

  const { isLoading: isTxPending, isSuccess } = useWaitForTransaction({
    hash: txData?.hash,
    onSuccess: () => setStatus('success'),
  });

  const executeTransaction = async () => {
    try {
      setStatus('estimating');
      setErrorMessage('');

      // Estimate gas
      const gasEstimate = await publicClient.estimateContractGas({
        address: contractAddress,
        abi,
        functionName,
        args,
        value: value ? parseEther(value) : undefined,
      });

      const gasLimit = (gasEstimate * 120n) / 100n; // 20% buffer

      setStatus('signing');

      // Execute transaction
      await write({
        args,
        value: value ? parseEther(value) : undefined,
        gas: gasLimit,
      });

      setStatus('pending');
    } catch (error: any) {
      setStatus('error');
      if (error.message.includes('insufficient funds')) {
        setErrorMessage('Insufficient funds for gas');
      } else if (error.message.includes('user rejected')) {
        setErrorMessage('Transaction rejected');
      } else {
        setErrorMessage(error.shortMessage || error.message);
      }
    }
  };

  const buttonText = {
    idle: 'Execute',
    estimating: 'Estimating gas...',
    signing: 'Please sign...',
    pending: 'Pending...',
    success: 'Success!',
    error: 'Try again',
  }[status];

  return (
    <div>
      <button
        onClick={executeTransaction}
        disabled={status !== 'idle' && status !== 'error'}
        className="px-4 py-2 bg-blue-500 text-white rounded disabled:opacity-50"
      >
        {buttonText}
      </button>

      {status === 'error' && (
        <div className="mt-2 text-red-500">{errorMessage}</div>
      )}

      {status === 'success' && txData?.hash && (
        <div className="mt-2 text-green-500">
          <a
            href={`https://etherscan.io/tx/${txData.hash}`}
            target="_blank"
            rel="noopener noreferrer"
            className="underline"
          >
            View on Etherscan
          </a>
        </div>
      )}
    </div>
  );
}
```

## Event Listening

```typescript
// hooks/useContractEvents.ts
import { useContractEvent } from 'wagmi';
import { useState } from 'react';

export function useTransferEvents(tokenAddress: `0x${string}`) {
  const [transfers, setTransfers] = useState<any[]>([]);

  useContractEvent({
    address: tokenAddress,
    abi: ERC20_ABI,
    eventName: 'Transfer',
    listener(logs) {
      const newTransfers = logs.map((log) => ({
        from: log.args.from,
        to: log.args.to,
        value: log.args.value,
        txHash: log.transactionHash,
      }));
      setTransfers((prev) => [...newTransfers, ...prev].slice(0, 10)); // Keep latest 10
    },
  });

  return transfers;
}
```

## NFT Gallery

```typescript
// components/NFTGallery.tsx
import { useAccount, useContractRead } from 'wagmi';
import { useState, useEffect } from 'react';

const NFT_ABI = [
  {
    inputs: [{ name: 'owner', type: 'address' }],
    name: 'balanceOf',
    outputs: [{ name: '', type: 'uint256' }],
    stateMutability: 'view',
    type: 'function',
  },
  {
    inputs: [{ name: 'owner', type: 'address' }, { name: 'index', type: 'uint256' }],
    name: 'tokenOfOwnerByIndex',
    outputs: [{ name: '', type: 'uint256' }],
    stateMutability: 'view',
    type: 'function',
  },
  {
    inputs: [{ name: 'tokenId', type: 'uint256' }],
    name: 'tokenURI',
    outputs: [{ name: '', type: 'string' }],
    stateMutability: 'view',
    type: 'function',
  },
] as const;

export function NFTGallery({ nftAddress }: { nftAddress: `0x${string}` }) {
  const { address } = useAccount();
  const [tokenIds, setTokenIds] = useState<bigint[]>([]);

  // Get balance
  const { data: balance } = useContractRead({
    address: nftAddress,
    abi: NFT_ABI,
    functionName: 'balanceOf',
    args: address ? [address] : undefined,
    enabled: !!address,
  });

  // Fetch all token IDs
  useEffect(() => {
    const fetchTokenIds = async () => {
      if (!balance || !address) return;

      const ids: bigint[] = [];
      for (let i = 0; i < Number(balance); i++) {
        // This would ideally use batch reads
        // For now, simplified version
        ids.push(BigInt(i));
      }
      setTokenIds(ids);
    };

    fetchTokenIds();
  }, [balance, address]);

  return (
    <div className="grid grid-cols-3 gap-4">
      {tokenIds.map((tokenId) => (
        <NFTCard key={tokenId.toString()} nftAddress={nftAddress} tokenId={tokenId} />
      ))}
    </div>
  );
}

function NFTCard({ nftAddress, tokenId }: { nftAddress: `0x${string}`; tokenId: bigint }) {
  const { data: tokenURI } = useContractRead({
    address: nftAddress,
    abi: NFT_ABI,
    functionName: 'tokenURI',
    args: [tokenId],
  });

  const [metadata, setMetadata] = useState<any>(null);

  useEffect(() => {
    if (!tokenURI) return;

    const fetchMetadata = async () => {
      const response = await fetch(tokenURI.replace('ipfs://', 'https://ipfs.io/ipfs/'));
      const data = await response.json();
      setMetadata(data);
    };

    fetchMetadata();
  }, [tokenURI]);

  if (!metadata) return <div>Loading...</div>;

  return (
    <div className="border rounded p-4">
      <img
        src={metadata.image.replace('ipfs://', 'https://ipfs.io/ipfs/')}
        alt={metadata.name}
        className="w-full h-48 object-cover rounded"
      />
      <h3 className="mt-2 font-bold">{metadata.name}</h3>
      <p className="text-sm text-gray-600">#{tokenId.toString()}</p>
    </div>
  );
}
```

## DeFi Swap Interface

```typescript
// components/SwapInterface.tsx
import { useState } from 'react';
import { useContractWrite, useContractRead } from 'wagmi';
import { parseUnits, formatUnits } from 'viem';

const ROUTER_ABI = [
  // Simplified Uniswap V2 Router ABI
  {
    inputs: [
      { name: 'amountIn', type: 'uint256' },
      { name: 'amountOutMin', type: 'uint256' },
      { name: 'path', type: 'address[]' },
      { name: 'to', type: 'address' },
      { name: 'deadline', type: 'uint256' },
    ],
    name: 'swapExactTokensForTokens',
    outputs: [{ name: 'amounts', type: 'uint256[]' }],
    stateMutability: 'nonpayable',
    type: 'function',
  },
  {
    inputs: [
      { name: 'amountIn', type: 'uint256' },
      { name: 'path', type: 'address[]' },
    ],
    name: 'getAmountsOut',
    outputs: [{ name: 'amounts', type: 'uint256[]' }],
    stateMutability: 'view',
    type: 'function',
  },
] as const;

export function SwapInterface({
  routerAddress,
  tokenInAddress,
  tokenOutAddress,
}: {
  routerAddress: `0x${string}`;
  tokenInAddress: `0x${string}`;
  tokenOutAddress: `0x${string}`;
}) {
  const [amountIn, setAmountIn] = useState('');
  const [slippage, setSlippage] = useState('0.5'); // 0.5%

  // Get expected output amount
  const { data: amountsOut } = useContractRead({
    address: routerAddress,
    abi: ROUTER_ABI,
    functionName: 'getAmountsOut',
    args: amountIn
      ? [parseUnits(amountIn, 18), [tokenInAddress, tokenOutAddress]]
      : undefined,
    enabled: !!amountIn && parseFloat(amountIn) > 0,
    watch: true, // Update on every block
  });

  const expectedOutput = amountsOut?.[1]
    ? formatUnits(amountsOut[1], 18)
    : '0';

  const minOutput = amountsOut?.[1]
    ? (amountsOut[1] * BigInt(Math.floor((100 - parseFloat(slippage)) * 100))) / 10000n
    : 0n;

  const { write: swap, isLoading } = useContractWrite({
    address: routerAddress,
    abi: ROUTER_ABI,
    functionName: 'swapExactTokensForTokens',
  });

  const handleSwap = () => {
    if (!amountIn || !amountsOut) return;

    const deadline = Math.floor(Date.now() / 1000) + 60 * 20; // 20 minutes

    swap({
      args: [
        parseUnits(amountIn, 18),
        minOutput,
        [tokenInAddress, tokenOutAddress],
        address,
        BigInt(deadline),
      ],
    });
  };

  return (
    <div className="max-w-md mx-auto p-6 bg-white rounded-lg shadow">
      <h2 className="text-2xl font-bold mb-4">Swap Tokens</h2>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">Amount In</label>
          <input
            type="number"
            value={amountIn}
            onChange={(e) => setAmountIn(e.target.value)}
            placeholder="0.0"
            className="w-full p-2 border rounded"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Expected Output</label>
          <div className="p-2 bg-gray-100 rounded">
            {expectedOutput}
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">
            Slippage Tolerance: {slippage}%
          </label>
          <input
            type="range"
            min="0.1"
            max="5"
            step="0.1"
            value={slippage}
            onChange={(e) => setSlippage(e.target.value)}
            className="w-full"
          />
        </div>

        <button
          onClick={handleSwap}
          disabled={isLoading || !amountIn || parseFloat(amountIn) <= 0}
          className="w-full px-4 py-2 bg-blue-500 text-white rounded disabled:opacity-50"
        >
          {isLoading ? 'Swapping...' : 'Swap'}
        </button>
      </div>
    </div>
  );
}
```

## Error Handling

```typescript
// utils/parseContractError.ts
import { BaseError, ContractFunctionRevertedError } from 'viem';

export function parseContractError(error: unknown): string {
  if (error instanceof BaseError) {
    const revertError = error.walk(
      (err) => err instanceof ContractFunctionRevertedError
    );

    if (revertError instanceof ContractFunctionRevertedError) {
      const errorName = revertError.data?.errorName ?? '';
      return `Contract error: ${errorName}`;
    }

    // Handle specific error types
    if (error.message.includes('insufficient funds')) {
      return 'Insufficient funds for gas';
    }
    if (error.message.includes('user rejected')) {
      return 'Transaction rejected by user';
    }
  }

  return 'An unknown error occurred';
}
```

## Best Practices

### 1. Gas Estimation
```typescript
// Always estimate gas before transactions
const gasEstimate = await publicClient.estimateContractGas({
  address: contractAddress,
  abi: ABI,
  functionName: 'transfer',
  args: [recipient, amount],
});

// Add 20% buffer
const gasLimit = (gasEstimate * 120n) / 100n;
```

### 2. Error Handling
```typescript
try {
  await write({ args: [...] });
} catch (error) {
  const errorMessage = parseContractError(error);
  toast.error(errorMessage);
}
```

### 3. Loading States
```typescript
// Show different states
if (isConnecting) return <div>Connecting...</div>;
if (isWriting) return <div>Please confirm transaction...</div>;
if (isTxPending) return <div>Transaction pending...</div>;
if (isTxSuccess) return <div>Success!</div>;
```

### 4. Optimistic Updates
```typescript
const queryClient = useQueryClient();

const { write } = useContractWrite({
  onMutate: async () => {
    // Optimistically update UI
    queryClient.setQueryData(['balance'], (old) => old + amount);
  },
  onError: () => {
    // Rollback on error
    queryClient.invalidateQueries(['balance']);
  },
  onSuccess: () => {
    // Refetch to ensure accuracy
    queryClient.invalidateQueries(['balance']);
  },
});
```

### 5. Network Switching
```typescript
import { useSwitchNetwork } from 'wagmi';
import { mainnet } from 'wagmi/chains';

function EnsureMainnet({ children }) {
  const { chain } = useNetwork();
  const { switchNetwork } = useSwitchNetwork();

  if (chain?.id !== mainnet.id) {
    return (
      <button onClick={() => switchNetwork?.(mainnet.id)}>
        Switch to Mainnet
      </button>
    );
  }

  return children;
}
```

## Production Checklist

- [ ] Error handling for all contract interactions
- [ ] Loading states for all async operations
- [ ] Gas estimation before transactions
- [ ] Slippage protection for swaps
- [ ] Network validation
- [ ] Transaction deadlines
- [ ] Proper TypeScript types
- [ ] Mobile responsive design
- [ ] Wallet disconnect handling
- [ ] Event listener cleanup
- [ ] Analytics integration
- [ ] SEO optimization
- [ ] Performance monitoring
