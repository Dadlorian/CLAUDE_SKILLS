"""
Legal Chatbot with Conversation Memory
Production-ready interactive legal assistant with session management
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from langchain.memory import ConversationBufferMemory, ConversationSummaryMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.callbacks import get_openai_callback
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LegalChatbot:
    """
    Production-ready conversational legal assistant

    Features:
    - Session management with persistence
    - Conversation history with summaries
    - Cost tracking per session
    - User feedback collection
    - Analytics and usage statistics
    - Configurable safety guardrails
    """

    def __init__(
        self,
        vectorstore,
        session_id: Optional[str] = None,
        session_dir: str = "./chat_sessions",
        model_name: str = "gpt-3.5-turbo",
        memory_type: str = "buffer",
        max_history_length: int = 10
    ):
        """
        Initialize Legal Chatbot

        Args:
            vectorstore: FAISS or similar vectorstore for retrieval
            session_id: Optional session ID (generates new if not provided)
            session_dir: Directory to store session data
            model_name: OpenAI model to use
            memory_type: Type of memory ('buffer' or 'summary')
            max_history_length: Maximum conversation turns to keep
        """
        self.session_id = session_id or str(uuid.uuid4())
        self.session_dir = session_dir
        self.vectorstore = vectorstore
        self.max_history_length = max_history_length

        # Initialize LLM
        self.llm = OpenAI(temperature=0.3, model_name=model_name)

        # Initialize memory
        if memory_type == "summary":
            self.memory = ConversationSummaryMemory(
                llm=self.llm,
                memory_key="chat_history",
                return_messages=True,
                output_key="answer"
            )
        else:
            self.memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True,
                output_key="answer"
            )

        # Session metadata
        self.session_metadata = {
            "session_id": self.session_id,
            "created_at": datetime.now().isoformat(),
            "total_messages": 0,
            "total_tokens": 0,
            "total_cost": 0.0,
            "user_info": {},
            "conversation_summary": ""
        }

        # Create QA chain with custom prompt
        self.qa_chain = self._create_qa_chain()

        # Load existing session if available
        self._load_session()

        logger.info(f"Chatbot initialized with session ID: {self.session_id}")

    def _create_qa_chain(self) -> ConversationalRetrievalChain:
        """Create conversational QA chain with legal-specific configuration"""

        # Custom prompt for legal chatbot
        condense_question_prompt = PromptTemplate.from_template(
            """Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question, in its original language.

Chat History:
{chat_history}
Follow Up Input: {question}
Standalone question:"""
        )

        qa_prompt = PromptTemplate.from_template(
            """You are a helpful legal assistant. Use the following pieces of context to answer the question at the end.

IMPORTANT DISCLAIMERS:
- This is general legal information, not legal advice
- Users should consult with a qualified attorney for specific legal matters
- Laws vary by jurisdiction

Context from legal documents:
{context}

Question: {question}

Instructions:
1. Provide clear, accurate information based on the context
2. Include relevant citations when available
3. If the information isn't in the context, say so
4. Remind users this is not legal advice for complex matters
5. Use plain language while maintaining legal accuracy

