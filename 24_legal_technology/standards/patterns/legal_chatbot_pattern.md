# Legal Chatbot Pattern

## Overview

The Legal Chatbot Pattern implements an intelligent conversational interface for legal services delivery, combining natural language understanding, knowledge management, and legal expertise to provide scalable first-line legal support. This pattern is designed to handle common legal inquiries, provide guidance, and escalate complex matters to human attorneys when necessary.

**Key Capabilities:**
- Natural language understanding for legal queries
- Knowledge base integration with legal documents
- Multi-turn conversation management
- Secure information handling and privacy protection
- Seamless escalation to human attorneys
- Usage analytics and continuous improvement

**Expected Outcomes:**
- 40-60% reduction in routine legal inquiries
- 24/7 availability of legal guidance
- Improved client satisfaction and engagement
- Reduced operational costs
- Better resource allocation for attorneys

## Architecture Components

### 1. Intent Recognition and Classification

```python
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Optional, Tuple
import json

class LegalQueryIntentType(Enum):
    CONTRACT_REVIEW = "contract_review"
    LEGAL_DEFINITION = "legal_definition"
    DOCUMENT_GENERATION = "document_generation"
    CASE_STATUS = "case_status"
    BILLING_INQUIRY = "billing_inquiry"
    APPOINTMENT_SCHEDULING = "appointment_scheduling"
    GENERAL_LEGAL_INFO = "general_legal_info"
    COMPLIANCE_QUESTION = "compliance_question"
    ESCALATION_REQUEST = "escalation_request"
    SMALL_TALK = "small_talk"

@dataclass
class UserQuery:
    query_id: str
    user_id: str
    query_text: str
    detected_intent: Optional[LegalQueryIntentType] = None
    confidence_score: float = 0.0
    entities: Dict[str, List[str]] = None
    context_history: List[str] = None
    timestamp: str = ""

class IntentRecognizer:
    def __init__(self):
        self.intent_patterns = self._initialize_patterns()
        self.confidence_threshold = 0.7

    def _initialize_patterns(self) -> Dict[str, Dict[str, any]]:
        """Initialize intent recognition patterns"""
        return {
            LegalQueryIntentType.CONTRACT_REVIEW: {
                "keywords": ["review", "contract", "agreement", "terms", "clause", "liability"],
                "sample_queries": [
                    "Can you review this contract?",
                    "What do these contract terms mean?",
                    "Are there any risky clauses?"
                ]
            },
            LegalQueryIntentType.LEGAL_DEFINITION: {
                "keywords": ["define", "what is", "meaning", "legal term", "term definition"],
                "sample_queries": [
                    "What does indemnification mean?",
                    "Define arbitration clause",
                    "What is a non-compete agreement?"
                ]
            },
            LegalQueryIntentType.DOCUMENT_GENERATION: {
                "keywords": ["generate", "create", "draft", "template", "form", "document"],
                "sample_queries": [
                    "Create a lease agreement",
                    "Generate an NDA",
                    "Draft a service agreement"
                ]
            },
            LegalQueryIntentType.APPOINTMENT_SCHEDULING: {
                "keywords": ["schedule", "appointment", "meeting", "consult", "available", "time"],
                "sample_queries": [
                    "Schedule a consultation",
                    "When are you available?",
                    "Book an appointment"
                ]
            },
            LegalQueryIntentType.ESCALATION_REQUEST: {
                "keywords": ["speak to lawyer", "talk to attorney", "human", "escalate", "urgent"],
                "sample_queries": [
                    "I need to speak with an attorney",
                    "This needs escalation",
                    "Connect me with a lawyer"
                ]
            }
        }

    def recognize_intent(self, query: UserQuery) -> Tuple[LegalQueryIntentType, float]:
        """Recognize intent from user query"""
        query_text_lower = query.query_text.lower()
        best_intent = None
        best_score = 0.0

        for intent_type, pattern_config in self.intent_patterns.items():
            keywords = pattern_config.get("keywords", [])

            # Calculate score based on keyword matches
            matches = sum(1 for kw in keywords if kw in query_text_lower)
            score = matches / len(keywords) if keywords else 0.0

            if score > best_score:
                best_score = score
                best_intent = intent_type

        # If no good match, classify as general info
        if best_score < self.confidence_threshold:
            best_intent = LegalQueryIntentType.GENERAL_LEGAL_INFO
            best_score = 0.5

        return best_intent, best_score

    def extract_entities(self, query: UserQuery) -> Dict[str, List[str]]:
        """Extract entities (people, documents, dates, etc.)"""
        entities = {
            "document_types": [],
            "legal_concepts": [],
            "names": [],
            "dates": [],
            "monetary_amounts": []
        }

        # Extract document types
        doc_types = ["contract", "agreement", "lease", "nda", "will", "trust", "ipo"]
        for doc_type in doc_types:
            if doc_type in query.query_text.lower():
                entities["document_types"].append(doc_type)

        # Extract legal concepts
        concepts = ["indemnification", "liability", "breach", "termination", "arbitration"]
        for concept in concepts:
            if concept in query.query_text.lower():
                entities["legal_concepts"].append(concept)

        return entities
```

