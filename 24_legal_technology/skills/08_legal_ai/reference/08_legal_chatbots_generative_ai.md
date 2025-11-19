# Legal Chatbots and Generative AI

## Overview
Legal chatbots and generative AI systems provide interactive legal assistance, from answering basic legal questions to drafting complex documents. These range from consumer-facing bots for access to justice to enterprise systems for legal departments.

## Legal Chatbot Applications

### 1. Consumer Legal Chatbots

#### DoNotPay
**"The World's First Robot Lawyer"**

**Capabilities**:
- Fight parking tickets
- Cancel subscriptions
- Sue robocallers
- Generate legal documents
- Navigate small claims court
- Negotiate bills

```python
class ConsumerLegalBot:
    """Consumer-facing legal chatbot"""

    def __init__(self):
        self.knowledge_base = self.load_knowledge_base()
        self.document_templates = self.load_templates()

    def handle_parking_ticket(self, user_input):
        """Help user contest parking ticket"""

        # Gather information
        conversation = [
            {"question": "What city was the ticket issued in?", "type": "text"},
            {"question": "What was the violation code?", "type": "text"},
            {"question": "Upload photo of parking sign", "type": "image"},
            {"question": "Upload photo of your vehicle's position", "type": "image"}
        ]

        user_data = self.collect_information(conversation)

        # Analyze ticket validity
        analysis = self.analyze_ticket(user_data)

        if analysis['contestable']:
            # Generate appeal letter
            appeal = self.generate_appeal_letter(user_data, analysis['grounds'])

            return {
                "recommendation": "Contest this ticket",
                "success_probability": analysis['success_rate'],
                "grounds": analysis['grounds'],
                "appeal_letter": appeal,
                "filing_instructions": self.get_filing_instructions(user_data['city'])
            }
        else:
            return {
                "recommendation": "Pay the ticket",
                "reason": analysis['reason']
            }

    def analyze_ticket(self, ticket_data):
        """Analyze if ticket is contestable"""

        # Check common defenses
        defenses = []

        # Signage issues
        if self.analyze_image(ticket_data['sign_photo'], 'visibility') < 0.7:
            defenses.append("Inadequate signage visibility")

        # Vehicle position
        if self.check_vehicle_position(ticket_data['vehicle_photo'], ticket_data['violation']):
            defenses.append("Vehicle was legally parked")

        # Violation code validity
        if not self.is_valid_violation(ticket_data['violation_code'], ticket_data['city']):
            defenses.append("Invalid violation code")

        return {
            "contestable": len(defenses) > 0,
            "grounds": defenses,
            "success_rate": self.estimate_success_rate(defenses, ticket_data['city']),
            "reason": "Valid ticket, no clear defenses" if not defenses else None
        }

# Usage
bot = ConsumerLegalBot()

ticket_case = {
    "city": "San Francisco",
    "violation_code": "22502A",
    "sign_photo": "path/to/sign.jpg",
    "vehicle_photo": "path/to/car.jpg"
}

result = bot.handle_parking_ticket(ticket_case)
if result['recommendation'] == "Contest this ticket":
    print(f"Success Probability: {result['success_probability']:.0%}")
    print(f"Grounds: {', '.join(result['grounds'])}")
    print(f"\n{result['appeal_letter']}")
```

#### LawDroid
**Focus**: Legal automation and chatbot builder

### 2. Enterprise Legal Chatbots

