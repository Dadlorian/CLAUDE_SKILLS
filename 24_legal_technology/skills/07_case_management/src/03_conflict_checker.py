"""
Conflict of Interest Checker - Automated Conflict Detection
Checks for conflicts of interest against all firm contacts and matters
"""

import requests
from typing import Dict, Any, List, Tuple
from datetime import datetime
from enum import Enum


class ConflictLevel(Enum):
    """Conflict severity levels"""
    NONE = "None"
    POTENTIAL = "Potential"
    DEFINITE = "Definite"


class ConflictType(Enum):
    """Types of conflicts"""
    ADVERSE_PARTY = "Adverse Party"
    RELATED_PARTY = "Related Party"
    FORMER_CLIENT = "Former Client"
    CONCURRENT_CLIENT = "Concurrent Client"
    ADVERSE_MATTER = "Adverse Matter"
    FINANCIAL_INTEREST = "Financial Interest"
    PERSONAL_RELATIONSHIP = "Personal Relationship"


class ConflictChecker:
    """Comprehensive conflict of interest checking system"""

    def __init__(self, api_key: str, base_url: str = "https://api.clio.com/v4.0"):
        """
        Initialize conflict checker

        Args:
            api_key: Clio API key
            base_url: API base URL
        """
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def _make_request(self, method: str, endpoint: str,
                     params: Dict = None, data: Dict = None) -> Dict[str, Any]:
        """Make API request"""
        url = f"{self.base_url}{endpoint}"
        try:
            if method == "GET":
                response = requests.get(url, headers=self.headers, params=params)
            else:
                response = requests.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API Error: {e}")
            raise

    def check_conflict(self, party_names: List[str],
                      matter_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Comprehensive conflict check for parties

        Args:
            party_names: List of party names to check
            matter_id: Optional matter ID (for related matter conflicts)

        Returns:
            Conflict check results
        """
        conflicts = []

        for party_name in party_names:
            # Check against existing contacts
            contact_conflicts = self._check_contacts(party_name)
            conflicts.extend(contact_conflicts)

            # Check against existing matters
            matter_conflicts = self._check_matters(party_name, matter_id)
            conflicts.extend(matter_conflicts)

            # Check against firm members/relationships
            relationship_conflicts = self._check_relationships(party_name)
            conflicts.extend(relationship_conflicts)

        return {
            "check_date": datetime.now().isoformat(),
            "parties_checked": party_names,
            "conflicts_found": len(conflicts) > 0,
            "conflict_level": self._determine_conflict_level(conflicts),
            "conflicts": conflicts,
            "status": "Clear" if len(conflicts) == 0 else "Requires Review"
        }

    def _check_contacts(self, party_name: str) -> List[Dict[str, Any]]:
        """Check party against all firm contacts"""
        conflicts = []

        try:
            # Get all contacts
            contacts_response = self._make_request(
                "GET",
                "/contacts",
                params={"limit": 500}
            )

            existing_contacts = contacts_response.get("data", [])

            for contact in existing_contacts:
                contact_name = f"{contact.get('first_name', '')} {contact.get('last_name', '')}".strip()

                # Check for name match (fuzzy matching)
                if self._fuzzy_match(party_name, contact_name):
                    # Get contact matters to determine conflict type
                    matters = self._get_contact_matters(contact.get('id'))

                    for matter in matters:
                        matter_status = matter.get('status', 'Unknown')

                        if matter_status == 'Active':
                            conflicts.append({
                                "type": ConflictType.CONCURRENT_CLIENT.value,
                                "severity": ConflictLevel.DEFINITE.value,
                                "description": f"Contact {contact_name} is client in active matter: {matter.get('display_name')}",
                                "conflicting_contact": contact.get('id'),
                                "conflicting_matter": matter.get('id'),
                                "details": contact
                            })
                        elif matter_status == 'Closed':
                            conflicts.append({
                                "type": ConflictType.FORMER_CLIENT.value,
                                "severity": ConflictLevel.POTENTIAL.value,
                                "description": f"Contact {contact_name} is former client in matter: {matter.get('display_name')}",
                                "conflicting_contact": contact.get('id'),
                                "conflicting_matter": matter.get('id'),
                                "closed_date": matter.get('close_date')
                            })

        except Exception as e:
            print(f"Error checking contacts: {e}")

        return conflicts

    def _check_matters(self, party_name: str,
                      exclude_matter_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Check party against all firm matters"""
        conflicts = []

        try:
            # Get all matters
            matters_response = self._make_request(
                "GET",
                "/matters",
                params={"limit": 500}
            )

            matters = matters_response.get("data", [])

            for matter in matters:
                if exclude_matter_id and matter.get('id') == exclude_matter_id:
                    continue

                # Check matter description and details for party name
                matter_details = matter.get('description', '') or ''
                if self._fuzzy_match(party_name, matter_details):
                    conflicts.append({
                        "type": ConflictType.ADVERSE_MATTER.value,
                        "severity": ConflictLevel.POTENTIAL.value,
                        "description": f"Party {party_name} mentioned in matter: {matter.get('display_name')}",
                        "conflicting_matter": matter.get('id'),
                        "matter_status": matter.get('status'),
                        "responsible_attorney": matter.get('responsible_attorney', {}).get('id')
                    })

        except Exception as e:
            print(f"Error checking matters: {e}")

        return conflicts

    def _check_relationships(self, party_name: str) -> List[Dict[str, Any]]:
        """Check for personal relationships and financial interests"""
        conflicts = []

        # Check against firm member relationships
        firm_members = self._get_firm_members()

        for member in firm_members:
            member_name = f"{member.get('first_name', '')} {member.get('last_name', '')}".strip()
            relationships = member.get('relationships', [])

            for relationship in relationships:
                if self._fuzzy_match(party_name, relationship.get('name', '')):
                    conflicts.append({
                        "type": ConflictType.PERSONAL_RELATIONSHIP.value,
                        "severity": ConflictLevel.POTENTIAL.value,
                        "description": f"Firm member {member_name} has relationship with {party_name}",
                        "firm_member": member.get('id'),
                        "relationship_type": relationship.get('type'),
                        "requires_review": True
                    })

        return conflicts

    def _get_contact_matters(self, contact_id: str) -> List[Dict[str, Any]]:
        """Get all matters for a specific contact"""
        try:
            response = self._make_request(
                "GET",
                f"/contacts/{contact_id}/matters"
            )
            return response.get("data", [])
        except:
            return []

    def _get_firm_members(self) -> List[Dict[str, Any]]:
        """Get all firm members/timekeepers"""
        try:
            response = self._make_request("GET", "/timekeepers")
            return response.get("data", [])
        except:
            return []

    def _fuzzy_match(self, str1: str, str2: str, threshold: float = 0.8) -> bool:
        """
        Fuzzy string matching

        Args:
            str1: First string
            str2: Second string
            threshold: Match threshold (0-1)

        Returns:
            True if strings match above threshold
        """
        str1_lower = str1.lower().strip()
        str2_lower = str2.lower().strip()

        # Exact match
        if str1_lower == str2_lower:
            return True

        # Partial match
        if str1_lower in str2_lower or str2_lower in str1_lower:
            return True

        # Simple Levenshtein-like comparison
        longer = max(len(str1_lower), len(str2_lower))
        if longer == 0:
            return False

        # Check for last name match (for person names)
        parts1 = str1_lower.split()
        parts2 = str2_lower.split()

        if len(parts1) > 0 and len(parts2) > 0:
            if parts1[-1] == parts2[-1]:
                return True

        return False

    def _determine_conflict_level(self, conflicts: List[Dict]) -> str:
        """Determine overall conflict level from all conflicts"""
        if not conflicts:
            return ConflictLevel.NONE.value

        severity_levels = [c.get('severity') for c in conflicts]

        if ConflictLevel.DEFINITE.value in severity_levels:
            return ConflictLevel.DEFINITE.value
        elif ConflictLevel.POTENTIAL.value in severity_levels:
            return ConflictLevel.POTENTIAL.value

        return ConflictLevel.NONE.value

    def check_before_engagement(self, client_name: str,
                               opposing_parties: List[str]) -> Dict[str, Any]:
        """
        Pre-engagement conflict check

        Args:
            client_name: New client name
            opposing_parties: List of opposing parties

        Returns:
            Comprehensive conflict check results
        """
        all_parties = [client_name] + opposing_parties

        results = {
            "engagement_check": True,
            "client": client_name,
            "opposing_parties": opposing_parties,
            "check_timestamp": datetime.now().isoformat(),
            "detailed_results": {}
        }

        for party in all_parties:
            party_check = self.check_conflict([party])
            results["detailed_results"][party] = party_check

        # Aggregate results
        all_conflicts = []
        for detail in results["detailed_results"].values():
            all_conflicts.extend(detail.get("conflicts", []))

        results["total_conflicts"] = len(all_conflicts)
        results["can_proceed"] = len(all_conflicts) == 0
        results["overall_status"] = "Clear to Proceed" if results["can_proceed"] else "Conflicts Detected"

        return results

    def generate_conflict_report(self, check_results: Dict[str, Any]) -> str:
        """Generate formatted conflict check report"""
        report = f"""
CONFLICT OF INTEREST CHECK REPORT
Generated: {check_results.get('check_timestamp')}

Overall Status: {check_results.get('overall_status')}
Can Proceed: {'YES' if check_results.get('can_proceed') else 'NO'}

Parties Checked:
- Client: {check_results.get('client')}
- Opposing Parties: {', '.join(check_results.get('opposing_parties', []))}

Summary:
Total Conflicts Found: {check_results.get('total_conflicts')}

"""

        if check_results.get('total_conflicts', 0) > 0:
            report += "\nDETAILED CONFLICTS:\n"
            for party, details in check_results.get('detailed_results', {}).items():
                if details.get('conflicts'):
                    report += f"\n{party}:\n"
                    for conflict in details.get('conflicts', []):
                        report += f"  - {conflict.get('type')}: {conflict.get('description')}\n"

        return report


# Example usage
if __name__ == "__main__":
    checker = ConflictChecker(api_key="your_clio_api_key")

    # Pre-engagement conflict check
    result = checker.check_before_engagement(
        client_name="Acme Corp",
        opposing_parties=["XYZ Industries", "John Smith"]
    )

    print(checker.generate_conflict_report(result))
