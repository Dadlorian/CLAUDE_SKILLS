"""
Conflict of Interest Checker - Database queries and conflict detection
"""

import sqlite3
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ConflictRecord:
    """Record of a potential conflict"""
    id: str
    client_name: str
    opposing_party: str
    conflict_type: str  # "direct", "related_entity", "prior_representation"
    matter_id: str
    severity: str  # "critical", "warning", "info"
    details: str
    resolution: Optional[str] = None
    resolved_date: Optional[datetime] = None


class ConflictDatabase:
    """Database of clients, matters, and conflicts"""

    def __init__(self, db_path: str = ":memory:"):
        """
        Initialize conflict database

        Args:
            db_path: SQLite database file path
        """
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        """Initialize database schema"""
        cursor = self.conn.cursor()

        # Current clients table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS current_clients (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                client_id TEXT,
                contact_type TEXT,
                added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Opposing parties table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS opposing_parties (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                matter_id TEXT,
                added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Prior representations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prior_representations (
                id INTEGER PRIMARY KEY,
                client_name TEXT NOT NULL,
                matter_id TEXT,
                end_date TIMESTAMP,
                UNIQUE(client_name, matter_id)
            )
        """)

        # Related entities table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS related_entities (
                id INTEGER PRIMARY KEY,
                parent_entity TEXT NOT NULL,
                related_entity TEXT NOT NULL,
                relationship_type TEXT,
                UNIQUE(parent_entity, related_entity)
            )
        """)

        # Conflicts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conflicts (
                id INTEGER PRIMARY KEY,
                conflict_id TEXT UNIQUE,
                client_name TEXT,
                opposing_party TEXT,
                conflict_type TEXT,
                matter_id TEXT,
                severity TEXT,
                details TEXT,
                resolution TEXT,
                resolved_date TIMESTAMP,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Employee/partner associations
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS employee_relationships (
                id INTEGER PRIMARY KEY,
                employee_name TEXT NOT NULL,
                entity_name TEXT,
                relationship_type TEXT,
                UNIQUE(employee_name, entity_name)
            )
        """)

        # Create indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_current_clients_name ON current_clients(name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_opposing_parties_name ON opposing_parties(name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_prior_reps_client ON prior_representations(client_name)")

        self.conn.commit()

    def add_current_client(self, name: str, client_id: str = None) -> None:
        """Add client to current clients list"""
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO current_clients (name, client_id) VALUES (?, ?)",
                (name.lower(), client_id)
            )
            self.conn.commit()
        except sqlite3.IntegrityError:
            pass  # Client already exists

    def add_opposing_party(self, name: str, matter_id: str) -> None:
        """Add opposing party to history"""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO opposing_parties (name, matter_id) VALUES (?, ?)",
            (name.lower(), matter_id)
        )
        self.conn.commit()

    def add_prior_representation(self, client_name: str, matter_id: str) -> None:
        """Add prior client representation"""
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO prior_representations (client_name, matter_id) VALUES (?, ?)",
                (client_name.lower(), matter_id)
            )
            self.conn.commit()
        except sqlite3.IntegrityError:
            pass

    def add_related_entity(self, parent_entity: str, related_entity: str,
                          relationship_type: str = "affiliated") -> None:
        """Add entity relationship"""
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                """INSERT INTO related_entities
                   (parent_entity, related_entity, relationship_type)
                   VALUES (?, ?, ?)""",
                (parent_entity.lower(), related_entity.lower(), relationship_type)
            )
            self.conn.commit()
        except sqlite3.IntegrityError:
            pass

    def get_current_clients(self) -> List[str]:
        """Get list of all current clients"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM current_clients")
        return [row[0] for row in cursor.fetchall()]

    def get_opposing_parties_for_matter(self, matter_id: str) -> List[str]:
        """Get opposing parties for specific matter"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT DISTINCT name FROM opposing_parties WHERE matter_id = ?", (matter_id,))
        return [row[0] for row in cursor.fetchall()]

    def get_all_opposing_parties(self) -> List[str]:
        """Get all opposing parties from history"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT DISTINCT name FROM opposing_parties")
        return [row[0] for row in cursor.fetchall()]

    def get_related_entities(self, entity_name: str) -> List[str]:
        """Get all entities related to given entity"""
        cursor = self.conn.cursor()
        entity_lower = entity_name.lower()

        # Get forward relationships
        cursor.execute(
            "SELECT related_entity FROM related_entities WHERE parent_entity = ?",
            (entity_lower,)
        )
        forward = [row[0] for row in cursor.fetchall()]

        # Get reverse relationships
        cursor.execute(
            "SELECT parent_entity FROM related_entities WHERE related_entity = ?",
            (entity_lower,)
        )
        reverse = [row[0] for row in cursor.fetchall()]

        return list(set(forward + reverse))


