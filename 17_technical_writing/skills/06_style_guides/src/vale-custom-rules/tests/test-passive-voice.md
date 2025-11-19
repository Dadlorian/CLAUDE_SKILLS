# Test: Passive Voice Detection

This file is used to test the TechWriter.Passive rule.

## Bad Examples (Should Flag)
- The function is called by the user. (PASSIVE - should flag)
- The configuration was set incorrectly. (PASSIVE - should flag)
- The server is managed by the operations team. (PASSIVE - should flag)
- The API is documented in our guide. (PASSIVE - should flag)

## Good Examples (Should NOT Flag)
- The user calls the function.
- The administrator set the configuration correctly.
- The operations team manages the server.
- Our guide documents the API.

## Edge Cases
- "is" by itself should not flag
- "is important" should not flag
- "is used" might flag correctly
