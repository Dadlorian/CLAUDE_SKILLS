"""
Advanced Email Threading Example
Demonstrates complex thread analysis and conversation grouping
"""

from typing import List, Dict, Set, Tuple
from collections import defaultdict
import re
from datetime import datetime, timedelta

class AdvancedThreadAnalyzer:
    """Performs advanced analysis on threaded emails"""

    @staticmethod
    def merge_related_threads(threads: List[List[Dict]],
                             time_gap_hours: int = 24,
                             subject_similarity: float = 0.7) -> List[List[Dict]]:
        """
        Merge separate threads that are actually related conversations

        Args:
            threads: List of email threads
            time_gap_hours: Maximum hours between emails to consider related
            subject_similarity: Minimum subject similarity score (0-1)

        Returns:
            List of merged threads
        """
        if not threads:
            return []

        merged = []
        processed = set()

        for i, thread1 in enumerate(threads):
            if i in processed:
                continue

            merged_thread = list(thread1)
            thread1_subject = thread1[0].get('subject', '')
            thread1_end = datetime.fromisoformat(thread1[-1].get('date', ''))

            # Look for related threads
            for j, thread2 in enumerate(threads):
                if j <= i or j in processed:
                    continue

                thread2_subject = thread2[0].get('subject', '')
                thread2_start = datetime.fromisoformat(thread2[0].get('date', ''))

                # Check time gap
                time_gap = thread2_start - thread1_end
                if time_gap > timedelta(hours=time_gap_hours):
                    continue

                # Check subject similarity
                similarity = AdvancedThreadAnalyzer._subject_similarity(
                    thread1_subject, thread2_subject
                )
                if similarity >= subject_similarity:
                    merged_thread.extend(thread2)
                    merged_thread.sort(key=lambda x: x.get('date', ''))
                    processed.add(j)

            merged.append(merged_thread)
            processed.add(i)

        return merged

    @staticmethod
    def _subject_similarity(subject1: str, subject2: str) -> float:
        """Calculate similarity between two subjects (0-1)"""
        # Clean subjects
        s1 = re.sub(r'^(RE:|FW:)+\s*', '', subject1, flags=re.IGNORECASE)
        s2 = re.sub(r'^(RE:|FW:)+\s*', '', subject2, flags=re.IGNORECASE)

        # Simple word overlap similarity
        words1 = set(s1.lower().split())
        words2 = set(s2.lower().split())

        if not words1 or not words2:
            return 0.0

        overlap = len(words1.intersection(words2))
        total = len(words1.union(words2))

        return overlap / total if total > 0 else 0.0

    @staticmethod
    def identify_decision_points(thread: List[Dict]) -> List[Dict]:
        """
        Identify emails that represent important decisions or turning points

        Args:
            thread: List of emails in thread

        Returns:
            List of decision point emails with context
        """
        decision_keywords = [
            'approve', 'reject', 'decline', 'agree', 'disagree',
            'proceed', 'cancel', 'delay', 'schedule', 'decided',
            'will do', 'confirmed', 'authorized'
        ]

        decision_points = []

        for i, email in enumerate(thread):
            body = email.get('body', '').lower()

            # Check for decision keywords
            has_decision = any(keyword in body for keyword in decision_keywords)

            if has_decision:
                decision_points.append({
                    "email_id": email.get('email_id'),
                    "date": email.get('date'),
                    "from": email.get('from'),
                    "subject": email.get('subject'),
                    "position": i,
                    "total_messages": len(thread)
                })

        return decision_points

    @staticmethod
    def extract_action_items(thread: List[Dict]) -> List[Dict]:
        """
        Extract action items and tasks from thread

        Args:
            thread: List of emails

        Returns:
            List of identified action items
        """
        action_patterns = [
            r'(?:please|pls|can you|could you|will you)\s+(.+?)(?:\.|$)',
            r'(?:need to|need)\s+(.+?)(?:\.|$)',
            r'(?:todo|to-do|action)[\s:]+(.+?)(?:\.|$)',
            r'(?:responsible|assigned)\s+(?:for|to)\s+(.+?)(?:\.|$)'
        ]

        actions = []

        for email in thread:
            body = email.get('body', '')

            for pattern in action_patterns:
                matches = re.finditer(pattern, body, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    actions.append({
                        "description": match.group(1).strip(),
                        "source_email": email.get('email_id'),
                        "assigned_by": email.get('from'),
                        "date": email.get('date')
                    })

        return actions


class ThreadingMetrics:
    """Calculate metrics about email threads"""

    @staticmethod
    def calculate_responsiveness(thread: List[Dict]) -> Dict:
        """
        Measure how responsive participants are in thread

        Args:
            thread: List of emails

        Returns:
            Responsiveness metrics
        """
        participant_responses = defaultdict(int)
        total_messages_by_person = defaultdict(int)

        for i, email in enumerate(thread):
            from_addr = email.get('from', '')
            total_messages_by_person[from_addr] += 1

            # Check if this is a response (not first message)
            if i > 0:
                participant_responses[from_addr] += 1

        # Calculate response ratios
        response_ratios = {}
        for person in total_messages_by_person:
            total = total_messages_by_person[person]
            responses = participant_responses.get(person, 0)
            response_ratios[person] = responses / total if total > 0 else 0.0

        return {
            "total_participants": len(total_messages_by_person),
            "response_ratios": response_ratios,
            "most_responsive": max(response_ratios.items(),
                                  key=lambda x: x[1])[0] if response_ratios else None
        }

    @staticmethod
    def identify_delayed_responses(thread: List[Dict]) -> List[Dict]:
        """
        Identify unusually delayed responses

        Args:
            thread: List of emails

        Returns:
            List of delayed response instances
        """
        delayed = []
        threshold_hours = 48  # Consider >48 hours as delayed

        for i in range(1, len(thread)):
            prev_email = thread[i - 1]
            curr_email = thread[i]

            prev_time = datetime.fromisoformat(prev_email.get('date', ''))
            curr_time = datetime.fromisoformat(curr_email.get('date', ''))

            time_diff = curr_time - prev_time
            hours = time_diff.total_seconds() / 3600

            if hours > threshold_hours:
                delayed.append({
                    "from_email": prev_email.get('email_id'),
                    "to_email": curr_email.get('email_id'),
                    "gap_hours": round(hours, 1),
                    "responder": curr_email.get('from'),
                    "date": curr_email.get('date')
                })

        return delayed

    @staticmethod
    def calculate_sentiment_shift(thread: List[Dict]) -> Dict:
        """
        Analyze how tone changes through thread

        Args:
            thread: List of emails

        Returns:
            Sentiment analysis across thread
        """
        sentiment_words = {
            "positive": ['good', 'great', 'excellent', 'fantastic', 'agree', 'support'],
            "negative": ['problem', 'issue', 'concern', 'disagree', 'failed', 'error'],
            "urgent": ['urgent', 'asap', 'immediate', 'critical', 'emergency']
        }

        sentiment_progression = []

        for email in thread:
            body = email.get('body', '').lower()

            sentiment = {
                "positive": sum(1 for word in sentiment_words["positive"] if word in body),
                "negative": sum(1 for word in sentiment_words["negative"] if word in body),
                "urgent": sum(1 for word in sentiment_words["urgent"] if word in body)
            }

            sentiment_progression.append({
                "email_id": email.get('email_id'),
                "date": email.get('date'),
                "from": email.get('from'),
                "sentiment": sentiment
            })

        return {
            "progression": sentiment_progression,
            "overall_tone": "positive" if sentiment_progression and
                          sentiment_progression[-1]["sentiment"]["positive"] > 0 else "neutral"
        }


# Example usage
if __name__ == "__main__":
    emails = [
        {
            "email_id": 1,
            "subject": "Project Status Update",
            "date": "2024-01-15T09:00:00",
            "from": "manager@company.com",
            "body": "Please provide an update on project status by end of week."
        },
        {
            "email_id": 2,
            "subject": "RE: Project Status Update",
            "date": "2024-01-16T14:30:00",
            "from": "developer@company.com",
            "body": "Project is progressing well. Agree with timeline. Need to schedule design review."
        },
        {
            "email_id": 3,
            "subject": "RE: Project Status Update",
            "date": "2024-01-18T10:00:00",
            "from": "manager@company.com",
            "body": "Great! Can you schedule the design review for next week? This is urgent."
        },
    ]

    analyzer = AdvancedThreadAnalyzer()
    decision_points = analyzer.identify_decision_points(emails)
    action_items = analyzer.extract_action_items(emails)

    print(f"Decision Points: {len(decision_points)}")
    print(f"Action Items: {len(action_items)}")

    metrics = ThreadingMetrics()
    responsiveness = metrics.calculate_responsiveness(emails)
    print(f"Responsiveness: {responsiveness}")
