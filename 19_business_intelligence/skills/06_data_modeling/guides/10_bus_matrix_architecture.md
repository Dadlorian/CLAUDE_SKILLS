# Bus Matrix and Enterprise Architecture Guide

## Purpose
The bus matrix is the architectural blueprint for Kimball dimensional modeling, showing which conformed dimensions are shared across business processes.

## Bus Matrix Structure

### Rows: Business Processes (Fact Tables)
Each row represents a measurable business process

### Columns: Conformed Dimensions
Each column represents a shared dimension

### Marks (X): Usage
X indicates dimension is used by that process

## Example Bus Matrix

```
Business Process      | Date | Time | Customer | Product | Store | Employee | Promotion | Payment
----------------------|------|------|----------|---------|-------|----------|-----------|----------
Retail Sales          |  X   |  X   |    X     |    X    |   X   |    X     |     X     |    X
Returns               |  X   |  X   |    X     |    X    |   X   |    X     |     X     |
Inventory Snapshot    |  X   |      |          |    X    |   X   |          |           |
Order Fulfillment     |  X   |      |    X     |    X    |       |          |     X     |    X
Customer Service Call |  X   |  X   |    X     |         |       |    X     |           |
Web Clickstream       |  X   |  X   |    X     |    X    |       |          |     X     |
```

## Reading the Matrix

### Column Analysis
**Date**: Used by all processes → Highest priority conformed dimension
**Product**: Used by most processes → High-priority conformance
**Payment**: Used by few → May not need full conformance

### Row Analysis
**Retail Sales**: Uses most dimensions → Central business process
**Inventory**: Fewer dimensions → Specialized process

## Building the Matrix

### Step 1: Identify Business Processes
List all business processes to be modeled:
- Retail sales transactions
- Product returns
- Inventory movements
- Order fulfillment
- Customer service
- Web analytics

### Step 2: Identify Candidate Dimensions
List potential conformed dimensions:
- Date (universal)
- Customer
- Product
- Geography/Location
- Employee
- Promotion

### Step 3: Map Relationships
For each process, identify which dimensions apply:
- Does Sales use Customer? Yes → X
- Does Inventory use Customer? No → blank

### Step 4: Prioritize Conformance
- Most-shared dimensions = highest priority
- Date always first
- Customer and Product typically next

## Using the Matrix

### Planning Tool
- Identify which dimensions to conform first
- Sequence data mart development
- Resource allocation

### Design Tool
- Validate dimension usage across processes
- Ensure consistency
- Identify integration opportunities

### Communication Tool
- Visualize enterprise architecture
- Executive presentations
- Stakeholder alignment

## Conformed Dimension Authority

Each conformed dimension needs:
- **Owner/Steward**: Responsible person/team
- **Definition**: Standard structure and attributes
- **Source**: Authoritative source system
- **SLA**: Update frequency and availability
- **Change Process**: How to request modifications

## Implementation Sequence

### Phase 1: Foundation (Months 1-3)
- Build DIM_DATE (universal)
- Implement first business process
- Establish conformed dimension standards

### Phase 2: Core Dimensions (Months 4-6)
- Conform DIM_CUSTOMER
- Conform DIM_PRODUCT
- Add second business process using conformed dimensions

### Phase 3: Expansion (Months 7-12)
- Add remaining high-priority dimensions
- Implement additional business processes
- Refine conformance

### Phase 4: Enterprise Integration (Ongoing)
- Add new dimensions as needed
- Extend existing dimensions
- Continuous improvement

## Best Practices

1. **Start Simple**: Begin with most critical process and dimensions
2. **Build Incrementally**: Add processes and dimensions over time
3. **Enforce Standards**: No non-conformed local versions
4. **Document Everything**: Structure, rules, sources, SLAs
5. **Communicate Changes**: All consumers notified of updates
6. **Monitor Usage**: Track drill-across queries
7. **Govern Firmly**: Change control for conformed dimensions
8. **Review Regularly**: Update matrix as needs evolve

## Success Metrics

- % of data marts using conformed dimensions
- Number of drill-across queries executed
- Time to develop new data mart (should decrease)
- User satisfaction with integrated reporting
- Data consistency scores

