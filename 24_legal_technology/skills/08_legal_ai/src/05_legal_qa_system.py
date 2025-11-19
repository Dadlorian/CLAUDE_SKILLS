"""
Legal Question Answering System using RAG
Answer legal questions with citations from legal documents
"""

from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.llms import OpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

class LegalQASystem:
    """Question answering system for legal queries"""

    def __init__(self, documents_path=None):
        self.embeddings = OpenAIEmbeddings()
        self.llm = OpenAI(temperature=0)

        # Load or create vector store
        if documents_path:
            self.vectorstore = self.load_documents(documents_path)
        else:
            self.vectorstore = None

        # Create QA chain
        self.qa_chain = self.create_qa_chain()

    def create_qa_chain(self):
        """Create QA chain with legal-specific prompt"""

        prompt_template = """You are a legal research assistant. Use the following legal sources to answer the question.
If you cannot find the answer in the sources, say so clearly.

Legal Sources:
{context}

Question: {question}

Provide your answer with citations to the relevant sources. Format: [Source: Document Name, Section X]

Answer:"""

        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )

        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(search_kwargs={"k": 3}),
            chain_type_kwargs={"prompt": PROMPT},
            return_source_documents=True
        )

        return qa_chain

    def answer_question(self, question):
        """Answer legal question with sources"""

        result = self.qa_chain({"query": question})

        return {
            "question": question,
            "answer": result['result'],
            "sources": result['source_documents']
        }
