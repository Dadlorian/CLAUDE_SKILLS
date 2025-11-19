/**
 * E-Signature Integration - Production-ready integration with e-signature services
 * Supports DocuSign, HelloSign, Adobe Sign with advanced features
 */

const axios = require('axios');
const fs = require('fs').promises;
const path = require('path');
const FormData = require('form-data');
const EventEmitter = require('events');

/**
 * Main E-Signature Service
 * Provides unified interface for multiple e-signature providers
 */
class ESignatureService extends EventEmitter {
  constructor(provider = 'docusign', config = {}) {
    super();
    this.provider = provider;
    this.config = config;
    this.client = this.initializeClient();
    this.webhookHandlers = new Map();
  }

  initializeClient() {
    switch (this.provider.toLowerCase()) {
      case 'docusign':
        return new DocuSignClient(this.config);
      case 'hellosign':
        return new HelloSignClient(this.config);
      case 'adobesign':
        return new AdobeSignClient(this.config);
      default:
        throw new Error(`Unknown provider: ${this.provider}`);
    }
  }

  /**
   * Send document for signature
   * @param {Object} options - Signature request options
   * @returns {Promise<Object>} Envelope information
   */
  async sendForSignature(options) {
    const {
      contractId,
      documentPath,
      signers,
      emailSubject,
      emailMessage,
      metadata = {},
      expirationDays = 30,
      reminderEnabled = true,
      reminderDelay = 2
    } = options;

    try {
      const result = await this.client.sendForSignature({
        contractId,
        documentPath,
        signers,
        emailSubject,
        emailMessage,
        metadata,
        expirationDays,
        reminderEnabled,
        reminderDelay
      });

      this.emit('envelope:sent', result);
      return result;
    } catch (error) {
      this.emit('error', { operation: 'sendForSignature', error });
      throw error;
    }
  }

  /**
   * Get signature status for an envelope
   * @param {string} envelopeId - Envelope identifier
   * @returns {Promise<Object>} Status information
   */
  async getSignatureStatus(envelopeId) {
    try {
      const status = await this.client.getStatus(envelopeId);
      this.emit('status:checked', { envelopeId, status });
      return status;
    } catch (error) {
      this.emit('error', { operation: 'getSignatureStatus', error });
      throw error;
    }
  }

  /**
   * Download signed document
   * @param {string} envelopeId - Envelope identifier
   * @param {string} outputPath - Path to save document
   * @returns {Promise<Object>} Download information
   */
  async downloadSignedDocument(envelopeId, outputPath) {
    try {
      const result = await this.client.downloadDocument(envelopeId, outputPath);
      this.emit('document:downloaded', { envelopeId, outputPath });
      return result;
    } catch (error) {
      this.emit('error', { operation: 'downloadSignedDocument', error });
      throw error;
    }
  }

  /**
   * Send reminder to signer
   * @param {string} envelopeId - Envelope identifier
   * @param {string} signerEmail - Signer email address
   * @returns {Promise<Object>} Reminder confirmation
   */
  async remindSigner(envelopeId, signerEmail) {
    try {
      const result = await this.client.sendReminder(envelopeId, signerEmail);
      this.emit('reminder:sent', { envelopeId, signerEmail });
      return result;
    } catch (error) {
      this.emit('error', { operation: 'remindSigner', error });
      throw error;
    }
  }

  /**
   * Cancel/void an envelope
   * @param {string} envelopeId - Envelope identifier
   * @param {string} reason - Reason for cancellation
   * @returns {Promise<Object>} Cancellation confirmation
   */
  async cancelEnvelope(envelopeId, reason) {
    try {
      const result = await this.client.cancelEnvelope(envelopeId, reason);
      this.emit('envelope:cancelled', { envelopeId, reason });
      return result;
    } catch (error) {
      this.emit('error', { operation: 'cancelEnvelope', error });
      throw error;
    }
  }

  /**
   * Get audit trail for an envelope
   * @param {string} envelopeId - Envelope identifier
   * @returns {Promise<Object>} Audit trail data
   */
  async getAuditTrail(envelopeId) {
    return await this.client.getAuditTrail(envelopeId);
  }

  /**
   * Handle webhook events
   * @param {string} eventType - Type of event
   * @param {Function} handler - Handler function
   */
  onWebhookEvent(eventType, handler) {
    this.webhookHandlers.set(eventType, handler);
  }

