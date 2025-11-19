#!/usr/bin/env python3
"""
Data Subject Access Request (DSAR) Automation
Retrieves personal data from multiple systems for GDPR/CCPA compliance
"""

import json
import requests
from datetime import datetime
import hashlib
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import zipfile
import io

class DSARProcessor:
    """Process Data Subject Access Requests"""
    
    def __init__(self, config):
        self.config = config
        self.data_sources = []
        
    def verify_identity(self, request_data):
        """Verify requester identity"""
        email = request_data.get('email')
        verification_code = request_data.get('verification_code')
        
        # Check verification code (sent via email)
        expected_code = self._generate_verification_code(email)
        
        if verification_code == expected_code:
            return True
        else:
            # Could implement additional verification (KBA, ID upload, etc.)
            return False
    
    def collect_personal_data(self, user_email):
        """Collect personal data from all systems"""
        data_package = {}
        
        # CRM Data (Salesforce)
        data_package['crm'] = self._get_salesforce_data(user_email)
        
        # Marketing Data (HubSpot)
        data_package['marketing'] = self._get_hubspot_data(user_email)
        
        # Support Tickets (Zendesk)
        data_package['support'] = self._get_zendesk_data(user_email)
        
        # Application Database
        data_package['application'] = self._get_app_database_data(user_email)
        
        # Analytics (Google Analytics)
        data_package['analytics'] = self._get_analytics_data(user_email)
        
        return data_package
    
    def _get_salesforce_data(self, email):
        """Retrieve data from Salesforce"""
        # Use Salesforce API
        sf_api_url = self.config['salesforce']['api_url']
        sf_token = self.config['salesforce']['access_token']
        
        headers = {
            'Authorization': f'Bearer {sf_token}',
            'Content-Type': 'application/json'
        }
        
        # Query for contact and related records
        query = f"SELECT Id, FirstName, LastName, Email, Phone, Account.Name FROM Contact WHERE Email = '{email}'"
        
        response = requests.get(
            f"{sf_api_url}/query/?q={query}",
            headers=headers
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {'error': 'Failed to retrieve Salesforce data'}
    
    def _get_hubspot_data(self, email):
        """Retrieve marketing data from HubSpot"""
        hs_api_key = self.config['hubspot']['api_key']
        
        # Get contact by email
        url = f"https://api.hubapi.com/contacts/v1/contact/email/{email}/profile"
        params = {'hapikey': hs_api_key}
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            contact = response.json()
            
            # Get associated emails, forms, lists
            contact_data = {
                'profile': contact,
                'email_subscriptions': self._get_hubspot_subscriptions(contact['vid']),
                'form_submissions': self._get_hubspot_forms(contact['vid'])
            }
            return contact_data
        else:
            return {'error': 'Contact not found in HubSpot'}
    
    def _get_hubspot_subscriptions(self, contact_id):
        """Get email subscription status"""
        # Implementation would query HubSpot subscription API
        return {}
    
    def _get_hubspot_forms(self, contact_id):
        """Get form submission history"""
        # Implementation would query HubSpot forms API
        return []
    
    def _get_zendesk_data(self, email):
        """Retrieve support tickets from Zendesk"""
        zd_url = self.config['zendesk']['url']
        zd_token = self.config['zendesk']['api_token']
        zd_email = self.config['zendesk']['email']
        
        headers = {
            'Content-Type': 'application/json',
        }
        
        # Search for user
        response = requests.get(
            f"{zd_url}/api/v2/users/search.json?query={email}",
            auth=(f"{zd_email}/token", zd_token),
            headers=headers
        )
        
        if response.status_code == 200 and response.json()['users']:
            user_id = response.json()['users'][0]['id']
            
            # Get user's tickets
            tickets_response = requests.get(
                f"{zd_url}/api/v2/users/{user_id}/tickets/requested.json",
                auth=(f"{zd_email}/token", zd_token)
            )
            
            return tickets_response.json() if tickets_response.status_code == 200 else {}
        else:
            return {'error': 'User not found in Zendesk'}
    
    def _get_app_database_data(self, email):
        """Retrieve data from application database"""
        # Connect to database and query user data
        # This is a placeholder - actual implementation would use database connection
        return {
            'user_profile': {},
            'orders': [],
            'preferences': {},
            'activity_log': []
        }
    
    def _get_analytics_data(self, email):
        """Retrieve analytics data (if tracked by email)"""
        # Most analytics are cookie-based, but if email is stored:
        return {
            'page_views': [],
            'events': [],
            'note': 'Analytics data is primarily cookie-based and not tied to email'
        }
    
    def generate_data_package(self, data_package, user_email):
        """Generate downloadable data package"""
        # Create ZIP file in memory
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add JSON file for each data source
            for source, data in data_package.items():
                json_data = json.dumps(data, indent=2)
                zip_file.writestr(f"{source}_data.json", json_data)
            
            # Add summary/index file
            summary = {
                'request_date': datetime.now().isoformat(),
                'user_email': user_email,
                'data_sources': list(data_package.keys()),
                'note': 'This package contains all personal data we hold about you.'
            }
            zip_file.writestr('README.json', json.dumps(summary, indent=2))
        
        zip_buffer.seek(0)
        return zip_buffer
    
    def deliver_data_package(self, user_email, zip_buffer):
        """Send data package to user via secure email"""
        msg = MIMEMultipart()
        msg['From'] = self.config['email']['from_address']
        msg['To'] = user_email
        msg['Subject'] = 'Your Personal Data Package'
        
        body = """
        Dear User,
        
        As requested, please find attached your personal data package.
        This ZIP file contains all personal information we hold about you.
        
        If you have any questions, please contact our privacy team at privacy@company.com
        
        Best regards,
        Privacy Team
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Attach ZIP file
        attachment = MIMEApplication(zip_buffer.getvalue())
        attachment.add_header('Content-Disposition', 'attachment', 
                            filename=f'personal_data_{datetime.now().strftime("%Y%m%d")}.zip')
        msg.attach(attachment)
        
        # Send email
        with smtplib.SMTP(self.config['email']['smtp_server'], 587) as server:
            server.starttls()
            server.login(self.config['email']['username'], self.config['email']['password'])
            server.send_message(msg)
        
        print(f"Data package sent to {user_email}")
    
    def process_dsar(self, request_data):
        """Main DSAR processing workflow"""
        user_email = request_data['email']
        
        # Step 1: Verify identity
        if not self.verify_identity(request_data):
            return {'status': 'error', 'message': 'Identity verification failed'}
        
        # Step 2: Collect data from all sources
        print(f"Collecting data for {user_email}...")
        data_package = self.collect_personal_data(user_email)
        
        # Step 3: Generate data package
        print("Generating data package...")
        zip_buffer = self.generate_data_package(data_package, user_email)
        
        # Step 4: Deliver to user
        print("Delivering data package...")
        self.deliver_data_package(user_email, zip_buffer)
        
        # Step 5: Log request for audit trail
        self._log_dsar_completion(user_email)
        
        return {'status': 'success', 'message': 'DSAR completed', 'completion_date': datetime.now().isoformat()}
    
    def _generate_verification_code(self, email):
        """Generate verification code for identity verification"""
        # In production, this would be stored and sent via email
        secret = self.config.get('verification_secret', 'default_secret')
        return hashlib.sha256(f"{email}{secret}".encode()).hexdigest()[:6].upper()
    
    def _log_dsar_completion(self, user_email):
        """Log DSAR for audit trail"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'email': user_email,
            'request_type': 'access',
            'status': 'completed'
        }
        
        # Write to audit log
        with open('dsar_audit.log', 'a') as f:
            f.write(json.dumps(log_entry) + '\n')

# Example usage
if __name__ == '__main__':
    config = {
        'salesforce': {
            'api_url': 'https://instance.salesforce.com/services/data/v54.0',
            'access_token': 'your_sf_token'
        },
        'hubspot': {
            'api_key': 'your_hs_key'
        },
        'zendesk': {
            'url': 'https://yourcompany.zendesk.com',
            'email': 'admin@company.com',
            'api_token': 'your_zd_token'
        },
        'email': {
            'smtp_server': 'smtp.gmail.com',
            'username': 'privacy@company.com',
            'password': 'email_password',
            'from_address': 'privacy@company.com'
        },
        'verification_secret': 'random_secret_key'
    }
    
    processor = DSARProcessor(config)
    
    # Example DSAR request
    request = {
        'email': 'customer@example.com',
        'verification_code': '123456',  # Would be sent via email first
        'request_type': 'access'
    }
    
    result = processor.process_dsar(request)
    print(result)
