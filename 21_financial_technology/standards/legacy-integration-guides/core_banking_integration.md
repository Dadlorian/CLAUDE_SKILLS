# Core Banking Integration Guide

## Table of Contents
1. [Introduction](#introduction)
2. [Legacy Core Banking Architecture](#legacy-core-banking-architecture)
3. [Mainframe Integration](#mainframe-integration)
4. [ESB and Message-Based Integration](#esb-and-message-based-integration)
5. [Database Replication and CDC](#database-replication-and-cdc)
6. [Strangler Fig Pattern](#strangler-fig-pattern)
7. [API Facade Patterns](#api-facade-patterns)
8. [Data Synchronization Strategies](#data-synchronization-strategies)
9. [Real-World Examples](#real-world-examples)
10. [Migration Strategies](#migration-strategies)
11. [Best Practices and Considerations](#best-practices-and-considerations)

---

## Introduction

Core banking systems are the backbone of financial institutions, managing accounts, transactions, and customer data. Many banks still operate on legacy mainframe systems built in the 1970s-1990s, primarily using COBOL, DB2, and proprietary technologies. This guide provides comprehensive patterns and strategies for integrating modern applications with legacy core banking systems.

### Key Challenges
- **Technology Gap**: 40-50 year old systems vs. modern cloud-native applications
- **Data Complexity**: Hierarchical data models, EBCDIC encoding, fixed-width records
- **Availability Requirements**: 24/7 operation with 99.99%+ uptime SLAs
- **Regulatory Constraints**: Cannot modify systems of record without extensive testing
- **Skills Gap**: Declining COBOL/mainframe expertise
- **Performance**: Batch processing windows, MIPS constraints

### Industry Standards Referenced
- **ISO 8583**: Financial transaction card originated messages
- **ISO 20022**: Universal financial industry message scheme
- **SWIFT MT**: Message types for banking operations
- **ANSI X9**: Financial services standards
- **NACHA**: ACH network rules and guidelines

---

## Legacy Core Banking Architecture

### Typical Components

#### 1. Mainframe Core (System of Record)
```
┌─────────────────────────────────────────────────┐
│          IBM z/OS Mainframe                     │
│                                                 │
│  ┌──────────────┐  ┌─────────────────────┐    │
│  │ COBOL        │  │ DB2 Databases       │    │
│  │ Applications │──│ - Account Master    │    │
│  │ - Deposits   │  │ - Transaction Log   │    │
│  │ - Loans      │  │ - Customer Master   │    │
│  │ - General    │  │ - Chart of Accounts │    │
│  │   Ledger     │  └─────────────────────┘    │
│  └──────────────┘                              │
│                                                 │
│  ┌──────────────┐  ┌─────────────────────┐    │
│  │ CICS/IMS     │  │ JCL Batch Jobs      │    │
│  │ Transaction  │  │ - EOD Processing    │    │
│  │ Servers      │  │ - Interest Calc     │    │
│  └──────────────┘  │ - Statements        │    │
│                    └─────────────────────┘    │
└─────────────────────────────────────────────────┘
```

#### 2. Data Characteristics
- **EBCDIC Encoding**: Extended Binary Coded Decimal Interchange Code
- **Fixed-Width Records**: COBOL copybook definitions
- **Packed Decimal**: COMP-3 fields for numeric data
- **Hierarchical Data**: IMS DB or VSAM file structures
- **Batch Windows**: Typically 10 PM - 6 AM for heavy processing

#### 3. Common Legacy Systems
- **Temenos T24/Transact**: Market leader
- **FIS Profile**: Comprehensive core banking
- **Jack Henry Silverlake**: Mid-tier banks
- **Oracle FLEXCUBE**: Global banking solution
- **SAP Banking Services**: Enterprise banking
- **Fiserv Premier**: Regional and community banks
- **Custom COBOL Systems**: Large banks with proprietary solutions

---

## Mainframe Integration

### Integration Approaches

#### 1. Direct CICS/IMS Calls

**Pattern**: Call mainframe transactions directly from distributed systems

```yaml
# IBM CICS Transaction Gateway Configuration
connection:
  host: mainframe.bank.com
  port: 2006
  connection_type: TCP/IP

transaction:
  name: ACCT0001  # Account Inquiry
  mirror_transaction: true
  sync_level: confirm

security:
  userid: APIUSER
  password: encrypted
  security_type: RACF
```

**Example: Account Balance Inquiry**

```java
// Java CICS TG Integration
import com.ibm.ctg.client.*;

public class MainframeAccountService {

    private ECIRequest createBalanceInquiry(String accountNumber) {
        ECIRequest eciRequest = new ECIRequest(
            ECIRequest.ECI_SYNC,           // Synchronous call
            "CICSA",                        // CICS region
            "ACCT0001",                     // Transaction ID
            null,                           // COMMAREA length calculated
            buildCommarea(accountNumber),   // Input data
            0,                              // No extended data
            ECIRequest.ECI_NO_EXTEND
        );
        return eciRequest;
    }

    private byte[] buildCommarea(String accountNumber) {
        // Build COBOL COMMAREA structure
        ByteBuffer buffer = ByteBuffer.allocate(512);

        // Transaction code (4 bytes)
        buffer.put("INQB".getBytes(StandardCharsets.UTF_8));

        // Account number (20 bytes, left-padded)
        String paddedAccount = String.format("%-20s", accountNumber);
        buffer.put(paddedAccount.getBytes(StandardCharsets.UTF_8));

        // Return code placeholder (4 bytes)
        buffer.put("0000".getBytes(StandardCharsets.UTF_8));

        return buffer.array();
    }

    public AccountBalance getBalance(String accountNumber)
            throws MainframeException {
        try {
            JavaGateway gateway = new JavaGateway();
            gateway.open("tcp://mainframe.bank.com:2006");

            ECIRequest request = createBalanceInquiry(accountNumber);
            gateway.flow(request);

            byte[] response = request.getCommarea();
            return parseBalanceResponse(response);

        } catch (Exception e) {
            throw new MainframeException("Balance inquiry failed", e);
        }
    }

    private AccountBalance parseBalanceResponse(byte[] commarea) {
        // Parse COBOL response structure
        ByteBuffer buffer = ByteBuffer.wrap(commarea);

        // Skip transaction code (4 bytes)
        buffer.position(4);

        // Account number (20 bytes)
        byte[] acctBytes = new byte[20];
        buffer.get(acctBytes);
        String account = new String(acctBytes).trim();

        // Return code (4 bytes)
        byte[] returnCode = new byte[4];
        buffer.get(returnCode);

        if (!new String(returnCode).equals("0000")) {
            throw new MainframeException("Transaction failed: " +
                new String(returnCode));
        }

        // Available balance (COMP-3, 8 bytes = 15 digits)
        byte[] balanceBytes = new byte[8];
        buffer.get(balanceBytes);
        BigDecimal balance = parseComp3(balanceBytes);

        return new AccountBalance(account, balance);
    }

    private BigDecimal parseComp3(byte[] packed) {
        // Parse COBOL COMP-3 (Packed Decimal) format
        long value = 0;
        boolean isNegative = false;

        for (int i = 0; i < packed.length; i++) {
            int highNibble = (packed[i] >> 4) & 0x0F;
            int lowNibble = packed[i] & 0x0F;

            if (i == packed.length - 1) {
                // Last byte: low nibble is sign
                value = value * 10 + highNibble;
                isNegative = (lowNibble == 0x0D);
            } else {
                value = value * 10 + highNibble;
                value = value * 10 + lowNibble;
            }
        }

        BigDecimal result = new BigDecimal(value).divide(
            new BigDecimal(100), 2, RoundingMode.HALF_UP
        );
        return isNegative ? result.negate() : result;
    }
}
```

#### 2. MQ Series Integration

**Pattern**: Use IBM MQ for asynchronous communication

```yaml
# IBM MQ Configuration
queue_manager:
  name: BANK_QM
  host: mqserver.bank.com
  port: 1414
  channel: SYSTEM.DEF.SVRCONN

queues:
  request_queue: ACCT.REQUEST.QUEUE
  response_queue: ACCT.RESPONSE.QUEUE
  error_queue: ACCT.ERROR.QUEUE

message_format:
  type: MQSTR  # String format
  persistence: PERSISTENT
  expiry: 300  # 5 minutes
  priority: 5
```

**Example: Asynchronous Transaction Processing**

```java
import com.ibm.mq.*;
import com.ibm.mq.constants.MQConstants;

public class MQCoreIntegration {

    private MQQueueManager queueManager;

    public void initializeConnection() throws MQException {
        MQEnvironment.hostname = "mqserver.bank.com";
        MQEnvironment.port = 1414;
        MQEnvironment.channel = "SYSTEM.DEF.SVRCONN";
        MQEnvironment.userID = "mquser";

        queueManager = new MQQueueManager("BANK_QM");
    }

    public String submitTransaction(TransactionRequest txn)
            throws MQException {

        // Open request queue
        int openOptions = MQConstants.MQOO_OUTPUT |
                         MQConstants.MQOO_FAIL_IF_QUIESCING;
        MQQueue requestQueue = queueManager.accessQueue(
            "ACCT.REQUEST.QUEUE",
            openOptions
        );

        try {
            // Build message
            MQMessage message = new MQMessage();
            message.format = MQConstants.MQFMT_STRING;
            message.persistence = MQConstants.MQPER_PERSISTENT;
            message.replyToQueueName = "ACCT.RESPONSE.QUEUE";

            // Generate correlation ID for tracking
            String correlationId = UUID.randomUUID().toString();
            message.correlationId = correlationId.getBytes();

            // Write transaction data
            String messageBody = buildTransactionMessage(txn);
            message.writeString(messageBody);

            // Put message on queue
            MQPutMessageOptions pmo = new MQPutMessageOptions();
            requestQueue.put(message, pmo);

            return correlationId;

        } finally {
            requestQueue.close();
        }
    }

    public TransactionResponse getResponse(String correlationId,
            int timeoutSeconds) throws MQException {

        int openOptions = MQConstants.MQOO_INPUT_AS_Q_DEF |
                         MQConstants.MQOO_FAIL_IF_QUIESCING;
        MQQueue responseQueue = queueManager.accessQueue(
            "ACCT.RESPONSE.QUEUE",
            openOptions
        );

        try {
            MQGetMessageOptions gmo = new MQGetMessageOptions();
            gmo.options = MQConstants.MQGMO_WAIT;
            gmo.waitInterval = timeoutSeconds * 1000;
            gmo.matchOptions = MQConstants.MQMO_MATCH_CORREL_ID;

            MQMessage message = new MQMessage();
            message.correlationId = correlationId.getBytes();

            responseQueue.get(message, gmo);

            String responseData = message.readStringOfByteLength(
                message.getDataLength()
            );

            return parseTransactionResponse(responseData);

        } catch (IOException e) {
            throw new MQException("Failed to read response",
                MQConstants.MQCC_FAILED, MQConstants.MQRC_UNEXPECTED_ERROR);
        } finally {
            responseQueue.close();
        }
    }

    private String buildTransactionMessage(TransactionRequest txn) {
        // Build fixed-width message format expected by mainframe
        StringBuilder msg = new StringBuilder();

        // Header (20 bytes)
        msg.append(String.format("%-8s", txn.getTransactionCode()));
        msg.append(String.format("%012d", System.currentTimeMillis()));

        // Account information (40 bytes)
        msg.append(String.format("%-20s", txn.getFromAccount()));
        msg.append(String.format("%-20s", txn.getToAccount()));

        // Amount (15 bytes: 13 digits + 2 decimal)
        long amountCents = txn.getAmount()
            .multiply(new BigDecimal(100))
            .longValue();
        msg.append(String.format("%015d", amountCents));

        // Description (50 bytes)
        msg.append(String.format("%-50s", txn.getDescription()));

        return msg.toString();
    }
}
```

#### 3. Web Services Gateway

**Pattern**: Use IBM DataPower or similar gateway to expose mainframe as web services

```xml
<!-- WSDL for Mainframe Account Service -->
<definitions name="CoreBankingService"
    targetNamespace="http://bank.com/core/v1"
    xmlns:tns="http://bank.com/core/v1"
    xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/"
    xmlns="http://schemas.xmlsoap.org/wsdl/">

    <types>
        <xsd:schema targetNamespace="http://bank.com/core/v1">
            <xsd:element name="AccountInquiryRequest">
                <xsd:complexType>
                    <xsd:sequence>
                        <xsd:element name="accountNumber" type="xsd:string"/>
                        <xsd:element name="inquiryType" type="xsd:string"/>
                    </xsd:sequence>
                </xsd:complexType>
            </xsd:element>

            <xsd:element name="AccountInquiryResponse">
                <xsd:complexType>
                    <xsd:sequence>
                        <xsd:element name="accountNumber" type="xsd:string"/>
                        <xsd:element name="accountName" type="xsd:string"/>
                        <xsd:element name="currentBalance" type="xsd:decimal"/>
                        <xsd:element name="availableBalance" type="xsd:decimal"/>
                        <xsd:element name="accountStatus" type="xsd:string"/>
                        <xsd:element name="currency" type="xsd:string"/>
                    </xsd:sequence>
                </xsd:complexType>
            </xsd:element>
        </xsd:schema>
    </types>

    <message name="AccountInquiryRequestMsg">
        <part name="parameters" element="tns:AccountInquiryRequest"/>
    </message>

    <message name="AccountInquiryResponseMsg">
        <part name="parameters" element="tns:AccountInquiryResponse"/>
    </message>

    <portType name="CoreBankingPortType">
        <operation name="AccountInquiry">
            <input message="tns:AccountInquiryRequestMsg"/>
            <output message="tns:AccountInquiryResponseMsg"/>
        </operation>
    </portType>
</definitions>
```

---

## ESB and Message-Based Integration

### Enterprise Service Bus Architecture

```
┌────────────────────────────────────────────────────────────┐
│                  Enterprise Service Bus                    │
│                                                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │   Routing    │  │ Transformation│ │   Mediation  │   │
│  │   Engine     │  │   Service     │ │   Layer      │   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
│                                                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │  Protocol    │  │   Message    │  │   Service    │   │
│  │  Adapters    │  │   Queue      │  │   Registry   │   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
└────────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Mainframe   │    │  Modern APIs │    │  External    │
│  Core        │    │  (REST/gRPC) │    │  Systems     │
└──────────────┘    └──────────────┘    └──────────────┘
```

### ESB Solutions

#### 1. IBM Integration Bus (IIB) / App Connect

```
# Message Flow Definition
BROKER SCHEMA com.bank.integration

CREATE COMPUTE MODULE AccountTransformModule
    CREATE FUNCTION Main() RETURNS BOOLEAN
    BEGIN
        -- Extract REST API request
        DECLARE accountNum CHARACTER InputRoot.JSON.Data.accountNumber;

        -- Build mainframe COMMAREA
        SET OutputRoot.BLOB.BLOB = CAST(
            OVERLAY(
                CAST(' ' AS BLOB CCSID 500 REPEAT 512),  -- EBCDIC spaces
                CAST('INQB' AS BLOB CCSID 500) FROM 1 FOR 4,
                CAST(accountNum AS BLOB CCSID 500) FROM 5 FOR 20
            )
            AS BLOB
        );

        RETURN TRUE;
    END;
END MODULE;

CREATE COMPUTE MODULE ResponseTransformModule
    CREATE FUNCTION Main() RETURNS BOOLEAN
    BEGIN
        -- Parse mainframe response
        DECLARE commarea BLOB InputRoot.BLOB.BLOB;

        -- Extract fields from EBCDIC COMMAREA
        DECLARE returnCode CHARACTER CAST(
            SUBSTRING(commarea FROM 25 FOR 4) AS CHARACTER CCSID 500
        );

        IF returnCode = '0000' THEN
            -- Build JSON response
            SET OutputRoot.JSON.Data.accountNumber = CAST(
                SUBSTRING(commarea FROM 5 FOR 20) AS CHARACTER CCSID 500
            );

            -- Parse COMP-3 balance field
            DECLARE balanceBytes BLOB SUBSTRING(commarea FROM 29 FOR 8);
            SET OutputRoot.JSON.Data.balance = parseComp3(balanceBytes);

            SET OutputRoot.JSON.Data.status = 'SUCCESS';
        ELSE
            SET OutputRoot.JSON.Data.status = 'ERROR';
            SET OutputRoot.JSON.Data.errorCode = returnCode;
        END IF;

        RETURN TRUE;
    END;
END MODULE;
```

#### 2. MuleSoft Integration

```yaml
# MuleSoft Flow Configuration
flows:
  - name: accountInquiryFlow
    source:
      type: http-listener
      config:
        path: /api/accounts/{accountId}
        method: GET

    processors:
      # Transform REST to mainframe format
      - type: dataweave
        script: |
          %dw 2.0
          output application/java
          ---
          {
            transactionCode: "INQB",
            accountNumber: attributes.uriParams.accountId,
            padding: " " * 488  // Fill to 512 bytes
          }

      # Call mainframe via CICS TG
      - type: cics-connector
        config:
          transaction-id: ACCT0001
          commarea-length: 512

      # Transform mainframe response to JSON
      - type: dataweave
        script: |
          %dw 2.0
          output application/json
          fun parseComp3(bytes) = (
            // Custom function to parse COMP-3
            bytes reduce (byte, acc = 0) ->
              acc * 100 + ((byte >> 4) * 10) + (byte & 0x0F)
          )
          ---
          {
            accountNumber: payload.accountNumber,
            balance: parseComp3(payload.balanceBytes) / 100,
            status: if (payload.returnCode == "0000")
                      "SUCCESS" else "ERROR"
          }
```

#### 3. Apache Camel Routes

```java
public class CoreBankingRoutes extends RouteBuilder {

    @Override
    public void configure() throws Exception {

        // REST API to Mainframe route
        rest("/api/accounts")
            .get("/{accountId}")
            .to("direct:mainframeInquiry");

        from("direct:mainframeInquiry")
            .routeId("accountInquiry")

            // Set correlation ID
            .setHeader("CorrelationId", simple("${exchangeId}"))

            // Transform to mainframe format
            .process(new MainframeRequestProcessor())

            // Send to MQ request queue
            .to("jms:queue:ACCT.REQUEST.QUEUE")

            // Wait for response with correlation
            .to("jms:queue:ACCT.RESPONSE.QUEUE?" +
                "selector=JMSCorrelationID='${header.CorrelationId}'&" +
                "receiveTimeout=30000")

            // Transform mainframe response to JSON
            .process(new MainframeResponseProcessor())

            // Handle errors
            .onException(TimeoutException.class)
                .handled(true)
                .setHeader("HTTP_RESPONSE_CODE", constant(504))
                .setBody(constant("{\"error\": \"Mainframe timeout\"}"));

        // Batch file processing route
        from("file:/data/core/incoming?noop=true")
            .routeId("batchFileProcessing")
            .split(body().tokenize("\n"))
            .streaming()
            .process(new FixedWidthRecordProcessor())
            .to("jms:queue:BATCH.PROCESS.QUEUE")
            .end();
    }
}

class MainframeRequestProcessor implements Processor {
    @Override
    public void process(Exchange exchange) throws Exception {
        String accountId = exchange.getIn()
            .getHeader("accountId", String.class);

        // Build fixed-width COMMAREA
        ByteBuffer buffer = ByteBuffer.allocate(512);

        buffer.put("INQB".getBytes("IBM500"));  // EBCDIC
        buffer.put(String.format("%-20s", accountId)
            .getBytes("IBM500"));

        // Fill remainder with EBCDIC spaces
        while (buffer.hasRemaining()) {
            buffer.put((byte) 0x40);  // EBCDIC space
        }

        exchange.getIn().setBody(buffer.array());
    }
}
```

---

## Database Replication and CDC

### Change Data Capture Patterns

#### 1. Log-Based CDC (Preferred)

**Tools**: IBM InfoSphere CDC, Oracle GoldenGate, Debezium for DB2

```yaml
# IBM InfoSphere CDC Configuration
source:
  type: DB2_ZOS
  host: mainframe.bank.com
  port: 446
  location: DBCG
  subsystem: DB2P

  tables:
    - schema: COREBANK
      table: ACCOUNT_MASTER
      columns:
        - ACCT_NBR
        - ACCT_NAME
        - CURRENT_BAL
        - AVAILABLE_BAL
        - ACCT_STATUS
        - LAST_UPDATE_TS

    - schema: COREBANK
      table: TRANSACTION_LOG
      columns: ALL

  capture_mode: LOG_BASED
  log_reader:
    type: DB2_LOG_READER
    read_delay: 5  # seconds

target:
  type: POSTGRESQL
  host: replica-db.bank.com
  port: 5432
  database: core_replica

  tables:
    - schema: public
      table: accounts
      mapping:
        ACCT_NBR: account_number
        ACCT_NAME: account_name
        CURRENT_BAL: current_balance
        AVAILABLE_BAL: available_balance
        ACCT_STATUS: status
        LAST_UPDATE_TS: updated_at

replication:
  mode: CONTINUOUS
  conflict_resolution: SOURCE_WINS
  initial_load: true
  apply_batch_size: 1000
```

**Example: Custom CDC Implementation**

```java
public class DB2ChangeDataCapture {

    private Connection db2Connection;
    private Connection targetConnection;

    public void startCDC() throws SQLException {
        // Enable DB2 change tracking
        String enableSQL =
            "VALUES ASNCDC.ASNCDCSERVICES(" +
            "  'start'," +
            "  'COREBANK.ACCOUNT_MASTER'" +
            ")";

        try (Statement stmt = db2Connection.createStatement()) {
            stmt.execute(enableSQL);
        }

        // Start continuous polling
        ScheduledExecutorService executor =
            Executors.newSingleThreadScheduledExecutor();

        executor.scheduleAtFixedRate(
            this::captureChanges,
            0,
            5,
            TimeUnit.SECONDS
        );
    }

    private void captureChanges() {
        String querySQL =
            "SELECT " +
            "  ASNCDCT.IBMSNAP_COMMITSEQ, " +
            "  ASNCDCT.IBMSNAP_INTENTSEQ, " +
            "  ASNCDCT.IBMSNAP_OPERATION, " +
            "  ACCT.* " +
            "FROM COREBANK.IBMSNAP_REGISTER REG " +
            "INNER JOIN COREBANK.IBMQREP_COLVERSION VER " +
            "  ON REG.SOURCE_OWNER = VER.SOURCE_OWNER " +
            "  AND REG.SOURCE_TABLE = VER.SOURCE_TABLE " +
            "INNER JOIN COREBANK.IBMSNAP_PRUNCNTL PRUNE " +
            "  ON REG.SOURCE_OWNER = PRUNE.SOURCE_OWNER " +
            "  AND REG.SOURCE_TABLE = PRUNE.SOURCE_TABLE " +
            "INNER JOIN COREBANK.ACCOUNT_MASTER_CT ASNCDCT " +
            "  ON ASNCDCT.IBMSNAP_COMMITSEQ > PRUNE.SYNCHPOINT " +
            "INNER JOIN COREBANK.ACCOUNT_MASTER ACCT " +
            "  ON ACCT.ACCT_NBR = ASNCDCT.ACCT_NBR " +
            "WHERE REG.SOURCE_TABLE = 'ACCOUNT_MASTER' " +
            "ORDER BY ASNCDCT.IBMSNAP_COMMITSEQ, " +
            "         ASNCDCT.IBMSNAP_INTENTSEQ";

        try (PreparedStatement stmt = db2Connection.prepareStatement(querySQL);
             ResultSet rs = stmt.executeQuery()) {

            List<ChangeRecord> changes = new ArrayList<>();

            while (rs.next()) {
                ChangeRecord change = new ChangeRecord();
                change.setCommitSeq(rs.getLong("IBMSNAP_COMMITSEQ"));
                change.setIntentSeq(rs.getLong("IBMSNAP_INTENTSEQ"));
                change.setOperation(rs.getString("IBMSNAP_OPERATION"));

                // Extract account data
                change.setAccountNumber(rs.getString("ACCT_NBR"));
                change.setAccountName(rs.getString("ACCT_NAME"));

                // Handle COMP-3 balance fields
                byte[] balanceBytes = rs.getBytes("CURRENT_BAL");
                change.setCurrentBalance(parseComp3(balanceBytes));

                changes.add(change);
            }

            // Apply changes to target database
            if (!changes.isEmpty()) {
                applyChanges(changes);
                updateSyncPoint(changes.get(changes.size() - 1).getCommitSeq());
            }

        } catch (SQLException e) {
            logger.error("CDC capture failed", e);
        }
    }

    private void applyChanges(List<ChangeRecord> changes) throws SQLException {
        String upsertSQL =
            "INSERT INTO accounts " +
            "  (account_number, account_name, current_balance, " +
            "   available_balance, status, updated_at) " +
            "VALUES (?, ?, ?, ?, ?, ?) " +
            "ON CONFLICT (account_number) " +
            "DO UPDATE SET " +
            "  account_name = EXCLUDED.account_name, " +
            "  current_balance = EXCLUDED.current_balance, " +
            "  available_balance = EXCLUDED.available_balance, " +
            "  status = EXCLUDED.status, " +
            "  updated_at = EXCLUDED.updated_at";

        try (PreparedStatement stmt = targetConnection.prepareStatement(upsertSQL)) {
            for (ChangeRecord change : changes) {
                if ("D".equals(change.getOperation())) {
                    // Handle delete
                    deleteRecord(change.getAccountNumber());
                    continue;
                }

                stmt.setString(1, change.getAccountNumber());
                stmt.setString(2, change.getAccountName());
                stmt.setBigDecimal(3, change.getCurrentBalance());
                stmt.setBigDecimal(4, change.getAvailableBalance());
                stmt.setString(5, change.getStatus());
                stmt.setTimestamp(6, new Timestamp(System.currentTimeMillis()));

                stmt.addBatch();
            }

            stmt.executeBatch();
            targetConnection.commit();
        }
    }
}
```

#### 2. Trigger-Based CDC

```sql
-- DB2 z/OS Change Tracking Trigger
CREATE TRIGGER COREBANK.ACCOUNT_CHANGE_TRIGGER
AFTER INSERT OR UPDATE OR DELETE ON COREBANK.ACCOUNT_MASTER
REFERENCING NEW AS N OLD AS O
FOR EACH ROW MODE DB2SQL
BEGIN ATOMIC
  DECLARE v_operation CHAR(1);
  DECLARE v_acct_nbr CHAR(20);

  -- Determine operation type
  IF INSERTING THEN
    SET v_operation = 'I';
    SET v_acct_nbr = N.ACCT_NBR;
  ELSEIF UPDATING THEN
    SET v_operation = 'U';
    SET v_acct_nbr = N.ACCT_NBR;
  ELSEIF DELETING THEN
    SET v_operation = 'D';
    SET v_acct_nbr = O.ACCT_NBR;
  END IF;

  -- Write to change table
  INSERT INTO COREBANK.ACCOUNT_CHANGES (
    CHANGE_SEQ,
    CHANGE_TS,
    OPERATION,
    ACCT_NBR,
    ACCT_NAME,
    CURRENT_BAL,
    AVAILABLE_BAL,
    ACCT_STATUS
  ) VALUES (
    NEXT VALUE FOR COREBANK.CHANGE_SEQ,
    CURRENT TIMESTAMP,
    v_operation,
    v_acct_nbr,
    CASE WHEN v_operation = 'D' THEN O.ACCT_NAME ELSE N.ACCT_NAME END,
    CASE WHEN v_operation = 'D' THEN O.CURRENT_BAL ELSE N.CURRENT_BAL END,
    CASE WHEN v_operation = 'D' THEN O.AVAILABLE_BAL ELSE N.AVAILABLE_BAL END,
    CASE WHEN v_operation = 'D' THEN O.ACCT_STATUS ELSE N.ACCT_STATUS END
  );
END;
```

---

## Strangler Fig Pattern

### Incremental Migration Strategy

```
Phase 1: Initial State
┌─────────────────────────────────────┐
│         Web/Mobile Apps             │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│      Legacy Core Banking            │
│      (100% of traffic)              │
└─────────────────────────────────────┘

Phase 2: Facade Layer
┌─────────────────────────────────────┐
│         Web/Mobile Apps             │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│        API Facade Layer             │
│      (Routing & Transformation)     │
└──────┬─────────────────────┬────────┘
       │                     │
       ▼                     ▼
┌─────────────┐      ┌──────────────┐
│   Legacy    │      │    Modern    │
│   Core      │      │   Services   │
│  (90%)      │      │    (10%)     │
└─────────────┘      └──────────────┘

Phase 3: Progressive Migration
┌─────────────────────────────────────┐
│         Web/Mobile Apps             │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│        API Facade Layer             │
│      (Routing & Transformation)     │
└──────┬─────────────────────┬────────┘
       │                     │
       ▼                     ▼
┌─────────────┐      ┌──────────────┐
│   Legacy    │◄────►│    Modern    │
│   Core      │ Sync │   Services   │
│  (50%)      │      │    (50%)     │
└─────────────┘      └──────────────┘

Phase 4: Final State
┌─────────────────────────────────────┐
│         Web/Mobile Apps             │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│      Modern Core Services           │
│      (100% of traffic)              │
└─────────────────────────────────────┘
```

### Implementation Example

```java
@Service
public class StranglerFacadeService {

    @Autowired
    private LegacyCoreService legacyCore;

    @Autowired
    private ModernAccountService modernService;

    @Autowired
    private FeatureToggleService featureToggles;

    @Autowired
    private DataSyncService dataSync;

    public AccountResponse getAccount(String accountId) {
        // Check feature toggle for migration status
        boolean usemodern = featureToggles.isEnabled(
            "account-service-migration",
            accountId
        );

        if (useModern) {
            return getFromModernService(accountId);
        } else {
            return getFromLegacyCore(accountId);
        }
    }

    public TransactionResponse createTransaction(TransactionRequest request) {
        // Write to both systems during transition
        boolean dualWrite = featureToggles.isEnabled(
            "dual-write-transactions"
        );

        TransactionResponse response;

        if (dualWrite) {
            // Write to legacy (authoritative during transition)
            response = legacyCore.createTransaction(request);

            // Async write to modern system
            CompletableFuture.runAsync(() -> {
                try {
                    modernService.createTransaction(request);
                } catch (Exception e) {
                    logger.warn("Modern service write failed", e);
                    // Log discrepancy for reconciliation
                    dataSync.logDiscrepancy(request, e);
                }
            });

        } else {
            // Fully migrated - write only to modern
            response = modernService.createTransaction(request);
        }

        return response;
    }

    @Scheduled(cron = "0 */5 * * * *")  // Every 5 minutes
    public void reconcileData() {
        // Find accounts in transition
        List<String> transitionAccounts = featureToggles
            .getAccountsInTransition("account-service-migration");

        for (String accountId : transitionAccounts) {
            try {
                AccountResponse legacy = legacyCore.getAccount(accountId);
                AccountResponse modern = modernService.getAccount(accountId);

                if (!accountsMatch(legacy, modern)) {
                    logger.warn("Data mismatch for account: {}", accountId);
                    dataSync.reconcile(accountId, legacy, modern);
                }
            } catch (Exception e) {
                logger.error("Reconciliation failed for " + accountId, e);
            }
        }
    }

    private boolean accountsMatch(AccountResponse legacy, AccountResponse modern) {
        return Objects.equals(legacy.getBalance(), modern.getBalance()) &&
               Objects.equals(legacy.getStatus(), modern.getStatus()) &&
               Math.abs(legacy.getLastUpdateTime() - modern.getLastUpdateTime()) < 60000;
    }
}

@Configuration
public class FeatureToggleConfiguration {

    @Bean
    public FeatureToggleService featureToggles() {
        return FeatureToggleService.builder()
            // Gradual rollout by account number hash
            .toggle("account-service-migration")
                .percentage(25)  // 25% of accounts
                .hashAttribute("accountId")
                .build()

            // Dual-write enabled for safety
            .toggle("dual-write-transactions")
                .enabled(true)
                .build()

            .build();
    }
}
```

---

## API Facade Patterns

### 1. Adapter Pattern

```java
// Clean API contract
public interface AccountService {
    Account getAccount(String accountId);
    List<Transaction> getTransactions(String accountId,
        LocalDate startDate, LocalDate endDate);
    TransferResult transfer(String fromAccount, String toAccount,
        BigDecimal amount);
}

// Legacy mainframe adapter
@Service
public class MainframeAccountAdapter implements AccountService {

    @Autowired
    private CICSGateway cicsGateway;

    @Override
    public Account getAccount(String accountId) {
        // Call mainframe transaction
        CommareaRequest request = new CommareaRequest()
            .transactionId("ACCT0001")
            .field("ACCT-NBR", accountId, 20)
            .field("INQUIRY-TYPE", "FULL", 4);

        CommareaResponse response = cicsGateway.call(request);

        if (!response.isSuccess()) {
            throw new AccountNotFoundException(accountId);
        }

        // Parse COBOL copybook response
        return Account.builder()
            .accountId(response.getString("ACCT-NBR", 20).trim())
            .accountName(response.getString("ACCT-NAME", 50).trim())
            .currentBalance(response.getDecimal("CURRENT-BAL", 15, 2))
            .availableBalance(response.getDecimal("AVAILABLE-BAL", 15, 2))
            .status(mapAccountStatus(response.getString("ACCT-STATUS", 2)))
            .currency(response.getString("CURRENCY-CODE", 3).trim())
            .openDate(response.getDate("OPEN-DATE", "yyyyMMdd"))
            .lastActivityDate(response.getDate("LAST-ACTIVITY", "yyyyMMdd"))
            .build();
    }

    @Override
    public List<Transaction> getTransactions(String accountId,
            LocalDate startDate, LocalDate endDate) {

        List<Transaction> transactions = new ArrayList<>();

        // Mainframe uses batch file extract for transaction history
        String batchJobName = submitTransactionExtract(accountId,
            startDate, endDate);

        // Wait for batch job completion (with timeout)
        waitForBatchCompletion(batchJobName, Duration.ofMinutes(5));

        // Read output file
        String outputFile = String.format(
            "/batch/output/%s.TXN.OUTPUT", batchJobName
        );

        try (BufferedReader reader = new BufferedReader(
                new FileReader(outputFile))) {

            String line;
            while ((line = reader.readLine()) != null) {
                Transaction txn = parseTransactionRecord(line);
                transactions.add(txn);
            }
        }

        return transactions;
    }

    private Transaction parseTransactionRecord(String record) {
        // Parse fixed-width COBOL record
        // Record layout: ACCT(20) | DATE(8) | TIME(6) | TYPE(4) |
        //                AMOUNT(15) | DESC(50) | BALANCE(15)

        return Transaction.builder()
            .accountId(record.substring(0, 20).trim())
            .transactionDate(LocalDate.parse(
                record.substring(20, 28),
                DateTimeFormatter.ofPattern("yyyyMMdd")
            ))
            .transactionTime(LocalTime.parse(
                record.substring(28, 34),
                DateTimeFormatter.ofPattern("HHmmss")
            ))
            .type(record.substring(34, 38).trim())
            .amount(new BigDecimal(record.substring(38, 53).trim())
                .divide(new BigDecimal(100)))
            .description(record.substring(53, 103).trim())
            .balance(new BigDecimal(record.substring(103, 118).trim())
                .divide(new BigDecimal(100)))
            .build();
    }

    @Override
    public TransferResult transfer(String fromAccount, String toAccount,
            BigDecimal amount) {

        // Build transfer request COMMAREA
        CommareaRequest request = new CommareaRequest()
            .transactionId("XFER0001")
            .field("FROM-ACCT", fromAccount, 20)
            .field("TO-ACCT", toAccount, 20)
            .field("AMOUNT", amount.multiply(new BigDecimal(100))
                .longValue(), 15)
            .field("CURRENCY", "USD", 3);

        CommareaResponse response = cicsGateway.call(request);

        String returnCode = response.getString("RETURN-CODE", 4);

        return TransferResult.builder()
            .success("0000".equals(returnCode))
            .transactionId(response.getString("TXN-ID", 16).trim())
            .confirmationNumber(response.getString("CONFIRM-NBR", 20).trim())
            .timestamp(response.getTimestamp("TXN-TIMESTAMP"))
            .errorCode("0000".equals(returnCode) ? null : returnCode)
            .errorMessage(mapErrorMessage(returnCode))
            .build();
    }

    private AccountStatus mapAccountStatus(String status) {
        switch (status) {
            case "AC": return AccountStatus.ACTIVE;
            case "FR": return AccountStatus.FROZEN;
            case "CL": return AccountStatus.CLOSED;
            case "DR": return AccountStatus.DORMANT;
            default: return AccountStatus.UNKNOWN;
        }
    }
}
```

### 2. Anti-Corruption Layer

```java
@Component
public class CoreBankingAntiCorruptionLayer {

    // Translate domain models to/from legacy format

    public MainframeAccountRequest toMainframeFormat(
            CreateAccountRequest request) {

        MainframeAccountRequest mfRequest = new MainframeAccountRequest();

        // Map customer ID to legacy format (numeric only, 10 digits)
        String customerId = request.getCustomerId();
        mfRequest.setCustomerNumber(
            extractNumericId(customerId).substring(0, 10)
        );

        // Map account type to legacy codes
        mfRequest.setAccountType(mapAccountType(request.getProductType()));

        // Map currency
        mfRequest.setCurrencyCode(
            getCurrencyNumericCode(request.getCurrency())
        );

        // Map branch - legacy uses 4-digit branch codes
        String branchCode = branchMapper.getLegacyBranchCode(
            request.getBranchId()
        );
        mfRequest.setBranchCode(branchCode);

        // Initial deposit amount - convert to cents
        long amountCents = request.getInitialDeposit()
            .multiply(new BigDecimal(100))
            .setScale(0, RoundingMode.HALF_UP)
            .longValue();
        mfRequest.setInitialBalance(amountCents);

        // Tax ID - format SSN/EIN appropriately
        mfRequest.setTaxId(formatTaxId(request.getTaxId()));

        return mfRequest;
    }

    public Account fromMainframeFormat(MainframeAccountResponse response) {

        Account account = new Account();

        // Reverse mappings
        account.setAccountId(formatAccountId(response.getAccountNumber()));
        account.setCustomerId(formatCustomerId(response.getCustomerNumber()));
        account.setProductType(reverseMapAccountType(response.getAccountType()));
        account.setCurrency(Currency.getInstance(
            getCurrencyAlphaCode(response.getCurrencyCode())
        ));

        // Parse balances from COMP-3
        account.setCurrentBalance(
            parseComp3Amount(response.getCurrentBalanceBytes())
        );
        account.setAvailableBalance(
            parseComp3Amount(response.getAvailableBalanceBytes())
        );

        // Dates from mainframe format (YYYYMMDD)
        account.setOpenDate(parseMainframeDate(response.getOpenDate()));
        account.setLastActivityDate(
            parseMainframeDate(response.getLastActivityDate())
        );

        // Status mapping with defaults for unknown codes
        account.setStatus(
            mapAccountStatus(response.getStatusCode(), AccountStatus.UNKNOWN)
        );

        return account;
    }

    private String mapAccountType(ProductType productType) {
        // Modern enum to legacy 2-character code
        Map<ProductType, String> mapping = Map.of(
            ProductType.CHECKING, "CK",
            ProductType.SAVINGS, "SV",
            ProductType.MONEY_MARKET, "MM",
            ProductType.CD, "CD",
            ProductType.IRA, "IR"
        );

        return mapping.getOrDefault(productType, "CK");
    }

    private ProductType reverseMapAccountType(String legacyCode) {
        Map<String, ProductType> mapping = Map.of(
            "CK", ProductType.CHECKING,
            "SV", ProductType.SAVINGS,
            "MM", ProductType.MONEY_MARKET,
            "CD", ProductType.CD,
            "IR", ProductType.IRA,
            "TR", ProductType.TRUST
        );

        return mapping.getOrDefault(legacyCode, ProductType.UNKNOWN);
    }
}
```

---

## Data Synchronization Strategies

### 1. Event-Driven Synchronization

```java
@Service
public class CoreBankingEventPublisher {

    @Autowired
    private KafkaTemplate<String, AccountEvent> kafkaTemplate;

    @Autowired
    private DB2ChangeDataCapture cdc;

    @PostConstruct
    public void startEventPublishing() {
        // Subscribe to CDC changes
        cdc.subscribe("COREBANK.ACCOUNT_MASTER", this::publishAccountEvent);
        cdc.subscribe("COREBANK.TRANSACTION_LOG", this::publishTransactionEvent);
    }

    private void publishAccountEvent(CDCChange change) {
        AccountEvent event = AccountEvent.builder()
            .eventId(UUID.randomUUID().toString())
            .eventType(mapOperationType(change.getOperation()))
            .timestamp(change.getTimestamp())
            .accountId(change.getString("ACCT_NBR"))
            .currentBalance(change.getDecimal("CURRENT_BAL"))
            .availableBalance(change.getDecimal("AVAILABLE_BAL"))
            .status(change.getString("ACCT_STATUS"))
            .build();

        kafkaTemplate.send("core.account.events",
            event.getAccountId(),
            event);
    }

    private void publishTransactionEvent(CDCChange change) {
        TransactionEvent event = TransactionEvent.builder()
            .eventId(UUID.randomUUID().toString())
            .eventType(EventType.TRANSACTION_POSTED)
            .timestamp(change.getTimestamp())
            .transactionId(change.getString("TXN_ID"))
            .accountId(change.getString("ACCT_NBR"))
            .amount(change.getDecimal("TXN_AMOUNT"))
            .type(change.getString("TXN_TYPE"))
            .description(change.getString("TXN_DESC"))
            .build();

        kafkaTemplate.send("core.transaction.events",
            event.getAccountId(),
            event);
    }
}

@Service
public class AccountProjectionService {

    @Autowired
    private AccountRepository accountRepository;

    @KafkaListener(topics = "core.account.events", groupId = "account-projection")
    public void handleAccountEvent(AccountEvent event) {
        switch (event.getEventType()) {
            case ACCOUNT_CREATED:
                createAccountProjection(event);
                break;
            case ACCOUNT_UPDATED:
                updateAccountProjection(event);
                break;
            case ACCOUNT_CLOSED:
                closeAccountProjection(event);
                break;
        }
    }

    private void updateAccountProjection(AccountEvent event) {
        accountRepository.findById(event.getAccountId())
            .ifPresentOrElse(
                account -> {
                    account.setCurrentBalance(event.getCurrentBalance());
                    account.setAvailableBalance(event.getAvailableBalance());
                    account.setStatus(event.getStatus());
                    account.setLastSyncTime(event.getTimestamp());
                    accountRepository.save(account);
                },
                () -> {
                    logger.warn("Account not found for update: {}",
                        event.getAccountId());
                    // Trigger full sync for this account
                    syncService.syncAccount(event.getAccountId());
                }
            );
    }
}
```

### 2. Scheduled Batch Synchronization

```java
@Service
public class BatchSynchronizationService {

    @Autowired
    private LegacyCoreService legacyCore;

    @Autowired
    private AccountRepository accountRepository;

    @Scheduled(cron = "0 0 2 * * *")  // Daily at 2 AM
    public void fullAccountSync() {
        logger.info("Starting full account synchronization");

        // Request batch extract from mainframe
        String jobName = legacyCore.submitBatchExtract(
            "ACCOUNT_FULL_EXTRACT",
            LocalDate.now()
        );

        // Wait for job completion
        BatchJobStatus status = legacyCore.waitForCompletion(
            jobName,
            Duration.ofHours(2)
        );

        if (!status.isSuccessful()) {
            logger.error("Batch extract failed: {}", status.getErrorMessage());
            alerting.sendAlert("SYNC_FAILED", status);
            return;
        }

        // Process output file
        String outputFile = status.getOutputDataset();
        processBatchFile(outputFile);
    }

    private void processBatchFile(String dataset) {
        try {
            // Download from mainframe
            File localFile = legacyCore.downloadDataset(dataset);

            // Process records
            try (BufferedReader reader = new BufferedReader(
                    new FileReader(localFile))) {

                String line;
                int recordCount = 0;
                int updateCount = 0;

                while ((line = reader.readLine()) != null) {
                    try {
                        AccountRecord record = parseAccountRecord(line);
                        upsertAccount(record);
                        updateCount++;
                    } catch (Exception e) {
                        logger.error("Failed to process record: {}", line, e);
                    }

                    recordCount++;

                    if (recordCount % 10000 == 0) {
                        logger.info("Processed {} records", recordCount);
                    }
                }

                logger.info("Sync complete: {} records processed, {} updated",
                    recordCount, updateCount);
            }

        } catch (IOException e) {
            logger.error("File processing failed", e);
            throw new SyncException("Batch sync failed", e);
        }
    }

    @Transactional
    private void upsertAccount(AccountRecord record) {
        Account account = accountRepository
            .findById(record.getAccountId())
            .orElse(new Account());

        account.setAccountId(record.getAccountId());
        account.setAccountName(record.getAccountName());
        account.setCurrentBalance(record.getCurrentBalance());
        account.setAvailableBalance(record.getAvailableBalance());
        account.setStatus(record.getStatus());
        account.setLastSyncTime(Instant.now());

        accountRepository.save(account);
    }
}
```

---

## Real-World Examples

### Example 1: Large Bank Modernization (Capital One)

**Challenge**: Migrate from mainframe to cloud-native architecture while maintaining 24/7 operations.

**Approach**:
1. Built API facade layer using AWS API Gateway + Lambda
2. Implemented dual-write pattern for transactions
3. Used Strangler Fig to incrementally migrate account types
4. Maintained mainframe as system of record during transition

```java
// Capital One-style routing service
@Service
public class AccountRoutingService {

    @Autowired
    private DynamoDBAccountRepository modernRepo;

    @Autowired
    private MainframeAccountService legacyService;

    public Account getAccount(String accountId) {
        // Check migration status in DynamoDB
        MigrationStatus status = getMigrationStatus(accountId);

        switch (status) {
            case NOT_MIGRATED:
                return legacyService.getAccount(accountId);

            case IN_PROGRESS:
                // Read from both, compare, return legacy
                Account legacy = legacyService.getAccount(accountId);
                Account modern = modernRepo.findById(accountId).orElse(null);

                if (modern != null && !accountsMatch(legacy, modern)) {
                    logDiscrepancy(accountId, legacy, modern);
                }

                return legacy;

            case MIGRATED:
                return modernRepo.findById(accountId)
                    .orElseThrow(() -> new AccountNotFoundException(accountId));

            default:
                throw new IllegalStateException("Unknown migration status");
        }
    }
}
```

### Example 2: Regional Bank API Modernization

**Challenge**: Expose legacy Fiserv Premier core banking through modern REST APIs.

**Solution**:
```java
@RestController
@RequestMapping("/api/v1/accounts")
public class AccountAPIController {

    @Autowired
    private FiservPremierAdapter fiservAdapter;

    @GetMapping("/{accountId}")
    public ResponseEntity<AccountDTO> getAccount(
            @PathVariable String accountId,
            @RequestHeader("X-Request-ID") String requestId) {

        // Log request
        auditLog.logRequest(requestId, "GET_ACCOUNT", accountId);

        try {
            // Call legacy system through adapter
            Account account = fiservAdapter.getAccount(accountId);

            // Transform to API model
            AccountDTO dto = AccountMapper.toDTO(account);

            // Return with caching headers
            return ResponseEntity.ok()
                .cacheControl(CacheControl.maxAge(60, TimeUnit.SECONDS))
                .header("X-Request-ID", requestId)
                .body(dto);

        } catch (AccountNotFoundException e) {
            return ResponseEntity.notFound()
                .header("X-Request-ID", requestId)
                .build();
        }
    }
}
```

### Example 3: Payment Processing Integration

**Challenge**: Integrate real-time payment processing with batch-oriented core banking.

**Solution**: Event-driven architecture with eventual consistency

```java
@Service
public class PaymentProcessingService {

    @Autowired
    private KafkaTemplate<String, PaymentEvent> kafka;

    @Autowired
    private CoreBankingService coreService;

    @Transactional
    public PaymentResponse processPayment(PaymentRequest request) {
        // Validate with core banking
        AccountValidation validation = coreService.validateAccount(
            request.getDebitAccount()
        );

        if (!validation.isValid()) {
            return PaymentResponse.rejected(validation.getReason());
        }

        // Create pending payment
        Payment payment = Payment.builder()
            .id(UUID.randomUUID().toString())
            .status(PaymentStatus.PENDING)
            .amount(request.getAmount())
            .debitAccount(request.getDebitAccount())
            .creditAccount(request.getCreditAccount())
            .build();

        paymentRepository.save(payment);

        // Publish event for async processing
        PaymentEvent event = PaymentEvent.builder()
            .paymentId(payment.getId())
            .type(PaymentEventType.PAYMENT_INITIATED)
            .timestamp(Instant.now())
            .payload(payment)
            .build();

        kafka.send("payments.initiated", payment.getId(), event);

        return PaymentResponse.accepted(payment.getId());
    }

    @KafkaListener(topics = "payments.initiated")
    public void handlePaymentInitiated(PaymentEvent event) {
        try {
            // Post to core banking system
            PostingResult result = coreService.postTransaction(
                event.getPayload().getDebitAccount(),
                event.getPayload().getCreditAccount(),
                event.getPayload().getAmount()
            );

            // Update payment status
            updatePaymentStatus(event.getPaymentId(),
                PaymentStatus.POSTED,
                result.getTransactionId());

            // Publish completion event
            kafka.send("payments.completed", event.getPaymentId(),
                PaymentEvent.completed(event, result));

        } catch (Exception e) {
            logger.error("Payment posting failed", e);

            // Update to failed status
            updatePaymentStatus(event.getPaymentId(),
                PaymentStatus.FAILED,
                null);

            // Publish failure event
            kafka.send("payments.failed", event.getPaymentId(),
                PaymentEvent.failed(event, e.getMessage()));
        }
    }
}
```

---

## Migration Strategies

### 1. Phased Migration Approach

```
Phase 1: Assessment (2-3 months)
- Inventory legacy systems and dependencies
- Map data models and business logic
- Identify integration points
- Define success criteria

Phase 2: Foundation (3-6 months)
- Build API facade layer
- Implement CDC for data replication
- Create adapter services
- Set up monitoring and observability

Phase 3: Pilot (3-4 months)
- Select low-risk account segment
- Implement dual-write pattern
- Migrate pilot accounts
- Validate functionality and performance

Phase 4: Incremental Migration (12-24 months)
- Migrate account types progressively
- Implement feature toggles
- Continuous reconciliation
- Gradual traffic shift

Phase 5: Decommissioning (6-12 months)
- Complete data migration
- Archive historical data
- Decommission legacy systems
- Knowledge transfer
```

### 2. Risk Mitigation

```java
@Component
public class MigrationSafetyChecks {

    @Scheduled(cron = "*/5 * * * *")  // Every 5 minutes
    public void validateDataConsistency() {
        List<String> migratedAccounts = getMigratedAccounts();

        for (String accountId : migratedAccounts) {
            Account legacy = legacyService.getAccount(accountId);
            Account modern = modernService.getAccount(accountId);

            if (Math.abs(legacy.getBalance().subtract(modern.getBalance())
                    .doubleValue()) > 0.01) {
                // Balance mismatch!
                alert.critical("Balance mismatch for account: " + accountId);

                // Auto-rollback if configured
                if (config.isAutoRollbackEnabled()) {
                    rollbackAccount(accountId);
                }
            }
        }
    }

    @Transactional
    public void rollbackAccount(String accountId) {
        logger.warn("Rolling back account to legacy: {}", accountId);

        // Update routing to send traffic back to legacy
        routingService.routeToLegacy(accountId);

        // Mark migration as failed
        migrationStatus.markFailed(accountId, "Data inconsistency");

        // Trigger investigation
        incidentManagement.createIncident(
            "Migration Rollback",
            "Account " + accountId + " rolled back due to data inconsistency"
        );
    }
}
```

---

## Best Practices and Considerations

### 1. Performance Optimization

- **Connection Pooling**: Maintain persistent connections to mainframe
- **Caching**: Cache reference data and frequently accessed accounts
- **Async Processing**: Use message queues for non-real-time operations
- **Batch Operations**: Group transactions where possible

### 2. Security

- **Encryption**: Encrypt data in transit (TLS) and at rest
- **Authentication**: Use RACF/ACF2 integration for mainframe access
- **Audit Logging**: Log all access to core banking systems
- **Data Masking**: Mask PII in non-production environments

### 3. Monitoring and Observability

```java
@Aspect
@Component
public class CoreBankingMonitoring {

    @Around("@annotation(MonitorCoreIntegration)")
    public Object monitorIntegration(ProceedingJoinPoint joinPoint)
            throws Throwable {

        String operation = joinPoint.getSignature().getName();
        Timer.Sample sample = Timer.start(meterRegistry);

        try {
            Object result = joinPoint.proceed();

            sample.stop(Timer.builder("core.integration.duration")
                .tag("operation", operation)
                .tag("status", "success")
                .register(meterRegistry));

            return result;

        } catch (Exception e) {
            sample.stop(Timer.builder("core.integration.duration")
                .tag("operation", operation)
                .tag("status", "error")
                .register(meterRegistry));

            Counter.builder("core.integration.errors")
                .tag("operation", operation)
                .tag("error_type", e.getClass().getSimpleName())
                .register(meterRegistry)
                .increment();

            throw e;
        }
    }
}
```

### 4. Disaster Recovery

- **Data Backup**: Regular backups of both legacy and modern systems
- **Fallback Procedures**: Ability to route all traffic back to legacy
- **Sync State Tracking**: Maintain detailed migration state
- **Recovery Testing**: Regular DR drills

### 5. Compliance Considerations

- **Data Residency**: Ensure compliance with local regulations
- **Audit Trails**: Maintain complete audit history
- **Regulatory Reporting**: Ensure new systems meet reporting requirements
- **SOX Compliance**: Maintain controls through migration

---

## Conclusion

Legacy core banking integration requires a thoughtful, incremental approach that balances innovation with risk management. The patterns and examples in this guide provide a foundation for successful modernization projects while maintaining the reliability and compliance that financial institutions require.

### Key Takeaways

1. **Start with a Facade**: Build an API layer before migrating
2. **Incremental Migration**: Use Strangler Fig pattern for gradual transition
3. **Dual-Write for Safety**: Write to both systems during migration
4. **Continuous Validation**: Implement reconciliation and monitoring
5. **Plan for Rollback**: Always have an exit strategy

### References

- ISO 20022 Financial Services Standards
- IBM CICS Transaction Gateway Documentation
- Martin Fowler - Strangler Fig Pattern
- "Modernizing Legacy Systems" by Chris Birchall
- Financial Services Cloud Adoption Framework (AWS/Azure/GCP)
