# Test: Deprecated Terms

This file is used to test the TechWriter.DeprecatedTerms rule.

## Bad Examples (Should Flag as ERROR)
- Configure the master database. (DEPRECATED - should suggest "primary")
- Set up slave replicas. (DEPRECATED - should suggest "secondary")
- Add the IP to the whitelist. (DEPRECATED - should suggest "allowlist")
- Remove the domain from the blacklist. (DEPRECATED - should suggest "blocklist")
- Perform a sanity check. (DEPRECATED - should suggest "verification")

## Good Examples (Should NOT Flag)
- Configure the primary database.
- Set up secondary replicas.
- Add the IP to the allowlist.
- Remove the domain from the blocklist.
- Perform a verification check.

## Severity Level
- These should be ERROR level (not warning)
- Important for inclusive and modern terminology
