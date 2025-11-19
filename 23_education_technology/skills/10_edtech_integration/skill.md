# EdTech Integration & Interoperability Skill

## Purpose

You are an expert in educational technology standards, LTI, xAPI, SCORM, OneRoster, and building interoperable platforms. You enable seamless integration between LMS, SIS, assessment tools, and third-party applications, reducing data silos and enabling comprehensive learning analytics.

## Core Competencies

### LTI 1.3 / LTI Advantage Architecture

**LTI (Learning Tools Interoperability)**: Standard for launching external tools from LMS

```python
class LTI13Implementation:
    """
    LTI 1.3 uses OAuth 2.0 and OIDC for secure tool launching.
    Tool (assessment app) launches from LMS (Canvas, Moodle).
    User context (name, email, role) passed securely.
    """

    def platform_(self, client_id, client_secret, key_set_url):
        """
        LMS (Canvas) side: Registers as OAuth provider.
        """
        self.client_id = client_id      # Platform's identifier
        self.client_secret = client_secret
        self.key_set_url = key_set_url  # Public key for verifying signatures

    def tool_launch_request(self):
        """
        User clicks 'Launch Quiz' in Canvas.
        Canvas redirects to assessment tool with auth code.

        Canvas -> Tool: id_token (signed JWT with user info)
        {
            "sub": "user123",
            "name": "Jane Doe",
            "email": "jane@university.edu",
            "iss": "https://canvas.instructure.com",
            "aud": "assessment_tool_client_id",
            "iat": 1234567890,
            "exp": 1234571490
        }
        """
        pass

    def assignment_and_grade_services(self, course_id, assignment_id):
        """
        Tool sends grades back to Canvas (bidirectional sync).
        Tool -> Canvas: POST /grades with student scores
        """
        grade_submission = {
            'userId': 'user123',
            'scoreGiven': 85,
            'scoreMaximum': 100,
            'activityProgress': 'Completed',
            'gradingProgress': 'FullyGraded'
        }
        # Canvas updates gradebook automatically

    def names_and_role_provisioning(self, course_id):
        """
        Tool gets roster from Canvas (who's in the course?).
        Tool -> Canvas: GET /lineitem for course
        """
        roster = [
            {'userId': 'user123', 'name': 'Jane Doe', 'role': 'Learner'},
            {'userId': 'user456', 'name': 'John Smith', 'role': 'Instructor'}
        ]
        return roster

    def deep_linking(self):
        """
        Instructor selects content from tool to embed in course.
        Tool -> Canvas: Returns content_item_id + URL
        """
        # Tool provides content picker UI
        # Returns link back to Canvas to embed in course
        pass
```

**LTI Setup Flow**:
1. **Registration**: Tool registers with LMS (client_id, secret, key URL)
2. **Authentication**: User clicks "Launch Tool" in LMS
3. **Authorization**: LMS sends signed JWT with user context
4. **Tool Response**: Tool returns content + grade callback endpoint
5. **Grade Passback**: Tool sends grade back to LMS (optional)

### xAPI (Experience API) Full Stack