### 2. Knowledge Base Management

```python
from abc import ABC, abstractmethod

@dataclass
class KnowledgeArticle:
    article_id: str
    title: str
    content: str
    category: str
    tags: List[str]
    relevant_intents: List[LegalQueryIntentType]
    embedding: Optional[List[float]] = None
    created_date: str = ""
    last_updated: str = ""
    view_count: int = 0

class KnowledgebaseProvider(ABC):
    @abstractmethod
    def search(self, query: str, top_k: int = 5) -> List[KnowledgeArticle]:
        pass

    @abstractmethod
    def get_article(self, article_id: str) -> Optional[KnowledgeArticle]:
        pass

    @abstractmethod
    def add_article(self, article: KnowledgeArticle):
        pass

class SemanticKnowledgebase(KnowledgebaseProvider):
    def __init__(self):
        self.articles: Dict[str, KnowledgeArticle] = {}
        self._initialize_base_articles()

    def _initialize_base_articles(self):
        """Initialize base knowledge articles"""
        articles = [
            KnowledgeArticle(
                article_id="ind_001",
                title="Understanding Indemnification Clauses",
                content="""
                Indemnification is a contractual obligation where one party (indemnitor) agrees to
                compensate the other party (indemnitee) for losses, damages, or liabilities.

                Key aspects:
                1. Scope: Define what losses are covered
                2. Triggers: Specify circumstances that trigger indemnification
                3. Limits: Set monetary caps on indemnification
                4. Procedures: Establish claim notification requirements

                Common indemnification types:
                - Sole indemnification (one party only)
                - Mutual indemnification (both parties)
                - Limited indemnification (specific events only)
                - Broad indemnification (covers most scenarios)
                """,
                category="Contract Law",
                tags=["indemnification", "contract", "liability"],
                relevant_intents=[
                    LegalQueryIntentType.CONTRACT_REVIEW,
                    LegalQueryIntentType.LEGAL_DEFINITION
                ]
            ),
            KnowledgeArticle(
                article_id="nda_001",
                title="Non-Disclosure Agreements (NDA)",
                content="""
                An NDA is a legal contract that protects confidential information shared
                between parties.

                Essential NDA components:
                1. Definition of confidential information
                2. Permitted uses and restrictions
                3. Duration of confidentiality obligations
                4. Remedies for breach
                5. Return or destruction of information

                NDA types:
                - Unilateral: One party discloses, one receives
                - Mutual: Both parties disclose to each other
                - Multilateral: Multiple parties exchange information
                """,
                category="Contract Law",
                tags=["nda", "confidentiality", "contract"],
                relevant_intents=[
                    LegalQueryIntentType.CONTRACT_REVIEW,
                    LegalQueryIntentType.LEGAL_DEFINITION,
                    LegalQueryIntentType.DOCUMENT_GENERATION
                ]
            )
        ]

        for article in articles:
            self.articles[article.article_id] = article

    def search(self, query: str, top_k: int = 5) -> List[KnowledgeArticle]:
        """Search knowledge base by semantic similarity"""
        results = []
        query_lower = query.lower()

        # Simple keyword-based search (in production, use embeddings)
        for article in self.articles.values():
            relevance_score = 0.0

            # Title match
            if query_lower in article.title.lower():
                relevance_score += 0.5

            # Content match
            content_lower = article.content.lower()
            word_matches = sum(1 for word in query_lower.split() if word in content_lower)
            relevance_score += word_matches / len(query_lower.split())

            # Tag match
            tag_matches = sum(1 for tag in article.tags if tag in query_lower)
            relevance_score += tag_matches * 0.3

            if relevance_score > 0:
                results.append((article, relevance_score))

        # Sort by relevance and return top_k
        results.sort(key=lambda x: x[1], reverse=True)
        return [article for article, _ in results[:top_k]]

    def get_article(self, article_id: str) -> Optional[KnowledgeArticle]:
        return self.articles.get(article_id)

    def add_article(self, article: KnowledgeArticle):
        self.articles[article.article_id] = article
```

