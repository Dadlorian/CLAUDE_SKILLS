# Test: Acronym Definition

This file is used to test the TechWriter.Acronyms rule.

## Bad Examples (Should Flag)
- The API is documented. (ACRONYM - should flag first use)
- Use REST for communication. (ACRONYM - should flag first use)
- JSON format is required. (ACRONYM - should flag first use)
- The XML schema is here. (ACRONYM - should flag first use)

## Good Examples (Should NOT Flag)
- The API (Application Programming Interface) is documented.
- Use REST (Representational State Transfer) for communication.
- JSON (JavaScript Object Notation) format is required.
- The XML (Extensible Markup Language) schema is here.
- The API reference document shows all methods. (Subsequent use)

## Rules
- First use of acronym must include definition
- Subsequent uses don't need definition
- May require configuration of known acronyms
