"""
Legal Question Answering System using RAG
Answer legal questions with citations from legal documents
"""

import os
import logging
from typing import List, Dict, Optional, Any
from pathlib import Path
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.llms import OpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.document_loaders import (
    PyPDFLoader,
    TextLoader,
    UnstructuredWordDocumentLoader,
    DirectoryLoader
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.callbacks import get_openai_callback
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LegalQASystem:
    """
    Production-ready Question Answering System for legal queries

    Features:
    - Multi-format document loading (PDF, DOCX, TXT)
    - Intelligent chunking with overlap
    - Vector store persistence
    - Cost tracking
    - Confidence scoring
    - Source attribution
    """

    def __init__(
        self,
        documents_path: Optional[str] = None,
        vectorstore_path: Optional[str] = None,
        model_name: str = "gpt-3.5-turbo",
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ):
        """
        Initialize Legal QA System

        Args:
            documents_path: Path to documents directory
            vectorstore_path: Path to save/load vector store
            model_name: OpenAI model to use
            chunk_size: Size of text chunks for processing
            chunk_overlap: Overlap between chunks
        """
        self.embeddings = OpenAIEmbeddings()
        self.llm = OpenAI(temperature=0, model_name=model_name)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.vectorstore_path = vectorstore_path
        self.usage_stats = {"total_tokens": 0, "total_cost": 0.0}

        # Load or create vector store
        if vectorstore_path and os.path.exists(vectorstore_path):
            logger.info(f"Loading existing vector store from {vectorstore_path}")
            self.vectorstore = FAISS.load_local(vectorstore_path, self.embeddings)
        elif documents_path:
            logger.info(f"Creating new vector store from {documents_path}")
            self.vectorstore = self.load_documents(documents_path)
            if vectorstore_path:
                self.save_vectorstore()
        else:
            raise ValueError("Must provide either documents_path or vectorstore_path")

        # Create QA chain
        self.qa_chain = self.create_qa_chain()

    def load_documents(self, documents_path: str) -> FAISS:
        """
        Load documents from various formats and create vector store

        Args:
            documents_path: Path to documents or directory

        Returns:
            FAISS vector store
        """
        documents = []
        path = Path(documents_path)

        if path.is_file():
            documents = self._load_single_document(str(path))
        elif path.is_dir():
            # Load all supported file types
            for ext, loader_cls in [
                ("pdf", PyPDFLoader),
                ("txt", TextLoader),
                ("docx", UnstructuredWordDocumentLoader)
            ]:
                pattern = f"**/*.{ext}"
                try:
                    loader = DirectoryLoader(
                        documents_path,
                        glob=pattern,
                        loader_cls=loader_cls
                    )
                    docs = loader.load()
                    documents.extend(docs)
                    logger.info(f"Loaded {len(docs)} {ext.upper()} documents")
                except Exception as e:
                    logger.warning(f"Error loading {ext} files: {e}")

        if not documents:
            raise ValueError(f"No documents found in {documents_path}")

        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        splits = text_splitter.split_documents(documents)
        logger.info(f"Created {len(splits)} text chunks from {len(documents)} documents")

        # Create vector store
        vectorstore = FAISS.from_documents(splits, self.embeddings)
        return vectorstore

    def _load_single_document(self, file_path: str) -> List:
        """Load a single document based on file extension"""
        ext = Path(file_path).suffix.lower()

        loaders = {
            '.pdf': PyPDFLoader,
            '.txt': TextLoader,
            '.docx': UnstructuredWordDocumentLoader
        }

        loader_cls = loaders.get(ext)
        if not loader_cls:
            raise ValueError(f"Unsupported file type: {ext}")

        loader = loader_cls(file_path)
        return loader.load()

    def save_vectorstore(self):
        """Save vector store to disk"""
        if self.vectorstore_path:
            self.vectorstore.save_local(self.vectorstore_path)
            logger.info(f"Vector store saved to {self.vectorstore_path}")

    def create_qa_chain(self) -> RetrievalQA:
        """Create QA chain with legal-specific prompt"""

        prompt_template = """You are a legal research assistant. Use the following legal sources to answer the question.
If you cannot find the answer in the sources, say so clearly. Do not make up information.

Legal Sources:
{context}

Question: {question}

Instructions:
1. Provide a clear, accurate answer based solely on the sources
2. Include specific citations in format [Source: Document Name, Page/Section]
3. If multiple sources support your answer, cite all relevant sources
4. If the sources don't contain enough information, state this clearly
5. Use precise legal terminology where appropriate

Answer:"""

        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )

        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 5}
            ),
            chain_type_kwargs={"prompt": PROMPT},
            return_source_documents=True
        )

        return qa_chain

    def answer_question(
        self,
        question: str,
        include_metadata: bool = True
    ) -> Dict[str, Any]:
        """
        Answer legal question with sources and metadata

        Args:
            question: Legal question to answer
            include_metadata: Whether to include usage stats and metadata

        Returns:
            Dictionary with answer, sources, and optional metadata
        """
        if not question or not question.strip():
            raise ValueError("Question cannot be empty")

        logger.info(f"Processing question: {question[:100]}...")

        # Track API usage
        with get_openai_callback() as cb:
            result = self.qa_chain({"query": question})

            # Update usage stats
            self.usage_stats["total_tokens"] += cb.total_tokens
            self.usage_stats["total_cost"] += cb.total_cost

        response = {
            "question": question,
            "answer": result['result'],
            "sources": self._format_sources(result['source_documents']),
            "num_sources": len(result['source_documents'])
        }

        if include_metadata:
            response["metadata"] = {
                "tokens_used": cb.total_tokens,
                "cost": cb.total_cost,
                "model": self.llm.model_name
            }

        return response

    def _format_sources(self, source_documents: List) -> List[Dict[str, str]]:
        """Format source documents for better readability"""
        formatted = []
        for doc in source_documents:
            source = {
                "content": doc.page_content[:500],  # First 500 chars
                "metadata": doc.metadata
            }
            formatted.append(source)
        return formatted

    def batch_answer(
        self,
        questions: List[str],
        save_results: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Answer multiple questions in batch

        Args:
            questions: List of questions to answer
            save_results: Optional path to save results JSON

        Returns:
            List of answer dictionaries
        """
        results = []

        for i, question in enumerate(questions, 1):
            logger.info(f"Processing question {i}/{len(questions)}")
            try:
                result = self.answer_question(question)
                results.append(result)
            except Exception as e:
                logger.error(f"Error processing question {i}: {e}")
                results.append({
                    "question": question,
                    "error": str(e)
                })

        if save_results:
            with open(save_results, 'w') as f:
                json.dump(results, f, indent=2)
            logger.info(f"Results saved to {save_results}")

        return results

    def add_documents(self, documents_path: str):
        """Add more documents to existing vector store"""
        new_vectorstore = self.load_documents(documents_path)
        self.vectorstore.merge_from(new_vectorstore)
        logger.info("New documents added to vector store")

        if self.vectorstore_path:
            self.save_vectorstore()

    def get_usage_stats(self) -> Dict[str, Any]:
        """Get API usage statistics"""
        return self.usage_stats.copy()

    def search_similar(
        self,
        query: str,
        k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents without generating an answer

        Args:
            query: Search query
            k: Number of results to return

        Returns:
            List of similar documents with scores
        """
        docs = self.vectorstore.similarity_search_with_score(query, k=k)

        results = []
        for doc, score in docs:
            results.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "similarity_score": float(score)
            })

        return results


# Example usage and testing
if __name__ == "__main__":
    # Initialize system
    qa_system = LegalQASystem(
        documents_path="/path/to/legal/documents",
        vectorstore_path="/path/to/vectorstore",
        chunk_size=1000,
        chunk_overlap=200
    )

    # Single question
    result = qa_system.answer_question(
        "What are the requirements for a valid contract?"
    )
    print(f"Answer: {result['answer']}")
    print(f"Sources: {len(result['sources'])}")

    # Batch processing
    questions = [
        "What is force majeure?",
        "What are liquidated damages?",
        "What constitutes breach of contract?"
    ]
    results = qa_system.batch_answer(questions, save_results="qa_results.json")

    # Get usage statistics
    stats = qa_system.get_usage_stats()
    print(f"Total tokens used: {stats['total_tokens']}")
    print(f"Total cost: ${stats['total_cost']:.4f}")
