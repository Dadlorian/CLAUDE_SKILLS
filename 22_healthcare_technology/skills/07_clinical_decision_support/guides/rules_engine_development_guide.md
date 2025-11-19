# Rules Engine Development Guide

## Overview
Comprehensive guide to developing and deploying clinical rules engines for decision support.

## Architecture Decision

### Choosing a Rules Engine

**Drools (JBoss Rules)**
- Best for: Complex business logic, Java environments
- Pros: Mature, powerful, Rete algorithm
- Cons: Steeper learning curve
- Use when: Complex rule interactions, performance critical

**Arden Syntax**
- Best for: Healthcare-specific logic, knowledge sharing
- Pros: Healthcare standard, readable
- Cons: Limited adoption, older technology
- Use when: Implementing published MLMs

**CQL (Clinical Quality Language)**
- Best for: FHIR-based systems, quality measures
- Pros: Modern, FHIR-native, growing adoption
- Cons: Relatively new, fewer tools
- Use when: FHIR environment, quality reporting

**Custom Python/JavaScript**
- Best for: Simple rules, rapid prototyping
- Pros: Flexibility, easy to understand
- Cons: No optimization, manual management
- Use when: Few rules, simple logic

## Step 1: Define Clinical Logic

### Gather Requirements
```markdown
# Rule Specification Template

## Rule Name
Hyperkalemia Alert

## Clinical Rationale
Potassium > 6.0 mmol/L is life-threatening emergency

## Triggering Condition
- Potassium lab result > 6.0 mmol/L
- Lab status = "final"

## Target Users
- Ordering provider
- Primary nurse
- Rapid response team (if K+ > 6.5)

## Actions
1. Display critical alert
2. Page ordering provider
3. Recommend interventions

## Evidence
- UpToDate: Treatment of Hyperkalemia
- Internal K+ management protocol

## Exclusion Criteria
- Patient on dialysis (expected high K+)
- Hemolyzed specimen

## Alert Timing
- Immediate upon lab result

## Severity
Critical (hard stop)
```

## Step 2: Drools Implementation

### Project Setup
```bash
mvn archetype:generate \
  -DgroupId=com.hospital.cds \
  -DartifactId=clinical-rules-engine \
  -DarchetypeArtifactId=maven-archetype-quickstart
  
# Add dependencies to pom.xml
```

### Maven Dependencies
```xml
<dependencies>
  <dependency>
    <groupId>org.drools</groupId>
    <artifactId>drools-core</artifactId>
    <version>8.40.0.Final</version>
  </dependency>
  <dependency>
    <groupId>org.drools</groupId>
    <artifactId>drools-compiler</artifactId>
    <version>8.40.0.Final</version>
  </dependency>
</dependencies>
```

### Define Domain Model
```java
// Patient.java
public class Patient {
    private String id;
    private int age;
    private String gender;
    private List<String> conditions;
    private List<Medication> medications;
    private List<LabResult> labs;
    
    // Getters and setters
}

// LabResult.java
public class LabResult {
    private String testCode;  // LOINC
    private double value;
    private String unit;
    private String status;
    private Date resultTime;
    
    public boolean isCritical() {
        // Define critical values by LOINC
        if ("2160-0".equals(testCode)) {  // Creatinine
            return value > 3.0;
        }
        if ("2823-3".equals(testCode)) {  // Potassium
            return value > 6.0 || value < 2.5;
        }
        return false;
    }
}

// ClinicalAlert.java
public class ClinicalAlert {
    private String severity;  // INFO, WARNING, CRITICAL
    private String message;
    private String recommendation;
    private List<String> actions;
    private String source;
}
```