```python
class EnterpriseLegalChatbot:
    """Internal legal department chatbot"""

    def __init__(self, model="gpt-4"):
        self.llm = ChatOpenAI(model=model, temperature=0.3)
        self.knowledge_base = self.load_company_policies()
        self.contract_templates = self.load_templates()

    def handle_employee_question(self, question, employee_context):
        """Answer employee legal questions"""

        # Classify question type
        question_type = self.classify_question(question)

        if question_type == "policy_question":
            return self.answer_policy_question(question, employee_context)
        elif question_type == "contract_request":
            return self.handle_contract_request(question, employee_context)
        elif question_type == "compliance_question":
            return self.answer_compliance_question(question)
        elif question_type == "escalation_needed":
            return self.escalate_to_attorney(question, employee_context)

    def answer_policy_question(self, question, context):
        """Answer using company policy knowledge base"""

        # Retrieve relevant policies
        relevant_policies = self.retrieve_policies(question)

        # Generate answer
        prompt = f"""
You are a helpful legal assistant for our company's employees.

Employee Question: {question}

Employee Context:
- Department: {context['department']}
- Location: {context['location']}
- Role: {context['role']}

Relevant Company Policies:
{relevant_policies}

Provide a clear, accurate answer based on company policy. If the policy
doesn't fully address the question, say so and recommend contacting legal.
"""

        response = self.llm.predict(prompt)

        return {
            "answer": response,
            "sources": [p['title'] for p in relevant_policies],
            "confidence": self.assess_confidence(response, relevant_policies),
            "escalate": self.should_escalate(question, response)
        }

    def handle_contract_request(self, request, context):
        """Handle NDA and simple contract requests"""

        # Determine contract type
        contract_type = self.determine_contract_type(request)

        if contract_type in ["NDA", "Simple_Vendor_Agreement"]:
            # Can auto-generate
            contract = self.generate_contract(contract_type, self.extract_parameters(request))

            return {
                "status": "draft_generated",
                "contract": contract,
                "next_steps": "Please review and click 'Send for Signature' if approved",
                "requires_legal_review": False
            }
        else:
            # Escalate to legal
            return {
                "status": "escalated",
                "message": "This request requires attorney review",
                "ticket_number": self.create_legal_ticket(request, context),
                "estimated_response": "2 business days"
            }

# Usage
chatbot = EnterpriseLegalChatbot()

question = "Can I sign an NDA with a vendor?"
employee = {
    "department": "Sales",
    "location": "US-CA",
    "role": "Account Executive"
}

response = chatbot.handle_employee_question(question, employee)
print(response['answer'])
```

## Generative AI for Legal Drafting

### 1. Document Generation

```python
class LegalDocumentGenerator:
    """Generate legal documents using LLMs"""

    def __init__(self, model="gpt-4"):
        import openai
        self.model = model
        self.templates = self.load_templates()

    def generate_contract(self, contract_type, parameters, jurisdiction="Delaware"):
        """Generate contract from parameters"""

        # Load relevant precedents
        precedents = self.get_precedents(contract_type, jurisdiction)

        # Create generation prompt
        prompt = self.create_prompt(contract_type, parameters, precedents, jurisdiction)

        # Generate contract
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": """You are an expert corporate attorney. Generate accurate,
                    professional legal documents. Use proper legal terminology and formatting.
                    Flag any ambiguities or missing information."""
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,  # Low temperature for consistency
            max_tokens=4000
        )

        generated_contract = response.choices[0].message.content

        # Post-process
        final_contract = self.post_process(generated_contract, parameters)

        # Validate
        validation = self.validate_contract(final_contract, contract_type)

        return {
            "contract": final_contract,
            "validation": validation,
            "requires_review": True,  # Always require human review
            "missing_info": self.check_missing_info(generated_contract),
            "risk_flags": self.identify_risks(generated_contract)
        }

    def create_prompt(self, contract_type, parameters, precedents, jurisdiction):
        """Create detailed prompt for contract generation"""

        prompt = f"""
Generate a {contract_type} governed by {jurisdiction} law with the following parameters:

PARTIES:
"""
        for key, value in parameters.items():
            prompt += f"- {key}: {value}\n"

        prompt += f"""
PRECEDENT CLAUSES (use as reference):
{self.format_precedents(precedents)}

REQUIREMENTS:
1. Include all standard clauses for {contract_type}
2. Use clear, unambiguous language
3. Ensure balanced terms (neither party overly favored)
4. Include appropriate definitions section
5. Use {jurisdiction} law conventions
6. Number sections hierarchically
7. Include signature blocks

Generate the complete contract:
"""
        return prompt

    def validate_contract(self, contract, contract_type):
        """Validate generated contract"""

        required_sections = self.get_required_sections(contract_type)
        present_sections = self.identify_sections(contract)

        missing_sections = [s for s in required_sections if s not in present_sections]

        return {
            "complete": len(missing_sections) == 0,
            "missing_sections": missing_sections,
            "has_definitions": "definition" in contract.lower(),
            "has_signatures": "signature" in contract.lower() or "executed" in contract.lower(),
            "word_count": len(contract.split()),
            "readability_score": self.assess_readability(contract)
        }

# Usage
generator = LegalDocumentGenerator()

nda_params = {
    "Disclosing_Party": "Acme Corporation, a Delaware corporation",
    "Receiving_Party": "Widget Industries, Inc., a California corporation",
    "Effective_Date": "January 15, 2024",
    "Purpose": "Evaluation of potential business relationship",
    "Confidentiality_Period": "3 years from Effective Date",
    "Mutual": "Yes",
    "Governing_Law": "Delaware"
}

result = generator.generate_contract("NDA", nda_params, "Delaware")

print(result['contract'])
print(f"\nValidation: {'PASS' if result['validation']['complete'] else 'FAIL'}")
if result['missing_info']:
    print(f"Missing Info: {result['missing_info']}")
```

