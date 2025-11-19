# Learning Management Systems (LMS) Skill

## Purpose

You are an expert in Learning Management System (LMS) architecture, development, deployment, and optimization. You design and build scalable, accessible, feature-rich platforms that facilitate online and blended learning for K-12, higher education, and corporate training.

## Core Expertise

### LMS Architecture Patterns

**Multi-Tenancy Models**:
- **Shared Database, Shared Schema**: Single database, tenant_id columns (Moodle approach)
- **Shared Database, Separate Schemas**: PostgreSQL schemas per tenant
- **Separate Databases**: Full isolation, higher cost but maximum security
- **Hybrid**: Shared core data, isolated course/user data

**Microservices Architecture**:
- **Core Services**: Authentication, authorization, user management
- **Course Services**: Course catalog, enrollments, content delivery
- **Assessment Services**: Quizzing, grading, submissions
- **Analytics Services**: Learning records, reporting, dashboards
- **Integration Hub**: LTI, xAPI, SIS sync

### Database Schema Design

**Key Entities**:
```sql
-- Simplified LMS schema
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  username VARCHAR(255) UNIQUE NOT NULL,
  email VARCHAR(255) UNIQUE NOT NULL,
  hashed_password VARCHAR(255),
  role VARCHAR(50) DEFAULT 'student',
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE courses (
  id SERIAL PRIMARY KEY,
  code VARCHAR(50) UNIQUE,
  title VARCHAR(500) NOT NULL,
  description TEXT,
  start_date DATE,
  end_date DATE,
  published BOOLEAN DEFAULT false
);

CREATE TABLE enrollments (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
  course_id INTEGER REFERENCES courses(id) ON DELETE CASCADE,
  role VARCHAR(50) DEFAULT 'student', -- student, instructor, ta, observer
  enrolled_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(user_id, course_id)
);

CREATE TABLE course_modules (
  id SERIAL PRIMARY KEY,
  course_id INTEGER REFERENCES courses(id) ON DELETE CASCADE,
  title VARCHAR(500),
  position INTEGER,
  published BOOLEAN DEFAULT false
);

CREATE TABLE assignments (
  id SERIAL PRIMARY KEY,
  course_id INTEGER REFERENCES courses(id) ON DELETE CASCADE,
  module_id INTEGER REFERENCES course_modules(id) ON DELETE SET NULL,
  title VARCHAR(500) NOT NULL,
  description TEXT,
  points_possible DECIMAL(10, 2),
  due_at TIMESTAMP,
  submission_types VARCHAR(255)[], -- ['online_upload', 'online_text_entry', 'online_url']
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE submissions (
  id SERIAL PRIMARY KEY,
  assignment_id INTEGER REFERENCES assignments(id) ON DELETE CASCADE,
  user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
  submitted_at TIMESTAMP DEFAULT NOW(),
  attempt INTEGER DEFAULT 1,
  body TEXT, -- for text submissions
  url VARCHAR(2048), -- for URL submissions
  workflow_state VARCHAR(50) DEFAULT 'submitted', -- submitted, graded, returned
  UNIQUE(assignment_id, user_id, attempt)
);

CREATE TABLE grades (
  id SERIAL PRIMARY KEY,
  submission_id INTEGER REFERENCES submissions(id) ON DELETE CASCADE,
  grader_id INTEGER REFERENCES users(id),
  score DECIMAL(10, 2),
  comment TEXT,
  graded_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE gradebook_entries (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
  assignment_id INTEGER REFERENCES assignments(id) ON DELETE CASCADE,
  course_id INTEGER REFERENCES courses(id) ON DELETE CASCADE,
  score DECIMAL(10, 2),
  grade VARCHAR(10), -- 'A', 'B+', 'Pass', etc.
  updated_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(user_id, assignment_id)
);
```

### Gradebook Engine

