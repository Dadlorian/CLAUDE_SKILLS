# Integration APIs for Document Automation

## Overview

Integration APIs enable document automation systems to connect with practice management systems, CRM platforms, cloud storage, e-signature services, and other business applications.

## Common Integration Patterns

### 1. Practice Management Systems

**Clio**:
```python
import requests

class ClioIntegration:
    def __init__(self, access_token):
        self.base_url = "https://app.clio.com/api/v4"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

    def get_matter(self, matter_id):
        """Retrieve matter details from Clio"""
        response = requests.get(
            f"{self.base_url}/matters/{matter_id}.json",
            headers=self.headers
        )
        return response.json()

    def get_client(self, client_id):
        """Retrieve client details"""
        response = requests.get(
            f"{self.base_url}/contacts/{client_id}.json",
            headers=self.headers
        )
        return response.json()

    def upload_document(self, matter_id, document_path, document_name):
        """Upload generated document to matter"""
        with open(document_path, 'rb') as f:
            files = {'document': (document_name, f)}
            data = {
                'parent': json.dumps({
                    'type': 'Matter',
                    'id': matter_id
                })
            }

            response = requests.post(
                f"{self.base_url}/documents.json",
                headers=self.headers,
                files=files,
                data=data
            )
        return response.json()

# Usage
clio = ClioIntegration(access_token="your_token")

# Get matter data
matter = clio.get_matter(12345)
client_id = matter['data']['client']['id']
client = clio.get_client(client_id)

# Prepare data for document generation
doc_data = {
    'client_name': client['data']['name'],
    'matter_number': matter['data']['display_number'],
    'matter_description': matter['data']['description']
}

# Generate document
generated_doc = generate_document(template, doc_data)

# Upload back to Clio
clio.upload_document(12345, generated_doc, "Stock Purchase Agreement.pdf")
```

**MyCase**:
```python
class MyCaseIntegration:
    def __init__(self, firm_id, api_token):
        self.base_url = f"https://{firm_id}.mycase.com/api/v1"
        self.headers = {
            "Authorization": f"Token {api_token}",
            "Content-Type": "application/json"
        }

    def get_case(self, case_id):
        """Get case details"""
        response = requests.get(
            f"{self.base_url}/cases/{case_id}",
            headers=self.headers
        )
        return response.json()

    def create_document(self, case_id, document_data):
        """Create document in MyCase"""
        response = requests.post(
            f"{self.base_url}/cases/{case_id}/documents",
            headers=self.headers,
            files={'file': open(document_data['path'], 'rb')},
            data={
                'name': document_data['name'],
                'description': document_data['description']
            }
        )
        return response.json()
```

### 2. CRM Systems

**Salesforce**:
```python
from simple_salesforce import Salesforce

class SalesforceIntegration:
    def __init__(self, username, password, security_token):
        self.sf = Salesforce(
            username=username,
            password=password,
            security_token=security_token
        )

    def get_opportunity(self, opportunity_id):
        """Get opportunity details"""
        return self.sf.Opportunity.get(opportunity_id)

    def get_account(self, account_id):
        """Get account details"""
        return self.sf.Account.get(account_id)

    def create_content_version(self, title, file_path, description=''):
        """Upload document to Salesforce Files"""
        with open(file_path, 'rb') as f:
            file_data = base64.b64encode(f.read()).decode()

        content_version = self.sf.ContentVersion.create({
            'Title': title,
            'PathOnClient': os.path.basename(file_path),
            'VersionData': file_data,
            'Description': description
        })

        return content_version

    def link_document_to_record(self, content_version_id, record_id):
        """Link uploaded document to record (Account, Opportunity, etc.)"""

        # Get ContentDocument ID from ContentVersion
        cv = self.sf.query(f"""
            SELECT ContentDocumentId
            FROM ContentVersion
            WHERE Id = '{content_version_id}'
        """)
        content_document_id = cv['records'][0]['ContentDocumentId']

        # Create ContentDocumentLink
        link = self.sf.ContentDocumentLink.create({
            'ContentDocumentId': content_document_id,
            'LinkedEntityId': record_id,
            'ShareType': 'V'  # Viewer permission
        })

        return link

# Usage
sf = SalesforceIntegration(username, password, token)

# Get deal data
opp = sf.get_opportunity('0061234567890ABC')
account = sf.get_account(opp['AccountId'])

# Generate document
doc_data = {
    'buyer_name': account['Name'],
    'deal_value': opp['Amount'],
    'close_date': opp['CloseDate']
}
generated_doc = generate_document(template, doc_data)

# Upload to Salesforce
cv = sf.create_content_version(
    "Stock Purchase Agreement",
    generated_doc,
    f"Generated for {account['Name']}"
)

# Link to opportunity
sf.link_document_to_record(cv['id'], opp['Id'])
```

