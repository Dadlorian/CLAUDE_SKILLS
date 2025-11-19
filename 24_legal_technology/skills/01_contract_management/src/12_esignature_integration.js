/**
 * E-Signature Integration - Integrate with e-signature services
 * Supports DocuSign, HelloSign, etc.
 */

class ESignatureService {
  constructor(provider = 'docusign', config = {}) {
    this.provider = provider;
    this.config = config;
    this.client = this.initializeClient();
  }

  initializeClient() {
    switch (this.provider) {
      case 'docusign':
        return new DocuSignClient(this.config);
      case 'hellosign':
        return new HelloSignClient(this.config);
      default:
        throw new Error(`Unknown provider: ${this.provider}`);
    }
  }

  async sendForSignature(contractId, documentPath, signers) {
    return this.client.sendForSignature(contractId, documentPath, signers);
  }

  async getSignatureStatus(envelopeId) {
    return this.client.getStatus(envelopeId);
  }

  async downloadSignedDocument(envelopeId) {
    return this.client.downloadDocument(envelopeId);
  }

  async remindSigner(envelopeId, signerEmail) {
    return this.client.sendReminder(envelopeId, signerEmail);
  }
}

module.exports = { ESignatureService };
