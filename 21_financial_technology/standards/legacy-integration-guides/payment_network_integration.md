# Payment Network Integration Guide

## Table of Contents
1. [Introduction](#introduction)
2. [Card Network Integration](#card-network-integration)
3. [ACH File Processing](#ach-file-processing)
4. [SWIFT Message Integration](#swift-message-integration)
5. [Wire Transfer Protocols](#wire-transfer-protocols)
6. [Real-Time Payment Networks](#real-time-payment-networks)
7. [ISO 8583 Message Handling](#iso-8583-message-handling)
8. [ISO 20022 Migration Strategies](#iso-20022-migration-strategies)
9. [Best Practices](#best-practices)

---

## Introduction

Payment networks form the critical infrastructure enabling fund transfers between financial institutions. This guide covers integration patterns for legacy and modern payment systems, including card networks, ACH, SWIFT, wire transfers, and real-time payment rails.

### Key Payment Networks
- **Card Networks**: Visa, Mastercard, American Express, Discover
- **ACH**: NACHA-governed automated clearing house
- **SWIFT**: Society for Worldwide Interbank Financial Telecommunication
- **Wire Transfer**: Fedwire, CHIPS
- **Real-Time Payments**: RTP (The Clearing House), FedNow (Federal Reserve)
- **International**: SEPA, TARGET2, local schemes

### Industry Standards
- **ISO 8583**: Card transaction messaging
- **ISO 20022**: Universal financial messaging
- **NACHA Operating Rules**: ACH processing standards
- **SWIFT MT**: Legacy SWIFT message types
- **SWIFT MX**: ISO 20022-based SWIFT messages
- **PCI DSS**: Payment Card Industry Data Security Standard

---

## Card Network Integration

### ISO 8583 Message Structure

ISO 8583 is the international standard for financial transaction card originated interchange messaging. Messages consist of:

```
┌─────────────────────────────────────────────┐
│  Message Type Indicator (MTI) - 4 digits    │
├─────────────────────────────────────────────┤
│  Bitmap(s) - 64 or 128 or 192 bits          │
├─────────────────────────────────────────────┤
│  Data Elements - Variable fields            │
└─────────────────────────────────────────────┘
```

#### Message Type Indicators

```
Format: VXYZ
V - Version (0-9)
X - Message Class
  0 - Management
  1 - Authorization
  2 - Financial
  3 - File Action
  4 - Reversal/Chargeback
  5 - Reconciliation
  6 - Administrative
  7 - Fee Collection
  8 - Network Management
  9 - Reserved

Y - Message Function
  0 - Request
  1 - Request Response
  2 - Advice
  3 - Advice Response
  4 - Notification
  5-9 - Reserved

Z - Transaction Originator
  0 - Acquirer
  1 - Acquirer Repeat
  2 - Issuer
  3 - Issuer Repeat
  4 - Other
  5-9 - Reserved

Examples:
0100 - Authorization Request
0110 - Authorization Response
0200 - Financial Transaction Request
0210 - Financial Transaction Response
0420 - Reversal Request
0430 - Reversal Response
```

### Implementation Example

```java
package com.bank.payments.iso8583;

import org.jpos.iso.*;
import org.jpos.iso.packager.GenericPackager;

public class ISO8583CardProcessor {

    private ISOPackager packager;
    private ISOChannel channel;

    public void initialize() throws Exception {
        // Load ISO8583 configuration
        packager = new GenericPackager("iso8583-visa.xml");

        // Initialize network connection to card network
        ServerChannel serverChannel = new NACChannel(
            "cardnetwork.visa.com",
            9000,
            packager
        );

        serverChannel.setTimeout(60000);  // 60 second timeout
        serverChannel.connect();

        this.channel = serverChannel;
    }

    public AuthorizationResponse authorize(AuthorizationRequest request)
            throws ISOException {

        // Build ISO 8583 0100 message
        ISOMsg authMessage = new ISOMsg();
        authMessage.setPackager(packager);

        // Set MTI for authorization request
        authMessage.setMTI("0100");

        // Primary Account Number (PAN)
        authMessage.set(2, request.getCardNumber());

        // Processing Code
        // Format: TTFFAA (Transaction Type, From Account, To Account)
        authMessage.set(3, "000000");  // Purchase from default account

        // Transaction Amount (12 digits, right justified, zero filled)
        long amountCents = request.getAmount()
            .multiply(new BigDecimal(100))
            .longValue();
        authMessage.set(4, String.format("%012d", amountCents));

        // Transmission Date & Time (MMDDhhmmss)
        authMessage.set(7, new SimpleDateFormat("MMddHHmmss")
            .format(new Date()));

        // System Trace Audit Number (STAN)
        authMessage.set(11, generateSTAN());

        // Time, Local Transaction (hhmmss)
        authMessage.set(12, new SimpleDateFormat("HHmmss")
            .format(new Date()));

        // Date, Local Transaction (MMDD)
        authMessage.set(13, new SimpleDateFormat("MMdd")
            .format(new Date()));

        // Date, Expiration (YYMM)
        authMessage.set(14, request.getExpirationDate());

        // Merchant Type (MCC)
        authMessage.set(18, request.getMerchantCategoryCode());

        // POS Entry Mode
        // 01 = Manual, 02 = Magnetic Stripe, 05 = Chip, 07 = Contactless
        authMessage.set(22, "051");  // Chip with PIN

        // Card Sequence Number
        authMessage.set(23, "001");

        // Function Code (authorization)
        authMessage.set(24, "100");

        // Acquiring Institution ID
        authMessage.set(32, request.getAcquirerId());

        // Forwarding Institution ID
        authMessage.set(33, "999999");  // Card network

        // Track 2 Data (if magnetic stripe)
        if (request.getTrack2Data() != null) {
            authMessage.set(35, request.getTrack2Data());
        }

        // Retrieval Reference Number
        authMessage.set(37, generateRRN());

        // Authorization ID Response (for reversal/clearing)
        if (request.getAuthorizationId() != null) {
            authMessage.set(38, request.getAuthorizationId());
        }

        // Response Code (blank for request)
        // authMessage.set(39, "  ");

        // Card Acceptor Terminal ID
        authMessage.set(41, request.getTerminalId());

        // Card Acceptor ID Code (Merchant ID)
        authMessage.set(42, request.getMerchantId());

        // Card Acceptor Name/Location
        authMessage.set(43, request.getMerchantName() + " " +
            request.getMerchantCity() + " " + request.getMerchantState());

        // Currency Code (ISO 4217)
        authMessage.set(49, request.getCurrencyCode());

        // PIN Data
        if (request.getPinBlock() != null) {
            authMessage.set(52, ISOUtil.hex2byte(request.getPinBlock()));
        }

        // Security Related Control Information
        authMessage.set(53, "2600000000000000");  // PIN encryption

        // EMV Data (ICC/Chip Data)
        if (request.getEmvData() != null) {
            authMessage.set(55, ISOUtil.hex2byte(request.getEmvData()));
        }

        // Additional amounts (cashback, etc.)
        if (request.getCashbackAmount() != null) {
            long cashbackCents = request.getCashbackAmount()
                .multiply(new BigDecimal(100))
                .longValue();
            authMessage.set(54, String.format("40%012d", cashbackCents));
        }

        // Network Management Information Code
        authMessage.set(70, "001");  // Original message

        // Send message and receive response
        channel.send(authMessage);
        ISOMsg response = channel.receive();

        return parseAuthorizationResponse(response);
    }

    private AuthorizationResponse parseAuthorizationResponse(ISOMsg response)
            throws ISOException {

        AuthorizationResponse authResponse = new AuthorizationResponse();

        // Verify MTI
        if (!"0110".equals(response.getMTI())) {
            throw new ISOException("Invalid response MTI: " +
                response.getMTI());
        }

        // Response Code (Field 39)
        String responseCode = response.getString(39);
        authResponse.setResponseCode(responseCode);
        authResponse.setApproved("00".equals(responseCode));

        // Authorization ID Code (Field 38)
        if (response.hasField(38)) {
            authResponse.setAuthorizationId(response.getString(38));
        }

        // System Trace Audit Number (Field 11)
        authResponse.setSystemTraceNumber(response.getString(11));

        // Retrieval Reference Number (Field 37)
        authResponse.setRetrievalReferenceNumber(response.getString(37));

        // Available Balance (Field 54)
        if (response.hasField(54)) {
            String additionalAmounts = response.getString(54);
            // Parse additional amounts format: AATTTCCCCCCCCCCCC
            // AA = Account Type, TTT = Amount Type, CC = Currency Code
            // CCCCCCCCCCCC = Amount
            authResponse.setAvailableBalance(
                parseAdditionalAmount(additionalAmounts)
            );
        }

        // EMV Response Data (Field 55)
        if (response.hasField(55)) {
            byte[] emvData = response.getBytes(55);
            authResponse.setEmvResponseData(ISOUtil.hexString(emvData));
        }

        return authResponse;
    }

    public CaptureResponse capture(CaptureRequest request) throws ISOException {
        // Build ISO 8583 0200 message for financial transaction
        ISOMsg captureMessage = new ISOMsg();
        captureMessage.setPackager(packager);
        captureMessage.setMTI("0200");

        // Similar to authorization, but with different MTI and function code
        captureMessage.set(2, request.getCardNumber());
        captureMessage.set(3, "000000");  // Purchase

        long amountCents = request.getAmount()
            .multiply(new BigDecimal(100))
            .longValue();
        captureMessage.set(4, String.format("%012d", amountCents));

        captureMessage.set(7, new SimpleDateFormat("MMddHHmmss")
            .format(new Date()));
        captureMessage.set(11, generateSTAN());
        captureMessage.set(12, new SimpleDateFormat("HHmmss")
            .format(new Date()));
        captureMessage.set(13, new SimpleDateFormat("MMdd")
            .format(new Date()));

        // Function Code (200 = financial presentment)
        captureMessage.set(24, "200");

        captureMessage.set(37, request.getRetrievalReferenceNumber());
        captureMessage.set(38, request.getAuthorizationId());
        captureMessage.set(41, request.getTerminalId());
        captureMessage.set(42, request.getMerchantId());
        captureMessage.set(49, request.getCurrencyCode());

        channel.send(captureMessage);
        ISOMsg response = channel.receive();

        return parseCaptureResponse(response);
    }

    public ReversalResponse reverse(ReversalRequest request) throws ISOException {
        // Build ISO 8583 0420 reversal message
        ISOMsg reversalMessage = new ISOMsg();
        reversalMessage.setPackager(packager);
        reversalMessage.setMTI("0420");

        // Copy fields from original transaction
        reversalMessage.set(2, request.getOriginalCardNumber());
        reversalMessage.set(3, request.getOriginalProcessingCode());
        reversalMessage.set(4, request.getOriginalAmount());
        reversalMessage.set(11, generateSTAN());  // New STAN
        reversalMessage.set(37, request.getOriginalRRN());
        reversalMessage.set(38, request.getOriginalAuthId());
        reversalMessage.set(41, request.getTerminalId());
        reversalMessage.set(42, request.getMerchantId());

        // Reason for reversal (Field 56)
        // 4021 = Customer cancellation
        // 4030 = Suspected fraud
        // 4352 = Timeout
        reversalMessage.set(56, request.getReversalReasonCode());

        // Original Data Elements (Field 90)
        String originalData = String.format(
            "%s%s%s%s",
            request.getOriginalMTI(),
            request.getOriginalSTAN(),
            request.getOriginalTransmissionDateTime(),
            request.getOriginalAcquirerID()
        );
        reversalMessage.set(90, originalData);

        channel.send(reversalMessage);
        ISOMsg response = channel.receive();

        return parseReversalResponse(response);
    }

    private String generateSTAN() {
        // System Trace Audit Number: 6-digit unique number
        // Should be sequential and unique per day
        return String.format("%06d",
            stanCounter.incrementAndGet() % 1000000);
    }

    private String generateRRN() {
        // Retrieval Reference Number: 12-character alphanumeric
        // Format: YYDDDHHNNNNNN (Year, Day of Year, Hour, Sequence)
        Calendar cal = Calendar.getInstance();
        return String.format(
            "%02d%03d%02d%06d",
            cal.get(Calendar.YEAR) % 100,
            cal.get(Calendar.DAY_OF_YEAR),
            cal.get(Calendar.HOUR_OF_DAY),
            rrnCounter.incrementAndGet() % 1000000
        );
    }
}
```

### Visa/Mastercard Specific Integration

#### Visa VisaNet Configuration

```xml
<!-- iso8583-visa.xml packager configuration -->
<isopackager>
  <isofield
      id="0"
      length="4"
      name="MESSAGE TYPE INDICATOR"
      class="org.jpos.iso.IFA_NUMERIC"/>

  <isofield
      id="1"
      length="16"
      name="BIT MAP"
      class="org.jpos.iso.IFA_BITMAP"/>

  <isofield
      id="2"
      length="19"
      name="PAN - PRIMARY ACCOUNT NUMBER"
      class="org.jpos.iso.IFA_LLNUM"/>

  <isofield
      id="3"
      length="6"
      name="PROCESSING CODE"
      class="org.jpos.iso.IFA_NUMERIC"/>

  <isofield
      id="4"
      length="12"
      name="AMOUNT, TRANSACTION"
      class="org.jpos.iso.IFA_NUMERIC"/>

  <!-- Additional fields... -->

  <isofield
      id="55"
      length="999"
      name="ICC DATA – EMV HAVING MULTIPLE TAGS"
      class="org.jpos.iso.IFB_LLLBINARY"/>
</isopackager>
```

#### Mastercard IPM Integration

```java
public class MastercardIPMProcessor {

    /**
     * IPM (Interbank Payment Message) for Mastercard clearing
     */
    public IPMMessage buildIPMMessage(ClearingTransaction transaction) {
        IPMMessage ipm = new IPMMessage();

        // Message Type: 1240 = First Presentment
        ipm.setMessageType("1240");

        // PDS (Presentation Data Set) - Main transaction data
        PDS0105 pds = new PDS0105();  // Card payment transaction

        // Transaction identifier
        pds.setDestinationAmount(transaction.getAmount()
            .multiply(new BigDecimal(100))
            .longValue());

        pds.setTransactionCurrencyCode(
            getCurrencyCode(transaction.getCurrency())
        );

        pds.setMerchantCategoryCode(transaction.getMCC());

        // Card acceptor data
        pds.setCardAcceptorBusinessCode(transaction.getMerchantId());
        pds.setCardAcceptorTerminalId(transaction.getTerminalId());

        // Cardholder verification method
        pds.setCVMResults(transaction.getCVMResults());

        // EMV chip data
        if (transaction.hasEMVData()) {
            pds.setICCData(transaction.getEMVData());
        }

        // PDS 0023 - Cardholder authentication data
        if (transaction.has3DSecure()) {
            PDS0023 authData = new PDS0023();
            authData.setECommerceIndicator(
                transaction.get3DSecureECI()
            );
            authData.setTransactionId(
                transaction.get3DSecureTransactionId()
            );
            ipm.addPDS(authData);
        }

        ipm.setPrimaryPDS(pds);

        return ipm;
    }

    public void sendToMastercard(IPMMessage message) {
        // Connect to Mastercard clearing system
        // Typically via dedicated network connection or VPN
        MastercardConnection connection = mastercardConnectionPool.getConnection();

        try {
            // Serialize IPM message
            byte[] messageBytes = message.serialize();

            // Send via MATCH (Mastercard Authorization System)
            connection.send(messageBytes);

            // Receive acknowledgment
            byte[] ack = connection.receive();

            if (!isAcknowledged(ack)) {
                throw new ClearingException("IPM rejected by Mastercard");
            }

        } finally {
            connection.release();
        }
    }
}
```

---

## ACH File Processing

### NACHA File Format

ACH (Automated Clearing House) files follow NACHA specifications:

```
File Structure:
┌─────────────────────────────────┐
│  File Header Record (1)         │  94 bytes
├─────────────────────────────────┤
│  ┌─────────────────────────────┐│
│  │ Batch Header Record (5)     ││  94 bytes
│  ├─────────────────────────────┤│
│  │ Entry Detail Record (6)     ││  94 bytes (multiple)
│  ├─────────────────────────────┤│
│  │ Addenda Record (7) optional ││  94 bytes (multiple)
│  ├─────────────────────────────┤│
│  │ Batch Control Record (8)    ││  94 bytes
│  └─────────────────────────────┘│
│  (Multiple batches...)          │
├─────────────────────────────────┤
│  File Control Record (9)        │  94 bytes
└─────────────────────────────────┘
```

### ACH File Generation

```java
public class ACHFileGenerator {

    private static final int RECORD_LENGTH = 94;

    public String generateACHFile(ACHBatch batch) {
        StringBuilder ach = new StringBuilder();

        // File Header Record (Type 1)
        ach.append(buildFileHeader(batch));

        // Batch Header Record (Type 5)
        ach.append(buildBatchHeader(batch));

        // Entry Detail Records (Type 6)
        int entryHash = 0;
        BigDecimal totalDebit = BigDecimal.ZERO;
        BigDecimal totalCredit = BigDecimal.ZERO;

        for (ACHEntry entry : batch.getEntries()) {
            ach.append(buildEntryDetail(entry));

            // Calculate entry hash (sum of routing numbers, mod 10)
            String routingNumber = entry.getReceivingDFI();
            entryHash += Integer.parseInt(routingNumber.substring(0, 8));

            if (entry.isDebit()) {
                totalDebit = totalDebit.add(entry.getAmount());
            } else {
                totalCredit = totalCredit.add(entry.getAmount());
            }

            // Addenda Records if needed
            if (entry.hasAddenda()) {
                for (ACHAddenda addenda : entry.getAddenda()) {
                    ach.append(buildAddenda(addenda));
                }
            }
        }

        // Batch Control Record (Type 8)
        ach.append(buildBatchControl(batch, entryHash, totalDebit, totalCredit));

        // File Control Record (Type 9)
        ach.append(buildFileControl(batch));

        return ach.toString();
    }

    private String buildFileHeader(ACHBatch batch) {
        StringBuilder header = new StringBuilder();

        // Position 1-1: Record Type Code
        header.append("1");

        // Position 2-3: Priority Code (01-99)
        header.append("01");

        // Position 4-13: Immediate Destination (routing number)
        header.append(String.format(" %9s", batch.getDestinationRoutingNumber()));

        // Position 14-23: Immediate Origin (company ID)
        header.append(String.format("%10s", batch.getOriginatorId()));

        // Position 24-29: File Creation Date (YYMMDD)
        header.append(new SimpleDateFormat("yyMMdd").format(batch.getCreationDate()));

        // Position 30-33: File Creation Time (HHMM)
        header.append(new SimpleDateFormat("HHmm").format(batch.getCreationDate()));

        // Position 34: File ID Modifier (A-Z, 0-9)
        header.append(batch.getFileIdModifier());

        // Position 35-37: Record Size (094)
        header.append("094");

        // Position 38-39: Blocking Factor (10)
        header.append("10");

        // Position 40: Format Code (1)
        header.append("1");

        // Position 41-63: Immediate Destination Name
        header.append(String.format("%-23s", batch.getDestinationName()));

        // Position 64-86: Immediate Origin Name
        header.append(String.format("%-23s", batch.getOriginatorName()));

        // Position 87-94: Reference Code
        header.append(String.format("%-8s", batch.getReferenceCode()));

        return padToLength(header.toString(), RECORD_LENGTH) + "\n";
    }

    private String buildBatchHeader(ACHBatch batch) {
        StringBuilder header = new StringBuilder();

        // Record Type Code: 5
        header.append("5");

        // Service Class Code
        // 200 = Mixed debits and credits
        // 220 = Credits only
        // 225 = Debits only
        header.append(batch.getServiceClassCode());

        // Company Name (16 characters)
        header.append(String.format("%-16s", batch.getCompanyName()));

        // Company Discretionary Data (20 characters)
        header.append(String.format("%-20s",
            batch.getDiscretionaryData() != null ?
                batch.getDiscretionaryData() : ""));

        // Company Identification (10 characters)
        header.append(String.format("%10s", batch.getCompanyId()));

        // Standard Entry Class Code (3 characters)
        // PPD = Prearranged Payment and Deposit
        // CCD = Corporate Credit or Debit
        // WEB = Internet-Initiated Entry
        // TEL = Telephone-Initiated Entry
        header.append(batch.getStandardEntryClassCode());

        // Company Entry Description (10 characters)
        header.append(String.format("%-10s", batch.getCompanyEntryDescription()));

        // Company Descriptive Date (6 characters, YYMMDD)
        if (batch.getDescriptiveDate() != null) {
            header.append(new SimpleDateFormat("yyMMdd")
                .format(batch.getDescriptiveDate()));
        } else {
            header.append("      ");
        }

        // Effective Entry Date (6 characters, YYMMDD)
        header.append(new SimpleDateFormat("yyMMdd")
            .format(batch.getEffectiveDate()));

        // Settlement Date (3 characters, Julian)
        header.append("   ");  // Assigned by ACH operator

        // Originator Status Code (1 character)
        header.append("1");  // 1 = Bank

        // Originating DFI Identification (8 characters)
        String routingNumber = batch.getOriginatorRoutingNumber();
        header.append(routingNumber.substring(0, 8));

        // Batch Number (7 digits)
        header.append(String.format("%07d", batch.getBatchNumber()));

        return padToLength(header.toString(), RECORD_LENGTH) + "\n";
    }

    private String buildEntryDetail(ACHEntry entry) {
        StringBuilder detail = new StringBuilder();

        // Record Type Code: 6
        detail.append("6");

        // Transaction Code (2 digits)
        // 22 = Checking Credit (deposit)
        // 27 = Checking Debit (withdrawal)
        // 32 = Savings Credit
        // 37 = Savings Debit
        detail.append(entry.getTransactionCode());

        // Receiving DFI Identification (8 digits)
        String routingNumber = entry.getReceivingDFI();
        detail.append(routingNumber.substring(0, 8));

        // Check Digit (1 digit) - 9th digit of routing number
        detail.append(routingNumber.substring(8, 9));

        // DFI Account Number (17 characters, left-justified)
        detail.append(String.format("%-17s", entry.getAccountNumber()));

        // Amount (10 digits, right-justified, zero-filled, in cents)
        long amountCents = entry.getAmount()
            .multiply(new BigDecimal(100))
            .longValue();
        detail.append(String.format("%010d", amountCents));

        // Individual Identification Number (15 characters)
        detail.append(String.format("%-15s",
            entry.getIndividualId() != null ?
                entry.getIndividualId() : ""));

        // Individual Name (22 characters)
        detail.append(String.format("%-22s", entry.getIndividualName()));

        // Discretionary Data (2 characters)
        detail.append("  ");

        // Addenda Record Indicator (1 character)
        detail.append(entry.hasAddenda() ? "1" : "0");

        // Trace Number (15 digits)
        // First 8: Originating DFI routing number
        // Last 7: Sequence number
        detail.append(String.format("%8s%07d",
            entry.getOriginatingDFI().substring(0, 8),
            entry.getTraceSequence()));

        return padToLength(detail.toString(), RECORD_LENGTH) + "\n";
    }

    private String buildBatchControl(ACHBatch batch, int entryHash,
            BigDecimal totalDebit, BigDecimal totalCredit) {

        StringBuilder control = new StringBuilder();

        // Record Type Code: 8
        control.append("8");

        // Service Class Code (same as batch header)
        control.append(batch.getServiceClassCode());

        // Entry/Addenda Count (6 digits)
        int totalRecords = batch.getEntries().size() +
            batch.getEntries().stream()
                .mapToInt(e -> e.getAddenda().size())
                .sum();
        control.append(String.format("%06d", totalRecords));

        // Entry Hash (10 digits, rightmost 10 digits of sum)
        control.append(String.format("%010d", entryHash % 10000000000L));

        // Total Debit Entry Dollar Amount (12 digits, in cents)
        long debitCents = totalDebit.multiply(new BigDecimal(100)).longValue();
        control.append(String.format("%012d", debitCents));

        // Total Credit Entry Dollar Amount (12 digits, in cents)
        long creditCents = totalCredit.multiply(new BigDecimal(100)).longValue();
        control.append(String.format("%012d", creditCents));

        // Company Identification (10 characters)
        control.append(String.format("%10s", batch.getCompanyId()));

        // Message Authentication Code (19 characters)
        control.append(String.format("%-19s", ""));  // Usually blank

        // Reserved (6 characters)
        control.append("      ");

        // Originating DFI Identification (8 characters)
        String routingNumber = batch.getOriginatorRoutingNumber();
        control.append(routingNumber.substring(0, 8));

        // Batch Number (7 digits)
        control.append(String.format("%07d", batch.getBatchNumber()));

        return padToLength(control.toString(), RECORD_LENGTH) + "\n";
    }

    private String buildFileControl(ACHBatch batch) {
        StringBuilder control = new StringBuilder();

        // Record Type Code: 9
        control.append("9");

        // Batch Count (6 digits)
        control.append(String.format("%06d", 1));  // Single batch

        // Block Count (6 digits) - number of physical blocks
        int recordCount = 4 + batch.getEntries().size();  // Header, batch header/control, file control
        int blockCount = (int) Math.ceil(recordCount / 10.0);
        control.append(String.format("%06d", blockCount));

        // Entry/Addenda Count (8 digits)
        int totalRecords = batch.getEntries().size();
        control.append(String.format("%08d", totalRecords));

        // Entry Hash (10 digits)
        int entryHash = batch.getEntries().stream()
            .mapToInt(e -> Integer.parseInt(e.getReceivingDFI().substring(0, 8)))
            .sum();
        control.append(String.format("%010d", entryHash % 10000000000L));

        // Total Debit Amount (12 digits)
        BigDecimal totalDebit = batch.getEntries().stream()
            .filter(ACHEntry::isDebit)
            .map(ACHEntry::getAmount)
            .reduce(BigDecimal.ZERO, BigDecimal::add);
        long debitCents = totalDebit.multiply(new BigDecimal(100)).longValue();
        control.append(String.format("%012d", debitCents));

        // Total Credit Amount (12 digits)
        BigDecimal totalCredit = batch.getEntries().stream()
            .filter(e -> !e.isDebit())
            .map(ACHEntry::getAmount)
            .reduce(BigDecimal.ZERO, BigDecimal::add);
        long creditCents = totalCredit.multiply(new BigDecimal(100)).longValue();
        control.append(String.format("%012d", creditCents));

        // Reserved (39 characters)
        control.append(String.format("%-39s", ""));

        return padToLength(control.toString(), RECORD_LENGTH) + "\n";
    }

    private String padToLength(String s, int length) {
        if (s.length() >= length) {
            return s.substring(0, length);
        }
        return s + " ".repeat(length - s.length());
    }
}
```

### ACH File Parsing

```java
public class ACHFileParser {

    public ACHFile parse(String achFileContent) throws ACHParseException {
        String[] lines = achFileContent.split("\n");

        ACHFile achFile = new ACHFile();

        int lineIndex = 0;

        // Parse File Header (Record Type 1)
        if (!lines[lineIndex].startsWith("1")) {
            throw new ACHParseException("Missing file header");
        }
        achFile.setFileHeader(parseFileHeader(lines[lineIndex++]));

        // Parse batches
        while (lineIndex < lines.length) {
            String line = lines[lineIndex];

            if (line.startsWith("5")) {
                // Batch Header
                ACHBatch batch = new ACHBatch();
                batch.setBatchHeader(parseBatchHeader(line));
                lineIndex++;

                // Parse entries
                while (lineIndex < lines.length &&
                       lines[lineIndex].startsWith("6")) {
                    ACHEntry entry = parseEntryDetail(lines[lineIndex++]);

                    // Check for addenda
                    while (lineIndex < lines.length &&
                           lines[lineIndex].startsWith("7")) {
                        ACHAddenda addenda = parseAddenda(lines[lineIndex++]);
                        entry.addAddenda(addenda);
                    }

                    batch.addEntry(entry);
                }

                // Parse Batch Control (Record Type 8)
                if (!lines[lineIndex].startsWith("8")) {
                    throw new ACHParseException("Missing batch control");
                }
                batch.setBatchControl(parseBatchControl(lines[lineIndex++]));

                achFile.addBatch(batch);

            } else if (line.startsWith("9")) {
                // File Control Record
                achFile.setFileControl(parseFileControl(line));
                break;
            } else {
                throw new ACHParseException("Unexpected record type: " +
                    line.charAt(0));
            }
        }

        // Validate file
        validateACHFile(achFile);

        return achFile;
    }

    private ACHEntry parseEntryDetail(String line) {
        ACHEntry entry = new ACHEntry();

        // Record Type (position 1)
        if (line.charAt(0) != '6') {
            throw new ACHParseException("Invalid entry detail record");
        }

        // Transaction Code (positions 2-3)
        entry.setTransactionCode(line.substring(1, 3));

        // Receiving DFI Identification (positions 4-11)
        String routingFirst8 = line.substring(3, 11);

        // Check Digit (position 12)
        String checkDigit = line.substring(11, 12);

        entry.setReceivingDFI(routingFirst8 + checkDigit);

        // DFI Account Number (positions 13-29)
        entry.setAccountNumber(line.substring(12, 29).trim());

        // Amount (positions 30-39, in cents)
        long amountCents = Long.parseLong(line.substring(29, 39));
        entry.setAmount(new BigDecimal(amountCents).divide(new BigDecimal(100)));

        // Individual Identification Number (positions 40-54)
        entry.setIndividualId(line.substring(39, 54).trim());

        // Individual Name (positions 55-76)
        entry.setIndividualName(line.substring(54, 76).trim());

        // Addenda Record Indicator (position 79)
        entry.setHasAddenda(line.charAt(78) == '1');

        // Trace Number (positions 80-94)
        entry.setOriginatingDFI(line.substring(79, 87));
        entry.setTraceSequence(Integer.parseInt(line.substring(87, 94)));

        return entry;
    }

    private void validateACHFile(ACHFile achFile) throws ACHParseException {
        // Validate batch counts
        int actualBatches = achFile.getBatches().size();
        int expectedBatches = achFile.getFileControl().getBatchCount();

        if (actualBatches != expectedBatches) {
            throw new ACHParseException(
                String.format("Batch count mismatch: expected %d, found %d",
                    expectedBatches, actualBatches)
            );
        }

        // Validate entry counts and amounts
        for (ACHBatch batch : achFile.getBatches()) {
            int actualEntries = batch.getEntries().size();
            int expectedEntries = batch.getBatchControl().getEntryCount();

            if (actualEntries != expectedEntries) {
                throw new ACHParseException(
                    String.format("Entry count mismatch in batch %d: expected %d, found %d",
                        batch.getBatchNumber(), expectedEntries, actualEntries)
                );
            }

            // Validate amounts
            BigDecimal actualDebit = batch.getEntries().stream()
                .filter(ACHEntry::isDebit)
                .map(ACHEntry::getAmount)
                .reduce(BigDecimal.ZERO, BigDecimal::add);

            BigDecimal expectedDebit = batch.getBatchControl().getTotalDebit();

            if (actualDebit.compareTo(expectedDebit) != 0) {
                throw new ACHParseException(
                    String.format("Debit amount mismatch in batch %d",
                        batch.getBatchNumber())
                );
            }
        }
    }
}
```

---

## SWIFT Message Integration

### SWIFT MT Message Format

SWIFT MT (Message Type) messages are text-based with a specific structure:

```
{1:Basic Header Block}
{2:Application Header Block}
{3:User Header Block}
{4:Text Block
:20:Transaction Reference
:32A:Value Date/Currency/Amount
:50K:Ordering Customer
:59:Beneficiary Customer
-}
{5:Trailers Block}
```

### MT103 (Single Customer Credit Transfer)

```java
public class SWIFTMessageGenerator {

    public String generateMT103(WireTransfer transfer) {
        StringBuilder mt103 = new StringBuilder();

        // Block 1: Basic Header
        mt103.append("{1:").append(buildBasicHeader()).append("}");

        // Block 2: Application Header
        mt103.append("{2:").append(buildApplicationHeader("MT103")).append("}");

        // Block 3: User Header (optional)
        if (transfer.hasUserHeader()) {
            mt103.append("{3:").append(buildUserHeader(transfer)).append("}");
        }

        // Block 4: Text Block
        mt103.append("{4:\n");

        // Field 20: Sender's Reference
        mt103.append(":20:").append(transfer.getReference()).append("\n");

        // Field 23B: Bank Operation Code
        mt103.append(":23B:CRED\n");  // Credit transfer

        // Field 32A: Value Date, Currency Code, Amount
        mt103.append(":32A:")
            .append(formatDate(transfer.getValueDate()))
            .append(transfer.getCurrency())
            .append(formatAmount(transfer.getAmount()))
            .append("\n");

        // Field 50K: Ordering Customer
        mt103.append(":50K:")
            .append(formatAccount(transfer.getOrderingAccount()))
            .append("\n")
            .append(formatNameAddress(transfer.getOrderingCustomer()))
            .append("\n");

        // Field 52A/52D: Ordering Institution
        if (transfer.hasOrderingInstitution()) {
            mt103.append(":52A:")
                .append(transfer.getOrderingInstitutionBIC())
                .append("\n");
        }

        // Field 56A/56D: Intermediary Institution (optional)
        if (transfer.hasIntermediaryBank()) {
            mt103.append(":56A:")
                .append(transfer.getIntermediaryBIC())
                .append("\n");
        }

        // Field 57A/57D: Account With Institution
        mt103.append(":57A:")
            .append(transfer.getBeneficiaryBankBIC())
            .append("\n");

        // Field 59: Beneficiary Customer
        mt103.append(":59:")
            .append(formatAccount(transfer.getBeneficiaryAccount()))
            .append("\n")
            .append(formatNameAddress(transfer.getBeneficiaryCustomer()))
            .append("\n");

        // Field 70: Remittance Information
        if (transfer.hasRemittanceInfo()) {
            mt103.append(":70:")
                .append(formatRemittanceInfo(transfer.getRemittanceInfo()))
                .append("\n");
        }

        // Field 71A: Details of Charges
        mt103.append(":71A:").append(transfer.getChargeBearer()).append("\n");
        // OUR = Sender pays all charges
        // BEN = Beneficiary pays all charges
        // SHA = Charges shared

        mt103.append("-}");

        // Block 5: Trailers (optional - for authentication)
        if (transfer.requiresAuthentication()) {
            mt103.append("{5:").append(buildTrailers(transfer)).append("}");
        }

        return mt103.toString();
    }

    private String formatDate(LocalDate date) {
        // Format: YYMMDD
        return date.format(DateTimeFormatter.ofPattern("yyMMdd"));
    }

    private String formatAmount(BigDecimal amount) {
        // Format: Up to 15 digits with comma as decimal separator
        // Example: 1234567,89
        String formatted = amount.setScale(2, RoundingMode.HALF_UP)
            .toPlainString()
            .replace(".", ",");

        return formatted;
    }

    private String formatAccount(String account) {
        // Format: /account_number
        return "/" + account;
    }

    private String formatNameAddress(Address address) {
        // Format: Up to 4 lines of 35 characters each
        StringBuilder formatted = new StringBuilder();

        // Line 1: Name
        formatted.append(truncate(address.getName(), 35)).append("\n");

        // Line 2: Address Line 1
        formatted.append(truncate(address.getAddressLine1(), 35)).append("\n");

        // Line 3: Address Line 2 or City
        if (address.getAddressLine2() != null) {
            formatted.append(truncate(address.getAddressLine2(), 35)).append("\n");
        }

        // Line 4: City, State, Postal Code
        String cityLine = String.format("%s %s %s",
            address.getCity(),
            address.getState() != null ? address.getState() : "",
            address.getPostalCode() != null ? address.getPostalCode() : ""
        ).trim();
        formatted.append(truncate(cityLine, 35));

        return formatted.toString();
    }

    private String formatRemittanceInfo(String info) {
        // Maximum 4 lines of 35 characters
        String[] lines = splitIntoLines(info, 35, 4);
        return String.join("\n", lines);
    }
}
```

### SWIFT MT Parser

```java
public class SWIFTMTParser {

    public SWIFTMessage parse(String message) {
        SWIFTMessage swift = new SWIFTMessage();

        // Extract blocks using regex
        Pattern blockPattern = Pattern.compile("\\{(\\d):([^}]+)\\}");
        Matcher matcher = blockPattern.matcher(message);

        while (matcher.find()) {
            String blockNumber = matcher.group(1);
            String blockContent = matcher.group(2);

            switch (blockNumber) {
                case "1":
                    swift.setBasicHeader(parseBasicHeader(blockContent));
                    break;
                case "2":
                    swift.setApplicationHeader(parseApplicationHeader(blockContent));
                    break;
                case "3":
                    swift.setUserHeader(parseUserHeader(blockContent));
                    break;
                case "4":
                    swift.setTextBlock(parseTextBlock(blockContent));
                    break;
                case "5":
                    swift.setTrailers(parseTrailers(blockContent));
                    break;
            }
        }

        return swift;
    }

    private Map<String, String> parseTextBlock(String textBlock) {
        Map<String, String> fields = new LinkedHashMap<>();

        // Parse field tags (format :TAG:value)
        Pattern fieldPattern = Pattern.compile(":([^:]+):((?:(?!:)[\\s\\S])*)", Pattern.MULTILINE);
        Matcher matcher = fieldPattern.matcher(textBlock);

        while (matcher.find()) {
            String tag = matcher.group(1);
            String value = matcher.group(2).trim();
            fields.put(tag, value);
        }

        return fields;
    }

    public WireTransfer parseToWireTransfer(SWIFTMessage message) {
        Map<String, String> fields = message.getTextBlock();

        WireTransfer transfer = new WireTransfer();

        // Field 20: Transaction Reference
        transfer.setReference(fields.get("20"));

        // Field 32A: Value Date, Currency, Amount
        String field32A = fields.get("32A");
        transfer.setValueDate(parseDate(field32A.substring(0, 6)));
        transfer.setCurrency(field32A.substring(6, 9));
        transfer.setAmount(parseAmount(field32A.substring(9)));

        // Field 50K: Ordering Customer
        transfer.setOrderingCustomer(parseNameAddress(fields.get("50K")));

        // Field 59: Beneficiary Customer
        transfer.setBeneficiaryCustomer(parseNameAddress(fields.get("59")));

        // Field 70: Remittance Information
        if (fields.containsKey("70")) {
            transfer.setRemittanceInfo(fields.get("70"));
        }

        // Field 71A: Details of Charges
        if (fields.containsKey("71A")) {
            transfer.setChargeBearer(fields.get("71A"));
        }

        return transfer;
    }
}
```

---

## Wire Transfer Protocols

### Fedwire Integration

```java
public class FedwireService {

    private FedwireConnection connection;

    /**
     * Fedwire message format (FAIM - Fedwire Accounting and Information Management)
     */
    public FedwireResponse sendWire(FedwireRequest request) {
        // Build Fedwire message
        FedwireMessage message = new FedwireMessage();

        // Type and Subtype Tag {1510}
        message.addTag("1510", "1000");  // 1000 = Customer Transfer

        // IMAD (Input Message Accountability Data) {1520}
        String imad = generateIMAD();
        message.addTag("1520", imad);

        // Amount {2000}
        message.addTag("2000", formatFedwireAmount(request.getAmount()));

        // Sender DFI {3100}
        message.addTag("3100", request.getSenderABA());

        // Receiver DFI {3400}
        message.addTag("3400", request.getReceiverABA());

        // Originator {5000}
        message.addTag("5000", formatOriginatorInfo(request.getOriginator()));

        // Beneficiary {4200}
        message.addTag("4200", formatBeneficiaryInfo(request.getBeneficiary()));

        // Originator to Beneficiary Information {6000}
        if (request.hasPaymentInfo()) {
            message.addTag("6000", request.getPaymentInfo());
        }

        // Send via Fedwire network
        FedwireResponse response = connection.send(message);

        return response;
    }

    private String generateIMAD() {
        // IMAD format: YYYYMMDDSSSSSSSSNNNNNNNN
        // YYYYMMDD = Date
        // SSSSSSSS = Source (ABA routing number)
        // NNNNNNNN = Sequence number

        String date = LocalDate.now().format(DateTimeFormatter.ofPattern("yyyyMMdd"));
        String source = configuration.getRoutingNumber();
        String sequence = String.format("%08d", getNextSequence());

        return date + source + sequence;
    }

    private String formatFedwireAmount(BigDecimal amount) {
        // Format: 12 digits, cents, zero-filled
        long cents = amount.multiply(new BigDecimal(100)).longValue();
        return String.format("%012d", cents);
    }
}
```

### CHIPS Integration (Clearing House Interbank Payments System)

```java
public class CHIPSService {

    /**
     * CHIPS processes large-value USD payments
     */
    public CHIPSResponse sendCHIPSPayment(CHIPSPayment payment) {
        CHIPSMessage message = new CHIPSMessage();

        // Message Type: Payment Order
        message.setMessageType("100");

        // Sender's Reference
        message.setSenderReference(payment.getReference());

        // Value Date
        message.setValueDate(payment.getValueDate());

        // Currency and Amount
        message.setCurrency("USD");
        message.setAmount(payment.getAmount());

        // Sender UID (Universal Identifier)
        message.setSenderUID(payment.getSenderUID());

        // Receiver UID
        message.setReceiverUID(payment.getReceiverUID());

        // Beneficiary Information
        message.setBeneficiaryAccount(payment.getBeneficiaryAccount());
        message.setBeneficiaryName(payment.getBeneficiaryName());

        // Send to CHIPS
        CHIPSResponse response = chipsGateway.send(message);

        // CHIPS provides real-time settlement
        if (response.isAccepted()) {
            // Payment is final and irrevocable
            updateAccountBalances(payment);
        }

        return response;
    }
}
```

---

## Real-Time Payment Networks

### RTP (Real-Time Payments) - The Clearing House

```java
public class RTPIntegration {

    private RTPConnection rtpConnection;

    /**
     * RTP uses ISO 20022 messages
     */
    public RTPResponse sendRTPPayment(RTPPaymentRequest request) {
        // Create ISO 20022 pain.001 (CustomerCreditTransferInitiationV09)
        Document doc = new Document();

        CstmrCdtTrfInitn initiation = new CstmrCdtTrfInitn();

        // Group Header
        GrpHdr grpHdr = new GrpHdr();
        grpHdr.setMsgId(UUID.randomUUID().toString());
        grpHdr.setCreDtTm(Instant.now());
        grpHdr.setNbOfTxs("1");
        grpHdr.setCtrlSum(request.getAmount());

        // Initiating Party
        PartyIdentification party = new PartyIdentification();
        party.setNm(request.getInitiatingPartyName());
        grpHdr.setInitgPty(party);

        initiation.setGrpHdr(grpHdr);

        // Payment Information
        PmtInf pmtInf = new PmtInf();
        pmtInf.setPmtInfId(request.getPaymentId());
        pmtInf.setPmtMtd("TRF");  // Transfer

        // Requested Execution Date (for RTP, typically immediate)
        pmtInf.setReqdExctnDt(LocalDate.now());

        // Debtor
        PartyIdentification debtor = new PartyIdentification();
        debtor.setNm(request.getDebtorName());
        pmtInf.setDbtr(debtor);

        // Debtor Account
        CashAccount debtorAcct = new CashAccount();
        debtorAcct.setId(request.getDebtorAccount());
        pmtInf.setDbtrAcct(debtorAcct);

        // Debtor Agent (Bank)
        FinancialInstitutionIdentification debtorAgent =
            new FinancialInstitutionIdentification();
        debtorAgent.setBICFI(request.getDebtorBankBIC());
        pmtInf.setDbtrAgt(debtorAgent);

        // Credit Transfer Transaction Information
        CdtTrfTxInf txInfo = new CdtTrfTxInf();

        // Payment ID
        PmtId pmtId = new PmtId();
        pmtId.setEndToEndId(request.getEndToEndId());
        txInfo.setPmtId(pmtId);

        // Amount
        AmountType amt = new AmountType();
        amt.setInstdAmt(request.getAmount());
        amt.setCcy(request.getCurrency());
        txInfo.setAmt(amt);

        // Creditor Agent
        FinancialInstitutionIdentification creditorAgent =
            new FinancialInstitutionIdentification();
        creditorAgent.setBICFI(request.getCreditorBankBIC());
        txInfo.setCdtrAgt(creditorAgent);

        // Creditor
        PartyIdentification creditor = new PartyIdentification();
        creditor.setNm(request.getCreditorName());
        txInfo.setCdtr(creditor);

        // Creditor Account
        CashAccount creditorAcct = new CashAccount();
        creditorAcct.setId(request.getCreditorAccount());
        txInfo.setCdtrAcct(creditorAcct);

        // Remittance Information
        if (request.hasRemittanceInfo()) {
            RemittanceInformation remittance = new RemittanceInformation();
            remittance.setUstrd(request.getRemittanceInfo());
            txInfo.setRmtInf(remittance);
        }

        pmtInf.addCdtTrfTxInf(txInfo);
        initiation.addPmtInf(pmtInf);

        doc.setCstmrCdtTrfInitn(initiation);

        // Send to RTP network
        RTPResponse response = rtpConnection.send(doc);

        // RTP provides response within seconds
        return response;
    }

    /**
     * Handle incoming RTP payment request (pain.013)
     */
    @RTPMessageHandler("pain.013")
    public void handleIncomingPaymentRequest(
            CdtrPmtActvtnReq paymentRequest) {

        // Validate beneficiary account
        String accountNumber = paymentRequest.getCdtrAcct().getId();
        Account account = accountService.getAccount(accountNumber);

        if (account == null || !account.isActive()) {
            // Reject payment
            sendRTPRejection(paymentRequest, "AC03",
                "Invalid creditor account number");
            return;
        }

        // Check for fraud/sanctions
        if (fraudService.isSuspicious(paymentRequest)) {
            sendRTPRejection(paymentRequest, "FF01",
                "Operation code/transaction code incorrect");
            return;
        }

        // Accept and credit account
        creditAccount(account, paymentRequest.getAmt());

        // Send positive acknowledgment (pain.014)
        sendRTPAcceptance(paymentRequest);

        // Notify customer in real-time
        notificationService.notifyIncomingPayment(
            account.getCustomerId(),
            paymentRequest
        );
    }
}
```

### FedNow Integration

```java
public class FedNowService {

    /**
     * FedNow also uses ISO 20022 messaging
     * Similar to RTP but operated by Federal Reserve
     */
    public FedNowResponse sendPayment(FedNowPaymentRequest request) {
        // Build pacs.008 (FIToFICustomerCreditTransfer)
        Document doc = new Document();

        FIToFICstmrCdtTrf transfer = new FIToFICstmrCdtTrf();

        // Group Header
        GrpHdr grpHdr = new GrpHdr();
        grpHdr.setMsgId(generateMessageId());
        grpHdr.setCreDtTm(Instant.now());
        grpHdr.setNbOfTxs("1");
        grpHdr.setSttlmInf(buildSettlementInfo());

        transfer.setGrpHdr(grpHdr);

        // Credit Transfer Transaction
        CdtTrfTxInf txInfo = new CdtTrfTxInf();

        // Payment Identification
        PmtId pmtId = new PmtId();
        pmtId.setInstrId(request.getInstructionId());
        pmtId.setEndToEndId(request.getEndToEndId());
        pmtId.setTxId(request.getTransactionId());
        txInfo.setPmtId(pmtId);

        // Interbank Settlement Amount
        ActiveCurrencyAndAmount amt = new ActiveCurrencyAndAmount();
        amt.setCcy("USD");  // FedNow is USD only
        amt.setValue(request.getAmount());
        txInfo.setIntrBkSttlmAmt(amt);

        // Instructed Amount (customer-level)
        ActiveOrHistoricCurrencyAndAmount instdAmt =
            new ActiveOrHistoricCurrencyAndAmount();
        instdAmt.setCcy("USD");
        instdAmt.setValue(request.getAmount());
        txInfo.setInstdAmt(instdAmt);

        // Debtor Agent (sending bank)
        BranchAndFinancialInstitutionIdentification dbtrAgt =
            new BranchAndFinancialInstitutionIdentification();
        FinancialInstitutionIdentification finInstnId =
            new FinancialInstitutionIdentification();
        finInstnId.setOthr(buildRoutingNumber(request.getDebtorBankRouting()));
        dbtrAgt.setFinInstnId(finInstnId);
        txInfo.setDbtrAgt(dbtrAgt);

        // Creditor Agent (receiving bank)
        BranchAndFinancialInstitutionIdentification cdtrAgt =
            new BranchAndFinancialInstitutionIdentification();
        FinancialInstitutionIdentification cdtrFinInstnId =
            new FinancialInstitutionIdentification();
        cdtrFinInstnId.setOthr(buildRoutingNumber(request.getCreditorBankRouting()));
        cdtrAgt.setFinInstnId(cdtrFinInstnId);
        txInfo.setCdtrAgt(cdtrAgt);

        // Debtor (sender)
        PartyIdentification dbtr = new PartyIdentification();
        dbtr.setNm(request.getDebtorName());
        txInfo.setDbtr(dbtr);

        // Debtor Account
        CashAccount dbtrAcct = new CashAccount();
        AccountIdentification acctId = new AccountIdentification();
        acctId.setOthr(request.getDebtorAccount());
        dbtrAcct.setId(acctId);
        txInfo.setDbtrAcct(dbtrAcct);

        // Creditor (receiver)
        PartyIdentification cdtr = new PartyIdentification();
        cdtr.setNm(request.getCreditorName());
        txInfo.setCdtr(cdtr);

        // Creditor Account
        CashAccount cdtrAcct = new CashAccount();
        AccountIdentification cdtrAcctId = new AccountIdentification();
        cdtrAcctId.setOthr(request.getCreditorAccount());
        cdtrAcct.setId(cdtrAcctId);
        txInfo.setCdtrAcct(cdtrAcct);

        // Purpose (optional)
        if (request.hasPurpose()) {
            Purpose purpose = new Purpose();
            purpose.setPrtry(request.getPurposeCode());
            txInfo.setPurp(purpose);
        }

        // Remittance Information
        if (request.hasRemittanceInfo()) {
            RemittanceInformation rmtInf = new RemittanceInformation();
            rmtInf.setUstrd(Collections.singletonList(
                request.getRemittanceInfo()
            ));
            txInfo.setRmtInf(rmtInf);
        }

        transfer.addCdtTrfTxInf(txInfo);
        doc.setFIToFICstmrCdtTrf(transfer);

        // Send to FedNow Service
        FedNowResponse response = fedNowConnection.send(doc);

        return response;
    }
}
```

---

## ISO 8583 Message Handling

### Advanced ISO 8583 Features

```java
public class AdvancedISO8583Handler {

    /**
     * Handle EMV chip transaction data (Field 55)
     */
    public void processEMVData(byte[] field55) {
        TLVParser parser = new TLVParser();
        List<TLVEntry> tlvEntries = parser.parse(field55);

        for (TLVEntry entry : tlvEntries) {
            String tag = entry.getTag();
            byte[] value = entry.getValue();

            switch (tag) {
                case "9F26":  // Application Cryptogram
                    String cryptogram = ISOUtil.hexString(value);
                    validateCryptogram(cryptogram);
                    break;

                case "9F27":  // Cryptogram Information Data
                    String cid = ISOUtil.hexString(value);
                    // 00 = AAC (declined), 40 = TC (approved), 80 = ARQC (online auth)
                    break;

                case "9F33":  // Terminal Capabilities
                    // Indicates terminal's capabilities
                    break;

                case "9F34":  // CVM Results
                    // Cardholder Verification Method results
                    // Indicates if PIN, signature, or no CVM was used
                    break;

                case "9F36":  // Application Transaction Counter (ATC)
                    // Counter maintained by the card
                    break;

                case "95":    // Terminal Verification Results (TVR)
                    // Results of terminal risk management
                    break;

                case "9A":    // Transaction Date
                    String txnDate = new String(value);
                    break;

                case "9C":    // Transaction Type
                    // 00 = Purchase, 09 = Cash withdrawal, 20 = Refund
                    break;

                case "5F2A":  // Transaction Currency Code
                    String currencyCode = ISOUtil.hexString(value);
                    break;
            }
        }
    }

    /**
     * Build Field 55 EMV data for authorization request
     */
    public byte[] buildEMVField55(EMVTransactionData emvData) {
        TLVBuilder builder = new TLVBuilder();

        // Application Interchange Profile (82)
        builder.addTag("82", emvData.getAIP());

        // Application Transaction Counter (9F36)
        builder.addTag("9F36", emvData.getATC());

        // Application Cryptogram (9F26)
        builder.addTag("9F26", emvData.getCryptogram());

        // Cryptogram Information Data (9F27)
        builder.addTag("9F27", emvData.getCryptogramInfo());

        // Issuer Application Data (9F10)
        builder.addTag("9F10", emvData.getIssuerApplicationData());

        // Unpredictable Number (9F37)
        builder.addTag("9F37", emvData.getUnpredictableNumber());

        // Terminal Verification Results (95)
        builder.addTag("95", emvData.getTVR());

        // Transaction Date (9A)
        builder.addTag("9A", emvData.getTransactionDate());

        // Transaction Type (9C)
        builder.addTag("9C", emvData.getTransactionType());

        // Transaction Amount (9F02)
        builder.addTag("9F02", emvData.getAmount());

        // Transaction Currency Code (5F2A)
        builder.addTag("5F2A", emvData.getCurrencyCode());

        return builder.build();
    }

    /**
     * Network message encryption and MAC calculation
     */
    public ISOMsg secureMessage(ISOMsg message, byte[] sessionKey) {
        try {
            // Calculate MAC (Message Authentication Code) for field 64
            byte[] macData = buildMACData(message);
            byte[] mac = calculateMAC(macData, sessionKey);
            message.set(64, mac);

            // Encrypt sensitive fields (PIN, track data)
            if (message.hasField(52)) {
                byte[] pinBlock = message.getBytes(52);
                byte[] encryptedPIN = encryptPINBlock(pinBlock, sessionKey);
                message.set(52, encryptedPIN);
            }

            return message;

        } catch (Exception e) {
            throw new SecurityException("Message security failed", e);
        }
    }

    private byte[] calculateMAC(byte[] data, byte[] key) throws Exception {
        // ISO 9797-1 MAC Algorithm 3 (Retail MAC)
        Cipher cipher = Cipher.getInstance("DESede/CBC/NoPadding");
        SecretKeySpec keySpec = new SecretKeySpec(key, "DESede");
        IvParameterSpec ivSpec = new IvParameterSpec(new byte[8]);  // Zero IV

        cipher.init(Cipher.ENCRYPT_MODE, keySpec, ivSpec);

        byte[] encrypted = cipher.doFinal(padData(data));

        // Return last 8 bytes as MAC
        byte[] mac = new byte[8];
        System.arraycopy(encrypted, encrypted.length - 8, mac, 0, 8);

        return mac;
    }
}
```

---

## ISO 20022 Migration Strategies

### Dual Message Format Support

```java
@Service
public class PaymentMessageRouter {

    @Autowired
    private SWIFTMT103Handler mtHandler;

    @Autowired
    private ISO20022Pacs008Handler mxHandler;

    /**
     * Support both MT and MX (ISO 20022) message formats during migration
     */
    public PaymentResponse routePayment(String message) {
        MessageFormat format = detectMessageFormat(message);

        switch (format) {
            case SWIFT_MT:
                return processMTMessage(message);

            case ISO_20022:
                return processMXMessage(message);

            default:
                throw new UnsupportedMessageFormatException(
                    "Unknown message format"
                );
        }
    }

    private MessageFormat detectMessageFormat(String message) {
        if (message.startsWith("{1:")) {
            return MessageFormat.SWIFT_MT;
        } else if (message.startsWith("<?xml") ||
                   message.contains("<Document xmlns=")) {
            return MessageFormat.ISO_20022;
        } else {
            return MessageFormat.UNKNOWN;
        }
    }

    /**
     * Translation service for MT to MX conversion
     */
    @Service
    public class MTtoMXTranslator {

        public Document translateMT103ToPacs008(MT103 mt103) {
            Document doc = new Document();
            FIToFICstmrCdtTrf pacs008 = new FIToFICstmrCdtTrf();

            // Map MT103 fields to pacs.008 elements
            // Field 20 -> PmtId.InstrId
            // Field 32A -> IntrBkSttlmAmt, IntrBkSttlmDt
            // Field 50K -> Dbtr
            // Field 59 -> Cdtr
            // Field 70 -> RmtInf
            // etc.

            // Group Header
            GrpHdr grpHdr = new GrpHdr();
            grpHdr.setMsgId(mt103.getField20());  // Sender's reference
            grpHdr.setCreDtTm(Instant.now());
            grpHdr.setNbOfTxs("1");

            // Settlement Information
            SettlementInstruction sttlmInf = new SettlementInstruction();
            sttlmInf.setSttlmMtd("CLRG");  // Clearing
            grpHdr.setSttlmInf(sttlmInf);

            pacs008.setGrpHdr(grpHdr);

            // Credit Transfer Transaction Information
            CdtTrfTxInf txInfo = new CdtTrfTxInf();

            // Payment Identification
            PmtId pmtId = new PmtId();
            pmtId.setInstrId(mt103.getField20());
            pmtId.setEndToEndId(mt103.getField20());
            txInfo.setPmtId(pmtId);

            // Parse Field 32A (Value Date/Currency/Amount)
            String field32A = mt103.getField32A();
            LocalDate valueDate = parseDate(field32A.substring(0, 6));
            String currency = field32A.substring(6, 9);
            BigDecimal amount = parseAmount(field32A.substring(9));

            // Interbank Settlement Amount
            ActiveCurrencyAndAmount sttlmAmt = new ActiveCurrencyAndAmount();
            sttlmAmt.setCcy(currency);
            sttlmAmt.setValue(amount);
            txInfo.setIntrBkSttlmAmt(sttlmAmt);

            // Interbank Settlement Date
            txInfo.setIntrBkSttlmDt(valueDate);

            // Map Field 50K (Ordering Customer) to Debtor
            PartyIdentification dbtr = mapField50KToParty(mt103.getField50K());
            txInfo.setDbtr(dbtr);

            // Map Field 59 (Beneficiary) to Creditor
            PartyIdentification cdtr = mapField59ToParty(mt103.getField59());
            txInfo.setCdtr(cdtr);

            // Map Field 70 (Remittance Info)
            if (mt103.hasField70()) {
                RemittanceInformation rmtInf = new RemittanceInformation();
                rmtInf.setUstrd(Collections.singletonList(mt103.getField70()));
                txInfo.setRmtInf(rmtInf);
            }

            pacs008.addCdtTrfTxInf(txInfo);
            doc.setFIToFICstmrCdtTrf(pacs008);

            return doc;
        }
    }
}
```

### Migration Best Practices

```java
/**
 * Phased migration approach for ISO 20022
 */
@Configuration
public class ISO20022MigrationStrategy {

    /**
     * Phase 1: Dual message support (both MT and MX)
     * Phase 2: Preference for MX, fallback to MT
     * Phase 3: MX only (after SWIFT mandate)
     */

    @Bean
    public MessageFormatStrategy migrationStrategy() {
        LocalDate now = LocalDate.now();
        LocalDate swiftDeadline = LocalDate.of(2025, 11, 1);

        if (now.isBefore(swiftDeadline.minusMonths(6))) {
            // Phase 1: Support both formats
            return new DualFormatStrategy();
        } else if (now.isBefore(swiftDeadline)) {
            // Phase 2: Prefer MX, support MT
            return new MXPreferredStrategy();
        } else {
            // Phase 3: MX only
            return new MXOnlyStrategy();
        }
    }

    /**
     * Feature flag for gradual rollout
     */
    @Bean
    public ISO20022FeatureFlags featureFlags() {
        return ISO20022FeatureFlags.builder()
            .enableMXReceive(true)
            .enableMXSend(percentageRollout(50))  // 50% of outbound messages
            .enableMTtoMXTranslation(true)
            .enableDataEnrichment(true)  // Use ISO 20022 richer data
            .build();
    }
}
```

---

## Best Practices

### 1. Error Handling and Retries

```java
@Service
public class ResilientPaymentService {

    @Retryable(
        value = {NetworkException.class, TimeoutException.class},
        maxAttempts = 3,
        backoff = @Backoff(delay = 1000, multiplier = 2)
    )
    public PaymentResponse sendPayment(PaymentRequest request) {
        // Send payment with automatic retry
        return paymentGateway.send(request);
    }

    @Recover
    public PaymentResponse recover(NetworkException e, PaymentRequest request) {
        // After retries exhausted, log and queue for manual review
        logger.error("Payment failed after retries: {}", request.getId(), e);

        // Store in dead letter queue
        deadLetterQueue.add(request);

        // Return failure response
        return PaymentResponse.builder()
            .status(PaymentStatus.FAILED)
            .errorCode("NETWORK_ERROR")
            .errorMessage("Payment failed due to network error")
            .build();
    }
}
```

### 2. Idempotency

```java
@Service
public class IdempotentPaymentService {

    @Autowired
    private PaymentRepository paymentRepo;

    @Transactional
    public PaymentResponse processPayment(PaymentRequest request) {
        String idempotencyKey = request.getIdempotencyKey();

        // Check if already processed
        Optional<Payment> existing = paymentRepo.findByIdempotencyKey(idempotencyKey);

        if (existing.isPresent()) {
            // Return cached response
            logger.info("Returning cached response for idempotency key: {}",
                idempotencyKey);
            return existing.get().getResponse();
        }

        // Process new payment
        PaymentResponse response = executePayment(request);

        // Store with idempotency key
        Payment payment = new Payment();
        payment.setIdempotencyKey(idempotencyKey);
        payment.setRequest(request);
        payment.setResponse(response);
        payment.setProcessedAt(Instant.now());

        paymentRepo.save(payment);

        return response;
    }
}
```

### 3. Monitoring and Alerting

```java
@Aspect
@Component
public class PaymentMonitoring {

    @Autowired
    private MetricRegistry metrics;

    @Around("@annotation(MonitorPayment)")
    public Object monitorPayment(ProceedingJoinPoint joinPoint) throws Throwable {
        String paymentType = extractPaymentType(joinPoint);

        Timer.Context timer = metrics.timer("payment.duration." + paymentType).time();

        try {
            Object result = joinPoint.proceed();

            metrics.counter("payment.success." + paymentType).inc();

            return result;

        } catch (Exception e) {
            metrics.counter("payment.failure." + paymentType).inc();
            metrics.counter("payment.failure." + paymentType + "." +
                e.getClass().getSimpleName()).inc();

            throw e;

        } finally {
            timer.stop();
        }
    }

    @Scheduled(fixedRate = 60000)  // Every minute
    public void checkPaymentHealth() {
        long failureCount = metrics.counter("payment.failure.total").getCount();
        long successCount = metrics.counter("payment.success.total").getCount();

        double failureRate = (double) failureCount / (failureCount + successCount);

        if (failureRate > 0.05) {  // 5% failure threshold
            alerting.sendAlert(
                "HIGH_PAYMENT_FAILURE_RATE",
                String.format("Payment failure rate: %.2f%%", failureRate * 100)
            );
        }
    }
}
```

### 4. Compliance and Audit

```java
@Service
public class PaymentAuditService {

    @Autowired
    private AuditRepository auditRepo;

    @EventListener
    public void auditPayment(PaymentEvent event) {
        AuditRecord audit = AuditRecord.builder()
            .eventId(UUID.randomUUID().toString())
            .timestamp(Instant.now())
            .eventType(event.getType())
            .userId(event.getUserId())
            .paymentId(event.getPaymentId())
            .amount(event.getAmount())
            .currency(event.getCurrency())
            .debtorAccount(maskAccount(event.getDebtorAccount()))
            .creditorAccount(maskAccount(event.getCreditorAccount()))
            .ipAddress(event.getIpAddress())
            .userAgent(event.getUserAgent())
            .status(event.getStatus())
            .build();

        auditRepo.save(audit);

        // Also send to compliance monitoring system
        if (requiresComplianceReview(event)) {
            complianceSystem.submitForReview(audit);
        }
    }

    private boolean requiresComplianceReview(PaymentEvent event) {
        // Large payments, international transfers, high-risk countries
        return event.getAmount().compareTo(new BigDecimal("10000")) > 0 ||
               isInternational(event) ||
               isHighRiskCountry(event.getDestinationCountry());
    }
}
```

---

## Conclusion

Payment network integration requires careful attention to message formats, security, compliance, and reliability. The transition to ISO 20022 provides an opportunity to modernize payment systems while maintaining backward compatibility with legacy MT formats.

### Key Takeaways

1. **Understand Message Standards**: Master ISO 8583, SWIFT MT, and ISO 20022 formats
2. **Ensure Idempotency**: Prevent duplicate payments through proper key management
3. **Plan for Migration**: Support dual formats during ISO 20022 transition
4. **Monitor Continuously**: Track success rates, latencies, and failures
5. **Maintain Compliance**: Implement comprehensive audit trails

### Industry Resources

- ISO 8583 Standard Documentation
- SWIFT Standards (MT and MX messages)
- NACHA Operating Rules and Guidelines
- ISO 20022 Registration Authority
- The Clearing House RTP Developer Guide
- Federal Reserve FedNow Service Documentation
- PCI Security Standards Council
