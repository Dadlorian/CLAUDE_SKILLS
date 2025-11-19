"""
Patent Classification System
Handles IPC, CPC, and USPC classification systems
Provides patent classification and reclassification tools
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import re

logger = logging.getLogger(__name__)


class ClassificationSystem(Enum):
    """Patent classification systems"""
    CPC = "CPC"  # Cooperative Patent Classification
    IPC = "IPC"  # International Patent Classification
    USPC = "USPC"  # United States Patent Classification


@dataclass
class Classification:
    """Patent classification details"""
    system: ClassificationSystem
    code: str
    title: str
    description: str
    hierarchy_level: int
    parent_code: Optional[str] = None
    subclasses: List[str] = None

    def __post_init__(self):
        if self.subclasses is None:
            self.subclasses = []


@dataclass
class ClassificationHierarchy:
    """Classification hierarchy structure"""
    section: str
    class_code: str
    subclass: str
    group: Optional[str] = None
    subgroup: Optional[str] = None


class CPCClassifier:
    """Cooperative Patent Classification system handler"""

    def __init__(self):
        """Initialize CPC classifier"""
        # Load CPC classification scheme
        self.classifications = self._load_cpc_scheme()

    def classify_patent(self, title: str, abstract: str, claims: List[str]) -> List[Classification]:
        """
        Classify patent using CPC system

        Args:
            title: Patent title
            abstract: Patent abstract
            claims: List of patent claims

        Returns:
            List of applicable CPC classifications
        """
        classifications = []

        try:
            # Extract technical terms
            terms = self._extract_technical_terms(title, abstract, claims)

            # Map terms to classifications
            for term in terms:
                matched_classes = self._match_cpc_classification(term)
                classifications.extend(matched_classes)

            # Remove duplicates and rank
            unique_classes = {c.code: c for c in classifications}.values()
            classifications = sorted(
                list(unique_classes),
                key=lambda x: x.hierarchy_level
            )

            return classifications

        except Exception as e:
            logger.error(f"CPC classification failed: {e}")
            return []

    def get_classification(self, code: str) -> Optional[Classification]:
        """
        Get classification details by code

        Args:
            code: CPC classification code

        Returns:
            Classification object or None
        """
        return self.classifications.get(code)

    def parse_cpc_code(self, code: str) -> Optional[ClassificationHierarchy]:
        """
        Parse CPC code into components

        Args:
            code: CPC code (e.g., "H02S30/20")

        Returns:
            ClassificationHierarchy object
        """
        # CPC format: Section + Class + Subclass / Group - Subgroup
        match = re.match(r'([A-H])(\d{2})([A-Z])(\d+)/?(\d+)?', code)

        if match:
            section = match.group(1)
            class_code = match.group(2)
            subclass = match.group(3)
            group = match.group(4) if match.group(4) else None
            subgroup = match.group(5) if match.group(5) else None

            return ClassificationHierarchy(
                section=section,
                class_code=class_code,
                subclass=subclass,
                group=group,
                subgroup=subgroup
            )

        return None

    def get_parent_classification(self, code: str) -> Optional[str]:
        """Get parent classification of given code"""
        hierarchy = self.parse_cpc_code(code)
        if not hierarchy or not hierarchy.subgroup:
            return None

        # Parent is same code without subgroup
        parent_code = f"{hierarchy.section}{hierarchy.class_code}{hierarchy.subclass}{hierarchy.group}"
        return parent_code

    def get_child_classifications(self, code: str) -> List[str]:
        """Get child classifications of given code"""
        children = []

        for cls_code, cls_obj in self.classifications.items():
            if cls_obj.parent_code == code:
                children.append(cls_code)

        return children

    def _extract_technical_terms(self, title: str, abstract: str, claims: List[str]) -> List[str]:
        """Extract technical terms from patent content"""
        text = f"{title} {abstract} {' '.join(claims)}".lower()

        # Common technical terms by field
        technical_terms = {
            "solar": ["solar panel", "photovoltaic", "pv cell"],
            "battery": ["battery", "cell", "electrode", "electrolyte"],
            "motor": ["motor", "electric motor", "ac motor", "dc motor"],
            "semiconductor": ["semiconductor", "transistor", "diode", "ic"],
            "communication": ["wireless", "antenna", "transmission", "signal"],
        }

        found_terms = []
        for category, terms in technical_terms.items():
            for term in terms:
                if term in text:
                    found_terms.append(term)

        return list(set(found_terms)) if found_terms else ["general"]

    def _match_cpc_classification(self, term: str) -> List[Classification]:
        """Match technical term to CPC classifications"""
        matched = []

        # Simplified matching logic
        term_lower = term.lower()

        for code, classification in self.classifications.items():
            title_lower = classification.title.lower()
            if term_lower in title_lower or title_lower in term_lower:
                matched.append(classification)

        return matched

    def _load_cpc_scheme(self) -> Dict[str, Classification]:
        """Load CPC classification scheme"""
        # Simplified CPC scheme
        scheme = {
            "H02S30/20": Classification(
                system=ClassificationSystem.CPC,
                code="H02S30/20",
                title="Conversion of scattered light or diffuse radiation",
                description="Solar cells with optical concentrators",
                hierarchy_level=2,
                parent_code="H02S30"
            ),
            "H02S40/40": Classification(
                system=ClassificationSystem.CPC,
                code="H02S40/40",
                title="Tracking systems for solar arrays",
                description="Sun-tracking systems for photovoltaic arrays",
                hierarchy_level=2,
                parent_code="H02S40"
            ),
            "H01L31/00": Classification(
                system=ClassificationSystem.CPC,
                code="H01L31/00",
                title="Semiconductor devices sensitive to infrared radiation",
                description="Solar cells and photodiodes",
                hierarchy_level=1
            ),
        }

        return scheme


class IPCClassifier:
    """International Patent Classification handler"""

    def __init__(self):
        """Initialize IPC classifier"""
        self.classifications = self._load_ipc_scheme()

    def classify_patent(self, title: str, abstract: str, claims: List[str]) -> List[Classification]:
        """
        Classify patent using IPC system

        Args:
            title: Patent title
            abstract: Patent abstract
            claims: List of claims

        Returns:
            List of IPC classifications
        """
        classifications = []

        try:
            # IPC classification logic
            terms = self._extract_technical_terms(title, abstract, claims)

            for term in terms:
                matched = self._match_ipc_classification(term)
                classifications.extend(matched)

            # Rank by relevance
            unique = {c.code: c for c in classifications}.values()
            return sorted(list(unique), key=lambda x: x.hierarchy_level)

        except Exception as e:
            logger.error(f"IPC classification failed: {e}")
            return []

    def parse_ipc_code(self, code: str) -> Optional[ClassificationHierarchy]:
        """
        Parse IPC code format: Section Class / Subclass Group - Subgroup

        Args:
            code: IPC code (e.g., "H02S30/20")

        Returns:
            ClassificationHierarchy object
        """
        match = re.match(r'([A-H])(\d{2})([A-Z])(/?)(\d+)(-)?(\d+)?', code)

        if match:
            section = match.group(1)
            class_code = match.group(2)
            subclass = match.group(3)
            group = match.group(5) if match.group(5) else None
            subgroup = match.group(7) if match.group(7) else None

            return ClassificationHierarchy(
                section=section,
                class_code=class_code,
                subclass=subclass,
                group=group,
                subgroup=subgroup
            )

        return None

    def _extract_technical_terms(self, title: str, abstract: str, claims: List[str]) -> List[str]:
        """Extract technical terms"""
        text = f"{title} {abstract}".lower()
        return list(set(re.findall(r'\b\w+\b', text)))

    def _match_ipc_classification(self, term: str) -> List[Classification]:
        """Match term to IPC classifications"""
        matched = []

        for code, classification in self.classifications.items():
            if term.lower() in classification.title.lower():
                matched.append(classification)

        return matched

    def _load_ipc_scheme(self) -> Dict[str, Classification]:
        """Load IPC classification scheme"""
        scheme = {
            "H02S30/20": Classification(
                system=ClassificationSystem.IPC,
                code="H02S30/20",
                title="Conversion of scattered light",
                description="Photovoltaic cells with concentrators",
                hierarchy_level=2
            ),
            "H01L31/00": Classification(
                system=ClassificationSystem.IPC,
                code="H01L31/00",
                title="Semiconductor devices",
                description="Solar cells",
                hierarchy_level=1
            ),
        }

        return scheme


class USPCClassifier:
    """United States Patent Classification handler"""

    def __init__(self):
        """Initialize USPC classifier"""
        self.classifications = self._load_uspc_scheme()

    def classify_patent(self, title: str, abstract: str, claims: List[str]) -> List[Classification]:
        """Classify patent using USPC system"""
        classifications = []

        try:
            terms = self._extract_technical_terms(title, abstract, claims)

            for term in terms:
                matched = self._match_uspc_classification(term)
                classifications.extend(matched)

            unique = {c.code: c for c in classifications}.values()
            return sorted(list(unique), key=lambda x: x.hierarchy_level)

        except Exception as e:
            logger.error(f"USPC classification failed: {e}")
            return []

    def parse_uspc_code(self, code: str) -> Optional[Tuple[int, Optional[int]]]:
        """
        Parse USPC code (Class/Subclass format)

        Args:
            code: USPC code (e.g., "290/54")

        Returns:
            Tuple of (class, subclass) or None
        """
        match = re.match(r'(\d+)(?:\.(\d+))?', code)

        if match:
            class_code = int(match.group(1))
            subclass = int(match.group(2)) if match.group(2) else None
            return (class_code, subclass)

        return None

    def _extract_technical_terms(self, title: str, abstract: str, claims: List[str]) -> List[str]:
        """Extract technical terms"""
        text = f"{title} {abstract}".lower()
        return list(set(re.findall(r'\b\w+\b', text)))

    def _match_uspc_classification(self, term: str) -> List[Classification]:
        """Match term to USPC classifications"""
        matched = []

        for code, classification in self.classifications.items():
            if term.lower() in classification.title.lower():
                matched.append(classification)

        return matched

    def _load_uspc_scheme(self) -> Dict[str, Classification]:
        """Load USPC classification scheme"""
        scheme = {
            "290.54": Classification(
                system=ClassificationSystem.USPC,
                code="290.54",
                title="Solar cells",
                description="Photovoltaic energy conversion",
                hierarchy_level=2
            ),
        }

        return scheme


class ClassificationMapper:
    """Map between different classification systems"""

    def __init__(self):
        """Initialize classification mapper"""
        self.ipc_to_cpc = self._load_ipc_cpc_mapping()
        self.ipc_to_uspc = self._load_ipc_uspc_mapping()

    def map_ipc_to_cpc(self, ipc_code: str) -> List[str]:
        """Convert IPC code to CPC"""
        return self.ipc_to_cpc.get(ipc_code, [ipc_code])

    def map_ipc_to_uspc(self, ipc_code: str) -> List[str]:
        """Convert IPC code to USPC"""
        return self.ipc_to_uspc.get(ipc_code, [])

    def map_cpc_to_ipc(self, cpc_code: str) -> List[str]:
        """Convert CPC to IPC"""
        # Reverse mapping
        reverse_mapping = {v: k for k, vs in self.ipc_to_cpc.items() for v in vs}
        return [reverse_mapping.get(cpc_code, cpc_code)]

    def _load_ipc_cpc_mapping(self) -> Dict[str, List[str]]:
        """Load IPC to CPC mapping"""
        return {
            "H02S30/20": ["H02S30/20"],
            "H01L31/00": ["H01L31/00"],
        }

    def _load_ipc_uspc_mapping(self) -> Dict[str, List[str]]:
        """Load IPC to USPC mapping"""
        return {
            "H02S30/20": ["290.54"],
            "H01L31/00": ["257.21"],
        }


def main():
    """Example usage"""
    cpc = CPCClassifier()
    ipc = IPCClassifier()
    uspc = USPCClassifier()

    title = "Solar Panel with Tracking System"
    abstract = "A photovoltaic array with sun-tracking capability"
    claims = ["A method for tracking solar radiation"]

    cpc_classes = cpc.classify_patent(title, abstract, claims)
    ipc_classes = ipc.classify_patent(title, abstract, claims)
    uspc_classes = uspc.classify_patent(title, abstract, claims)

    print(f"CPC Classifications: {[c.code for c in cpc_classes]}")
    print(f"IPC Classifications: {[c.code for c in ipc_classes]}")
    print(f"USPC Classifications: {[c.code for c in uspc_classes]}")

    # Map between systems
    mapper = ClassificationMapper()
    cpc_equiv = mapper.map_ipc_to_cpc("H02S30/20")
    print(f"IPC H02S30/20 -> CPC: {cpc_equiv}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
