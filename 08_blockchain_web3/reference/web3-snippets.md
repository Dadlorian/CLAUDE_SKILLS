# Web3 Integration Snippets

## Wallet Connection (wagmi + RainbowKit)
```typescript
import { ConnectButton } from '@rainbow-me/rainbowkit';
<ConnectButton />
```

## Read Contract
```typescript
const { data: balance } = useContractRead({
  address: '0x...',
  abi: ERC20_ABI,
  functionName: 'balanceOf',
  args: [userAddress],
  watch: true,
});
```

## Write Contract
```typescript
const { write, isLoading } = useContractWrite({
  address: '0x...',
  abi: CONTRACT_ABI,
  functionName: 'transfer',
  args: [recipient, parseEther('1')],
  onSuccess: (data) => toast.success(`Tx: ${data.hash}`),
});
```

## Listen to Events
```typescript
useContractEvent({
  address: '0x...',
  abi: CONTRACT_ABI,
  eventName: 'Transfer',
  listener(logs) {
    console.log('New transfer:', logs);
  },
});
```

## Get Signer
```typescript
const { data: signer } = useSigner();
const contract = new Contract(address, abi, signer);
await contract.transfer(to, amount);
```

## Format Values
```typescript
import { parseEther, formatEther, parseUnits, formatUnits } from 'viem';

parseEther('1.0')        // 1000000000000000000n
formatEther(1000000000000000000n) // '1.0'
parseUnits('1', 6)       // 1000000n (USDC)
formatUnits(1000000n, 6) // '1.0'
```