### 3. Conversation Management

```python
@dataclass
class ConversationTurn:
    turn_id: str
    user_message: str
    bot_response: str
    intent: Optional[LegalQueryIntentType]
    confidence: float
    timestamp: str

class ConversationManager:
    def __init__(self, knowledge_base: KnowledgebaseProvider):
        self.knowledge_base = knowledge_base
        self.conversations: Dict[str, List[ConversationTurn]] = {}
        self.escalation_queue: List[Dict[str, Any]] = []

    def process_query(self, user_id: str, query_text: str) -> Dict[str, Any]:
        """Process user query and generate response"""
        # Initialize conversation if new user
        if user_id not in self.conversations:
            self.conversations[user_id] = []

        # Create user query object
        user_query = UserQuery(
            query_id=f"q_{user_id}_{len(self.conversations[user_id])}",
            user_id=user_id,
            query_text=query_text,
            context_history=[t.user_message for t in self.conversations[user_id][-5:]],
            timestamp=str(datetime.now())
        )

        # Recognize intent
        intent_recognizer = IntentRecognizer()
        detected_intent, confidence = intent_recognizer.recognize_intent(user_query)

        # Handle escalation requests
        if detected_intent == LegalQueryIntentType.ESCALATION_REQUEST:
            return self._handle_escalation(user_id, query_text)

        # Generate response based on intent
        response = self._generate_response(query_text, detected_intent)

        # Store conversation turn
        turn = ConversationTurn(
            turn_id=user_query.query_id,
            user_message=query_text,
            bot_response=response,
            intent=detected_intent,
            confidence=confidence,
            timestamp=user_query.timestamp
        )
        self.conversations[user_id].append(turn)

        return {
            "response": response,
            "intent": detected_intent.value if detected_intent else None,
            "confidence": confidence,
            "follow_up_options": self._generate_follow_ups(detected_intent)
        }

    def _generate_response(self, query: str, intent: LegalQueryIntentType) -> str:
        """Generate appropriate response based on intent"""
        if intent == LegalQueryIntentType.LEGAL_DEFINITION:
            # Search knowledge base for definitions
            articles = self.knowledge_base.search(query, top_k=2)
            if articles:
                return f"Based on our knowledge base: {articles[0].content[:300]}...\n\nWould you like more details?"

        elif intent == LegalQueryIntentType.CONTRACT_REVIEW:
            return """I can help you review contracts. Please provide:
1. The type of contract (e.g., service agreement, NDA)
2. Specific clauses or terms of concern
3. Any business context

What specific aspect would you like me to review?"""

        elif intent == LegalQueryIntentType.DOCUMENT_GENERATION:
            return """I can help you generate legal documents. What type of document do you need?
- Service Agreement
- NDA/Confidentiality Agreement
- Non-Compete Agreement
- Lease Agreement
- Employment Agreement

Please select or specify."""

        elif intent == LegalQueryIntentType.APPOINTMENT_SCHEDULING:
            return """I can help schedule a consultation. What's your availability?
- Morning (9 AM - 12 PM)
- Afternoon (1 PM - 5 PM)
- Evening (5 PM - 8 PM)

And preferred date?"""

        else:
            return f"""I can help with legal questions and document review. Based on your inquiry, you might be interested in:
1. Getting legal definitions
2. Reviewing contracts
3. Generating documents
4. Scheduling a consultation with an attorney

How can I assist you further?"""

    def _generate_follow_ups(self, intent: LegalQueryIntentType) -> List[str]:
        """Generate contextual follow-up questions"""
        follow_ups = {
            LegalQueryIntentType.CONTRACT_REVIEW: [
                "Would you like me to identify potential risks?",
                "Do you need help with specific clauses?",
                "Would you like to compare with a template?"
            ],
            LegalQueryIntentType.LEGAL_DEFINITION: [
                "Would you like examples of this term?",
                "Do you need related concepts explained?",
                "Would you like case law references?"
            ],
            LegalQueryIntentType.DOCUMENT_GENERATION: [
                "Would you like a template?",
                "Do you need customization for specific terms?",
                "Would you like a review after generation?"
            ]
        }

        return follow_ups.get(intent, ["Would you like more information?", "Is there anything else I can help with?"])

    def _handle_escalation(self, user_id: str, reason: str) -> Dict[str, Any]:
        """Handle escalation to human attorney"""
        escalation = {
            "escalation_id": f"esc_{user_id}_{datetime.now().timestamp()}",
            "user_id": user_id,
            "reason": reason,
            "timestamp": str(datetime.now()),
            "status": "queued",
            "estimated_wait": "5-15 minutes"
        }

        self.escalation_queue.append(escalation)

        return {
            "response": f"""I'm connecting you with a human attorney.

Escalation ID: {escalation['escalation_id']}
Estimated wait time: {escalation['estimated_wait']}

An attorney will be with you shortly. Thank you for your patience.""",
            "escalation_info": escalation
        }

    def get_conversation_history(self, user_id: str) -> List[Dict[str, str]]:
        """Retrieve conversation history for user"""
        if user_id not in self.conversations:
            return []

        return [
            {
                "turn_id": turn.turn_id,
                "user": turn.user_message,
                "bot": turn.bot_response,
                "intent": turn.intent.value if turn.intent else None,
                "timestamp": turn.timestamp
            }
            for turn in self.conversations[user_id]
        ]
```

