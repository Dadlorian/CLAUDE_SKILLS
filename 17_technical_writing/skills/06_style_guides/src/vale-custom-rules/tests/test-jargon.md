# Test: Jargon Detection

This file is used to test the TechWriter.Jargon rule.

## Bad Examples (Should Flag)
- The blockchain technology enables transactions. (JARGON - should flag)
- Cryptography protects your data. (JARGON - should flag)
- Use the API to integrate. (JARGON - should flag)
- The OAuth mechanism authenticates users. (JARGON - should flag)

## Good Examples (Should NOT Flag)
- Blockchain, a distributed ledger technology, enables transactions.
- Cryptography, which is the practice of secure communication, protects your data.
- An API (Application Programming Interface) provides a way to integrate.
- OAuth, which is an authentication protocol, authenticates users.

## Expected Behavior
- First mention without explanation should trigger warning
- Explanation in appositive or definition should not trigger
