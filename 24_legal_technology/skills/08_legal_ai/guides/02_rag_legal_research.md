# RAG for Legal Research

## Overview
Retrieval-Augmented Generation (RAG) combines the power of large language models with precise legal document retrieval to create accurate, citation-backed legal research systems.

## Architecture

```
┌──────────────────────────────────────────────────┐
│              RAG Legal System                    │
├──────────────────────────────────────────────────┤
│  1. INGESTION                                    │
│     → Legal documents (cases, statutes, memos)   │
│     → Chunk into passages                        │
│     → Generate embeddings                        │
│     → Store in vector database                   │
├──────────────────────────────────────────────────┤
│  2. RETRIEVAL                                    │
│     → User query                                 │
│     → Embed query                                │
│     → Semantic search in vector DB               │
│     → Retrieve top-k relevant passages           │
├──────────────────────────────────────────────────┤
│  3. GENERATION                                   │
│     → Combine query + retrieved passages         │
│     → LLM generates answer                       │
│     → Include citations                          │
│     → Return response + sources                  │
└──────────────────────────────────────────────────┘
```

## Implementation

### Step 1: Document Ingestion

```python
from langchain.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Pinecone
import pinecone

class LegalDocumentIngestion:
    """Ingest legal documents into RAG system"""

    def __init__(self, pinecone_api_key, openai_api_key):
        # Initialize Pinecone
        pinecone.init(api_key=pinecone_api_key, environment="us-west1-gcp")

        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)

        self.index_name = "legal-knowledge-base"

    def ingest_legal_documents(self, directory_path):
        """Ingest all legal documents from directory"""

        # Load documents
        loader = DirectoryLoader(
            directory_path,
            glob="**/*.pdf",
            loader_cls=PyPDFLoader
        )
        documents = loader.load()

        print(f"Loaded {len(documents)} documents")

        # Split documents
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

        splits = text_splitter.split_documents(documents)
        print(f"Created {len(splits)} chunks")

        # Add metadata
        for i, split in enumerate(splits):
            split.metadata.update({
                "chunk_id": i,
                "doc_type": self.classify_document(split.page_content),
                "jurisdiction": self.extract_jurisdiction(split.page_content),
                "citations": self.extract_citations(split.page_content)
            })

        # Create vector store
        vectorstore = Pinecone.from_documents(
            documents=splits,
            embedding=self.embeddings,
            index_name=self.index_name
        )

        return vectorstore

    def classify_document(self, text):
        """Classify type of legal document"""
        if any(word in text.lower() for word in ["plaintiff", "defendant", "court"]):
            return "case_law"
        elif any(word in text.lower() for word in ["section", "statute", "code"]):
            return "statute"
        elif "agreement" in text.lower() or "contract" in text.lower():
            return "contract"
        else:
            return "other"

    def extract_jurisdiction(self, text):
        """Extract jurisdiction from text"""
        import re

        # Common court patterns
        courts = {
            r"Supreme Court": "SCOTUS",
            r"(\d+)(?:st|nd|rd|th) Circuit": "Circuit",
            r"([A-Z]{2}) Court of Appeals": "State Appellate",
            r"District Court": "District"
        }

        for pattern, jurisdiction in courts.items():
            if re.search(pattern, text):
                return jurisdiction

        return "Unknown"

    def extract_citations(self, text):
        """Extract legal citations from text"""
        import re

        # Simplified citation patterns
        patterns = [
            r"\d+\s+U\.S\.\s+\d+",  # Supreme Court
            r"\d+\s+F\.\d+[d]?\s+\d+",  # Federal
            r"\d+\s+S\.Ct\.\s+\d+"  # Supreme Court Reporter
        ]

        citations = []
        for pattern in patterns:
            citations.extend(re.findall(pattern, text))

        return list(set(citations))

# Usage
ingestion = LegalDocumentIngestion(
    pinecone_api_key="your-key",
    openai_api_key="your-key"
)

vectorstore = ingestion.ingest_legal_documents("/path/to/legal/documents")
```

### Step 2: Retrieval

```python
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor

class LegalRetriever:
    """Advanced retrieval for legal documents"""

    def __init__(self, vectorstore, llm):
        self.vectorstore = vectorstore
        self.llm = llm

    def hybrid_search(self, query, k=5):
        """Combine semantic and keyword search"""

        # Semantic search
        semantic_results = self.vectorstore.similarity_search(query, k=k)

        # Keyword search for exact citations
        if self.contains_citation(query):
            citation = self.extract_citation(query)
            keyword_results = self.vectorstore.similarity_search(
                citation,
                k=3,
                filter={"citations": {"$contains": citation}}
            )
            # Merge results
            all_results = semantic_results + keyword_results
            # Deduplicate
            seen = set()
            unique_results = []
            for doc in all_results:
                doc_id = f"{doc.metadata.get('source', '')}_{doc.metadata.get('chunk_id', '')}"
                if doc_id not in seen:
                    seen.add(doc_id)
                    unique_results.append(doc)
            return unique_results[:k]
        else:
            return semantic_results

    def contextual_compression(self, query, k=5):
        """Use LLM to extract only relevant parts"""

        base_retriever = self.vectorstore.as_retriever(search_kwargs={"k": k*2})

        compressor = LLMChainExtractor.from_llm(self.llm)

        compression_retriever = ContextualCompressionRetriever(
            base_compressor=compressor,
            base_retriever=base_retriever
        )

        compressed_docs = compression_retriever.get_relevant_documents(query)

        return compressed_docs

    def multi_query_retrieval(self, query, k=5):
        """Generate multiple query variations for better recall"""

        from langchain.retrievers.multi_query import MultiQueryRetriever

        retriever = MultiQueryRetriever.from_llm(
            retriever=self.vectorstore.as_retriever(search_kwargs={"k": k}),
            llm=self.llm
        )

        docs = retriever.get_relevant_documents(query)
        return docs
```

