# FIX Protocol Reference

## Overview
FIX (Financial Information Exchange) is the industry standard for electronic communication of trade-related messages. Currently on FIX 4.4 with ongoing 5.0 development.

## Session Management

### Session States
- **Disconnected**: No active session
- **LogInPending**: LogIn message sent, awaiting LogOn
- **LogOnReceived**: LogOn confirmed, ready for trading
- **LogOutPending**: LogOut initiated
- **ResynchronizationPending**: Sequence number correction

### Session Initialization
```
Client → Server: Logon (MsgType=A)
         - SenderCompID (49)
         - TargetCompID (56)
         - HeartBtInt (108) - Heartbeat interval
         - EncryptMethod (98)

Server → Client: Logon (MsgType=A)
         - Confirmation of connection
         - ResetSeqNumFlag if sequence reset

Both → Each: Heartbeat (MsgType=0) at regular intervals
```

## Message Structure

### Header
```
BeginString (8)       - Protocol version (FIX.4.4)
BodyLength (9)        - Message length excluding header
MsgType (35)          - Message type identifier
SenderCompID (49)     - Sending party
TargetCompID (56)     - Receiving party
MsgSeqNum (34)        - Sequence number for ordering
SendingTime (52)      - Message timestamp
```

### Trailer
```
SignLength (93)       - Signature length (if encrypted)
Signature (89)        - Digital signature
CheckSum (10)         - Checksum (calculated mod 256)
```

## Common Message Types

### Trading Messages
- **D - New Order Single**: Place new order
- **G - New Order List**: Place multiple orders
- **F - Order Cancel Request**: Cancel existing order
- **E - Order Cancel/Replace Request**: Amend order
- **8 - Execution Report**: Confirm execution or rejection

### Order Cancel/Replace
```
OrderID (37)          - Original order ID
ClOrdID (11)          - New order ID
ClOrdLinkID (583)     - Link to original
OrderQty (38)         - New quantity
Price (44)            - New price (if changed)
```

### Execution Reports
```
OrderID (37)          - Exchange order ID
ClOrdID (11)          - Client order ID
OrderStatus (39)      - Current status (0=New, 1=Partial, 2=Filled, 8=Rejected)
CumQty (14)           - Cumulative quantity filled
LastQty (32)          - Last fill quantity
LastPx (31)           - Last fill price
LeavesQty (151)       - Remaining quantity
AvgPx (6)             - Average execution price
```

## Resynchronization Protocol

### Sequence Number Management
- **InSeqNum**: Next expected incoming sequence
- **OutSeqNum**: Next outgoing sequence
- **Gap Detection**: Missing messages between expected and received

### Resynchronization Process
```
Client detects gap in sequences

Client → Server: Resend Request (MsgType=2)
                - BeginSeqNo (7): First sequence to resend
                - EndSeqNo (16): Last sequence to resend

Server → Client: Resend (MsgType=X): Gap fill messages

Client verifies sequence integrity and continues
```

## Heartbeat & Timeout Handling

### Heartbeat Mechanism
```
Sender → Receiver: Heartbeat at HeartBtInt intervals
- MsgType=0
- No additional fields

Receiver expects heartbeat within HeartBtInt + 2 seconds
If timeout: disconnect and resynchronize
```

### Test Request
```
Sender → Receiver: Test Request (MsgType=1)
                  - TestReqID (112): Identifier

Receiver → Sender: Heartbeat (MsgType=0)
                  - TestReqID (112): Echo of request
```

## Data Types

### String: Alphanumeric text (max length variable)
- Symbols: "AAPL", "IBM"
- CompIDs: "CLIENT1", "EXCH"

### Numeric: Integer values
- OrderQty: Quantity in shares
- MsgSeqNum: Sequence numbers

### Price: Decimal with 4 decimal places
- 100.2500 for $100.25
- Represented as numeric field

### Boolean: 'Y' for yes, 'N' for no
- ExecInst (108): Y/N values
- ResetSeqNumFlag: Y/N

### DateTime: YYYYMMDD-HH:MM:SS[.sss]
- UTCTimestamp format
- Nanosecond precision in some implementations

## Order Types

### Market Order
```
OrdType (40) = 1 (Market)
Price field: omitted
TimeInForce (59) = 0 (Day)
```

### Limit Order
```
OrdType (40) = 2 (Limit)
Price (44) = limit price
TimeInForce (59) = 0 (Day) or 1 (GTC) or 3 (IOC) or 4 (FOK)
```

### Stop Order
```
OrdType (40) = 3 (Stop)
StopPx (99) = stop trigger price
```

### Stop-Limit Order
```
OrdType (40) = 4 (Stop-Limit)
Price (44) = limit price
StopPx (99) = stop price
```

## Pegged Orders
```
ExecInst (108) = P (Pegged to primary mid)
PegOffsetValue (211) = offset from mid-price
PegPriceType (1094) = offset basis
```

## Iceberg Orders
```
DisplayQty (1138) = quantity to display
MaxFloor (210) = maximum visible quantity
```

## Session-Level Encryption (Optional)
- **EncryptMethod (98)**: 0 (None), 1 (PKCS), 2 (DES), etc.
- **SecDataLen (90)**: Length of encrypted data
- **SecData (91)**: Encrypted data block

## Performance Considerations

### Parsing Optimization
- Use SOH (Start of Message) delimiters: \x01
- Stream parsing without buffering entire message
- Pre-compiled field lookups
- Binary encoding alternatives (FIXT)

### Latency Targets
- Message parsing: <10µs
- Field extraction: <1µs per field
- Message generation: <10µs
- Session management: <1ms

### Best Practices
1. Use binary FIX for latency-critical flows
2. Implement message pooling for allocation efficiency
3. Use lock-free concurrent structures
4. Avoid string parsing in hot paths
5. Batch heartbeats efficiently

## Regulatory Compliance
- **Message Ordering**: Sequential MsgSeqNum required
- **Timestamp Accuracy**: Sub-second precision required
- **Non-repudiation**: Signature field for compliance
- **Audit Trail**: Complete message history
