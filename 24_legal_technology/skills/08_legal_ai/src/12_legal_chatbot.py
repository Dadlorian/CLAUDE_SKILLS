"""
Legal Chatbot with Conversation Memory
Interactive legal assistant for employee questions
"""

from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.llms import OpenAI

class LegalChatbot:
    """Conversational legal assistant"""

    def __init__(self, vectorstore):
        self.llm = OpenAI(temperature=0.3)
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="answer"
        )

        self.qa_chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=vectorstore.as_retriever(),
            memory=self.memory,
            return_source_documents=True
        )

    def chat(self, user_message):
        """Process user message and generate response"""

        result = self.qa_chain({"question": user_message})

        return {
            "response": result['answer'],
            "sources": result['source_documents'],
            "chat_history": result['chat_history']
        }

    def reset_conversation(self):
        """Clear conversation history"""

        self.memory.clear()