### 4. Response Generation and Personalization

```python
class ResponseGenerator:
    def __init__(self, knowledge_base: KnowledgebaseProvider):
        self.knowledge_base = knowledge_base

    def generate_definition_response(self, term: str) -> str:
        """Generate definition response"""
        articles = self.knowledge_base.search(term, top_k=3)

        if not articles:
            return f"I don't have specific information about '{term}' in my knowledge base. I recommend consulting with an attorney for this question."

        response = f"## {term.title()}\n\n"
        response += articles[0].content[:500] + "\n\n"

        if len(articles) > 1:
            response += "**Related Topics:**\n"
            for article in articles[1:]:
                response += f"- {article.title}\n"

        return response

    def generate_contract_review_response(self, document_type: str, concerns: List[str]) -> str:
        """Generate contract review guidance"""
        response = f"## {document_type.title()} Review Checklist\n\n"

        # Standard checklist items
        checklist = {
            "contract": [
                "Effective date and duration",
                "Parties and their roles",
                "Scope of services/deliverables",
                "Payment terms and conditions",
                "Liability limitations",
                "Indemnification clauses",
                "Termination provisions",
                "Confidentiality and IP ownership",
                "Dispute resolution mechanism",
                "Amendment procedures"
            ],
            "nda": [
                "Definition of confidential information",
                "Permitted uses",
                "Recipient obligations",
                "Duration of confidentiality",
                "Return/destruction procedures",
                "Exceptions to confidentiality",
                "Remedies and injunctive relief",
                "Governing law and jurisdiction"
            ]
        }

        items = checklist.get(document_type.lower(), [])
        response += "**Key Items to Review:**\n"
        for item in items:
            response += f"- [ ] {item}\n"

        if concerns:
            response += "\n**Specific Concerns You Mentioned:**\n"
            for concern in concerns:
                response += f"- {concern}\n"

        response += "\n**Recommendation:** For a detailed review tailored to your specific situation, I recommend speaking with an attorney."

        return response

    def generate_document_template(self, document_type: str, customizations: Dict[str, str]) -> str:
        """Generate document template"""
        templates = {
            "nda": """MUTUAL NON-DISCLOSURE AGREEMENT

THIS AGREEMENT made and entered into as of {date}

BETWEEN: {party_a_name}
AND: {party_b_name}

WHEREAS the parties wish to disclose certain confidential information;

NOW THEREFORE in consideration of the mutual covenants herein:

1. CONFIDENTIAL INFORMATION
   1.1 Means any information disclosed by one party to the other...

2. OBLIGATIONS OF RECEIVING PARTY
   2.1 The Receiving Party shall:
       (a) Maintain confidentiality
       (b) Limit use to authorized purposes
       (c) Implement reasonable security measures

3. TERM
   3.1 This Agreement shall commence on {effective_date}
   3.2 Confidentiality obligations shall survive for {duration} years

4. GOVERNING LAW
   This Agreement shall be governed by the laws of {jurisdiction}

Executed this {date}
""",
            "service_agreement": """SERVICE AGREEMENT

This Service Agreement ("Agreement") is entered into on {date}

By and Between: {service_provider} ("Provider")
And: {client} ("Client")

1. SERVICES
   The Provider agrees to provide: {services_description}

2. FEES
   Client shall pay Provider: {fee_amount} {fee_frequency}

3. TERM
   This Agreement begins on {start_date} and ends on {end_date}

4. CONFIDENTIALITY
   Both parties agree to maintain confidentiality as outlined in Exhibit A

5. LIMITATION OF LIABILITY
   Neither party's liability shall exceed {liability_cap}

6. TERMINATION
   Either party may terminate with {termination_notice} written notice

Executed on {date}
"""
        }

        template = templates.get(document_type.lower(), "")

        # Apply customizations
        for key, value in customizations.items():
            template = template.replace(f"{{{key}}}", value)

        return template
```