  /**
   * Process incoming webhook
   * @param {Object} payload - Webhook payload
   * @returns {Promise<void>}
   */
  async processWebhook(payload) {
    const eventType = this.client.parseWebhookEvent(payload);
    const handler = this.webhookHandlers.get(eventType);

    if (handler) {
      await handler(payload);
    }

    this.emit('webhook:received', { eventType, payload });
  }
}

/**
 * DocuSign Client Implementation
 */
class DocuSignClient {
  constructor(config) {
    this.config = {
      apiUrl: config.apiUrl || 'https://demo.docusign.net/restapi',
      accountId: config.accountId,
      accessToken: config.accessToken,
      integrationKey: config.integrationKey,
      ...config
    };

    this.axios = axios.create({
      baseURL: `${this.config.apiUrl}/v2.1/accounts/${this.config.accountId}`,
      headers: {
        'Authorization': `Bearer ${this.config.accessToken}`,
        'Content-Type': 'application/json'
      }
    });
  }

  async sendForSignature(options) {
    const {
      documentPath,
      signers,
      emailSubject,
      emailMessage,
      metadata,
      expirationDays,
      reminderEnabled,
      reminderDelay
    } = options;

    // Read document
    const documentContent = await fs.readFile(documentPath);
    const documentBase64 = documentContent.toString('base64');
    const documentName = path.basename(documentPath);

    // Build envelope definition
    const envelopeDefinition = {
      emailSubject: emailSubject || 'Please sign this document',
      emailBlurb: emailMessage || 'Please review and sign the attached document.',
      status: 'sent',
      documents: [{
        documentBase64,
        name: documentName,
        fileExtension: path.extname(documentPath).substring(1),
        documentId: '1'
      }],
      recipients: {
        signers: signers.map((signer, index) => ({
          email: signer.email,
          name: signer.name,
          recipientId: String(index + 1),
          routingOrder: String(signer.order || index + 1),
          tabs: {
            signHereTabs: signer.signaturePositions || [{
              documentId: '1',
              pageNumber: '1',
              xPosition: '100',
              yPosition: '100'
            }]
          }
        }))
      },
      notification: reminderEnabled ? {
        useAccountDefaults: false,
        reminders: {
          reminderEnabled: true,
          reminderDelay: reminderDelay,
          reminderFrequency: '2'
        },
        expirations: {
          expireEnabled: true,
          expireAfter: expirationDays,
          expireWarn: '7'
        }
      } : undefined,
      customFields: metadata ? {
        textCustomFields: Object.entries(metadata).map(([name, value]) => ({
          name,
          value: String(value),
          show: 'true',
          required: 'false'
        }))
      } : undefined
    };

    // Send envelope
    const response = await this.axios.post('/envelopes', envelopeDefinition);

    return {
      envelopeId: response.data.envelopeId,
      status: response.data.status,
      statusDateTime: response.data.statusDateTime,
      uri: response.data.uri
    };
  }

  async getStatus(envelopeId) {
    const response = await this.axios.get(`/envelopes/${envelopeId}`);

    return {
      envelopeId: response.data.envelopeId,
      status: response.data.status,
      statusChangedDateTime: response.data.statusChangedDateTime,
      recipients: response.data.recipients,
      createdDateTime: response.data.createdDateTime,
      sentDateTime: response.data.sentDateTime,
      completedDateTime: response.data.completedDateTime
    };
  }

  async downloadDocument(envelopeId, outputPath) {
    const response = await this.axios.get(
      `/envelopes/${envelopeId}/documents/combined`,
      { responseType: 'arraybuffer' }
    );

    await fs.writeFile(outputPath, response.data);

    return {
      envelopeId,
      outputPath,
      size: response.data.length,
      downloadedAt: new Date().toISOString()
    };
  }

  async sendReminder(envelopeId, signerEmail) {
    const statusResponse = await this.axios.get(`/envelopes/${envelopeId}`);
    const recipient = statusResponse.data.recipients.signers.find(
      s => s.email === signerEmail
    );

    if (!recipient) {
      throw new Error(`Signer ${signerEmail} not found in envelope`);
    }

    await this.axios.put(`/envelopes/${envelopeId}/recipients/${recipient.recipientId}/notification`, {
      expirations: {
        expireEnabled: true,
        expireAfter: 120,
        expireWarn: 7
      }
    });

    return { success: true, recipientId: recipient.recipientId };
  }