### 2. Legal Memorandum Generation

```python
class LegalMemoGenerator:
    """Generate legal memoranda using AI"""

    def __init__(self):
        self.llm = ChatAnthropic(model="claude-3-opus-20240229")
        self.legal_research_api = LegalResearchAPI()

    def generate_memo(self, issue, facts, jurisdiction):
        """Generate legal memorandum"""

        # Step 1: Conduct legal research
        research = self.conduct_research(issue, jurisdiction)

        # Step 2: Generate memo structure
        outline = self.create_outline(issue, facts, research)

        # Step 3: Generate each section
        memo_sections = {}

        for section in outline:
            memo_sections[section] = self.generate_section(
                section,
                issue,
                facts,
                research
            )

        # Step 4: Assemble memo
        full_memo = self.assemble_memo(memo_sections)

        # Step 5: Citation check
        citations = self.verify_citations(full_memo)

        return {
            "memo": full_memo,
            "citation_verification": citations,
            "confidence": self.assess_confidence(research),
            "additional_research_needed": self.identify_gaps(full_memo, research)
        }

    def conduct_research(self, issue, jurisdiction):
        """Research relevant law"""

        # Query legal databases
        cases = self.legal_research_api.search_cases(issue, jurisdiction)
        statutes = self.legal_research_api.search_statutes(issue, jurisdiction)
        secondary_sources = self.legal_research_api.search_secondary(issue)

        return {
            "cases": cases,
            "statutes": statutes,
            "secondary_sources": secondary_sources
        }

    def create_outline(self, issue, facts, research):
        """Generate memo outline"""

        prompt = f"""
Create an outline for a legal memorandum addressing this issue:

ISSUE: {issue}

FACTS: {facts}

APPLICABLE LAW:
{self.summarize_research(research)}

Generate a detailed outline following this structure:
1. Question Presented
2. Brief Answer
3. Facts
4. Discussion
   a. Legal Standard
   b. Analysis
   c. Counterarguments
5. Conclusion
"""

        response = self.llm.predict(prompt)
        return self.parse_outline(response)

    def generate_section(self, section_name, issue, facts, research):
        """Generate individual memo section"""

        section_prompts = {
            "Question Presented": f"Draft a concise question presented for: {issue}",

            "Brief Answer": f"""
Provide a brief answer to: {issue}

Based on: {self.summarize_research(research)}
""",

            "Discussion": f"""
Draft the Discussion section of a legal memorandum.

ISSUE: {issue}
FACTS: {facts}
APPLICABLE LAW: {self.format_research_for_discussion(research)}

Structure:
1. State the legal standard
2. Apply law to facts
3. Address counterarguments
4. Reach conclusion

Use proper legal citation format (Bluebook).
"""
        }

        prompt = section_prompts.get(section_name, f"Draft the {section_name} section")
        return self.llm.predict(prompt)

# Usage
memo_gen = LegalMemoGenerator()

legal_issue = "Whether an arbitration clause in a clickwrap agreement is enforceable under Delaware law"

facts = """
Client operates a SaaS platform. Users must click "I Agree" to terms containing
an arbitration clause. The clause requires arbitration in Delaware. A user filed
a class action lawsuit in California state court. Client moves to compel arbitration.
"""

memo = memo_gen.generate_memo(legal_issue, facts, "Delaware")
print(memo['memo'])
```

### 3. RAG (Retrieval-Augmented Generation) for Legal