### 5. Analytics and Monitoring

```python
class ChatbotAnalytics:
    def __init__(self):
        self.query_log: List[Dict[str, Any]] = []
        self.escalation_log: List[Dict[str, Any]] = []

    def log_query(self, user_id: str, query_text: str, intent: LegalQueryIntentType,
                  confidence: float, response: str):
        """Log user query"""
        self.query_log.append({
            "timestamp": str(datetime.now()),
            "user_id": user_id,
            "query": query_text,
            "intent": intent.value if intent else None,
            "confidence": confidence,
            "response_length": len(response),
            "response_provided": bool(response)
        })

    def log_escalation(self, escalation: Dict[str, Any]):
        """Log escalation"""
        self.escalation_log.append(escalation)

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Generate performance metrics"""
        if not self.query_log:
            return {}

        total_queries = len(self.query_log)
        escalations = len(self.escalation_log)
        resolved_queries = total_queries - escalations

        # Intent distribution
        intent_counts = {}
        for log in self.query_log:
            intent = log.get("intent")
            intent_counts[intent] = intent_counts.get(intent, 0) + 1

        # Average confidence by intent
        avg_confidence = sum(log["confidence"] for log in self.query_log) / total_queries

        return {
            "total_queries": total_queries,
            "escalations": escalations,
            "escalation_rate": escalations / total_queries * 100,
            "resolved_queries": resolved_queries,
            "resolution_rate": resolved_queries / total_queries * 100,
            "average_confidence": avg_confidence,
            "intent_distribution": intent_counts,
            "peak_intent": max(intent_counts, key=intent_counts.get) if intent_counts else None
        }

    def get_user_satisfaction_metrics(self) -> Dict[str, Any]:
        """Get satisfaction metrics"""
        return {
            "average_satisfaction_score": 4.2,
            "resolution_satisfaction": 4.5,
            "escalation_satisfaction": 3.8,
            "response_time_ms": 450,
            "user_retention_rate": 0.78
        }
```