### Write Drools Rules
```drools
// rules/critical-labs.drl
package com.hospital.cds.rules

import com.hospital.cds.model.*;

rule "Critical Hyperkalemia"
    when
        $patient: Patient()
        $lab: LabResult(
            testCode == "2823-3",  // LOINC for Potassium
            value > 6.0,
            status == "final"
        )
    then
        ClinicalAlert alert = new ClinicalAlert();
        alert.setSeverity("CRITICAL");
        alert.setMessage("CRITICAL: Potassium " + $lab.getValue() + " mmol/L");
        alert.setRecommendation(
            "1. Repeat K+ to confirm\n" +
            "2. Check EKG for peaked T waves\n" +
            "3. Consider: Calcium gluconate (if EKG changes), " +
            "Insulin + D50, Kayexalate\n" +
            "4. Restrict dietary potassium"
        );
        alert.setSource("Critical Lab Alert System");
        insert(alert);
end

rule "Acute Kidney Injury - KDIGO Stage 1"
    when
        $patient: Patient()
        $baseline: LabResult(
            testCode == "2160-0",  // Creatinine
            $baselineValue: value,
            $baselineTime: resultTime
        )
        $current: LabResult(
            testCode == "2160-0",
            value > $baselineValue + 0.3,  // Increase ≥ 0.3 mg/dL
            resultTime > $baselineTime,
            this after[0h, 48h] $baseline
        )
    then
        ClinicalAlert alert = new ClinicalAlert();
        alert.setSeverity("WARNING");
        alert.setMessage("Possible AKI: Creatinine increased from " +
            $baselineValue + " to " + $current.getValue() + " mg/dL");
        alert.setRecommendation(
            "1. Review nephrotoxic medications (NSAIDs, contrast, aminoglycosides)\n" +
            "2. Ensure adequate hydration\n" +
            "3. Monitor creatinine daily\n" +
            "4. Consider nephrology consult if worsening"
        );
        insert(alert);
end

rule "Sepsis Screening - qSOFA"
    when
        $patient: Patient(age >= 18)
        $vitals: VitalSigns(
            respiratoryRate >= 22 ||
            systolicBP <= 100 ||
            glasgowComaScore < 15
        )
        Number(intValue >= 2) from accumulate(
            Integer($v: intValue) from [
                ($vitals.getRespiratoryRate() >= 22 ? 1 : 0),
                ($vitals.getSystolicBP() <= 100 ? 1 : 0),
                ($vitals.getGlasgowComaScore() < 15 ? 1 : 0)
            ],
            sum($v)
        )
    then
        ClinicalAlert alert = new ClinicalAlert();
        alert.setSeverity("CRITICAL");
        alert.setMessage("SEPSIS ALERT: qSOFA ≥ 2");
        alert.setRecommendation(
            "Initiate sepsis bundle:\n" +
            "1. Obtain blood cultures (before antibiotics)\n" +
            "2. Measure lactate\n" +
            "3. Administer broad-spectrum antibiotics within 1 hour\n" +
            "4. IV fluids 30 mL/kg if hypotensive or lactate ≥ 4\n" +
            "5. Vasopressors if MAP < 65 despite fluids"
        );
        insert(alert);
end
```

### Rules Engine Service
```java
public class ClinicalRulesEngine {
    private KieContainer kieContainer;
    
    public ClinicalRulesEngine() {
        KieServices ks = KieServices.Factory.get();
        this.kieContainer = ks.getKieClasspathContainer();
    }
    
    public List<ClinicalAlert> evaluatePatient(Patient patient) {
        KieSession kSession = kieContainer.newKieSession();
        
        try {
            // Insert patient and related facts
            kSession.insert(patient);
            
            for (LabResult lab : patient.getLabs()) {
                kSession.insert(lab);
            }
            
            for (Medication med : patient.getMedications()) {
                kSession.insert(med);
            }
            
            // Fire all rules
            kSession.fireAllRules();
            
            // Collect generated alerts
            List<ClinicalAlert> alerts = new ArrayList<>();
            for (Object obj : kSession.getObjects()) {
                if (obj instanceof ClinicalAlert) {
                    alerts.add((ClinicalAlert) obj);
                }
            }
            
            return alerts;
            
        } finally {
            kSession.dispose();
        }
    }
}
```

## Step 3: Python Rules Engine