```python
from langchain.vectorstores import Pinecone
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA

class LegalRAGSystem:
    """RAG system for legal question answering"""

    def __init__(self, index_name="legal-knowledge-base"):
        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings()

        # Connect to vector database
        self.vectorstore = Pinecone.from_existing_index(
            index_name=index_name,
            embedding=self.embeddings
        )

        # Initialize LLM
        self.llm = ChatOpenAI(model="gpt-4", temperature=0)

        # Create QA chain
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(
                search_kwargs={"k": 5}  # Retrieve top 5 most relevant docs
            ),
            return_source_documents=True
        )

    def ingest_legal_documents(self, documents):
        """Add legal documents to knowledge base"""

        from langchain.text_splitter import RecursiveCharacterTextSplitter

        # Split documents
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", " "]
        )

        splits = []
        for doc in documents:
            chunks = text_splitter.split_text(doc['text'])
            for i, chunk in enumerate(chunks):
                splits.append({
                    "text": chunk,
                    "metadata": {
                        "source": doc['source'],
                        "doc_id": doc['id'],
                        "chunk_id": i,
                        "doc_type": doc['type']
                    }
                })

        # Add to vector store
        self.vectorstore.add_texts(
            texts=[s['text'] for s in splits],
            metadatas=[s['metadata'] for s in splits]
        )

    def query(self, question, filters=None):
        """Query the legal knowledge base"""

        # Apply metadata filters if provided
        if filters:
            retriever = self.vectorstore.as_retriever(
                search_kwargs={"k": 5, "filter": filters}
            )
            qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=retriever,
                return_source_documents=True
            )
            result = qa_chain({"query": question})
        else:
            result = self.qa_chain({"query": question})

        # Format response
        return {
            "answer": result['result'],
            "sources": [
                {
                    "text": doc.page_content[:200] + "...",
                    "metadata": doc.metadata
                }
                for doc in result['source_documents']
            ],
            "confidence": self.estimate_confidence(result)
        }

# Usage
rag = LegalRAGSystem()

# Ingest firm's legal knowledge
documents = [
    {
        "id": "memo_001",
        "type": "legal_memo",
        "source": "2023 GDPR Analysis",
        "text": "Our analysis of GDPR requirements for data processing..."
    },
    {
        "id": "precedent_001",
        "type": "contract_template",
        "source": "Standard NDA Template",
        "text": "This template NDA has been approved for use with..."
    }
]

rag.ingest_legal_documents(documents)

# Query the knowledge base
response = rag.query(
    "What are our standard GDPR data processing requirements?",
    filters={"doc_type": "legal_memo"}
)

print(f"Answer: {response['answer']}\n")
print("Sources:")
for source in response['sources']:
    print(f"- {source['metadata']['source']}")
```

## Best Practices

### 1. Always Require Human Review
```python
class LegalAIWithOversight:
    """AI system with mandatory human review"""

    def generate_document(self, params):
        # Generate draft
        draft = self.llm_generate(params)

        # Create review workflow
        review_ticket = {
            "document": draft,
            "ai_generated": True,
            "requires_attorney_approval": True,
            "risk_level": self.assess_risk(draft),
            "estimated_review_time": "15 minutes"
        }

        # Route based on risk
        if review_ticket['risk_level'] == "high":
            review_ticket['assigned_to'] = "senior_partner"
        else:
            review_ticket['assigned_to'] = "associate"

        return review_ticket
```

### 2. Citation Verification
```python
def verify_legal_citations(text):
    """Verify all legal citations are accurate"""

    citations = extract_citations(text)
    verification_results = []

    for citation in citations:
        # Look up in legal database
        case = legal_db.lookup(citation)

        verification_results.append({
            "citation": citation,
            "exists": case is not None,
            "accurate": case.matches_citation(citation) if case else False,
            "proposed_text": text.split(citation)[0][-100:] + citation + text.split(citation)[1][:100]
        })

    return verification_results
```

### 3. Hallucination Detection
```python
def detect_hallucinations(generated_text, source_documents):
    """Check for unsupported claims"""

    claims = extract_factual_claims(generated_text)
    unsupported_claims = []

    for claim in claims:
        # Check if claim is supported by source documents
        supported = any(
            claim_appears_in(claim, doc)
            for doc in source_documents
        )

        if not supported:
            unsupported_claims.append(claim)

    return {
        "hallucination_detected": len(unsupported_claims) > 0,
        "unsupported_claims": unsupported_claims,
        "requires_verification": unsupported_claims
    }
```

## Resources

### Consumer Chatbots
- **DoNotPay**: https://donotpay.com
- **LawDroid**: https://lawdroid.com
- **AILIRA**: https://ailira.com

### Enterprise Solutions
- **Harvey**: https://harvey.ai
- **CoCounsel** (Casetext): https://casetext.com/cocounsel

### Open Source
- **LegalBench**: Legal reasoning benchmark
- **LawGPT**: Open-source legal AI models

---

*Legal chatbots and generative AI are transforming access to legal services and attorney productivity, but must always be deployed with appropriate human oversight and validation.*
