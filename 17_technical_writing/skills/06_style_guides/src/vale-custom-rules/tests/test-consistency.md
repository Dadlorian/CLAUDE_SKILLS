# Test: Terminology Consistency

This file is used to test the TechWriter.Consistency rule.

## Bad Examples (Should Flag)
- The user facing interface is clean. (Should be "user-facing")
- Client side validation is required. (Should be "client-side")
- Server side processing happens here. (Should be "server-side")
- Real time updates are available. (Should be "real-time")
- The back-end code is optimized. (Should be "backend")
- Front-end developers use this tool. (Should be "frontend")

## Good Examples (Should NOT Flag)
- The user-facing interface is clean.
- Client-side validation is required.
- Server-side processing happens here.
- Real-time updates are available.
- The backend code is optimized.
- Frontend developers use this tool.

## Scope
- Applies primarily to compound technical terms
- Ensures consistency across documentation
