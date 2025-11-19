#!/usr/bin/env python3
"""
Direct Protocol Client
Production-grade implementation for sending/receiving Direct secure email
"""

import smtplib
import imaplib
import ssl
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Dict, Optional
import os
import logging

logger = logging.getLogger(__name__)

class DirectClient:
    """Client for Direct Protocol secure email"""

    def __init__(self, direct_address: str, password: str, hisp_server: str, smtp_port: int = 465):
        self.direct_address = direct_address
        self.password = password
        self.hisp_server = hisp_server
        self.smtp_port = smtp_port
        self.imap_port = 993

    def send_message(self, recipient_direct_address: str, subject: str, body: str,
                    attachments: Optional[List[tuple]] = None) -> bool:
        """Send Direct secure email"""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.direct_address
            msg['To'] = recipient_direct_address
            msg['Subject'] = subject

            # Add body
            msg.attach(MIMEText(body, 'plain'))

            # Add attachments
            if attachments:
                for filename, file_data in attachments:
                    self._attach_file(msg, filename, file_data)

            # Create TLS connection
            context = ssl.create_default_context()

            with smtplib.SMTP_SSL(self.hisp_server, self.smtp_port, context=context) as server:
                server.login(self.direct_address, self.password)
                server.send_message(msg)

            logger.info(f"Message sent to {recipient_direct_address}")
            return True

        except smtplib.SMTPException as e:
            logger.error(f"SMTP error: {e}")
            return False
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return False

    def receive_messages(self, max_messages: int = 10) -> List[Dict]:
        """Receive Direct secure email messages"""
        messages = []

        try:
            # Create IMAP connection
            imap = imaplib.IMAP4_SSL(self.hisp_server, self.imap_port)
            imap.login(self.direct_address, self.password)
            imap.select('INBOX')

            # Search for messages
            status, message_ids = imap.search(None, 'ALL')

            if status != 'OK':
                return messages

            # Fetch messages
            for msg_id in message_ids[0].split()[-max_messages:]:
                status, msg_data = imap.fetch(msg_id, '(RFC822)')

                if status != 'OK':
                    continue

                # Parse message
                msg = email.message_from_bytes(msg_data[0][1])

                message_info = {
                    'from': msg['From'],
                    'to': msg['To'],
                    'subject': msg['Subject'],
                    'date': msg['Date'],
                    'body': self._extract_body(msg),
                    'attachments': self._extract_attachments(msg)
                }

                messages.append(message_info)

            imap.close()
            imap.logout()

            logger.info(f"Retrieved {len(messages)} messages")
            return messages

        except imaplib.IMAP4.error as e:
            logger.error(f"IMAP error: {e}")
            return []
        except Exception as e:
            logger.error(f"Error receiving messages: {e}")
            return []

    def send_with_retry(self, recipient: str, subject: str, body: str,
                       attachments: Optional[List[tuple]] = None,
                       max_retries: int = 3, retry_delay: int = 5) -> bool:
        """Send with retry logic"""
        import time

        for attempt in range(1, max_retries + 1):
            try:
                if self.send_message(recipient, subject, body, attachments):
                    return True

            except Exception as e:
                logger.warning(f"Attempt {attempt} failed: {e}")

                if attempt < max_retries:
                    time.sleep(retry_delay)
                    continue

        logger.error(f"Failed to send after {max_retries} attempts")
        return False

    def mark_message_as_read(self, message_id: str) -> bool:
        """Mark message as read"""
        try:
            imap = imaplib.IMAP4_SSL(self.hisp_server, self.imap_port)
            imap.login(self.direct_address, self.password)
            imap.select('INBOX')

            imap.store(message_id, '+FLAGS', '\\Seen')

            imap.close()
            imap.logout()

            return True

        except Exception as e:
            logger.error(f"Error marking message: {e}")
            return False

    def delete_message(self, message_id: str) -> bool:
        """Delete message"""
        try:
            imap = imaplib.IMAP4_SSL(self.hisp_server, self.imap_port)
            imap.login(self.direct_address, self.password)
            imap.select('INBOX')

            imap.store(message_id, '+FLAGS', '\\Deleted')
            imap.expunge()

            imap.close()
            imap.logout()

            return True

        except Exception as e:
            logger.error(f"Error deleting message: {e}")
            return False

    def _attach_file(self, msg: MIMEMultipart, filename: str, file_data: bytes):
        """Attach file to message"""
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(file_data)
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename= {os.path.basename(filename)}')
        msg.attach(part)

    def _extract_body(self, msg) -> str:
        """Extract message body"""
        body = ''

        if msg.is_multipart():
            for part in msg.get_payload():
                if part.get_content_type() == 'text/plain':
                    body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    break
        else:
            body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')

        return body

    def _extract_attachments(self, msg) -> List[Dict]:
        """Extract attachments from message"""
        attachments = []

        if msg.is_multipart():
            for part in msg.get_payload():
                if part.get_content_disposition() == 'attachment':
                    filename = part.get_filename()
                    if filename:
                        attachments.append({
                            'filename': filename,
                            'data': part.get_payload(decode=True)
                        })

        return attachments


class DirectDirectoryService:
    """Look up Direct addresses"""

    def __init__(self):
        self.cache = {}

    def resolve_address(self, direct_address: str) -> Optional[Dict]:
        """Resolve Direct address to certificates and metadata"""
        # In production, query official Direct directory
        # This is a placeholder

        if direct_address in self.cache:
            return self.cache[direct_address]

        # Query LDAP or HTTP-based directory
        # Return certificate and metadata

        return None

    def cache_address(self, direct_address: str, metadata: Dict):
        """Cache address metadata"""
        self.cache[direct_address] = metadata


if __name__ == '__main__':
    # Example usage
    client = DirectClient(
        direct_address='provider@hospital.direct',
        password='your_password',
        hisp_server='direct.hisp.com'
    )

    # Send message
    result = client.send_message(
        recipient_direct_address='specialist@clinic.direct',
        subject='Patient Referral',
        body='Please find attached referral document',
        attachments=[('referral.pdf', b'PDF data here')]
    )

    print(f"Send result: {result}")

    # Receive messages
    messages = client.receive_messages(max_messages=5)
    print(f"Received {len(messages)} messages")

    for msg in messages:
        print(f"From: {msg['from']}")
        print(f"Subject: {msg['subject']}")