**xAPI Statement Structure** (comprehensive):
```python
class xAPIStatementBuilder:
    """
    Create complete xAPI statements for comprehensive learning tracking.
    Not limited to LMS - tracks any learning (informal, workplace, social).
    """

    def comprehensive_statement(self):
        """
        Complete xAPI statement with all optional fields.
        """
        return {
            "actor": {
                "objectType": "Agent",
                "name": "Jane Doe",
                "mbox": "mailto:jane@university.edu",  # or account, openid
                "account": {
                    "homePage": "https://university.edu/",
                    "name": "jane_doe_student_id_12345"
                }
            },
            "verb": {
                "id": "http://adlnet.gov/expapi/verbs/completed",
                "display": {
                    "en-US": "completed",
                    "es": "completó"
                }
            },
            "object": {
                "id": "https://university.edu/courses/bio101/modules/photosynthesis",
                "objectType": "Activity",
                "definition": {
                    "name": {
                        "en-US": "Photosynthesis Module"
                    },
                    "description": {
                        "en-US": "Understanding light and dark reactions"
                    },
                    "type": "http://adlnet.gov/expapi/activities/module",
                    "moreInfo": "https://university.edu/courses/bio101/modules/photosynthesis",
                    "extensions": {
                        "http://example.com/difficulty": "intermediate",
                        "http://example.com/subject": "biology"
                    }
                }
            },
            "result": {
                "score": {
                    "scaled": 0.85,  # 0.0-1.0
                    "raw": 85,
                    "min": 0,
                    "max": 100
                },
                "success": True,
                "completion": True,
                "response": "Answer: Photosynthesis converts CO2 to glucose",
                "duration": "PT50M",  # ISO 8601 duration
                "extensions": {
                    "http://example.com/attempts": 2,
                    "http://example.com/time_on_task": 45
                }
            },
            "context": {
                "registration": "ec531277-b57b-4c15-8d91-d292c5b2b8f7",
                "instructor": {
                    "objectType": "Agent",
                    "name": "Dr. Smith",
                    "mbox": "mailto:smith@university.edu"
                },
                "team": {
                    "objectType": "Group",
                    "name": "Bio 101 Section A",
                    "mbox": "mailto:bio101a@university.edu"
                },
                "contextActivities": {
                    "parent": [
                        {
                            "id": "https://university.edu/courses/bio101",
                            "objectType": "Activity"
                        }
                    ],
                    "grouping": [
                        {
                            "id": "https://university.edu/courses/bio101/semester/spring2025",
                            "objectType": "Activity"
                        }
                    ]
                },
                "language": "en-US",
                "extensions": {
                    "http://example.com/location": "Science Building Room 201"
                }
            },
            "timestamp": "2025-11-19T14:30:00Z",
            "stored": "2025-11-19T14:31:00Z",
            "authority": {
                "objectType": "Agent",
                "mbox": "mailto:lrs@university.edu"
            }
        }

    def query_learning_record_store(self, lrs_url, auth_token):
        """
        Query LRS for analytics.
        Examples:
        - Get all statements for user jane@university.edu
        - Get all completed activities in past 30 days
        - Get statements with specific verb (attempted, submitted, etc.)
        """
        query_params = {
            'agent': '{"mbox":"mailto:jane@university.edu"}',
            'verb': 'http://adlnet.gov/expapi/verbs/completed',
            'since': '2025-10-19T00:00:00Z',
            'until': '2025-11-19T23:59:59Z',
            'limit': 1000
        }
        # GET /statements?agent=...&verb=...&since=...
        # Returns array of xAPI statements matching filter
```

**LRS (Learning Record Store) Implementation**:
```python
class LearningRecordStore:
    """
    Store, retrieve, and analyze xAPI statements.
    Examples: Watershed LRS, Learning Locker, Collect.
    """

    def __init__(self, database):
        self.db = database
        self.statements = []

    def store_statement(self, statement):
        """
        Save xAPI statement to LRS.
        Validate: Required fields present, valid IDs/URLs.
        """
        # Validate statement
        required_fields = ['actor', 'verb', 'object']
        assert all(field in statement for field in required_fields)

        # Add metadata
        statement['id'] = uuid.uuid4()
        statement['stored'] = datetime.utcnow().isoformat() + 'Z'

        # Store
        self.db.statements.insert_one(statement)
        return statement['id']

    def query_statements(self, filters):
        """
        Query stored statements with filters.
        Returns aggregated results for learning analytics.
        """
        # Example: "Show me all students who completed Module 1"
        results = self.db.statements.find(filters)
        return list(results)

    def aggregate_analytics(self, agent_email, course_id):
        """
        Generate analytics from stored statements.
        Examples: Time spent, completion rate, mastery level.
        """
        statements = self.query_statements({
            'actor.mbox': f'mailto:{agent_email}',
            'context.contextActivities.parent.id': course_id
        })

        analytics = {
            'total_activities': len(statements),
            'completed': sum(1 for s in statements if s['result']['completion']),
            'avg_score': sum(s['result']['score']['scaled'] for s in statements
                           if 'score' in s['result']) / len(statements),
            'time_spent': sum(self.parse_duration(s['result']['duration'])
                            for s in statements if 'duration' in s['result'])
        }
        return analytics
```

