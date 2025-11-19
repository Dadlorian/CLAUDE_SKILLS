"""
DocuSign API Integration - Handle e-signature workflows
Integrates with DocuSign for contract signing and tracking
"""

import requests
import json
from typing import Dict, List
from datetime import datetime, timedelta
import base64

class DocuSignIntegration:
    """Handle DocuSign e-signature integration"""
    
    BASE_URL = "https://demo.docusign.net/restapi"  # Demo URL, use prod for production
    
    def __init__(self, client_id: str, client_secret: str, account_id: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.account_id = account_id
        self.access_token = None
        self.token_expires_at = None
    
    def authenticate(self) -> str:
        """Get OAuth access token from DocuSign"""
        auth_url = f"{self.BASE_URL}/oauth/token"
        
        auth_header = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode()
        ).decode()
        
        headers = {
            'Authorization': f'Basic {auth_header}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'grant_type': 'client_credentials',
            'scope': 'signature'
        }
        
        response = requests.post(auth_url, headers=headers, data=data)
        result = response.json()
        
        self.access_token = result['access_token']
        self.token_expires_at = datetime.now() + timedelta(seconds=result['expires_in'])
        
        return self.access_token
    
    def create_envelope(self, document_path: str, recipients: List[Dict]) -> Dict:
        """Create and send envelope for signing"""
        
        if not self.access_token or datetime.now() >= self.token_expires_at:
            self.authenticate()
        
        # Read document
        with open(document_path, 'rb') as f:
            document_content = base64.b64encode(f.read()).decode()
        
        # Prepare envelope
        envelope_definition = {
            "emailSubject": "Contract Review and Signature",
            "documents": [
                {
                    "documentId": "1",
                    "name": "Contract",
                    "fileExtension": "pdf",
                    "documentBase64": document_content
                }
            ],
            "recipients": {
                "signers": [
                    {
                        "email": recipient['email'],
                        "name": recipient['name'],
                        "recipientId": str(i + 1),
                        "routingOrder": str(i + 1),
                        "tabs": {
                            "signHereTabs": [
                                {
                                    "documentId": "1",
                                    "pageNumber": recipient.get('sign_page', "1"),
                                    "xPosition": "100",
                                    "yPosition": "100"
                                }
                            ],
                            "initialHereTabs": [
                                {
                                    "documentId": "1",
                                    "pageNumber": recipient.get('initial_page', "1"),
                                    "xPosition": "50",
                                    "yPosition": "50"
                                }
                            ]
                        }
                    }
                    for i, recipient in enumerate(recipients)
                ]
            },
            "status": "sent"
        }
        
        # Create envelope
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        url = f"{self.BASE_URL}/v2.1/accounts/{self.account_id}/envelopes"
        response = requests.post(url, json=envelope_definition, headers=headers)
        
        result = response.json()
        return {
            'envelope_id': result.get('envelopeId'),
            'status': result.get('status'),
            'uri': result.get('uri'),
            'created_at': datetime.now().isoformat()
        }
    
    def get_envelope_status(self, envelope_id: str) -> Dict:
        """Check envelope signing status"""
        
        if not self.access_token or datetime.now() >= self.token_expires_at:
            self.authenticate()
        
        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }
        
        url = f"{self.BASE_URL}/v2.1/accounts/{self.account_id}/envelopes/{envelope_id}"
        response = requests.get(url, headers=headers)
        
        result = response.json()
        return {
            'envelope_id': result.get('envelopeId'),
            'status': result.get('status'),
            'sent_date': result.get('sentDateTime'),
            'completed_date': result.get('completedDateTime'),
            'signers': [
                {
                    'name': signer.get('name'),
                    'email': signer.get('email'),
                    'status': signer.get('status'),
                    'signed_date': signer.get('signedDateTime')
                }
                for signer in result.get('recipients', {}).get('signers', [])
            ]
        }
    
    def download_signed_document(self, envelope_id: str, document_id: str = "1") -> bytes:
        """Download signed document"""
        
        if not self.access_token or datetime.now() >= self.token_expires_at:
            self.authenticate()
        
        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }
        
        url = f"{self.BASE_URL}/v2.1/accounts/{self.account_id}/envelopes/{envelope_id}/documents/{document_id}"
        response = requests.get(url, headers=headers)
        
        return response.content
    
    def send_reminder(self, envelope_id: str) -> Dict:
        """Send signing reminder to unsigned signers"""
        
        if not self.access_token or datetime.now() >= self.token_expires_at:
            self.authenticate()
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        url = f"{self.BASE_URL}/v2.1/accounts/{self.account_id}/envelopes/{envelope_id}/recipients/signers"
        data = {"resend_envelope": "true"}
        
        response = requests.put(url, json=data, headers=headers)
        return response.json()


# Example usage
if __name__ == "__main__":
    docusign = DocuSignIntegration(
        client_id="YOUR_CLIENT_ID",
        client_secret="YOUR_CLIENT_SECRET",
        account_id="YOUR_ACCOUNT_ID"
    )
    
    # Authenticate
    token = docusign.authenticate()
    print(f"Token: {token[:20]}...")
    
    # Create envelope for signing
    recipients = [
        {'email': 'vendor@company.com', 'name': 'Vendor Contact'},
        {'email': 'legal@ourcompany.com', 'name': 'Legal Review'}
    ]
    
    envelope = docusign.create_envelope("contract.pdf", recipients)
    print(f"Envelope created: {envelope['envelope_id']}")
    
    # Check status
    status = docusign.get_envelope_status(envelope['envelope_id'])
    print(f"Status: {status['status']}")