**Weighted Categories**:
```python
class GradebookCalculator:
    """
    Calculate course grades with weighted categories and dropped scores.

    Canvas-inspired gradebook with:
    - Weighted assignment groups (Homework 30%, Exams 50%, Participation 20%)
    - Drop lowest N scores per category
    - What-if score calculations
    - Letter grade thresholds
    """

    def calculate_course_grade(self, user_id, course_id):
        """
        Calculate total course grade for a student.

        Returns: {
            'score': 87.5,  # Weighted percentage
            'letter_grade': 'B+',
            'breakdown': {category: score}
        }
        """
        course = Course.objects.get(id=course_id)
        assignment_groups = course.assignment_groups.all()

        category_scores = {}
        total_weight = 0

        for group in assignment_groups:
            group_score = self.calculate_group_score(
                user_id,
                group,
                drop_lowest=group.drop_lowest
            )
            if group_score is not None:
                category_scores[group.name] = group_score
                total_weight += group.weight

        # Normalize if total weight != 100%
        if total_weight > 0:
            final_score = sum(
                score * (group.weight / total_weight)
                for group, score in category_scores.items()
            )
        else:
            final_score = 0

        return {
            'score': round(final_score, 2),
            'letter_grade': self.score_to_letter(final_score, course.grading_scheme),
            'breakdown': category_scores
        }

    def calculate_group_score(self, user_id, assignment_group, drop_lowest=0):
        """Calculate score for one assignment category."""
        assignments = assignment_group.assignments.filter(published=True)
        scores = []

        for assignment in assignments:
            grade = GradebookEntry.objects.filter(
                user_id=user_id,
                assignment=assignment
            ).first()

            if grade and grade.score is not None:
                percentage = (grade.score / assignment.points_possible) * 100
                scores.append(percentage)

        if not scores:
            return None

        # Drop lowest N scores
        if drop_lowest > 0 and len(scores) > drop_lowest:
            scores.sort()
            scores = scores[drop_lowest:]

        return sum(scores) / len(scores)

    def score_to_letter(self, score, grading_scheme):
        """Convert numeric score to letter grade."""
        # Default scheme: A (90-100), B (80-89), C (70-79), D (60-69), F (<60)
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'
```

### Content Organization

**Course Structure Hierarchy**:
```
Course
├── Modules (Units, Weeks)
│   ├── Items (Lessons, Activities)
│   │   ├── Pages (HTML content)
│   │   ├── Assignments
│   │   ├── Quizzes
│   │   ├── Discussions
│   │   ├── External Tools (LTI)
│   │   └── Files/Links
```

**Module Requirements** (prerequisites and sequence enforcement):
```python
class ModuleRequirement:
    """Enforce prerequisite completion before access."""

    REQUIREMENT_TYPES = [
        'view',        # Must view the item
        'submit',      # Must submit assignment
        'score_at_least',  # Must score X points
        'complete'     # Must mark as complete
    ]

    def check_requirement(self, user_id, module_item, requirement_type):
        """Check if user has met the requirement."""
        if requirement_type == 'view':
            return ModuleItemView.objects.filter(
                user_id=user_id,
                module_item=module_item
            ).exists()

        elif requirement_type == 'submit':
            return Submission.objects.filter(
                user_id=user_id,
                assignment=module_item.assignment
            ).exists()

        elif requirement_type == 'score_at_least':
            grade = GradebookEntry.objects.filter(
                user_id=user_id,
                assignment=module_item.assignment
            ).first()
            return grade and grade.score >= module_item.min_score

        # ... other requirement types

    def get_locked_items(self, user_id, module):
        """Return items user cannot access due to unmet requirements."""
        locked = []
        for item in module.items.all():
            if item.has_requirement and not self.check_requirement(user_id, item):
                locked.append(item)
        return locked
```

### Communication Systems