### Educational Data Standards

**OneRoster** (SIS Integration):
```python
class OneRosterSync:
    """
    Sync student rosters, enrollments, grades between SIS and LMS.
    OneRoster 1.2 provides standard API for educational data exchange.
    """

    def sync_enrollments(self, sis_api_key):
        """
        OneRoster API provides:
        - Schools (institutions)
        - Courses (offerings)
        - Classes (sections)
        - Users (students/instructors)
        - Enrollments (student -> class mapping)
        """

        # GET /ims/oneroster/v1p2/schools
        schools = [
            {
                'sourcedId': 'school_123',
                'identifier': 'PS-001',
                'orgType': 'School',
                'name': 'Lincoln High School'
            }
        ]

        # GET /ims/oneroster/v1p2/users
        users = [
            {
                'sourcedId': 'user_456',
                'identifier': 'jane_doe',
                'email': 'jane@school.edu',
                'givenName': 'Jane',
                'familyName': 'Doe',
                'role': 'student'
            }
        ]

        # GET /ims/oneroster/v1p2/enrollments
        enrollments = [
            {
                'sourcedId': 'enrollment_789',
                'class': {'sourcedId': 'class_101'},
                'user': {'sourcedId': 'user_456'},
                'role': 'student',
                'status': 'active'
            }
        ]

        # Sync to LMS: Create/update users, enrollments
        self.sync_to_lms(users, enrollments)

    def sync_grades_to_sis(self, lms_gradebook):
        """
        Send grades from LMS back to SIS.
        POST /ims/oneroster/v1p2/results
        """
        for enrollment in lms_gradebook.enrollments:
            result = {
                'sourcedId': f"result_{enrollment.id}",
                'enrollment': {'sourcedId': enrollment.id},
                'lineItem': {'sourcedId': 'assignment_1'},
                'scoreGiven': enrollment.grade,
                'scoreMaximum': 100
            }
            # POST result to SIS
```

**Ed-Fi** (K-12 Standard):
- Similar to OneRoster but more comprehensive
- Includes learning standards, assessments, discipline data
- Used by K-12 schools, primarily US

**Caliper Analytics** (IMS):
```python
class CaliperAnalyticsEvent:
    """
    IMS Caliper: Standard for learning analytics events.
    More structured than xAPI, focuses on pedagogical meaning.
    """

    def student_attempted_question(self, student_id, question_id):
        return {
            '@context': 'http://purl.imsglobal.org/ctx/caliper/v1p1',
            '@type': 'AssessmentItemEvent',
            'actor': {
                '@id': f'https://university.edu/users/{student_id}',
                '@type': 'Person'
            },
            'action': 'Attempted',
            'object': {
                '@id': f'https://university.edu/assessments/items/{question_id}',
                '@type': 'AssessmentItem'
            },
            'eventTime': '2025-11-19T14:30:00Z'
        }
```

### API Design & Implementation

```python
class EducationAPIDesign:
    """
    Best practices for EdTech APIs.
    Must support both traditional (REST) and modern (GraphQL) approaches.
    """

    def rest_api_with_oauth(self):
        """
        RESTful API for grade passback, roster sync.
        Secured with OAuth 2.0.
        """
        endpoints = {
            'GET /users': 'Fetch user list',
            'GET /users/{id}': 'Get user details',
            'POST /grades': 'Submit grades',
            'GET /courses/{id}/enrollments': 'Get enrollment list'
        }

        # OAuth flow:
        # 1. Tool requests access token
        # 2. LMS verifies client_id/client_secret
        # 3. LMS returns access token
        # 4. Tool uses token to call API (Authorization: Bearer token)

    def graphql_for_flexible_queries(self):
        """
        GraphQL allows clients to request exact data needed.
        Reduces over-fetching (unnecessary fields).
        """
        query = """
        query {
          course(id: "101") {
            title
            students {
              id
              name
              grades {
                assignment
                score
              }
            }
          }
        }
        """
        # Returns only requested fields, no extra data

    def webhooks_for_realtime(self):
        """
        Webhooks notify tool when grade is updated.
        Tool doesn't need to poll (check repeatedly).
        """
        webhook_config = {
            'url': 'https://assessmenttool.com/webhooks/grades',
            'events': ['grade.created', 'grade.updated'],
            'secret': 'webhook_secret_for_verification'
        }
        # LMS POSTs to webhook when event occurs

    def batch_and_delta_sync(self):
        """
        Efficient syncing for large datasets.
        Batch: Request all data (for initial load)
        Delta: Request only changes since last sync
        """
        return {
            'batch_api': '/users/full (all users)',
            'delta_api': '/users/delta?since=2025-11-18T00:00:00Z (only changed)'
        }
```

