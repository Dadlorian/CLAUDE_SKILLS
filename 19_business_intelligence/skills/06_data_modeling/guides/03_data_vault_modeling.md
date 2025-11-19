# Data Vault 2.0 Modeling - Deep Dive

## Overview

Data Vault 2.0 is an agile, scalable, and auditable data modeling methodology specifically designed for enterprise data warehouses. Created by Dan Linstedt, it focuses on insert-only patterns, complete audit trails, and business key-centric design.

**Core Philosophy**: Model the business, not the systems. Capture all data from all sources with complete audit trail, enable parallel loading, and support business agility.

## Key Principles

### 1. Insert-Only Architecture
- Never update or delete in raw vault
- New row for every change
- Complete history automatically maintained
- Simplified ETL (no complex update logic)

### 2. Hub-Link-Satellite Pattern
- **Hubs**: Business keys
- **Links**: Relationships between hubs
- **Satellites**: Descriptive data and history

### 3. Auditability
- Every row has load timestamp and source
- Complete lineage
- Reproducible at any point in time
- Compliance-ready

### 4. Scalability
- Parallel loading by source system
- Hash-based distribution
- Partition-friendly design
- Handles massive volumes

### 5. Agility
- Add new sources without redesigning existing structures
- Business rules in business vault (separate from raw vault)
- Schema changes minimal (just add satellites)
- Supports rapidly changing requirements

## Core Components

### Hubs

**Purpose**: Store unique business keys

**Structure**:
```
HUB_CUSTOMER
- customer_hash_key (PK, MD5/SHA of business key)
- customer_id (natural business key)
- load_date (when first seen)
- record_source (which system)
```

**Rules**:
- One hub per business concept
- Only business keys + metadata
- Never updated
- First occurrence only

### Links

**Purpose**: Relationships between business entities

**Structure**:
```
LINK_ORDER
- order_hash_key (PK, hash of all hub keys)
- customer_hash_key (FK to HUB_CUSTOMER)
- product_hash_key (FK to HUB_PRODUCT)
- store_hash_key (FK to HUB_STORE)
- load_date
- record_source
```

**Rules**:
- Connect hubs only (not other links)
- Can connect 2+ hubs
- No descriptive attributes
- Represents relationships/transactions

### Satellites

**Purpose**: Descriptive attributes and change tracking

**Structure**:
```
SAT_CUSTOMER
- customer_hash_key (PK, FK to hub)
- load_date (PK, part of composite key)
- load_end_date (when superseded)
- customer_name
- email
- phone
- hash_diff (hash of all attributes for change detection)
- record_source
```

**Rules**:
- One satellite per hub or link
- Track all changes (new row per change)
- Hash diff for efficient change detection
- Multiple satellites per hub for different sources

## Advanced Patterns

### Point-in-Time (PIT) Tables
Performance optimization for time-variant queries.

### Bridge Tables
Dimensional representation for BI tools.

### Business Vault
Calculated fields and business rules applied.

## When to Use Data Vault

**Choose Data Vault When**:
- Multiple source systems with frequent changes
- Complete audit trail required
- Parallel loading needed
- Agility is top priority
- Complex many-to-many relationships
- Compliance requirements

**Benefits**:
- Highly flexible and adaptable
- Excellent audit trail
- Handles source changes gracefully
- Parallel, scalable loading
- Historical accuracy guaranteed

**Trade-offs**:
- More complex than Kimball
- Requires dimensional views for BI
- Steeper learning curve
- More tables to manage

## Summary

Data Vault excels at enterprise data integration with complete auditability and flexibility. Best for organizations with complex, changing source systems requiring historical accuracy and regulatory compliance.