### 3. Cloud Storage

**Box**:
```python
from boxsdk import OAuth2, Client

class BoxIntegration:
    def __init__(self, client_id, client_secret, access_token):
        oauth = OAuth2(
            client_id=client_id,
            client_secret=client_secret,
            access_token=access_token
        )
        self.client = Client(oauth)

    def upload_file(self, file_path, folder_id='0'):
        """Upload file to Box"""
        folder = self.client.folder(folder_id)
        new_file = folder.upload(file_path)
        return new_file

    def create_folder(self, folder_name, parent_folder_id='0'):
        """Create folder in Box"""
        parent = self.client.folder(parent_folder_id)
        subfolder = parent.create_subfolder(folder_name)
        return subfolder

    def share_file(self, file_id, email, access_level='viewer'):
        """Share file with user"""
        file = self.client.file(file_id)
        collaboration = file.collaborate(
            email,
            access_level
        )
        return collaboration
```

**Dropbox**:
```python
import dropbox

class DropboxIntegration:
    def __init__(self, access_token):
        self.dbx = dropbox.Dropbox(access_token)

    def upload_file(self, file_path, dropbox_path):
        """Upload file to Dropbox"""
        with open(file_path, 'rb') as f:
            self.dbx.files_upload(
                f.read(),
                dropbox_path,
                mode=dropbox.files.WriteMode.overwrite
            )

    def create_shared_link(self, path):
        """Create shared link for file"""
        shared_link = self.dbx.sharing_create_shared_link_with_settings(
            path
        )
        return shared_link.url

    def share_folder(self, folder_path, email):
        """Share folder with user"""
        self.dbx.sharing_share_folder(
            folder_path,
            members=[dropbox.sharing.AddMember(
                member=dropbox.sharing.MemberSelector.email(email),
                access_level=dropbox.sharing.AccessLevel.viewer
            )]
        )
```

### 4. E-Signature Services