**Announcements, Discussions, Messaging**:
```python
# Announcement model
class Announcement(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=500)
    body = models.TextField()
    posted_at = models.DateTimeField(auto_now_add=True)
    pinned = models.BooleanField(default=False)

    # Notification settings
    notify_email = models.BooleanField(default=True)
    notify_push = models.BooleanField(default=True)

# Discussion forum (threaded)
class DiscussionTopic(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    module = models.ForeignKey(CourseModule, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=500)
    description = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=50)  # discussion, q_and_a, announcement
    graded = models.BooleanField(default=False)
    points_possible = models.DecimalField(max_digits=10, decimal_places=2, null=True)

class DiscussionPost(models.Model):
    topic = models.ForeignKey(DiscussionTopic, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    parent_post = models.ForeignKey('self', on_delete=models.CASCADE, null=True)
    body = models.TextField()
    posted_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(null=True)
    likes = models.ManyToManyField(User, related_name='liked_posts')
```

### LTI Integration Hub

**See standards/api-guides/lti_implementation_guide.md for complete implementation.**

**Key Integration Points**:
- Tool launch from course navigation, assignments, modules
- Deep linking for content selection
- Grade passback via Assignment and Grade Services (AGS)
- Roster sync via Names and Role Provisioning Service (NRPS)

### Mobile & Progressive Web App

**PWA Features**:
```javascript
// Service worker for offline caching
const CACHE_VERSION = 'lms-v1';
const STATIC_CACHE = [
  '/',
  '/css/main.css',
  '/js/app.js',
  '/images/logo.svg'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_VERSION)
      .then(cache => cache.addAll(STATIC_CACHE))
  );
});

// Network-first for API, cache-first for assets
self.addEventListener('fetch', event => {
  if (event.request.url.includes('/api/')) {
    // Network-first for fresh data
    event.respondWith(
      fetch(event.request)
        .then(response => {
          const clone = response.clone();
          caches.open(CACHE_VERSION)
            .then(cache => cache.put(event.request, clone));
          return response;
        })
        .catch(() => caches.match(event.request))
    );
  } else {
    // Cache-first for static assets
    event.respondWith(
      caches.match(event.request)
        .then(response => response || fetch(event.request))
    );
  }
});
```

### Performance & Scalability

**Caching Strategy**:
- Redis for session storage (fast access to user data)
- CDN for static assets and video content (CloudFront, Cloudflare)
- Database query caching for read-heavy endpoints (course content)
- Fragment caching for rendered HTML (course homepage)

**Database Optimization**:
- Read replicas for course content queries
- Sharding by institution or tenant
- Indexing on frequently queried columns (user_id, course_id, created_at)
- Denormalization for gradebook (pre-calculated totals)

**Auto-Scaling**:
- Kubernetes HPA based on CPU/memory
- Separate scaling for CPU-intensive services (video encoding, grading)
- Queue-based load leveling for batch operations (notifications, grade calculations)

### Analytics & Reporting

**Learning Records**:
- xAPI events for all learning activities
- Page views, time on task, resource access
- Assignment submissions, quiz attempts
- Discussion participation

**Instructor Dashboards**:
- Course analytics: Enrollment, completion, grade distribution
- Student progress tracking: At-risk indicators, engagement scores
- Assignment analytics: Average score, submission rate, time to complete

## Industry References

**Leading LMS Platforms**:
- **Canvas** (Instructure): React + Ruby on Rails, API-first
- **Moodle**: PHP, open-source, plugin architecture
- **Open edX**: Django, XBlock components, MOOC-focused
- **Blackboard Learn**: Java EE, enterprise-focused
- **Google Classroom**: Minimal LMS, G Suite integration

**Technologies**:
- Backend: Ruby on Rails, Django, Node.js, Java Spring Boot
- Frontend: React, Vue, Angular
- Databases: PostgreSQL, MySQL, MongoDB
- Caching: Redis, Memcached
- Queue: RabbitMQ, AWS SQS, Celery
- Search: Elasticsearch
- Video: Kaltura, AWS Elemental, custom HLS/DASH

---

**Version**: 1.0
**Last Updated**: 2025-11-19
**Maintained by**: CLAUDE_SKILLS Education Technology Domain
