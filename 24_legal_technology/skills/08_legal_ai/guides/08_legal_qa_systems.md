# Legal Question Answering Systems

## Overview
Build systems that answer legal questions from documents.

## Architecture
1. **Document Indexing**: Create searchable knowledge base
2. **Query Understanding**: Parse user question
3. **Retrieval**: Find relevant passages
4. **Answer Generation**: Synthesize answer with citations

## Implementation: RAG-based

### Step 1: Index Documents
```python
from langchain.vectorstores import Pinecone
from langchain.embeddings import OpenAIEmbeddings

embeddings = OpenAIEmbeddings()
vectorstore = Pinecone.from_documents(
    legal_documents,
    embeddings,
    index_name="legal-kb"
)
```

### Step 2: Create QA Chain
```python
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI

qa_chain = RetrievalQA.from_chain_type(
    llm=OpenAI(temperature=0),
    retriever=vectorstore.as_retriever(),
    return_source_documents=True
)
```

### Step 3: Query
```python
result = qa_chain({"query": "What is the liability cap?"})
answer = result['result']
sources = result['source_documents']
```

## Best Practices
- Always return source documents for verification
- Use low temperature (0-0.3) for factual accuracy
- Implement citation checking
- Human review for critical questions