## Integration with Legal Practice Management

```python
class PracticeIntegration:
    def __init__(self, pm_system_url: str):
        self.pm_system_url = pm_system_url

    def sync_escalation_to_pm(self, escalation: Dict[str, Any]) -> bool:
        """Sync escalation to practice management system"""
        # Create matter or append to existing case
        import requests

        payload = {
            "user_id": escalation["user_id"],
            "escalation_id": escalation["escalation_id"],
            "reason": escalation["reason"],
            "timestamp": escalation["timestamp"],
            "status": "open"
        }

        try:
            response = requests.post(
                f"{self.pm_system_url}/api/escalations",
                json=payload
            )
            return response.status_code == 201
        except Exception as e:
            return False

    def schedule_callback(self, user_id: str, preferred_time: str) -> Dict[str, Any]:
        """Schedule attorney callback"""
        return {
            "scheduled": True,
            "callback_id": f"cb_{user_id}_{datetime.now().timestamp()}",
            "scheduled_time": preferred_time,
            "assigned_attorney": "Attorney Name",
            "confirmation_sent": True
        }
```

## Best Practices

### 1. Safety and Liability
- Always include disclaimer that chatbot is not a substitute for legal advice
- Escalate complex legal matters to qualified attorneys
- Maintain audit trail of all interactions
- Implement privacy controls for sensitive information

### 2. Accuracy Maintenance
- Regular knowledge base updates
- Continuous model training on new legal developments
- Quality assurance testing on responses
- Legal team review of generated content

### 3. User Experience
- Clear escalation path to human attorneys
- Contextual help and guidance
- Natural conversation flow
- Multi-language support

### 4. Compliance
- GDPR/CCPA compliance for user data
- Maintain attorney-client privilege where applicable
- Secure data storage and transmission
- Regular security audits

## Deployment Architecture

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class ChatQuery(BaseModel):
    user_id: str
    message: str
    session_id: Optional[str] = None

@app.post("/api/chat/message")
async def chat_message(query: ChatQuery) -> Dict[str, Any]:
    """Chat endpoint"""
    kb = SemanticKnowledgebase()
    conv_manager = ConversationManager(kb)

    result = conv_manager.process_query(query.user_id, query.message)
    return result

@app.get("/api/chat/history/{user_id}")
async def get_history(user_id: str) -> List[Dict[str, str]]:
    """Get conversation history"""
    conv_manager = ConversationManager(SemanticKnowledgebase())
    return conv_manager.get_conversation_history(user_id)

@app.post("/api/chat/escalate")
async def escalate_conversation(user_id: str, reason: str) -> Dict[str, Any]:
    """Escalate to human attorney"""
    conv_manager = ConversationManager(SemanticKnowledgebase())
    return conv_manager._handle_escalation(user_id, reason)
```

## Key Metrics

| Metric | Target |
|--------|--------|
| Query Resolution Rate | 70%+ |
| First-Contact Resolution | 60%+ |
| User Satisfaction Score | 4.0+ |
| Average Response Time | <1 second |
| Escalation Rate | <30% |
| Knowledge Base Coverage | 90%+ |

This pattern provides a comprehensive framework for deploying intelligent legal chatbots that enhance client engagement while managing risk through appropriate escalation and oversight.
