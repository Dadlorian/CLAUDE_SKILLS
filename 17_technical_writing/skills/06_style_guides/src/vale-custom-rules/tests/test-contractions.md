# Test: Contractions

This file is used to test the TechWriter.Contractions rule.

## Bad Examples (Should Flag)
- Don't use that approach. (CONTRACTION - should flag to "do not")
- You can't modify this setting. (CONTRACTION - should flag to "cannot")
- The system won't restart. (CONTRACTION - should flag to "will not")
- It's important to understand. (CONTRACTION - should flag to "it is")
- That's the configuration. (CONTRACTION - should flag to "that is")

## Good Examples (Should NOT Flag)
- Do not use that approach.
- You cannot modify this setting.
- The system will not restart.
- It is important to understand.
- That is the configuration.

## Edge Cases
- Possessives like "user's" should not flag
- Only true contractions should trigger