### Integration Patterns & Architecture

```python
class IntegrationArchitecture:
    """
    Design patterns for connecting EdTech tools.
    """

    def hub_and_spoke(self):
        """
        Central LMS (hub) with tools (spokes).
        Example: Canvas with 20 third-party tools.
        Pros: Simple, centralized
        Cons: Doesn't work if tools need direct communication
        """
        diagram = """
        [Tool 1] - LTI
        [Tool 2] - LTI
        [Tool 3] - LTI
               \  |  /
                [Canvas LMS]
        """

    def full_integration_mesh(self):
        """
        All systems directly connected via APIs.
        Example: SIS <-> LMS <-> Assessment <-> Analytics
        Pros: Rich, direct communication
        Cons: Complex, many connections to maintain
        """
        diagram = """
        [SIS] <-> [LMS] <-> [Assessment Tool]
         ^   \____/   \____/   /
          \___________________ /
        [Analytics/Reporting]
        """

    def event_driven_architecture(self):
        """
        Systems communicate via event bus/streaming platform.
        When grade changes in LMS: Event published
        SIS subscribes: Receives event, updates database
        Pros: Loosely coupled, scalable
        Cons: Eventually consistent (not real-time)
        """
        return {
            'event_bus': 'Kafka, RabbitMQ, AWS EventBridge',
            'events': [
                'user.enrolled',
                'grade.submitted',
                'course.created',
                'attendance.recorded'
            ]
        }
```

### Data Privacy & Security in Integrations

```python
class IntegrationSecurity:
    """
    Secure data handling in multi-system integrations.
    """

    def jwt_signing_verification(self, tool_private_key, lms_public_key):
        """
        LMS signs JWT (with private key).
        Tool verifies signature (with LMS's public key).
        Tool trusts the claim because signature proves LMS sent it.
        """
        jwt_header = {
            'alg': 'RS256',
            'typ': 'JWT',
            'kid': 'key_id_123'  # Key ID for rotation
        }

    def pii_minimization(self):
        """
        Only send necessary data.
        Example: Tool only needs {user_id, role}, not {email, address}.
        """
        return {
            'lms_to_tool': ['user_id', 'role', 'course_id'],
            'tool_to_lms': ['user_id', 'score', 'completion_status']
        }

    def encryption_in_transit_and_rest(self):
        """
        HTTPS (in transit), database encryption (at rest).
        API keys/secrets: Never log, rotate regularly.
        """
        pass

    def audit_logging(self):
        """
        Log all API calls for compliance (FERPA, GDPR).
        Who accessed what data, when, from where.
        """
        log_entry = {
            'timestamp': '2025-11-19T14:30:00Z',
            'api_endpoint': 'POST /grades',
            'user_id': 'tool_service_account',
            'resource_id': 'course_101_student_jane',
            'action': 'submit_grade',
            'status': 'success'
        }
```

### Best Practices for Integration

1. **Standard-first**: Use LTI, xAPI, OneRoster when possible
2. **Secure by default**: HTTPS, OAuth 2.0, JWT validation
3. **Graceful degradation**: If integration fails, provide fallback
4. **Minimal data sharing**: Only exchange required fields
5. **Event-driven**: Use webhooks instead of polling
6. **Error handling**: Clear error messages for debugging
7. **Versioning**: API versions for backward compatibility
8. **Documentation**: Clear specs, example requests/responses
9. **Testing**: Automated integration tests
10. **Compliance**: FERPA, GDPR, ADA compliance built-in

---

**Version**: 2.0
**Last Updated**: 2025-11-19
**Maintained by**: CLAUDE_SKILLS Education Technology Domain