Helpful Answer:"""
        )

        qa_chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=self.vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 4}
            ),
            memory=self.memory,
            return_source_documents=True,
            condense_question_prompt=condense_question_prompt,
            combine_docs_chain_kwargs={"prompt": qa_prompt},
            verbose=False
        )

        return qa_chain

    def chat(
        self,
        user_message: str,
        user_id: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Process user message and generate response

        Args:
            user_message: User's message
            user_id: Optional user identifier
            metadata: Optional metadata for the message

        Returns:
            Dictionary with response and metadata
        """
        if not user_message or not user_message.strip():
            return {
                "error": "Message cannot be empty",
                "session_id": self.session_id
            }

        logger.info(f"Processing message in session {self.session_id}: {user_message[:100]}")

        # Track API usage
        with get_openai_callback() as cb:
            try:
                result = self.qa_chain({"question": user_message})

                # Update session metadata
                self.session_metadata["total_messages"] += 1
                self.session_metadata["total_tokens"] += cb.total_tokens
                self.session_metadata["total_cost"] += cb.total_cost

                if user_id:
                    self.session_metadata["user_info"]["user_id"] = user_id

                response = {
                    "session_id": self.session_id,
                    "response": result['answer'],
                    "sources": self._format_sources(result['source_documents']),
                    "num_sources": len(result['source_documents']),
                    "timestamp": datetime.now().isoformat(),
                    "metadata": {
                        "tokens_used": cb.total_tokens,
                        "cost": cb.total_cost,
                        "message_number": self.session_metadata["total_messages"]
                    }
                }

                # Save interaction
                self._save_interaction(user_message, response)

                # Manage memory length
                self._manage_memory_length()

                return response

            except Exception as e:
                logger.error(f"Error in chat: {e}")
                return {
                    "error": str(e),
                    "session_id": self.session_id,
                    "timestamp": datetime.now().isoformat()
                }

    def _format_sources(self, source_documents: List) -> List[Dict[str, str]]:
        """Format source documents for display"""
        formatted = []
        for i, doc in enumerate(source_documents, 1):
            source = {
                "source_number": i,
                "content_preview": doc.page_content[:300] + "...",
                "metadata": doc.metadata,
                "relevance": "high" if i <= 2 else "medium"
            }
            formatted.append(source)
        return formatted

    def _manage_memory_length(self):
        """Trim conversation history if too long"""
        if hasattr(self.memory, 'chat_memory'):
            messages = self.memory.chat_memory.messages
            if len(messages) > self.max_history_length * 2:  # *2 for user+assistant pairs
                # Keep only recent messages
                self.memory.chat_memory.messages = messages[-(self.max_history_length * 2):]
                logger.info(f"Trimmed conversation history to {self.max_history_length} turns")

    def _save_interaction(self, user_message: str, response: Dict):
        """Save interaction to session file"""
        os.makedirs(self.session_dir, exist_ok=True)
        session_file = os.path.join(self.session_dir, f"{self.session_id}.json")

        interaction = {
            "timestamp": datetime.now().isoformat(),
            "user_message": user_message,
            "assistant_response": response.get("response", ""),
            "sources_used": len(response.get("sources", [])),
            "tokens": response.get("metadata", {}).get("tokens_used", 0)
        }

        try:
            # Load existing session data
            if os.path.exists(session_file):
                with open(session_file, 'r') as f:
                    session_data = json.load(f)
            else:
                session_data = {
                    "session_metadata": self.session_metadata,
                    "interactions": []
                }

            # Add new interaction
            session_data["interactions"].append(interaction)
            session_data["session_metadata"] = self.session_metadata

            # Save updated session
            with open(session_file, 'w') as f:
                json.dump(session_data, f, indent=2)

        except Exception as e:
            logger.error(f"Error saving interaction: {e}")

    def _load_session(self):
        """Load existing session if available"""
        session_file = os.path.join(self.session_dir, f"{self.session_id}.json")

        if os.path.exists(session_file):
            try:
                with open(session_file, 'r') as f:
                    session_data = json.load(f)

                self.session_metadata = session_data.get("session_metadata", self.session_metadata)

                # Restore conversation history
                interactions = session_data.get("interactions", [])
                for interaction in interactions[-self.max_history_length:]:
                    self.memory.chat_memory.add_user_message(interaction["user_message"])
                    self.memory.chat_memory.add_ai_message(interaction["assistant_response"])

                logger.info(f"Loaded existing session with {len(interactions)} interactions")

            except Exception as e:
                logger.error(f"Error loading session: {e}")

    def reset_conversation(self):
        """Clear conversation history"""
        self.memory.clear()
        logger.info(f"Conversation history cleared for session {self.session_id}")

    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get formatted conversation history"""
        history = []

        if hasattr(self.memory, 'chat_memory'):
            messages = self.memory.chat_memory.messages

            for i in range(0, len(messages), 2):
                if i + 1 < len(messages):
                    history.append({
                        "user": messages[i].content,
                        "assistant": messages[i + 1].content
                    })

        return history

    def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics"""
        return {
            "session_id": self.session_id,
            "total_messages": self.session_metadata["total_messages"],
            "total_tokens": self.session_metadata["total_tokens"],
            "total_cost": self.session_metadata["total_cost"],
            "average_tokens_per_message": (
                self.session_metadata["total_tokens"] / self.session_metadata["total_messages"]
                if self.session_metadata["total_messages"] > 0 else 0
            ),
            "created_at": self.session_metadata["created_at"],
            "conversation_length": len(self.get_conversation_history())
        }

    def add_user_feedback(self, message_number: int, rating: int, comment: str = ""):
        """
        Add user feedback for a specific message

        Args:
            message_number: Message number to rate
            rating: Rating (1-5)
            comment: Optional feedback comment
        """
        session_file = os.path.join(self.session_dir, f"{self.session_id}.json")

        if os.path.exists(session_file):
            try:
                with open(session_file, 'r') as f:
                    session_data = json.load(f)

                if message_number <= len(session_data["interactions"]):
                    session_data["interactions"][message_number - 1]["feedback"] = {
                        "rating": rating,
                        "comment": comment,
                        "timestamp": datetime.now().isoformat()
                    }

                    with open(session_file, 'w') as f:
                        json.dump(session_data, f, indent=2)

                    logger.info(f"Feedback added for message {message_number}")

            except Exception as e:
                logger.error(f"Error adding feedback: {e}")

    def export_conversation(self, format: str = "json") -> str:
        """
        Export conversation in various formats

        Args:
            format: Export format ('json', 'txt', 'html')

        Returns:
            Exported content as string
        """
        history = self.get_conversation_history()

        if format == "json":
            return json.dumps({
                "session_stats": self.get_session_stats(),
                "conversation": history
            }, indent=2)

        elif format == "txt":
            lines = [f"Legal Chatbot Session: {self.session_id}\n"]
            lines.append(f"Created: {self.session_metadata['created_at']}\n")
            lines.append("=" * 80 + "\n\n")

            for i, turn in enumerate(history, 1):
                lines.append(f"User ({i}): {turn['user']}\n")
                lines.append(f"Assistant ({i}): {turn['assistant']}\n")
                lines.append("-" * 80 + "\n")

            return "".join(lines)

        elif format == "html":
            html = f"""
            <html>
            <head><title>Legal Chatbot Session {self.session_id}</title></head>
            <body>
            <h1>Legal Chatbot Conversation</h1>
            <p><strong>Session ID:</strong> {self.session_id}</p>
            <p><strong>Created:</strong> {self.session_metadata['created_at']}</p>
            <hr>
            """

            for i, turn in enumerate(history, 1):
                html += f"""
                <div style="margin: 20px 0;">
                    <p><strong>User:</strong> {turn['user']}</p>
                    <p><strong>Assistant:</strong> {turn['assistant']}</p>
                    <hr>
                </div>
                """

            html += "</body></html>"
            return html

        else:
            raise ValueError(f"Unsupported export format: {format}")


# Example usage
if __name__ == "__main__":
    from langchain.vectorstores import FAISS
    from langchain.embeddings import OpenAIEmbeddings

    # Initialize vector store (in production, load from disk)
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.load_local("/path/to/vectorstore", embeddings)

    # Create chatbot instance
    chatbot = LegalChatbot(
        vectorstore=vectorstore,
        session_dir="./chat_sessions",
        memory_type="buffer",
        max_history_length=10
    )

    # Interactive chat loop
    print(f"Legal Chatbot Session: {chatbot.session_id}")
    print("Type 'quit' to exit, 'stats' for statistics, 'export' to export conversation\n")

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() == 'quit':
            break
        elif user_input.lower() == 'stats':
            stats = chatbot.get_session_stats()
            print(json.dumps(stats, indent=2))
            continue
        elif user_input.lower() == 'export':
            exported = chatbot.export_conversation(format="txt")
            print(exported)
            continue

        response = chatbot.chat(user_input)

        if "error" in response:
            print(f"Error: {response['error']}")
        else:
            print(f"\nAssistant: {response['response']}")
            print(f"Sources used: {response['num_sources']}")
            print(f"Tokens: {response['metadata']['tokens_used']}\n")
