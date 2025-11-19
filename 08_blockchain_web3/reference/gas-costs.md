# Gas Costs Reference

## Storage Operations
| Operation | Gas Cost |
|-----------|----------|
| SSTORE (zero → non-zero) | 20,000 |
| SSTORE (non-zero → non-zero) | 5,000 |
| SSTORE (non-zero → zero) | 5,000 (15,000 refund) |
| SLOAD (cold) | 2,100 |
| SLOAD (warm) | 100 |

## Memory & Calldata
| Operation | Gas Cost |
|-----------|----------|
| Memory expansion | 3 + (words²/512) |
| MLOAD/MSTORE | 3 |
| Calldata byte (zero) | 4 |
| Calldata byte (non-zero) | 16 |

## Computation
| Operation | Gas Cost |
|-----------|----------|
| ADD/SUB/MUL | 3 |
| DIV/MOD | 5 |
| EXP | 10 + 50/byte |
| SHA3/KECCAK256 | 30 + 6/word |

## External Calls
| Operation | Gas Cost |
|-----------|----------|
| CALL (cold) | 2,600 |
| CALL (warm) | 100 |
| STATICCALL | 2,600 (cold) |
| DELEGATECALL | 2,600 (cold) |
| CREATE | 32,000 |
| CREATE2 | 32,000 |

## Logs & Events
| Operation | Gas Cost |
|-----------|----------|
| LOG0 | 375 |
| LOG1 (1 indexed) | 375 + 375 |
| LOG2 (2 indexed) | 375 + 750 |
| LOG3 (3 indexed) | 375 + 1,125 |
| LOG4 (4 indexed) | 375 + 1,500 |

## Transaction Base Costs
| Type | Gas Cost |
|------|----------|
| Transaction base | 21,000 |
| Contract creation | +32,000 |
| Calldata (zero byte) | 4 |
| Calldata (non-zero) | 16 |