class ConflictChecker:
    """Checks for conflicts of interest"""

    def __init__(self, database: ConflictDatabase):
        """
        Initialize conflict checker

        Args:
            database: ConflictDatabase instance
        """
        self.db = database

    def check_prospective_client(self, client_name: str, opposing_parties: List[str],
                                company: str = "") -> Dict[str, any]:
        """
        Check for conflicts before accepting new client

        Args:
            client_name: Prospective client name
            opposing_parties: List of opposing parties
            company: Client company (if applicable)

        Returns:
            Conflict check results
        """
        conflicts = []
        client_lower = client_name.lower()
        company_lower = company.lower() if company else ""

        # Check 1: Is prospective client already a current client?
        current_clients = self.db.get_current_clients()
        if client_lower in current_clients:
            conflicts.append({
                "type": "direct",
                "severity": "critical",
                "message": f"{client_name} is already a current client"
            })

        # Check 2: Is any opposing party a current client?
        for opposing_party in opposing_parties:
            opposing_lower = opposing_party.lower()
            if opposing_lower in current_clients:
                conflicts.append({
                    "type": "direct",
                    "severity": "critical",
                    "message": f"Opposing party {opposing_party} is a current client"
                })

        # Check 3: Prior representation conflicts
        prior_clients = self.db.conn.cursor().execute(
            "SELECT DISTINCT client_name FROM prior_representations"
        ).fetchall()
        prior_clients = [row[0] for row in prior_clients]

        for opposing_party in opposing_parties:
            if opposing_party.lower() in prior_clients:
                conflicts.append({
                    "type": "prior_representation",
                    "severity": "critical",
                    "message": f"We previously represented {opposing_party}"
                })

        # Check 4: Related entity conflicts
        if company:
            related_entities = self.db.get_related_entities(company_lower)
            opposing_lower_list = [opp.lower() for opp in opposing_parties]

            for entity in related_entities:
                if entity in opposing_lower_list or entity in current_clients:
                    conflicts.append({
                        "type": "related_entity",
                        "severity": "warning",
                        "message": f"Related entity {entity} may have conflict"
                    })

        return {
            "client_name": client_name,
            "has_conflicts": len(conflicts) > 0,
            "conflict_count": len(conflicts),
            "conflicts": conflicts,
            "clearance_status": "BLOCKED" if conflicts else "CLEARED",
            "check_date": datetime.now().isoformat()
        }

    def bulk_check_names(self, names: List[str]) -> Dict[str, List[str]]:
        """
        Perform bulk name checking

        Args:
            names: List of names to check

        Returns:
            Matches against conflict lists
        """
        results = {
            "current_client_matches": [],
            "opposing_party_matches": [],
            "prior_rep_matches": []
        }

        current_clients = self.db.get_current_clients()
        all_opposing = self.db.get_all_opposing_parties()

        cursor = self.db.conn.cursor()
        cursor.execute("SELECT DISTINCT client_name FROM prior_representations")
        prior_reps = [row[0] for row in cursor.fetchall()]

        for name in names:
            name_lower = name.lower()
            if name_lower in current_clients:
                results["current_client_matches"].append(name)
            if name_lower in all_opposing:
                results["opposing_party_matches"].append(name)
            if name_lower in prior_reps:
                results["prior_rep_matches"].append(name)

        return results

    def get_conflict_history(self) -> List[Dict]:
        """Get history of identified conflicts"""
        cursor = self.db.conn.cursor()
        cursor.execute("""
            SELECT conflict_id, client_name, opposing_party, conflict_type,
                   severity, details, resolution, resolved_date
            FROM conflicts
            ORDER BY created_date DESC
        """)

        conflicts = []
        for row in cursor.fetchall():
            conflicts.append({
                "id": row[0],
                "client": row[1],
                "opposing_party": row[2],
                "type": row[3],
                "severity": row[4],
                "details": row[5],
                "resolution": row[6],
                "resolved_date": row[7]
            })

        return conflicts


# Example usage
if __name__ == "__main__":
    # Initialize database
    db = ConflictDatabase()

    # Populate with sample data
    db.add_current_client("Acme Corporation", "c001")
    db.add_current_client("Smith Industries", "c002")
    db.add_opposing_party("Johnson Corp", "m001")
    db.add_opposing_party("Williams LLC", "m002")
    db.add_prior_representation("Tech Ventures", "m003")
    db.add_related_entity("Acme Corporation", "Acme Finance Inc", "subsidiary")
    db.add_related_entity("Acme Corporation", "Acme Ventures", "affiliate")

    # Initialize conflict checker
    checker = ConflictChecker(db)

    # Test 1: No conflict
    result = checker.check_prospective_client(
        "New Client Inc",
        ["Third Party Corp"],
        "New Client Inc"
    )
    print("Test 1 - No Conflict:")
    print(f"  Status: {result['clearance_status']}")
    print(f"  Conflicts: {result['conflict_count']}")

    # Test 2: Current client conflict
    result = checker.check_prospective_client(
        "Acme Corporation",
        ["Some Opponent"]
    )
    print("\nTest 2 - Current Client Conflict:")
    print(f"  Status: {result['clearance_status']}")
    print(f"  Conflicts: {len(result['conflicts'])}")

    # Test 3: Opposing party conflict
    result = checker.check_prospective_client(
        "New Client",
        ["Johnson Corp"]
    )
    print("\nTest 3 - Opposing Party Conflict:")
    print(f"  Status: {result['clearance_status']}")
    for conflict in result['conflicts']:
        print(f"  - {conflict['message']}")

    # Test 4: Bulk name checking
    bulk_result = checker.bulk_check_names([
        "Acme Corporation",
        "Johnson Corp",
        "Tech Ventures",
        "Unknown Company"
    ])
    print("\nTest 4 - Bulk Check Results:")
    print(f"  Current clients: {bulk_result['current_client_matches']}")
    print(f"  Opposing parties: {bulk_result['opposing_party_matches']}")
    print(f"  Prior reps: {bulk_result['prior_rep_matches']}")