  async cancelEnvelope(envelopeId, reason) {
    const response = await this.axios.put(`/envelopes/${envelopeId}`, {
      status: 'voided',
      voidedReason: reason
    });

    return {
      envelopeId,
      status: response.data.status,
      voidedReason: reason,
      voidedDateTime: new Date().toISOString()
    };
  }

  async getAuditTrail(envelopeId) {
    const response = await this.axios.get(
      `/envelopes/${envelopeId}/documents/certificate`,
      { responseType: 'arraybuffer' }
    );

    return {
      envelopeId,
      certificate: response.data.toString('base64'),
      retrievedAt: new Date().toISOString()
    };
  }

  parseWebhookEvent(payload) {
    return payload.event || 'unknown';
  }
}

/**
 * HelloSign Client Implementation
 */
class HelloSignClient {
  constructor(config) {
    this.config = {
      apiUrl: config.apiUrl || 'https://api.hellosign.com/v3',
      apiKey: config.apiKey,
      ...config
    };

    this.axios = axios.create({
      baseURL: this.config.apiUrl,
      headers: {
        'Authorization': `Basic ${Buffer.from(this.config.apiKey + ':').toString('base64')}`,
      }
    });
  }

  async sendForSignature(options) {
    const {
      documentPath,
      signers,
      emailSubject,
      emailMessage,
      metadata
    } = options;

    const formData = new FormData();
    formData.append('title', emailSubject || 'Signature Request');
    formData.append('subject', emailSubject || 'Signature Request');
    formData.append('message', emailMessage || 'Please sign this document');
    formData.append('file[0]', await fs.readFile(documentPath), path.basename(documentPath));

    signers.forEach((signer, index) => {
      formData.append(`signers[${index}][email_address]`, signer.email);
      formData.append(`signers[${index}][name]`, signer.name);
      formData.append(`signers[${index}][order]`, signer.order || index);
    });

    if (metadata) {
      Object.entries(metadata).forEach(([key, value]) => {
        formData.append(`metadata[${key}]`, value);
      });
    }

    const response = await this.axios.post('/signature_request/send', formData, {
      headers: formData.getHeaders()
    });

    return {
      envelopeId: response.data.signature_request.signature_request_id,
      status: 'sent',
      statusDateTime: new Date().toISOString()
    };
  }

  async getStatus(envelopeId) {
    const response = await this.axios.get(`/signature_request/${envelopeId}`);
    const sr = response.data.signature_request;

    return {
      envelopeId: sr.signature_request_id,
      status: sr.is_complete ? 'completed' : 'sent',
      recipients: sr.signatures,
      createdAt: new Date(sr.created_at * 1000).toISOString()
    };
  }

  async downloadDocument(envelopeId, outputPath) {
    const response = await this.axios.get(
      `/signature_request/files/${envelopeId}`,
      { responseType: 'arraybuffer' }
    );

    await fs.writeFile(outputPath, response.data);

    return {
      envelopeId,
      outputPath,
      size: response.data.length,
      downloadedAt: new Date().toISOString()
    };
  }

  async sendReminder(envelopeId, signerEmail) {
    await this.axios.post(`/signature_request/remind/${envelopeId}`, {
      email_address: signerEmail
    });

    return { success: true, email: signerEmail };
  }

  async cancelEnvelope(envelopeId, reason) {
    await this.axios.post(`/signature_request/cancel/${envelopeId}`);

    return {
      envelopeId,
      status: 'cancelled',
      reason,
      cancelledAt: new Date().toISOString()
    };
  }

  async getAuditTrail(envelopeId) {
    // HelloSign includes audit trail in the signed document
    const response = await this.axios.get(
      `/signature_request/files/${envelopeId}?file_type=pdf`,
      { responseType: 'arraybuffer' }
    );

    return {
      envelopeId,
      certificate: response.data.toString('base64'),
      retrievedAt: new Date().toISOString()
    };
  }

  parseWebhookEvent(payload) {
    return payload.event?.event_type || 'unknown';
  }
}

/**
 * Adobe Sign Client Implementation
 */
class AdobeSignClient {
  constructor(config) {
    this.config = {
      apiUrl: config.apiUrl || 'https://api.na1.adobesign.com/api/rest/v6',
      accessToken: config.accessToken,
      ...config
    };

    this.axios = axios.create({
      baseURL: this.config.apiUrl,
      headers: {
        'Authorization': `Bearer ${this.config.accessToken}`,
        'Content-Type': 'application/json'
      }
    });
  }

