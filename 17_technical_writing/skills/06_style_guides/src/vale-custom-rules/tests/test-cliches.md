# Test: Clichés and Weak Phrases

This file is used to test the TechWriter.Clichés rule.

## Bad Examples (Should Flag)
- A lot of users prefer this feature. (Should suggest "many")
- In order to install, run this command. (Should suggest "to")
- At the end of the day, performance matters. (Should replace with nothing)
- It goes without saying that security is important. (Should replace with nothing)
- Take into account the memory usage. (Should suggest "consider")

## Good Examples (Should NOT Flag)
- Many users prefer this feature.
- To install, run this command.
- Performance matters.
- Security is important.
- Consider the memory usage.

## Edge Cases
- Should handle case variations
- Should preserve surrounding punctuation