**DocuSign**:
```python
from docusign_esign import ApiClient, EnvelopesApi, EnvelopeDefinition, Document, Signer, SignHere, Tabs, Recipients

class DocuSignIntegration:
    def __init__(self, integrator_key, user_id, base_url, private_key_path):
        self.api_client = ApiClient()
        self.api_client.host = base_url
        self.api_client.set_oauth_host_name(base_url)

        # Authenticate with JWT
        self.access_token = self.api_client.request_jwt_user_token(
            client_id=integrator_key,
            user_id=user_id,
            oauth_host_name=base_url,
            private_key_bytes=open(private_key_path, 'rb').read(),
            expires_in=3600
        )

    def send_for_signature(self, document_path, signers, email_subject):
        """Send document for signature"""

        # Read document
        with open(document_path, 'rb') as file:
            content_bytes = file.read()
        base64_file_content = base64.b64encode(content_bytes).decode('ascii')

        # Create document
        document = Document(
            document_base64=base64_file_content,
            name='Stock Purchase Agreement',
            file_extension='pdf',
            document_id='1'
        )

        # Create signers
        signer_objects = []
        for idx, signer_info in enumerate(signers, start=1):
            # Create sign here tab
            sign_here = SignHere(
                document_id='1',
                page_number='1',
                recipient_id=str(idx),
                tab_label=f'Signature{idx}',
                x_position='100',
                y_position='200'
            )

            tabs = Tabs(sign_here_tabs=[sign_here])

            signer = Signer(
                email=signer_info['email'],
                name=signer_info['name'],
                recipient_id=str(idx),
                tabs=tabs
            )
            signer_objects.append(signer)

        # Create envelope
        envelope_definition = EnvelopeDefinition(
            email_subject=email_subject,
            documents=[document],
            recipients=Recipients(signers=signer_objects),
            status='sent'
        )

        # Send envelope
        envelopes_api = EnvelopesApi(self.api_client)
        results = envelopes_api.create_envelope(
            account_id=self.account_id,
            envelope_definition=envelope_definition
        )

        return results

# Usage
docusign = DocuSignIntegration(integrator_key, user_id, base_url, private_key_path)

signers = [
    {'name': 'John Smith', 'email': 'john@buyer.com'},
    {'name': 'Jane Doe', 'email': 'jane@seller.com'}
]

envelope = docusign.send_for_signature(
    'stock_purchase_agreement.pdf',
    signers,
    'Please sign: Stock Purchase Agreement'
)
```

**Adobe Sign**:
```python
class AdobeSignIntegration:
    def __init__(self, access_token, api_url):
        self.access_token = access_token
        self.api_url = api_url
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

    def upload_transient_document(self, file_path):
        """Upload document to Adobe Sign"""
        with open(file_path, 'rb') as f:
            files = {'File': (os.path.basename(file_path), f)}
            response = requests.post(
                f"{self.api_url}/transientDocuments",
                headers={'Authorization': f'Bearer {self.access_token}'},
                files=files
            )
        return response.json()['transientDocumentId']

    def create_agreement(self, transient_doc_id, signers, agreement_name):
        """Create signing agreement"""
        data = {
            'fileInfos': [{
                'transientDocumentId': transient_doc_id
            }],
            'name': agreement_name,
            'participantSetsInfo': [{
                'memberInfos': [{'email': signer['email']} for signer in signers],
                'order': 1,
                'role': 'SIGNER'
            }],
            'signatureType': 'ESIGN',
            'state': 'IN_PROCESS'
        }

        response = requests.post(
            f"{self.api_url}/agreements",
            headers=self.headers,
            json=data
        )
        return response.json()
```

### 5. Payment Processing

**Stripe**:
```python
import stripe

class StripeIntegration:
    def __init__(self, api_key):
        stripe.api_key = api_key

    def create_payment_intent(self, amount, currency='usd', description=''):
        """Create payment intent"""
        intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),  # Amount in cents
            currency=currency,
            description=description,
            metadata={
                'document_type': 'Stock Purchase Agreement',
                'matter_id': '12345'
            }
        )
        return intent

    def create_invoice(self, customer_id, items):
        """Create invoice for document generation"""
        # Create invoice
        invoice = stripe.Invoice.create(
            customer=customer_id,
            auto_advance=True
        )

        # Add line items
        for item in items:
            stripe.InvoiceItem.create(
                customer=customer_id,
                invoice=invoice.id,
                amount=int(item['amount'] * 100),
                currency='usd',
                description=item['description']
            )

        # Finalize invoice
        stripe.Invoice.finalize_invoice(invoice.id)

        return invoice
```

### 6. Document Assembly API