  async sendForSignature(options) {
    const {
      documentPath,
      signers,
      emailSubject,
      emailMessage
    } = options;

    // Upload document first
    const documentContent = await fs.readFile(documentPath);
    const formData = new FormData();
    formData.append('File', documentContent, path.basename(documentPath));

    const uploadResponse = await this.axios.post('/transientDocuments', formData, {
      headers: {
        ...formData.getHeaders(),
        'Authorization': `Bearer ${this.config.accessToken}`
      }
    });

    const transientDocumentId = uploadResponse.data.transientDocumentId;

    // Create agreement
    const agreementInfo = {
      fileInfos: [{
        transientDocumentId
      }],
      name: emailSubject || 'Signature Request',
      participantSetsInfo: [{
        order: 1,
        role: 'SIGNER',
        memberInfos: signers.map(signer => ({
          email: signer.email,
          name: signer.name
        }))
      }],
      signatureType: 'ESIGN',
      state: 'IN_PROCESS',
      emailOption: {
        sendOptions: {
          initEmails: 'ALL'
        }
      },
      message: emailMessage || 'Please sign this document'
    };

    const agreementResponse = await this.axios.post('/agreements', agreementInfo);

    return {
      envelopeId: agreementResponse.data.id,
      status: 'sent',
      statusDateTime: new Date().toISOString()
    };
  }

  async getStatus(envelopeId) {
    const response = await this.axios.get(`/agreements/${envelopeId}`);

    return {
      envelopeId: response.data.id,
      status: response.data.status,
      createdDate: response.data.createdDate,
      participants: response.data.participantSetsInfo
    };
  }

  async downloadDocument(envelopeId, outputPath) {
    const response = await this.axios.get(
      `/agreements/${envelopeId}/combinedDocument`,
      { responseType: 'arraybuffer' }
    );

    await fs.writeFile(outputPath, response.data);

    return {
      envelopeId,
      outputPath,
      size: response.data.length,
      downloadedAt: new Date().toISOString()
    };
  }

  async sendReminder(envelopeId, signerEmail) {
    await this.axios.post(`/agreements/${envelopeId}/reminders`, {
      recipientParticipantIds: [signerEmail]
    });

    return { success: true, email: signerEmail };
  }

  async cancelEnvelope(envelopeId, reason) {
    await this.axios.put(`/agreements/${envelopeId}/state`, {
      state: 'CANCELLED',
      agreementCancellationInfo: {
        comment: reason
      }
    });

    return {
      envelopeId,
      status: 'cancelled',
      reason,
      cancelledAt: new Date().toISOString()
    };
  }

  async getAuditTrail(envelopeId) {
    const response = await this.axios.get(
      `/agreements/${envelopeId}/auditTrail`,
      { responseType: 'arraybuffer' }
    );

    return {
      envelopeId,
      certificate: response.data.toString('base64'),
      retrievedAt: new Date().toISOString()
    };
  }

  parseWebhookEvent(payload) {
    return payload.webhookNotificationId || 'unknown';
  }
}

// Example usage
async function example() {
  const service = new ESignatureService('docusign', {
    accountId: 'your-account-id',
    accessToken: 'your-access-token'
  });

  // Listen to events
  service.on('envelope:sent', (data) => {
    console.log('Envelope sent:', data.envelopeId);
  });

  service.on('error', (error) => {
    console.error('Error:', error);
  });

  // Send for signature
  const result = await service.sendForSignature({
    contractId: 'contract-123',
    documentPath: '/path/to/contract.pdf',
    signers: [
      {
        email: 'signer1@example.com',
        name: 'John Doe',
        order: 1
      },
      {
        email: 'signer2@example.com',
        name: 'Jane Smith',
        order: 2
      }
    ],
    emailSubject: 'Please sign the employment contract',
    emailMessage: 'Please review and sign the attached employment contract.',
    expirationDays: 30,
    reminderEnabled: true,
    reminderDelay: 2,
    metadata: {
      contractType: 'employment',
      department: 'HR'
    }
  });

  console.log('Envelope ID:', result.envelopeId);

  // Check status
  const status = await service.getSignatureStatus(result.envelopeId);
  console.log('Status:', status);

  // Download when complete
  if (status.status === 'completed') {
    await service.downloadSignedDocument(
      result.envelopeId,
      '/path/to/signed-contract.pdf'
    );
  }
}

module.exports = {
  ESignatureService,
  DocuSignClient,
  HelloSignClient,
  AdobeSignClient
};
