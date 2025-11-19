"""
Email Threading Example
Demonstrates email conversation threading for efficient review
"""

from typing import List, Dict, Set, Tuple
from collections import defaultdict
import re

class EmailThreader:
    """Groups related emails into conversation threads"""

    def __init__(self):
        """Initialize email threader"""
        self.threads = {}
        self.email_to_thread = {}

    def thread_emails(self, emails: List[Dict]) -> Dict[int, List[Dict]]:
        """
        Group emails into conversation threads

        Args:
            emails: List of email dicts with required fields:
                - email_id: Unique identifier
                - message_id: RFC 2822 Message-ID
                - in_reply_to: Message-ID being replied to
                - references: List of referenced message IDs
                - subject: Email subject
                - date: Timestamp
                - from: Sender address
                - to: Recipient list

        Returns:
            Dict mapping thread_id to list of email dicts
        """
        threads = {}
        thread_id_counter = 0
        message_to_thread = {}  # message_id -> thread_id

        # First pass: create threads based on references
        for email in emails:
            message_id = email.get('message_id')
            references = email.get('references', [])

            # Find if any referenced message belongs to a thread
            existing_thread = None
            for ref_id in references:
                if ref_id in message_to_thread:
                    existing_thread = message_to_thread[ref_id]
                    break

            if existing_thread is None:
                # Create new thread
                existing_thread = thread_id_counter
                thread_id_counter += 1
                threads[existing_thread] = []

            # Assign email to thread
            message_to_thread[message_id] = existing_thread
            threads[existing_thread].append(email)

        # Sort emails within each thread by date
        for thread_id in threads:
            threads[thread_id].sort(key=lambda x: x.get('date', ''))

        return threads

    def get_thread_summary(self, thread: List[Dict]) -> Dict:
        """
        Generate summary for email thread

        Args:
            thread: List of emails in thread

        Returns:
            Summary dictionary with key information
        """
        if not thread:
            return {}

        # Get first and last email
        first_email = thread[0]
        last_email = thread[-1]

        # Extract participants
        participants = set()
        for email in thread:
            participants.add(email.get('from', ''))
            participants.update(email.get('to', []))
            participants.update(email.get('cc', []))

        # Clean subject line
        subject = self._clean_subject(first_email.get('subject', ''))

        return {
            "subject": subject,
            "thread_length": len(thread),
            "start_date": first_email.get('date'),
            "end_date": last_email.get('date'),
            "participants": list(participants),
            "email_ids": [email.get('email_id') for email in thread],
            "custodians": list(set(email.get('custodian', '') for email in thread))
        }

    @staticmethod
    def _clean_subject(subject: str) -> str:
        """Remove RE:, FW: prefixes from subject"""
        cleaned = re.sub(r'^(RE:|FW:|\[FW\]|\[RE\])+\s*', '', subject, flags=re.IGNORECASE)
        return cleaned.strip()

    def get_significant_emails(self, thread: List[Dict],
                              sample_size: int = 3) -> List[Dict]:
        """
        Select representative emails from thread for focused review

        Args:
            thread: List of emails in thread
            sample_size: Number of emails to select

        Returns:
            List of selected emails
        """
        if len(thread) <= sample_size:
            return thread

        # Return first, last, and middle emails
        selected = [thread[0], thread[-1]]

        if sample_size > 2:
            mid_index = len(thread) // 2
            selected.append(thread[mid_index])

        return selected

    def identify_key_participants(self, thread: List[Dict]) -> Dict[str, int]:
        """
        Identify most active participants in thread

        Args:
            thread: List of emails

        Returns:
            Dict mapping email address to message count
        """
        participant_count = defaultdict(int)

        for email in thread:
            participant_count[email.get('from', '')] += 1

        return dict(sorted(participant_count.items(),
                          key=lambda x: x[1], reverse=True))


class ConversationExtractor:
    """Extracts conversation context and threads"""

    @staticmethod
    def get_unique_content(email: Dict) -> str:
        """
        Extract unique content from email (not quoted text)

        Args:
            email: Email dictionary

        Returns:
            Unique content string
        """
        body = email.get('body', '')

        # Remove quoted text patterns
        lines = body.split('\n')
        unique_lines = []

        for line in lines:
            # Skip lines that look like quoted text
            if not line.startswith('>') and not line.startswith('|'):
                unique_lines.append(line)

        return '\n'.join(unique_lines).strip()

    @staticmethod
    def build_conversation_tree(thread: List[Dict]) -> Dict:
        """
        Build hierarchical conversation tree

        Args:
            thread: List of emails in thread

        Returns:
            Tree structure with nested replies
        """
        message_map = {}
        roots = []

        # Build message map
        for email in thread:
            message_map[email.get('message_id')] = {
                "email": email,
                "children": []
            }

        # Build parent-child relationships
        for email in thread:
            in_reply_to = email.get('in_reply_to')

            if in_reply_to and in_reply_to in message_map:
                message_map[in_reply_to]["children"].append(
                    message_map[email.get('message_id')]
                )
            else:
                roots.append(message_map[email.get('message_id')])

        return {
            "root_count": len(roots),
            "roots": roots,
            "total_messages": len(thread)
        }

    @staticmethod
    def get_thread_statistics(thread: List[Dict]) -> Dict:
        """
        Calculate statistics about thread

        Args:
            thread: List of emails

        Returns:
            Statistics dictionary
        """
        if not thread:
            return {}

        # Calculate metrics
        word_counts = [len(email.get('body', '').split()) for email in thread]
        avg_words = sum(word_counts) / len(word_counts) if word_counts else 0

        # Identify attachment status
        attachments = sum(1 for email in thread if email.get('has_attachments', False))

        return {
            "message_count": len(thread),
            "avg_message_length": int(avg_words),
            "max_message_length": max(word_counts) if word_counts else 0,
            "messages_with_attachments": attachments,
            "date_range": {
                "start": thread[0].get('date'),
                "end": thread[-1].get('date')
            }
        }


# Example usage
if __name__ == "__main__":
    # Sample emails
    emails = [
        {
            "email_id": 1,
            "message_id": "<original@example.com>",
            "in_reply_to": None,
            "references": [],
            "subject": "Q3 Budget Discussion",
            "date": "2024-01-15",
            "from": "manager@company.com",
            "to": ["team@company.com"],
            "body": "We need to discuss the Q3 budget allocation."
        },
        {
            "email_id": 2,
            "message_id": "<reply1@example.com>",
            "in_reply_to": "<original@example.com>",
            "references": ["<original@example.com>"],
            "subject": "RE: Q3 Budget Discussion",
            "date": "2024-01-15",
            "from": "analyst@company.com",
            "to": ["manager@company.com"],
            "body": "I agree. > We need to discuss the Q3 budget allocation."
        },
        {
            "email_id": 3,
            "message_id": "<reply2@example.com>",
            "in_reply_to": "<reply1@example.com>",
            "references": ["<original@example.com>", "<reply1@example.com>"],
            "subject": "RE: Q3 Budget Discussion",
            "date": "2024-01-16",
            "from": "manager@company.com",
            "to": ["analyst@company.com"],
            "body": "Let's schedule a meeting for next week."
        },
    ]

    # Thread emails
    threader = EmailThreader()
    threads = threader.thread_emails(emails)

    print("Email Threads:")
    for thread_id, thread in threads.items():
        summary = threader.get_thread_summary(thread)
        print(f"Thread {thread_id}: {summary['subject']}")
        print(f"  Length: {summary['thread_length']}")
        print(f"  Participants: {summary['participants']}")