**Custom REST API**:
```python
from flask import Flask, request, jsonify, send_file
from werkzeug.security import check_password_hash
import jwt
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'

def token_required(f):
    """Decorator for API authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({'message': 'Token is missing'}), 401

        try:
            token = token.split()[1]  # Remove 'Bearer '
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = get_user(data['user_id'])
        except:
            return jsonify({'message': 'Token is invalid'}), 401

        return f(current_user, *args, **kwargs)

    return decorated

@app.route('/api/v1/auth/login', methods=['POST'])
def login():
    """Authenticate and get token"""
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return jsonify({'message': 'Could not verify'}), 401

    user = get_user_by_username(auth.username)

    if not user or not check_password_hash(user.password, auth.password):
        return jsonify({'message': 'Could not verify'}), 401

    token = jwt.encode({
        'user_id': user.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }, app.config['SECRET_KEY'])

    return jsonify({'token': token})

@app.route('/api/v1/templates', methods=['GET'])
@token_required
def get_templates(current_user):
    """List available templates"""
    templates = Template.query.filter_by(
        organization_id=current_user.organization_id
    ).all()

    return jsonify({
        'templates': [{
            'id': t.id,
            'name': t.name,
            'description': t.description,
            'version': t.version
        } for t in templates]
    })

@app.route('/api/v1/documents/generate', methods=['POST'])
@token_required
def generate_document(current_user):
    """Generate document from template"""
    data = request.json

    template_id = data.get('template_id')
    answers = data.get('answers')
    output_format = data.get('output_format', 'pdf')

    # Validate template access
    template = Template.query.get(template_id)
    if not template or template.organization_id != current_user.organization_id:
        return jsonify({'message': 'Template not found'}), 404

    # Generate document
    try:
        output_path = generate_document_from_template(
            template,
            answers,
            output_format
        )

        # Store generation record
        doc_record = DocumentGeneration(
            template_id=template_id,
            user_id=current_user.id,
            output_path=output_path,
            timestamp=datetime.datetime.utcnow()
        )
        db.session.add(doc_record)
        db.session.commit()

        # Return document or download URL
        if request.args.get('return_file'):
            return send_file(output_path, as_attachment=True)
        else:
            download_url = generate_download_url(doc_record.id)
            return jsonify({
                'document_id': doc_record.id,
                'download_url': download_url,
                'expires_at': (datetime.datetime.utcnow() + datetime.timedelta(hours=24)).isoformat()
            })

    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/api/v1/documents/<int:document_id>', methods=['GET'])
@token_required
def get_document(current_user, document_id):
    """Download generated document"""
    doc = DocumentGeneration.query.get(document_id)

    if not doc or doc.user.organization_id != current_user.organization_id:
        return jsonify({'message': 'Document not found'}), 404

    return send_file(doc.output_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=False)
```

## Webhooks

**Receiving Webhooks**:
```python
from flask import Flask, request
import hmac
import hashlib

@app.route('/webhooks/docusign', methods=['POST'])
def docusign_webhook():
    """Handle DocuSign webhook"""

    # Verify signature
    signature = request.headers.get('X-DocuSign-Signature')
    if not verify_docusign_signature(request.data, signature):
        return 'Invalid signature', 401

    # Process event
    event = request.json

    if event['event'] == 'envelope-completed':
        envelope_id = event['data']['envelopeId']
        # Download signed document
        download_signed_document(envelope_id)
        # Update status in database
        update_document_status(envelope_id, 'signed')

    return '', 200

def verify_docusign_signature(payload, signature):
    """Verify webhook signature"""
    secret = os.environ.get('DOCUSIGN_WEBHOOK_SECRET')
    expected_signature = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(signature, expected_signature)
```

## Best Practices

1. **Authentication**: Use OAuth 2.0, not API keys when possible
2. **Rate Limiting**: Implement exponential backoff
3. **Error Handling**: Handle API errors gracefully
4. **Logging**: Log all API interactions
5. **Caching**: Cache frequently accessed data
6. **Webhooks**: Use webhooks instead of polling
7. **Security**: Never expose credentials in code
8. **Testing**: Test integrations in sandbox environments
9. **Documentation**: Document all integration points
10. **Monitoring**: Monitor API usage and errors

Integration APIs enable powerful workflows connecting document automation with the broader legal technology ecosystem.