### Step 3: Generation with Citations

```python
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI

class LegalRAGSystem:
    """Complete RAG system for legal research"""

    def __init__(self, vectorstore):
        self.vectorstore = vectorstore
        self.llm = ChatOpenAI(model="gpt-4", temperature=0)
        self.retriever = LegalRetriever(vectorstore, self.llm)

    def query(self, question, include_analysis=True):
        """Query the legal knowledge base"""

        # Retrieve relevant documents
        docs = self.retriever.hybrid_search(question, k=5)

        # Create context from retrieved docs
        context = self.format_context(docs)

        # Create prompt
        prompt = self.create_legal_prompt(question, context, include_analysis)

        # Generate response
        response = self.llm.predict(prompt)

        # Extract citations
        citations = self.extract_citations_from_response(response, docs)

        return {
            "answer": response,
            "sources": [doc.metadata for doc in docs],
            "citations": citations,
            "confidence": self.assess_confidence(docs, question)
        }

    def format_context(self, docs):
        """Format retrieved documents as context"""

        context = ""
        for i, doc in enumerate(docs, 1):
            context += f"\n[Source {i}]\n"
            context += f"Document: {doc.metadata.get('source', 'Unknown')}\n"
            context += f"Type: {doc.metadata.get('doc_type', 'Unknown')}\n"
            if doc.metadata.get('citations'):
                context += f"Citations: {', '.join(doc.metadata['citations'])}\n"
            context += f"Content: {doc.page_content}\n"
            context += "-" * 80 + "\n"

        return context

    def create_legal_prompt(self, question, context, include_analysis):
        """Create prompt for legal research"""

        prompt = f"""You are a legal research assistant. Answer the following legal question
based ONLY on the provided sources. Include citations to support your answer.

Legal Question:
{question}

Relevant Legal Sources:
{context}

Instructions:
1. Provide a direct answer to the question
2. Support your answer with citations to the sources
3. If the sources don't fully answer the question, clearly state what is missing
4. {"Include legal analysis showing your reasoning" if include_analysis else "Provide a concise answer"}
5. Format citations as [Source X]

Answer:"""

        return prompt

    def assess_confidence(self, docs, question):
        """Assess confidence in answer based on retrieved docs"""

        # Check relevance of top documents
        if not docs:
            return 0.0

        # Simple heuristic: check if question terms appear in top doc
        question_terms = set(question.lower().split())
        top_doc_terms = set(docs[0].page_content.lower().split())

        overlap = len(question_terms.intersection(top_doc_terms))
        confidence = min(1.0, overlap / len(question_terms))

        return confidence

# Usage
rag_system = LegalRAGSystem(vectorstore)

question = "What is the standard for summary judgment under Federal Rule 56?"

result = rag_system.query(question, include_analysis=True)

print(f"Answer:\n{result['answer']}\n")
print(f"Confidence: {result['confidence']:.0%}\n")
print(f"Sources: {len(result['sources'])} documents")
```

## Advanced Features

### Citation Verification

```python
class CitationVerifier:
    """Verify legal citations are accurate"""

    def __init__(self, legal_db_api_key):
        self.api_key = legal_db_api_key

    def verify_citation(self, citation):
        """Verify citation exists and is accurate"""

        # Query Westlaw/Lexis API
        case = self.lookup_case(citation)

        if not case:
            return {
                "valid": False,
                "error": "Citation not found"
            }

        return {
            "valid": True,
            "case_name": case['name'],
            "year": case['year'],
            "court": case['court'],
            "url": case['url']
        }

    def verify_rag_response(self, response):
        """Verify all citations in RAG response"""

        import re

        # Extract citations
        citations = re.findall(r'\d+\s+[A-Z]\.\d+[d]?\s+\d+', response)

        verification_results = []

        for citation in citations:
            result = self.verify_citation(citation)
            verification_results.append({
                "citation": citation,
                "verified": result['valid'],
                "details": result
            })

        all_valid = all(r['verified'] for r in verification_results)

        return {
            "all_citations_valid": all_valid,
            "results": verification_results
        }
```

### Conversational RAG

```python
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain

class ConversationalLegalRAG:
    """RAG with conversation history"""

    def __init__(self, vectorstore):
        self.llm = ChatOpenAI(model="gpt-4", temperature=0)
        self.vectorstore = vectorstore

        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="answer"
        )

        self.qa_chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=vectorstore.as_retriever(search_kwargs={"k": 5}),
            memory=self.memory,
            return_source_documents=True
        )

    def chat(self, question):
        """Have conversation about legal topics"""

        result = self.qa_chain({"question": question})

        return {
            "answer": result['answer'],
            "sources": result['source_documents'],
            "chat_history": result['chat_history']
        }

# Usage
conv_rag = ConversationalLegalRAG(vectorstore)

# Multi-turn conversation
response1 = conv_rag.chat("What is summary judgment?")
print(response1['answer'])

response2 = conv_rag.chat("What is the standard of review for that?")
print(response2['answer'])

response3 = conv_rag.chat("Can you give me an example case?")
print(response3['answer'])
```

## Best Practices

1. **Chunk Size**: Use 500-1000 tokens for legal documents
2. **Overlap**: 100-200 tokens to preserve context
3. **Metadata**: Always include jurisdiction, doc type, citations
4. **Verification**: Verify all AI-generated citations
5. **Human Review**: Require attorney review for all outputs

---

*RAG systems provide the best of both worlds: LLM capabilities with grounded, verifiable legal sources.*
