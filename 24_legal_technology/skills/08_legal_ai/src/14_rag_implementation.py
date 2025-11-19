"""
RAG Implementation for Legal Research
Complete Retrieval-Augmented Generation system
"""

from langchain.vectorstores import Pinecone
from langchain.embeddings import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.chains import RetrievalQA
import pinecone

class LegalRAGSystem:
    """Complete RAG system for legal research"""

    def __init__(self, pinecone_key, openai_key, index_name="legal-kb"):
        # Initialize Pinecone
        pinecone.init(api_key=pinecone_key, environment="us-west1-gcp")

        # Initialize embeddings and LLM
        self.embeddings = OpenAIEmbeddings(openai_api_key=openai_key)
        self.llm = OpenAI(temperature=0, openai_api_key=openai_key)

        # Load or create index
        self.vectorstore = Pinecone.from_existing_index(
            index_name=index_name,
            embedding=self.embeddings
        )

        # Create QA chain
        self.qa_chain = self.create_qa_chain()

    def create_qa_chain(self):
        """Create retrieval QA chain"""

        return RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(search_kwargs={"k": 5}),
            return_source_documents=True
        )

    def query(self, question):
        """Query the legal knowledge base"""

        result = self.qa_chain({"query": question})

        return {
            "answer": result['result'],
            "sources": [
                {
                    "content": doc.page_content[:200],
                    "metadata": doc.metadata
                }
                for doc in result['source_documents']
            ]
        }
