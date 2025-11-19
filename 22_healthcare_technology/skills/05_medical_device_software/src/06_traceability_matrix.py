"""IEC 62304 Requirements Traceability Matrix"""
import json
from typing import List, Dict
from dataclasses import dataclass, asdict

@dataclass
class TraceabilityLink:
    """Link between requirement, design, code, and test"""
    req_id: str
    design_id: str
    code_module: str
    test_case_id: str
    test_result: str  # PASS, FAIL
    evidence_file: str

class TraceabilityMatrix:
    """
    Maintain requirements traceability per IEC 62304.
    
    FDA expects complete forward and backward traceability:
    - Requirements → Design → Code → Tests
    - Tests → Code → Design → Requirements
    """
    
    def __init__(self, device_name: str):
        self.device_name = device_name
        self.links: List[TraceabilityLink] = []
        self.coverage_metrics = {}
    
    def add_link(self, link: TraceabilityLink):
        """Add a traceability link"""
        self.links.append(link)
    
    def calculate_coverage(self) -> Dict[str, float]:
        """Calculate traceability coverage percentages"""
        
        all_reqs = set(link.req_id for link in self.links)
        all_designs = set(link.design_id for link in self.links)
        all_tests = set(link.test_case_id for link in self.links)
        
        # All requirements should have tests
        tested_reqs = set(
            link.req_id for link in self.links 
            if link.test_result == 'PASS'
        )
        
        self.coverage_metrics = {
            'total_requirements': len(all_reqs),
            'total_tests': len(all_tests),
            'tested_requirements': len(tested_reqs),
            'coverage_percent': (len(tested_reqs) / len(all_reqs) * 100) 
                if all_reqs else 0,
            'all_tests_passed': all(
                link.test_result == 'PASS' for link in self.links
            )
        }
        
        return self.coverage_metrics
    
    def find_gaps(self) -> Dict[str, List[str]]:
        """Identify traceability gaps"""
        
        gaps = {
            'untested_requirements': [],
            'failed_tests': [],
            'design_without_tests': [],
            'code_without_tests': []
        }
        
        # Find requirements without test links
        tested_reqs = set(link.req_id for link in self.links if link.test_case_id)
        all_reqs = set(link.req_id for link in self.links)
        gaps['untested_requirements'] = list(all_reqs - tested_reqs)
        
        # Find failed tests
        gaps['failed_tests'] = [
            link.test_case_id for link in self.links 
            if link.test_result == 'FAIL'
        ]
        
        # Find designs without tests
        tested_designs = set(link.design_id for link in self.links if link.test_case_id)
        all_designs = set(link.design_id for link in self.links)
        gaps['design_without_tests'] = list(all_designs - tested_designs)
        
        return gaps
    
    def export_matrix(self, filename: str):
        """Export traceability matrix for submission"""
        data = {
            'device': self.device_name,
            'links': [asdict(link) for link in self.links],
            'coverage': self.coverage_metrics,
            'gaps': self.find_gaps()
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)

# Example: Glucose Monitoring Device Traceability
def example_traceability():
    matrix = TraceabilityMatrix("Glucose Monitoring SaMD v1.0")
    
    # Requirement 1: Glucose input validation
    matrix.add_link(TraceabilityLink(
        req_id='REQ-GLU-001',
        design_id='DESIGN-INPUT-VAL-001',
        code_module='glucose_validation.py',
        test_case_id='TC-001',
        test_result='PASS',
        evidence_file='test_report_v1.0.pdf'
    ))
    
    # Requirement 2: Display reading
    matrix.add_link(TraceabilityLink(
        req_id='REQ-GLU-002',
        design_id='DESIGN-DISPLAY-001',
        code_module='ui_display.py',
        test_case_id='TC-002',
        test_result='PASS',
        evidence_file='test_report_v1.0.pdf'
    ))
    
    # Requirement 3: Alert if high
    matrix.add_link(TraceabilityLink(
        req_id='REQ-GLU-003',
        design_id='DESIGN-ALERT-001',
        code_module='alert_system.py',
        test_case_id='TC-003',
        test_result='PASS',
        evidence_file='test_report_v1.0.pdf'
    ))
    
    # Calculate coverage
    coverage = matrix.calculate_coverage()
    print(f"Traceability Coverage: {coverage['coverage_percent']:.1f}%")
    print(f"All tests passed: {coverage['all_tests_passed']}")
    
    # Find gaps
    gaps = matrix.find_gaps()
    print(f"Untested requirements: {gaps['untested_requirements']}")
    
    return matrix
