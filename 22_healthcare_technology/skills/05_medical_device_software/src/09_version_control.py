"""Software Version Control and Configuration Management"""
from dataclasses import dataclass
from datetime import datetime
from typing import List

@dataclass
class SoftwareVersion:
    """Software release version per IEC 62304"""
    major: int
    minor: int
    patch: int
    release_date: str
    description: str
    changes: List[str]
    tested: bool = False
    approved: bool = False
    
    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"
    
    def is_release_candidate(self) -> bool:
        """Ready for release if tested and approved"""
        return self.tested and self.approved

class VersionManager:
    """Manage medical device software versions per configuration management plan"""
    
    def __init__(self, device_name: str):
        self.device_name = device_name
        self.versions: List[SoftwareVersion] = []
        self.current_version = None
        self.released_versions = []
    
    def create_version(
        self,
        major: int,
        minor: int,
        patch: int,
        description: str,
        changes: List[str]
    ) -> SoftwareVersion:
        """Create new development version"""
        
        version = SoftwareVersion(
            major=major,
            minor=minor,
            patch=patch,
            release_date=datetime.now().isoformat(),
            description=description,
            changes=changes
        )
        
        self.versions.append(version)
        self.current_version = version
        
        print(f"Created version {version}")
        return version
    
    def mark_tested(self, version: SoftwareVersion) -> bool:
        """Mark version as testing complete"""
        version.tested = True
        print(f"Version {version} marked as tested")
        return True
    
    def approve_release(self, version: SoftwareVersion, approver: str) -> bool:
        """Approve version for release"""
        
        if not version.tested:
            print(f"Version {version} not yet tested")
            return False
        
        version.approved = True
        self.released_versions.append(version)
        print(f"Version {version} approved for release by {approver}")
        return True
    
    def is_backward_compatible(self, old_version: SoftwareVersion, 
                               new_version: SoftwareVersion) -> bool:
        """Check backward compatibility"""
        # Patch version: fully compatible
        if old_version.major == new_version.major and \
           old_version.minor == new_version.minor:
            return True
        # Minor version: generally compatible (should test)
        if old_version.major == new_version.major:
            return True  # Assume compatible, require testing
        # Major version: likely incompatible
        return False

# Example: Glucose Monitor Version Management
def example_version_management():
    manager = VersionManager("Glucose Monitor SaMD")
    
    # Create v1.0.0
    v1_0_0 = manager.create_version(
        major=1, minor=0, patch=0,
        description="Initial release",
        changes=[
            "Core glucose reading functionality",
            "Basic UI display",
            "Alert for high glucose"
        ]
    )
    
    manager.mark_tested(v1_0_0)
    manager.approve_release(v1_0_0, "Dr. Smith (Quality)")
    
    # Create v1.1.0 (minor version - new features)
    v1_1_0 = manager.create_version(
        major=1, minor=1, patch=0,
        description="Add Bluetooth connectivity",
        changes=[
            "Bluetooth data synchronization",
            "Mobile app integration"
        ]
    )
    
    manager.mark_tested(v1_1_0)
    manager.approve_release(v1_1_0, "Dr. Smith (Quality)")
    
    # Create v2.0.0 (major version - architecture change)
    v2_0_0 = manager.create_version(
        major=2, minor=0, patch=0,
        description="Complete redesign with AI analysis",
        changes=[
            "Machine learning trend analysis",
            "Predictive alerts",
            "Cloud backup"
        ]
    )
    
    print(f"\nReleased versions: {[str(v) for v in manager.released_versions]}")
    print(f"Current version: {manager.current_version}")
