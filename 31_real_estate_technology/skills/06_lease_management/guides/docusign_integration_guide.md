# DocuSign Integration Guide

## Setup
```bash
npm install docusign-esign
```

## Authentication
```javascript
const docusign = require('docusign-esign');

const apiClient = new docusign.ApiClient();
apiClient.setBasePath('https://demo.docusign.net/restapi');
apiClient.addDefaultHeader('Authorization', `Bearer ${access_token}`);
```

## Create Envelope
```javascript
async function sendLeaseForSignature(lease) {
  const envelope = new docusign.EnvelopeDefinition();
  envelope.emailSubject = 'Please sign your lease';
  envelope.templateId = LEASE_TEMPLATE_ID;
  
  // Add signers
  const signer = docusign.TemplateRole.constructFromObject({
    email: lease.tenant_email,
    name: lease.tenant_name,
    roleName: 'Tenant'
  });
  
  envelope.templateRoles = [signer];
  envelope.status = 'sent';
  
  const envelopesApi = new docusign.EnvelopesApi(apiClient);
  return await envelopesApi.createEnvelope(accountId, {
    envelopeDefinition: envelope
  });
}
```

## Webhook Notifications
```javascript
app.post('/webhooks/docusign', (req, res) => {
  const event = req.body;
  
  if (event.event === 'envelope-completed') {
    // Update lease status
    updateLeaseStatus(event.envelopeId, 'signed');
  }
  
  res.send('OK');
});
```

## See Also
- lease_creation_workflow.md
