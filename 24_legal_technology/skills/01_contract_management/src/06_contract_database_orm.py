"""
Contract Database ORM - SQLAlchemy models for contract management
Database schema and relationships for CLM system
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey, JSON, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import enum

Base = declarative_base()

class ContractStatus(enum.Enum):
    DRAFT = "Draft"
    IN_NEGOTIATION = "In Negotiation"
    EXECUTED = "Executed"
    ACTIVE = "Active"
    RENEWED = "Renewed"
    EXPIRED = "Expired"
    TERMINATED = "Terminated"

class RiskLevel(enum.Enum):
    LOW = "Low"
    MODERATE = "Moderate"
    HIGH = "High"
    CRITICAL = "Critical"

class Contract(Base):
    """Main contract record"""
    __tablename__ = 'contracts'
    
    id = Column(Integer, primary_key=True)
    reference_number = Column(String(100), unique=True, nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    contract_type = Column(String(100))  # Service Agreement, Purchase, NDA, etc.
    status = Column(Enum(ContractStatus), default=ContractStatus.DRAFT)
    risk_score = Column(Float, default=0.0)
    risk_level = Column(Enum(RiskLevel), default=RiskLevel.MODERATE)
    
    # Key dates
    effective_date = Column(DateTime)
    execution_date = Column(DateTime)
    expiration_date = Column(DateTime)
    renewal_date = Column(DateTime)
    
    # Financial
    contract_value = Column(Float)
    currency = Column(String(3), default='USD')
    payment_terms = Column(String(200))
    
    # Relationships
    primary_party_id = Column(Integer, ForeignKey('parties.id'))
    counterparty_id = Column(Integer, ForeignKey('parties.id'))
    
    # Metadata
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(100))
    
    # Relationships
    primary_party = relationship("Party", foreign_keys=[primary_party_id])
    counterparty = relationship("Party", foreign_keys=[counterparty_id])
    clauses = relationship("Clause", back_populates="contract")
    documents = relationship("Document", back_populates="contract")
    approvals = relationship("Approval", back_populates="contract")

class Party(Base):
    """Contract parties (vendors, clients, etc.)"""
    __tablename__ = 'parties'
    
    id = Column(Integer, primary_key=True)
    legal_name = Column(String(500), nullable=False)
    party_type = Column(String(50))  # Vendor, Client, Internal, Partner
    address = Column(Text)
    contact_email = Column(String(100))
    contact_phone = Column(String(20))
    registration_number = Column(String(100))
    financial_rating = Column(String(20))  # Credit rating
    created_at = Column(DateTime, default=datetime.utcnow)

class Clause(Base):
    """Contract clauses"""
    __tablename__ = 'clauses'
    
    id = Column(Integer, primary_key=True)
    contract_id = Column(Integer, ForeignKey('contracts.id'))
    clause_type = Column(String(100))  # Liability, Termination, Payment, etc.
    title = Column(String(200))
    content = Column(Text)
    risk_score = Column(Float)
    is_standard = Column(Boolean, default=True)
    notes = Column(Text)
    
    contract = relationship("Contract", back_populates="clauses")

class Document(Base):
    """Contract documents and versions"""
    __tablename__ = 'documents'
    
    id = Column(Integer, primary_key=True)
    contract_id = Column(Integer, ForeignKey('contracts.id'))
    version = Column(Integer, default=1)
    filename = Column(String(500))
    file_path = Column(String(1000))
    file_size = Column(Integer)
    file_type = Column(String(10))  # PDF, DOCX, etc.
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    uploaded_by = Column(String(100))
    is_executed = Column(Boolean, default=False)
    signature_date = Column(DateTime)
    
    contract = relationship("Contract", back_populates="documents")

class Approval(Base):
    """Contract approval workflow"""
    __tablename__ = 'approvals'
    
    id = Column(Integer, primary_key=True)
    contract_id = Column(Integer, ForeignKey('contracts.id'))
    approver_name = Column(String(100))
    approver_role = Column(String(100))  # Legal, Finance, Management
    approval_status = Column(String(20))  # Pending, Approved, Rejected
    comments = Column(Text)
    approved_at = Column(DateTime)
    sequence = Column(Integer)  # Approval order
    
    contract = relationship("Contract", back_populates="approvals")

class ContractDatabase:
    """Database operations for contracts"""
    
    def __init__(self, database_url='postgresql://user:password@localhost/contract_db'):
        self.engine = create_engine(database_url)
        self.Session = sessionmaker(bind=self.engine)
    
    def create_tables(self):
        """Create all tables"""
        Base.metadata.create_all(self.engine)
    
    def create_contract(self, **kwargs) -> Contract:
        """Create new contract"""
        session = self.Session()
        contract = Contract(**kwargs)
        session.add(contract)
        session.commit()
        return contract
    
    def get_contract(self, contract_id: int) -> Contract:
        """Retrieve contract by ID"""
        session = self.Session()
        return session.query(Contract).filter(Contract.id == contract_id).first()
    
    def get_expiring_contracts(self, days=90) -> list:
        """Get contracts expiring soon"""
        session = self.Session()
        from sqlalchemy import and_
        from datetime import timedelta
        
        cutoff_date = datetime.utcnow() + timedelta(days=days)
        return session.query(Contract).filter(
            and_(
                Contract.expiration_date <= cutoff_date,
                Contract.expiration_date > datetime.utcnow(),
                Contract.status != ContractStatus.EXPIRED
            )
        ).all()
    
    def get_high_risk_contracts(self) -> list:
        """Get contracts with high risk scores"""
        session = self.Session()
        return session.query(Contract).filter(
            Contract.risk_level.in_([RiskLevel.HIGH, RiskLevel.CRITICAL])
        ).all()


# Example usage
if __name__ == "__main__":
    db = ContractDatabase()
    db.create_tables()
    
    # Create sample contract
    contract = db.create_contract(
        reference_number='CNT-2024-001',
        title='Service Agreement with Acme Corp',
        contract_type='Service Agreement',
        status=ContractStatus.ACTIVE,
        contract_value=100000.00,
        effective_date=datetime(2024, 1, 1)
    )
    print(f"Created contract: {contract.reference_number}")