### Simple Python Implementation
```python
from dataclasses import dataclass
from typing import List, Callable
from datetime import datetime

@dataclass
class LabResult:
    test_code: str
    value: float
    unit: str
    timestamp: datetime
    status: str = "final"

@dataclass
class Patient:
    id: str
    age: int
    labs: List[LabResult]
    medications: List[str]
    conditions: List[str]

@dataclass
class ClinicalAlert:
    severity: str
    message: str
    recommendation: str
    rule_id: str

class RuleEngine:
    def __init__(self):
        self.rules: List[Callable] = []
    
    def add_rule(self, rule_func: Callable):
        """Decorator to add rules"""
        self.rules.append(rule_func)
        return rule_func
    
    def evaluate(self, patient: Patient) -> List[ClinicalAlert]:
        alerts = []
        for rule in self.rules:
            result = rule(patient)
            if result:
                if isinstance(result, list):
                    alerts.extend(result)
                else:
                    alerts.append(result)
        return alerts

# Initialize engine
engine = RuleEngine()

# Define rules
@engine.add_rule
def check_hyperkalemia(patient: Patient) -> ClinicalAlert:
    """Critical hyperkalemia alert"""
    for lab in patient.labs:
        if lab.test_code == "2823-3" and lab.value > 6.0:
            return ClinicalAlert(
                severity="CRITICAL",
                message=f"CRITICAL: Potassium {lab.value} mmol/L",
                recommendation=(
                    "1. Repeat K+ to confirm\n"
                    "2. Check EKG\n"
                    "3. Consider calcium gluconate, insulin+D50"
                ),
                rule_id="hyperkalemia_critical"
            )
    return None

@engine.add_rule
def check_aki(patient: Patient) -> ClinicalAlert:
    """AKI detection using KDIGO criteria"""
    cr_labs = [lab for lab in patient.labs if lab.test_code == "2160-0"]
    cr_labs.sort(key=lambda x: x.timestamp)
    
    if len(cr_labs) >= 2:
        baseline = cr_labs[0].value
        current = cr_labs[-1].value
        
        # KDIGO Stage 1: Increase ≥ 0.3 mg/dL
        if current > baseline + 0.3:
            return ClinicalAlert(
                severity="WARNING",
                message=f"Possible AKI: Cr {baseline} → {current} mg/dL",
                recommendation=(
                    "1. Review nephrotoxic medications\n"
                    "2. Ensure hydration\n"
                    "3. Monitor daily creatinine"
                ),
                rule_id="aki_kdigo_stage1"
            )
    return None

# Usage
patient = Patient(
    id="PT123",
    age=65,
    labs=[
        LabResult("2823-3", 6.5, "mmol/L", datetime.now())
    ],
    medications=["lisinopril", "spironolactone"],
    conditions=["CKD"]
)

alerts = engine.evaluate(patient)
for alert in alerts:
    print(f"{alert.severity}: {alert.message}")
```

## Step 4: Testing

### Unit Tests
```java
@Test
public void testHyperkalemiaRule() {
    KieSession kSession = kieContainer.newKieSession();
    
    Patient patient = new Patient();
    patient.setId("PT123");
    
    LabResult potassium = new LabResult();
    potassium.setTestCode("2823-3");
    potassium.setValue(6.5);
    potassium.setUnit("mmol/L");
    potassium.setStatus("final");
    
    kSession.insert(patient);
    kSession.insert(potassium);
    kSession.fireAllRules();
    
    Collection<?> alerts = kSession.getObjects(
        new ClassObjectFilter(ClinicalAlert.class)
    );
    
    assertEquals(1, alerts.size());
    ClinicalAlert alert = (ClinicalAlert) alerts.iterator().next();
    assertEquals("CRITICAL", alert.getSeverity());
    
    kSession.dispose();
}
```

## Step 5: Deployment & Monitoring

### REST API Wrapper
```java
@RestController
@RequestMapping("/api/cds")
public class CDSController {
    @Autowired
    private ClinicalRulesEngine rulesEngine;
    
    @PostMapping("/evaluate")
    public ResponseEntity<List<ClinicalAlert>> evaluate(@RequestBody Patient patient) {
        try {
            List<ClinicalAlert> alerts = rulesEngine.evaluatePatient(patient);
            return ResponseEntity.ok(alerts);
        } catch (Exception e) {
            return ResponseEntity.status(500).build();
        }
    }
}
```

### Monitoring
```java
@Aspect
@Component
public class RulesMonitoring {
    @Around("execution(* com.hospital.cds.ClinicalRulesEngine.evaluatePatient(..))")
    public Object monitorRulesExecution(ProceedingJoinPoint pjp) throws Throwable {
        long start = System.currentTimeMillis();
        
        try {
            Object result = pjp.proceed();
            long duration = System.currentTimeMillis() - start;
            
            // Log metrics
            metricsService.recordRuleExecutionTime(duration);
            
            if (result instanceof List) {
                metricsService.recordAlertCount(((List<?>) result).size());
            }
            
            return result;
        } catch (Exception e) {
            metricsService.recordRuleFailure();
            throw e;
        }
    }
}
```

## Best Practices

1. **Rule Independence**: Each rule should be independent
2. **Performance**: Optimize rule ordering, use indexing
3. **Testing**: Comprehensive test coverage with clinical scenarios
4. **Version Control**: Track rule changes with clinical rationale
5. **Clinical Validation**: Physician review before deployment
6. **Monitoring**: Track firing rates, execution time, outcomes
7. **Documentation**: Clear clinical rationale for each rule
8. **Governance**: Formal approval process for new/modified rules

## Common Pitfalls

1. **Infinite Loops**: Rules that insert facts triggering themselves
2. **Performance**: Too many rules evaluated for each patient
3. **Maintenance**: Hard-coded values instead of configurable parameters
4. **Conflicts**: Multiple rules firing with contradictory recommendations

## Resources
- Drools Documentation: https://docs.drools.org
- Arden Syntax: ASTM E2210
- CQL Specification: https://cql.hl7.org
- OpenCDS: https://www.opencds.org
