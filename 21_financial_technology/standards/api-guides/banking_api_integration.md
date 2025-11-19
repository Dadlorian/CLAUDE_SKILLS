# Banking API Integration Guide

## Table of Contents
1. [Introduction](#introduction)
2. [Open Banking APIs](#open-banking-apis)
3. [Account Information Service (AIS) APIs](#account-information-service-ais-apis)
4. [Payment Initiation Service (PIS) APIs](#payment-initiation-service-pis-apis)
5. [Strong Customer Authentication (SCA)](#strong-customer-authentication-sca)
6. [OAuth 2.0 and OpenID Connect for Banking](#oauth-20-and-openid-connect-for-banking)
7. [Consent Management](#consent-management)
8. [Error Handling and Retry Logic](#error-handling-and-retry-logic)
9. [Rate Limiting Patterns](#rate-limiting-patterns)
10. [Security Considerations](#security-considerations)
11. [Production-Grade Practices](#production-grade-practices)
12. [Provider Examples](#provider-examples)

## Introduction

Banking API integration enables applications to securely access customer banking data and initiate payments with proper authorization. This guide covers Open Banking standards (PSD2, FDX) and best practices for secure, compliant banking integrations.

### Key Principles
- **Customer Consent**: Always obtain explicit consent before accessing data
- **Security**: Implement strong authentication and encryption
- **Compliance**: Adhere to PSD2, GDPR, and regional regulations
- **Data Minimization**: Request only necessary permissions
- **Transparency**: Clearly communicate data usage to customers

## Open Banking APIs

### PSD2 Standards (Europe)

```typescript
enum PSD2ServiceType {
  AIS = 'AIS', // Account Information Service
  PIS = 'PIS', // Payment Initiation Service
  PIIS = 'PIIS', // Payment Instrument Issuer Service
  CAF = 'CAF', // Confirmation of Availability of Funds
}

interface PSD2Provider {
  name: string;
  country: string;
  bic: string;
  apiVersion: string;
  sandboxUrl: string;
  productionUrl: string;
  supportedServices: PSD2ServiceType[];
}

class PSD2Client {
  private readonly baseUrl: string;
  private readonly certificate: string;
  private readonly privateKey: string;

  constructor(
    baseUrl: string,
    certificate: string,
    privateKey: string
  ) {
    this.baseUrl = baseUrl;
    this.certificate = certificate;
    this.privateKey = privateKey;
  }

  async getAccounts(consentId: string): Promise<BankAccount[]> {
    const response = await this.makeAuthenticatedRequest(
      'GET',
      '/v1/accounts',
      {
        headers: {
          'Consent-ID': consentId,
        },
      }
    );

    return response.accounts.map((acc: any) => ({
      accountId: acc.resourceId,
      iban: acc.iban,
      currency: acc.currency,
      name: acc.name,
      product: acc.product,
      cashAccountType: acc.cashAccountType,
      status: acc.status,
      bic: acc.bic,
    }));
  }

  async getTransactions(
    accountId: string,
    consentId: string,
    dateFrom?: Date,
    dateTo?: Date
  ): Promise<Transaction[]> {
    const response = await this.makeAuthenticatedRequest(
      'GET',
      `/v1/accounts/${accountId}/transactions`,
      {
        params: {
          dateFrom: dateFrom?.toISOString().split('T')[0],
          dateTo: dateTo?.toISOString().split('T')[0],
        },
        headers: {
          'Consent-ID': consentId,
        },
      }
    );

    return response.transactions.booked.map((tx: any) => ({
      transactionId: tx.transactionId,
      bookingDate: new Date(tx.bookingDate),
      valueDate: new Date(tx.valueDate),
      amount: parseFloat(tx.transactionAmount.amount),
      currency: tx.transactionAmount.currency,
      creditorName: tx.creditorName,
      debtorName: tx.debtorName,
      remittanceInformationUnstructured: tx.remittanceInformationUnstructured,
    }));
  }

  async getBalances(
    accountId: string,
    consentId: string
  ): Promise<Balance[]> {
    const response = await this.makeAuthenticatedRequest(
      'GET',
      `/v1/accounts/${accountId}/balances`,
      {
        headers: {
          'Consent-ID': consentId,
        },
      }
    );

    return response.balances.map((bal: any) => ({
      balanceType: bal.balanceType,
      amount: parseFloat(bal.balanceAmount.amount),
      currency: bal.balanceAmount.currency,
      referenceDate: new Date(bal.referenceDate),
    }));
  }

  private async makeAuthenticatedRequest(
    method: string,
    path: string,
    options: any = {}
  ): Promise<any> {
    // Implementation with mutual TLS authentication
    return {};
  }
}

interface BankAccount {
  accountId: string;
  iban: string;
  currency: string;
  name: string;
  product: string;
  cashAccountType: string;
  status: string;
  bic?: string;
}

interface Transaction {
  transactionId: string;
  bookingDate: Date;
  valueDate: Date;
  amount: number;
  currency: string;
  creditorName?: string;
  debtorName?: string;
  remittanceInformationUnstructured?: string;
}

interface Balance {
  balanceType: string;
  amount: number;
  currency: string;
  referenceDate: Date;
}
```

### FDX Standards (North America)

```typescript
interface FDXAccount {
  accountId: string;
  accountNumber: string;
  accountNumberDisplay: string;
  accountType: string;
  balance: number;
  availableBalance: number;
  currency: string;
  accountName: string;
  status: string;
}

class FDXClient {
  private readonly baseUrl: string;
  private readonly accessToken: string;

  constructor(baseUrl: string, accessToken: string) {
    this.baseUrl = baseUrl;
    this.accessToken = accessToken;
  }

  async getAccounts(): Promise<FDXAccount[]> {
    const response = await this.makeRequest(
      'GET',
      '/fdx/v4/accounts'
    );

    return response.accounts.map((acc: any) => ({
      accountId: acc.accountId,
      accountNumber: acc.accountNumber,
      accountNumberDisplay: acc.accountNumberDisplay,
      accountType: acc.accountType,
      balance: acc.balance,
      availableBalance: acc.availableBalance,
      currency: acc.currency,
      accountName: acc.accountName,
      status: acc.status,
    }));
  }

  async getTransactions(
    accountId: string,
    startDate?: Date,
    endDate?: Date
  ): Promise<FDXTransaction[]> {
    const response = await this.makeRequest(
      'GET',
      `/fdx/v4/accounts/${accountId}/transactions`,
      {
        params: {
          startDate: startDate?.toISOString(),
          endDate: endDate?.toISOString(),
        },
      }
    );

    return response.transactions.map((tx: any) => ({
      transactionId: tx.transactionId,
      description: tx.description,
      amount: tx.amount,
      currency: tx.currency,
      transactionDate: new Date(tx.transactionDate),
      postedDate: new Date(tx.postedDate),
      type: tx.type,
      category: tx.category,
      merchant: tx.merchant,
    }));
  }

  private async makeRequest(
    method: string,
    path: string,
    options: any = {}
  ): Promise<any> {
    // Implementation with OAuth 2.0 bearer token
    return {};
  }
}

interface FDXTransaction {
  transactionId: string;
  description: string;
  amount: number;
  currency: string;
  transactionDate: Date;
  postedDate: Date;
  type: string;
  category?: string;
  merchant?: string;
}
```

## Account Information Service (AIS) APIs

### Account Discovery and Selection

```typescript
class AccountInformationService {
  private readonly bankClient: any;

  constructor(bankClient: any) {
    this.bankClient = bankClient;
  }

  async discoverAccounts(
    customerId: string,
    accessToken: string
  ): Promise<BankAccount[]> {
    try {
      const accounts = await this.bankClient.getAccounts(accessToken);

      // Filter and categorize accounts
      return accounts.map((account: any) => ({
        accountId: account.accountId,
        iban: account.iban,
        currency: account.currency,
        name: account.name,
        product: account.product,
        cashAccountType: account.cashAccountType,
        status: account.status,
        bic: account.bic,
      }));
    } catch (error) {
      throw new AISError('Failed to discover accounts', error);
    }
  }

  async getAccountDetails(
    accountId: string,
    consentId: string
  ): Promise<AccountDetails> {
    const [account, balances] = await Promise.all([
      this.bankClient.getAccount(accountId, consentId),
      this.bankClient.getBalances(accountId, consentId),
    ]);

    return {
      accountId: account.accountId,
      iban: account.iban,
      currency: account.currency,
      name: account.name,
      product: account.product,
      balances: balances,
      owner: account.ownerName,
    };
  }

  async getAccountTransactions(
    accountId: string,
    consentId: string,
    options: {
      dateFrom?: Date;
      dateTo?: Date;
      limit?: number;
      offset?: number;
    }
  ): Promise<TransactionResponse> {
    const transactions = await this.bankClient.getTransactions(
      accountId,
      consentId,
      options.dateFrom,
      options.dateTo
    );

    // Apply pagination
    const start = options.offset || 0;
    const end = start + (options.limit || 100);
    const paginatedTransactions = transactions.slice(start, end);

    return {
      transactions: paginatedTransactions,
      totalCount: transactions.length,
      hasMore: end < transactions.length,
    };
  }

  async categorizeTransactions(
    transactions: Transaction[]
  ): Promise<CategorizedTransaction[]> {
    return transactions.map((tx) => ({
      ...tx,
      category: this.detectCategory(tx),
      subcategory: this.detectSubcategory(tx),
    }));
  }

  private detectCategory(transaction: Transaction): string {
    const description = transaction.remittanceInformationUnstructured?.toLowerCase() || '';

    if (description.includes('grocery') || description.includes('supermarket')) {
      return 'Food & Dining';
    } else if (description.includes('gas') || description.includes('fuel')) {
      return 'Transportation';
    } else if (description.includes('rent') || description.includes('mortgage')) {
      return 'Housing';
    } else if (description.includes('salary') || description.includes('payroll')) {
      return 'Income';
    }

    return 'Uncategorized';
  }

  private detectSubcategory(transaction: Transaction): string {
    // Implement subcategory detection logic
    return 'General';
  }
}

interface AccountDetails {
  accountId: string;
  iban: string;
  currency: string;
  name: string;
  product: string;
  balances: Balance[];
  owner: string;
}

interface TransactionResponse {
  transactions: Transaction[];
  totalCount: number;
  hasMore: boolean;
}

interface CategorizedTransaction extends Transaction {
  category: string;
  subcategory: string;
}

class AISError extends Error {
  constructor(message: string, public cause?: any) {
    super(message);
    this.name = 'AISError';
  }
}
```

### Balance Checking and Monitoring

```typescript
class BalanceMonitoringService {
  private readonly accountService: AccountInformationService;
  private balanceCache: Map<string, { balance: Balance[]; timestamp: number }>;
  private readonly cacheTTL: number = 5 * 60 * 1000; // 5 minutes

  constructor(accountService: AccountInformationService) {
    this.accountService = accountService;
    this.balanceCache = new Map();
  }

  async getCurrentBalance(
    accountId: string,
    consentId: string,
    useCache: boolean = true
  ): Promise<Balance[]> {
    if (useCache) {
      const cached = this.balanceCache.get(accountId);
      if (cached && Date.now() - cached.timestamp < this.cacheTTL) {
        return cached.balance;
      }
    }

    const balances = await this.accountService.getAccountDetails(
      accountId,
      consentId
    ).then((details) => details.balances);

    this.balanceCache.set(accountId, {
      balance: balances,
      timestamp: Date.now(),
    });

    return balances;
  }

  async getAvailableBalance(
    accountId: string,
    consentId: string
  ): Promise<number> {
    const balances = await this.getCurrentBalance(accountId, consentId);
    const available = balances.find((b) => b.balanceType === 'interimAvailable');
    return available?.amount || 0;
  }

  async checkSufficientFunds(
    accountId: string,
    consentId: string,
    requiredAmount: number
  ): Promise<boolean> {
    const available = await this.getAvailableBalance(accountId, consentId);
    return available >= requiredAmount;
  }

  async monitorLowBalance(
    accountId: string,
    consentId: string,
    threshold: number,
    callback: (balance: number) => void
  ): Promise<void> {
    const checkBalance = async () => {
      const balance = await this.getAvailableBalance(accountId, consentId);
      if (balance < threshold) {
        callback(balance);
      }
    };

    // Check immediately
    await checkBalance();

    // Set up periodic checking
    setInterval(checkBalance, 60 * 60 * 1000); // Check hourly
  }
}
```

## Payment Initiation Service (PIS) APIs

### Single Payment Initiation

```typescript
interface PaymentInitiationRequest {
  debtorAccountId: string;
  creditorName: string;
  creditorAccount: {
    iban: string;
    bic?: string;
  };
  amount: number;
  currency: string;
  remittanceInformation: string;
  requestedExecutionDate?: Date;
}

interface PaymentInitiationResponse {
  paymentId: string;
  status: PaymentStatus;
  transactionStatus: string;
  scaRedirect?: string;
  scaOAuth?: string;
  _links?: {
    scaRedirect?: { href: string };
    scaOAuth?: { href: string };
    scaStatus?: { href: string };
    status?: { href: string };
  };
}

enum PaymentStatus {
  RCVD = 'RCVD', // Received
  ACTC = 'ACTC', // AcceptedTechnicalValidation
  ACCP = 'ACCP', // AcceptedCustomerProfile
  ACSC = 'ACSC', // AcceptedSettlementCompleted
  RJCT = 'RJCT', // Rejected
  PDNG = 'PDNG', // Pending
  CANC = 'CANC', // Cancelled
}

class PaymentInitiationService {
  private readonly bankClient: any;

  constructor(bankClient: any) {
    this.bankClient = bankClient;
  }

  async initiatePayment(
    request: PaymentInitiationRequest,
    consentId: string
  ): Promise<PaymentInitiationResponse> {
    try {
      const response = await this.bankClient.post(
        '/v1/payments/sepa-credit-transfers',
        {
          debtorAccount: {
            iban: request.debtorAccountId,
          },
          creditorName: request.creditorName,
          creditorAccount: {
            iban: request.creditorAccount.iban,
            bic: request.creditorAccount.bic,
          },
          instructedAmount: {
            amount: request.amount.toFixed(2),
            currency: request.currency,
          },
          remittanceInformationUnstructured: request.remittanceInformation,
          requestedExecutionDate: request.requestedExecutionDate?.toISOString().split('T')[0],
        },
        {
          headers: {
            'Consent-ID': consentId,
            'PSU-IP-Address': this.getPSUIPAddress(),
            'X-Request-ID': this.generateRequestId(),
          },
        }
      );

      return {
        paymentId: response.data.paymentId,
        status: response.data.transactionStatus,
        transactionStatus: response.data.transactionStatus,
        scaRedirect: response.data._links?.scaRedirect?.href,
        scaOAuth: response.data._links?.scaOAuth?.href,
        _links: response.data._links,
      };
    } catch (error) {
      throw new PISError('Failed to initiate payment', error);
    }
  }

  async getPaymentStatus(
    paymentId: string,
    consentId: string
  ): Promise<PaymentStatus> {
    const response = await this.bankClient.get(
      `/v1/payments/sepa-credit-transfers/${paymentId}/status`,
      {
        headers: {
          'Consent-ID': consentId,
          'X-Request-ID': this.generateRequestId(),
        },
      }
    );

    return response.data.transactionStatus;
  }

  async cancelPayment(
    paymentId: string,
    consentId: string
  ): Promise<boolean> {
    try {
      await this.bankClient.delete(
        `/v1/payments/sepa-credit-transfers/${paymentId}`,
        {
          headers: {
            'Consent-ID': consentId,
            'X-Request-ID': this.generateRequestId(),
          },
        }
      );
      return true;
    } catch (error) {
      throw new PISError('Failed to cancel payment', error);
    }
  }

  private getPSUIPAddress(): string {
    // Get the actual PSU (Payment Service User) IP address
    return '127.0.0.1';
  }

  private generateRequestId(): string {
    return `${Date.now()}-${Math.random().toString(36).substring(7)}`;
  }
}

class PISError extends Error {
  constructor(message: string, public cause?: any) {
    super(message);
    this.name = 'PISError';
  }
}
```

### Bulk Payment Initiation

```typescript
interface BulkPaymentRequest {
  debtorAccountId: string;
  payments: Array<{
    creditorName: string;
    creditorAccount: {
      iban: string;
      bic?: string;
    };
    amount: number;
    currency: string;
    remittanceInformation: string;
  }>;
  requestedExecutionDate?: Date;
}

class BulkPaymentService {
  private readonly paymentService: PaymentInitiationService;

  constructor(paymentService: PaymentInitiationService) {
    this.paymentService = paymentService;
  }

  async initiateBulkPayment(
    request: BulkPaymentRequest,
    consentId: string
  ): Promise<BulkPaymentResponse> {
    const paymentResults: PaymentResult[] = [];

    for (const payment of request.payments) {
      try {
        const result = await this.paymentService.initiatePayment(
          {
            debtorAccountId: request.debtorAccountId,
            creditorName: payment.creditorName,
            creditorAccount: payment.creditorAccount,
            amount: payment.amount,
            currency: payment.currency,
            remittanceInformation: payment.remittanceInformation,
            requestedExecutionDate: request.requestedExecutionDate,
          },
          consentId
        );

        paymentResults.push({
          success: true,
          paymentId: result.paymentId,
          creditorName: payment.creditorName,
          amount: payment.amount,
        });
      } catch (error) {
        paymentResults.push({
          success: false,
          error: error.message,
          creditorName: payment.creditorName,
          amount: payment.amount,
        });
      }
    }

    return {
      totalPayments: request.payments.length,
      successfulPayments: paymentResults.filter((r) => r.success).length,
      failedPayments: paymentResults.filter((r) => !r.success).length,
      results: paymentResults,
    };
  }
}

interface PaymentResult {
  success: boolean;
  paymentId?: string;
  error?: string;
  creditorName: string;
  amount: number;
}

interface BulkPaymentResponse {
  totalPayments: number;
  successfulPayments: number;
  failedPayments: number;
  results: PaymentResult[];
}
```

## Strong Customer Authentication (SCA)

### SCA Flow Implementation

```typescript
enum SCAMethod {
  REDIRECT = 'REDIRECT',
  OAUTH = 'OAUTH',
  DECOUPLED = 'DECOUPLED',
  EMBEDDED = 'EMBEDDED',
}

enum SCAStatus {
  RECEIVED = 'received',
  PSUIDENTIFIED = 'psuIdentified',
  PSUAUTHENTICATED = 'psuAuthenticated',
  SCAMETHODSELECTED = 'scaMethodSelected',
  STARTED = 'started',
  FINALISED = 'finalised',
  FAILED = 'failed',
  EXEMPTED = 'exempted',
}

interface SCAChallenge {
  scaStatus: SCAStatus;
  authenticationMethodId?: string;
  challengeData?: {
    otpFormat: string;
    additionalInformation: string;
  };
  _links?: {
    scaOAuth?: { href: string };
    confirmation?: { href: string };
  };
}

class StrongCustomerAuthentication {
  private readonly bankClient: any;

  constructor(bankClient: any) {
    this.bankClient = bankClient;
  }

  async initiateRedirectSCA(
    consentId: string,
    redirectUrl: string
  ): Promise<string> {
    const response = await this.bankClient.post(
      '/v1/consents',
      {
        access: {
          accounts: [],
          balances: [],
          transactions: [],
        },
        recurringIndicator: true,
        validUntil: this.getValidUntilDate(),
        frequencyPerDay: 4,
      },
      {
        headers: {
          'TPP-Redirect-URI': redirectUrl,
          'X-Request-ID': this.generateRequestId(),
        },
      }
    );

    return response.data._links.scaRedirect.href;
  }

  async initiateOAuthSCA(
    consentId: string,
    redirectUri: string,
    scope: string
  ): Promise<string> {
    const authUrl = new URL('/oauth/authorize', this.bankClient.baseURL);

    authUrl.searchParams.set('response_type', 'code');
    authUrl.searchParams.set('client_id', this.getClientId());
    authUrl.searchParams.set('redirect_uri', redirectUri);
    authUrl.searchParams.set('scope', scope);
    authUrl.searchParams.set('state', this.generateState());

    return authUrl.toString();
  }

  async handleDecoupledSCA(
    consentId: string,
    authenticationMethodId: string
  ): Promise<SCAChallenge> {
    const response = await this.bankClient.put(
      `/v1/consents/${consentId}/authorisations`,
      {
        authenticationMethodId,
      },
      {
        headers: {
          'X-Request-ID': this.generateRequestId(),
        },
      }
    );

    return {
      scaStatus: response.data.scaStatus,
      authenticationMethodId: response.data.authenticationMethodId,
      challengeData: response.data.challengeData,
      _links: response.data._links,
    };
  }

  async pollSCAStatus(
    consentId: string,
    authorisationId: string,
    maxAttempts: number = 30,
    intervalMs: number = 2000
  ): Promise<SCAStatus> {
    for (let attempt = 0; attempt < maxAttempts; attempt++) {
      const response = await this.bankClient.get(
        `/v1/consents/${consentId}/authorisations/${authorisationId}`,
        {
          headers: {
            'X-Request-ID': this.generateRequestId(),
          },
        }
      );

      const status: SCAStatus = response.data.scaStatus;

      if (
        status === SCAStatus.FINALISED ||
        status === SCAStatus.FAILED ||
        status === SCAStatus.EXEMPTED
      ) {
        return status;
      }

      await this.sleep(intervalMs);
    }

    throw new SCAError('SCA timeout: maximum polling attempts reached');
  }

  async submitSCAAuthentication(
    consentId: string,
    authorisationId: string,
    authenticationData: string
  ): Promise<SCAStatus> {
    const response = await this.bankClient.put(
      `/v1/consents/${consentId}/authorisations/${authorisationId}`,
      {
        scaAuthenticationData: authenticationData,
      },
      {
        headers: {
          'X-Request-ID': this.generateRequestId(),
        },
      }
    );

    return response.data.scaStatus;
  }

  private getValidUntilDate(): string {
    const date = new Date();
    date.setMonth(date.getMonth() + 3); // 90 days validity
    return date.toISOString().split('T')[0];
  }

  private generateRequestId(): string {
    return `${Date.now()}-${Math.random().toString(36).substring(7)}`;
  }

  private getClientId(): string {
    return process.env.BANK_CLIENT_ID || '';
  }

  private generateState(): string {
    return Math.random().toString(36).substring(2, 15);
  }

  private sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}

class SCAError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'SCAError';
  }
}
```

### SCA Exemptions

```typescript
enum SCAExemption {
  LOW_VALUE = 'LOW_VALUE', // Transactions under €30
  RECURRING = 'RECURRING', // Recurring payments
  SECURE_CORPORATE = 'SECURE_CORPORATE', // Secure corporate payments
  TRUSTED_BENEFICIARY = 'TRUSTED_BENEFICIARY', // Payments to trusted beneficiaries
  TRANSACTION_RISK_ANALYSIS = 'TRANSACTION_RISK_ANALYSIS', // TRA
}

class SCAExemptionManager {
  async requestExemption(
    paymentRequest: PaymentInitiationRequest,
    exemptionType: SCAExemption
  ): Promise<boolean> {
    // Check if exemption is applicable
    if (exemptionType === SCAExemption.LOW_VALUE) {
      return this.checkLowValueExemption(paymentRequest);
    } else if (exemptionType === SCAExemption.RECURRING) {
      return this.checkRecurringExemption(paymentRequest);
    }

    return false;
  }

  private checkLowValueExemption(
    payment: PaymentInitiationRequest
  ): boolean {
    // Low value exemption: transactions under €30
    return payment.amount < 30 && payment.currency === 'EUR';
  }

  private checkRecurringExemption(
    payment: PaymentInitiationRequest
  ): boolean {
    // Check if payment is part of a recurring series
    // Implementation depends on business logic
    return false;
  }
}
```

## OAuth 2.0 and OpenID Connect for Banking

### OAuth 2.0 Authorization Code Flow

```typescript
import crypto from 'crypto';

interface OAuthConfig {
  clientId: string;
  clientSecret: string;
  authorizationUrl: string;
  tokenUrl: string;
  redirectUri: string;
  scope: string;
}

class BankingOAuthClient {
  private readonly config: OAuthConfig;

  constructor(config: OAuthConfig) {
    this.config = config;
  }

  generateAuthorizationUrl(state?: string): string {
    const authUrl = new URL(this.config.authorizationUrl);

    const codeVerifier = this.generateCodeVerifier();
    const codeChallenge = this.generateCodeChallenge(codeVerifier);

    // Store code verifier for later use
    this.storeCodeVerifier(state || 'default', codeVerifier);

    authUrl.searchParams.set('response_type', 'code');
    authUrl.searchParams.set('client_id', this.config.clientId);
    authUrl.searchParams.set('redirect_uri', this.config.redirectUri);
    authUrl.searchParams.set('scope', this.config.scope);
    authUrl.searchParams.set('state', state || this.generateState());
    authUrl.searchParams.set('code_challenge', codeChallenge);
    authUrl.searchParams.set('code_challenge_method', 'S256');

    return authUrl.toString();
  }

  async exchangeCodeForToken(
    code: string,
    state: string
  ): Promise<OAuthTokenResponse> {
    const codeVerifier = this.retrieveCodeVerifier(state);

    const response = await fetch(this.config.tokenUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': `Basic ${Buffer.from(`${this.config.clientId}:${this.config.clientSecret}`).toString('base64')}`,
      },
      body: new URLSearchParams({
        grant_type: 'authorization_code',
        code,
        redirect_uri: this.config.redirectUri,
        code_verifier: codeVerifier,
      }).toString(),
    });

    if (!response.ok) {
      throw new OAuthError('Failed to exchange code for token');
    }

    const data = await response.json();

    return {
      accessToken: data.access_token,
      refreshToken: data.refresh_token,
      expiresIn: data.expires_in,
      tokenType: data.token_type,
      scope: data.scope,
    };
  }

  async refreshAccessToken(
    refreshToken: string
  ): Promise<OAuthTokenResponse> {
    const response = await fetch(this.config.tokenUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': `Basic ${Buffer.from(`${this.config.clientId}:${this.config.clientSecret}`).toString('base64')}`,
      },
      body: new URLSearchParams({
        grant_type: 'refresh_token',
        refresh_token: refreshToken,
      }).toString(),
    });

    if (!response.ok) {
      throw new OAuthError('Failed to refresh access token');
    }

    const data = await response.json();

    return {
      accessToken: data.access_token,
      refreshToken: data.refresh_token,
      expiresIn: data.expires_in,
      tokenType: data.token_type,
      scope: data.scope,
    };
  }

  private generateCodeVerifier(): string {
    return crypto.randomBytes(32).toString('base64url');
  }

  private generateCodeChallenge(verifier: string): string {
    return crypto
      .createHash('sha256')
      .update(verifier)
      .digest('base64url');
  }

  private generateState(): string {
    return crypto.randomBytes(16).toString('hex');
  }

  private storeCodeVerifier(state: string, verifier: string): void {
    // Store in session or database
    // This is a simplified implementation
  }

  private retrieveCodeVerifier(state: string): string {
    // Retrieve from session or database
    return '';
  }
}

interface OAuthTokenResponse {
  accessToken: string;
  refreshToken?: string;
  expiresIn: number;
  tokenType: string;
  scope: string;
}

class OAuthError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'OAuthError';
  }
}
```

### Token Management and Refresh

```typescript
class TokenManager {
  private tokens: Map<string, StoredToken> = new Map();

  async getValidToken(userId: string): Promise<string> {
    const stored = this.tokens.get(userId);

    if (!stored) {
      throw new Error('No token found for user');
    }

    // Check if token is expired or about to expire
    const expiresAt = stored.obtainedAt + stored.expiresIn * 1000;
    const bufferMs = 5 * 60 * 1000; // 5 minutes buffer

    if (Date.now() + bufferMs >= expiresAt) {
      // Token is expired or about to expire, refresh it
      const oauthClient = new BankingOAuthClient(stored.config);
      const newToken = await oauthClient.refreshAccessToken(
        stored.refreshToken!
      );

      this.storeToken(userId, newToken, stored.config);
      return newToken.accessToken;
    }

    return stored.accessToken;
  }

  storeToken(
    userId: string,
    token: OAuthTokenResponse,
    config: OAuthConfig
  ): void {
    this.tokens.set(userId, {
      accessToken: token.accessToken,
      refreshToken: token.refreshToken,
      expiresIn: token.expiresIn,
      obtainedAt: Date.now(),
      config,
    });
  }

  revokeToken(userId: string): void {
    this.tokens.delete(userId);
  }
}

interface StoredToken {
  accessToken: string;
  refreshToken?: string;
  expiresIn: number;
  obtainedAt: number;
  config: OAuthConfig;
}
```

## Consent Management

### Consent Creation and Management

```typescript
interface ConsentRequest {
  access: {
    accounts?: string[];
    balances?: string[];
    transactions?: string[];
  };
  recurringIndicator: boolean;
  validUntil: Date;
  frequencyPerDay: number;
  combinedServiceIndicator?: boolean;
}

interface ConsentResponse {
  consentId: string;
  consentStatus: ConsentStatus;
  validUntil: Date;
  frequencyPerDay: number;
  lastActionDate: Date;
  _links: {
    scaRedirect?: { href: string };
    scaOAuth?: { href: string };
    status: { href: string };
  };
}

enum ConsentStatus {
  RECEIVED = 'received',
  REJECTED = 'rejected',
  VALID = 'valid',
  REVOKED_BY_PSU = 'revokedByPsu',
  EXPIRED = 'expired',
  TERMINATED_BY_TPP = 'terminatedByTpp',
}

class ConsentManager {
  private readonly bankClient: any;
  private consents: Map<string, ConsentResponse> = new Map();

  constructor(bankClient: any) {
    this.bankClient = bankClient;
  }

  async createConsent(
    request: ConsentRequest
  ): Promise<ConsentResponse> {
    const response = await this.bankClient.post(
      '/v1/consents',
      {
        access: request.access,
        recurringIndicator: request.recurringIndicator,
        validUntil: request.validUntil.toISOString().split('T')[0],
        frequencyPerDay: request.frequencyPerDay,
        combinedServiceIndicator: request.combinedServiceIndicator,
      },
      {
        headers: {
          'X-Request-ID': this.generateRequestId(),
        },
      }
    );

    const consent: ConsentResponse = {
      consentId: response.data.consentId,
      consentStatus: response.data.consentStatus,
      validUntil: new Date(response.data.validUntil),
      frequencyPerDay: response.data.frequencyPerDay,
      lastActionDate: new Date(),
      _links: response.data._links,
    };

    this.consents.set(consent.consentId, consent);

    return consent;
  }

  async getConsentStatus(consentId: string): Promise<ConsentStatus> {
    const response = await this.bankClient.get(
      `/v1/consents/${consentId}/status`,
      {
        headers: {
          'X-Request-ID': this.generateRequestId(),
        },
      }
    );

    return response.data.consentStatus;
  }

  async getConsentDetails(consentId: string): Promise<ConsentResponse> {
    const cached = this.consents.get(consentId);
    if (cached) {
      return cached;
    }

    const response = await this.bankClient.get(
      `/v1/consents/${consentId}`,
      {
        headers: {
          'X-Request-ID': this.generateRequestId(),
        },
      }
    );

    const consent: ConsentResponse = {
      consentId: response.data.consentId,
      consentStatus: response.data.consentStatus,
      validUntil: new Date(response.data.validUntil),
      frequencyPerDay: response.data.frequencyPerDay,
      lastActionDate: new Date(response.data.lastActionDate),
      _links: response.data._links,
    };

    this.consents.set(consentId, consent);

    return consent;
  }

  async revokeConsent(consentId: string): Promise<void> {
    await this.bankClient.delete(`/v1/consents/${consentId}`, {
      headers: {
        'X-Request-ID': this.generateRequestId(),
      },
    });

    this.consents.delete(consentId);
  }

  async checkConsentValidity(consentId: string): Promise<boolean> {
    const consent = await this.getConsentDetails(consentId);

    if (consent.consentStatus !== ConsentStatus.VALID) {
      return false;
    }

    if (new Date() > consent.validUntil) {
      return false;
    }

    return true;
  }

  private generateRequestId(): string {
    return `${Date.now()}-${Math.random().toString(36).substring(7)}`;
  }
}
```

### Consent Renewal and Extension

```typescript
class ConsentRenewalService {
  private readonly consentManager: ConsentManager;

  constructor(consentManager: ConsentManager) {
    this.consentManager = consentManager;
  }

  async renewConsent(
    existingConsentId: string,
    newValidUntil: Date
  ): Promise<ConsentResponse> {
    // Get existing consent details
    const existing = await this.consentManager.getConsentDetails(
      existingConsentId
    );

    // Create new consent with same permissions
    const newConsent = await this.consentManager.createConsent({
      access: {
        accounts: [],
        balances: [],
        transactions: [],
      },
      recurringIndicator: true,
      validUntil: newValidUntil,
      frequencyPerDay: existing.frequencyPerDay,
    });

    // Revoke old consent
    await this.consentManager.revokeConsent(existingConsentId);

    return newConsent;
  }

  async scheduleConsentRenewal(
    consentId: string,
    daysBeforeExpiry: number = 7
  ): Promise<void> {
    const consent = await this.consentManager.getConsentDetails(consentId);
    const expiryDate = consent.validUntil;
    const renewalDate = new Date(expiryDate);
    renewalDate.setDate(renewalDate.getDate() - daysBeforeExpiry);

    const timeUntilRenewal = renewalDate.getTime() - Date.now();

    if (timeUntilRenewal > 0) {
      setTimeout(async () => {
        const newValidUntil = new Date();
        newValidUntil.setMonth(newValidUntil.getMonth() + 3);

        await this.renewConsent(consentId, newValidUntil);
      }, timeUntilRenewal);
    }
  }
}
```

## Error Handling and Retry Logic

```typescript
enum BankingErrorType {
  CONSENT_INVALID = 'CONSENT_INVALID',
  CONSENT_EXPIRED = 'CONSENT_EXPIRED',
  INSUFFICIENT_FUNDS = 'INSUFFICIENT_FUNDS',
  ACCOUNT_BLOCKED = 'ACCOUNT_BLOCKED',
  TRANSACTION_NOT_PERMITTED = 'TRANSACTION_NOT_PERMITTED',
  RATE_LIMIT = 'RATE_LIMIT',
  NETWORK_ERROR = 'NETWORK_ERROR',
  SCA_REQUIRED = 'SCA_REQUIRED',
  SCA_FAILED = 'SCA_FAILED',
}

class BankingError extends Error {
  constructor(
    public type: BankingErrorType,
    public message: string,
    public retryable: boolean = false,
    public details?: any
  ) {
    super(message);
    this.name = 'BankingError';
  }
}

class BankingErrorHandler {
  static handleError(error: any): BankingError {
    const apiError = error.response?.data;

    if (!apiError) {
      return new BankingError(
        BankingErrorType.NETWORK_ERROR,
        'Network error occurred',
        true
      );
    }

    switch (apiError.code) {
      case 'CONSENT_INVALID':
        return new BankingError(
          BankingErrorType.CONSENT_INVALID,
          'Consent is invalid or revoked',
          false,
          apiError
        );

      case 'CONSENT_EXPIRED':
        return new BankingError(
          BankingErrorType.CONSENT_EXPIRED,
          'Consent has expired',
          false,
          apiError
        );

      case 'INSUFFICIENT_FUNDS':
        return new BankingError(
          BankingErrorType.INSUFFICIENT_FUNDS,
          'Insufficient funds in account',
          false,
          apiError
        );

      case 'RATE_LIMIT':
        return new BankingError(
          BankingErrorType.RATE_LIMIT,
          'Rate limit exceeded',
          true,
          apiError
        );

      default:
        return new BankingError(
          BankingErrorType.NETWORK_ERROR,
          apiError.message || 'Banking API error',
          true,
          apiError
        );
    }
  }
}

class BankingRetryHandler {
  private readonly maxRetries: number = 3;
  private readonly baseDelay: number = 1000;

  async executeWithRetry<T>(
    operation: () => Promise<T>,
    retryableErrors: BankingErrorType[]
  ): Promise<T> {
    let lastError: BankingError;

    for (let attempt = 0; attempt <= this.maxRetries; attempt++) {
      try {
        return await operation();
      } catch (error) {
        lastError = BankingErrorHandler.handleError(error);

        if (!lastError.retryable || !retryableErrors.includes(lastError.type)) {
          throw lastError;
        }

        if (attempt === this.maxRetries) {
          throw lastError;
        }

        const delay = this.baseDelay * Math.pow(2, attempt);
        console.log(`Retrying after ${delay}ms (attempt ${attempt + 1}/${this.maxRetries})`);
        await this.sleep(delay);
      }
    }

    throw lastError!;
  }

  private sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}
```

## Rate Limiting Patterns

```typescript
class BankingRateLimiter {
  private requestCount: number = 0;
  private readonly maxRequests: number = 4; // PSD2 default
  private readonly resetTime: Date;

  constructor(maxRequestsPerDay: number = 4) {
    this.maxRequests = maxRequestsPerDay;
    this.resetTime = this.getNextMidnight();
  }

  async checkLimit(): Promise<boolean> {
    if (Date.now() >= this.resetTime.getTime()) {
      this.reset();
    }

    return this.requestCount < this.maxRequests;
  }

  async acquirePermit(): Promise<void> {
    if (!(await this.checkLimit())) {
      const waitTime = this.resetTime.getTime() - Date.now();
      throw new Error(
        `Rate limit exceeded. Resets in ${Math.ceil(waitTime / 1000 / 60)} minutes`
      );
    }

    this.requestCount++;
  }

  private reset(): void {
    this.requestCount = 0;
    this.resetTime.setDate(this.resetTime.getDate() + 1);
  }

  private getNextMidnight(): Date {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    tomorrow.setHours(0, 0, 0, 0);
    return tomorrow;
  }
}
```

## Security Considerations

```typescript
import crypto from 'crypto';
import https from 'https';
import fs from 'fs';

class SecureBankingClient {
  private readonly certificate: Buffer;
  private readonly privateKey: Buffer;
  private readonly agent: https.Agent;

  constructor(certPath: string, keyPath: string) {
    this.certificate = fs.readFileSync(certPath);
    this.privateKey = fs.readFileSync(keyPath);

    this.agent = new https.Agent({
      cert: this.certificate,
      key: this.privateKey,
      rejectUnauthorized: true,
      minVersion: 'TLSv1.2',
    });
  }

  async makeSecureRequest(
    method: string,
    url: string,
    body?: any
  ): Promise<any> {
    const requestId = this.generateRequestId();
    const signature = this.signRequest(method, url, body, requestId);

    // Make request with mutual TLS
    return {
      headers: {
        'X-Request-ID': requestId,
        'Digest': this.calculateDigest(body),
        'Signature': signature,
      },
    };
  }

  private signRequest(
    method: string,
    url: string,
    body: any,
    requestId: string
  ): string {
    const digest = this.calculateDigest(body);
    const signingString = `(request-target): ${method.toLowerCase()} ${url}\ndigest: ${digest}\nx-request-id: ${requestId}`;

    const signature = crypto
      .createSign('RSA-SHA256')
      .update(signingString)
      .sign(this.privateKey, 'base64');

    return `keyId="cert",algorithm="rsa-sha256",headers="(request-target) digest x-request-id",signature="${signature}"`;
  }

  private calculateDigest(body: any): string {
    const bodyString = body ? JSON.stringify(body) : '';
    const hash = crypto.createHash('sha256').update(bodyString).digest('base64');
    return `SHA-256=${hash}`;
  }

  private generateRequestId(): string {
    return crypto.randomUUID();
  }
}
```

## Production-Grade Practices

```typescript
import winston from 'winston';

class BankingLogger {
  private logger: winston.Logger;

  constructor() {
    this.logger = winston.createLogger({
      level: 'info',
      format: winston.format.combine(
        winston.format.timestamp(),
        winston.format.json()
      ),
      transports: [
        new winston.transports.File({
          filename: 'banking-error.log',
          level: 'error',
        }),
        new winston.transports.File({
          filename: 'banking-audit.log',
        }),
      ],
    });
  }

  logConsentCreated(consentId: string, userId: string): void {
    this.logger.info('Consent created', {
      consentId,
      userId,
      timestamp: new Date().toISOString(),
    });
  }

  logPaymentInitiated(paymentId: string, amount: number): void {
    this.logger.info('Payment initiated', {
      paymentId,
      amount,
      timestamp: new Date().toISOString(),
    });
  }

  logError(error: BankingError, context: any): void {
    this.logger.error('Banking API error', {
      errorType: error.type,
      message: error.message,
      context,
      timestamp: new Date().toISOString(),
    });
  }
}
```

## Provider Examples

### Plaid Integration

```typescript
import { Configuration, PlaidApi, PlaidEnvironments } from 'plaid';

class PlaidIntegration {
  private client: PlaidApi;

  constructor(clientId: string, secret: string) {
    const configuration = new Configuration({
      basePath: PlaidEnvironments.sandbox,
      baseOptions: {
        headers: {
          'PLAID-CLIENT-ID': clientId,
          'PLAID-SECRET': secret,
        },
      },
    });

    this.client = new PlaidApi(configuration);
  }

  async createLinkToken(userId: string): Promise<string> {
    const response = await this.client.linkTokenCreate({
      user: { client_user_id: userId },
      client_name: 'My App',
      products: ['transactions'],
      country_codes: ['US'],
      language: 'en',
    });

    return response.data.link_token;
  }

  async exchangePublicToken(publicToken: string): Promise<string> {
    const response = await this.client.itemPublicTokenExchange({
      public_token: publicToken,
    });

    return response.data.access_token;
  }

  async getAccounts(accessToken: string): Promise<any[]> {
    const response = await this.client.accountsGet({
      access_token: accessToken,
    });

    return response.data.accounts;
  }

  async getTransactions(
    accessToken: string,
    startDate: string,
    endDate: string
  ): Promise<any[]> {
    const response = await this.client.transactionsGet({
      access_token: accessToken,
      start_date: startDate,
      end_date: endDate,
    });

    return response.data.transactions;
  }
}
```

### Yodlee Integration

```typescript
class YodleeIntegration {
  private readonly baseUrl: string;
  private readonly accessToken: string;

  constructor(baseUrl: string, accessToken: string) {
    this.baseUrl = baseUrl;
    this.accessToken = accessToken;
  }

  async getAccounts(): Promise<any[]> {
    const response = await fetch(`${this.baseUrl}/accounts`, {
      headers: {
        Authorization: `Bearer ${this.accessToken}`,
      },
    });

    const data = await response.json();
    return data.account;
  }

  async getTransactions(accountId: string): Promise<any[]> {
    const response = await fetch(
      `${this.baseUrl}/transactions?accountId=${accountId}`,
      {
        headers: {
          Authorization: `Bearer ${this.accessToken}`,
        },
      }
    );

    const data = await response.json();
    return data.transaction;
  }
}
```

### TrueLayer Integration

```typescript
class TrueLayerIntegration {
  private readonly baseUrl: string;
  private readonly accessToken: string;

  constructor(baseUrl: string, accessToken: string) {
    this.baseUrl = baseUrl;
    this.accessToken = accessToken;
  }

  async getAccounts(): Promise<any[]> {
    const response = await fetch(`${this.baseUrl}/data/v1/accounts`, {
      headers: {
        Authorization: `Bearer ${this.accessToken}`,
      },
    });

    const data = await response.json();
    return data.results;
  }

  async getBalance(accountId: string): Promise<any> {
    const response = await fetch(
      `${this.baseUrl}/data/v1/accounts/${accountId}/balance`,
      {
        headers: {
          Authorization: `Bearer ${this.accessToken}`,
        },
      }
    );

    return await response.json();
  }

  async getTransactions(accountId: string): Promise<any[]> {
    const response = await fetch(
      `${this.baseUrl}/data/v1/accounts/${accountId}/transactions`,
      {
        headers: {
          Authorization: `Bearer ${this.accessToken}`,
        },
      }
    );

    const data = await response.json();
    return data.results;
  }
}
```

## Conclusion

Banking API integration requires careful attention to security, compliance, and customer consent. Key takeaways:

1. **Consent Management**: Always obtain and manage customer consent properly
2. **Strong Authentication**: Implement SCA according to PSD2 requirements
3. **OAuth 2.0**: Use standard OAuth flows for secure authorization
4. **Rate Limiting**: Respect API frequency limits (typically 4 requests/day)
5. **Security**: Use mutual TLS and request signing
6. **Error Handling**: Implement proper retry logic for transient failures
7. **Compliance**: Adhere to PSD2, GDPR, and regional regulations
8. **Audit Trail**: Log all banking operations for compliance

Always test thoroughly in sandbox environments and maintain comprehensive monitoring for production systems.
