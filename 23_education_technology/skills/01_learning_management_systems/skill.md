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

### Production Deployment & Infrastructure

**Docker Containerization**:
```yaml
# docker-compose.yml for LMS deployment
version: '3.8'

services:
  web:
    build: ./app
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/lms_prod
      - REDIS_URL=redis://redis:6379/0
      - AWS_S3_BUCKET=lms-uploads
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      - db
      - redis
    volumes:
      - ./media:/app/media
    command: gunicorn lms.wsgi:application --bind 0.0.0.0:8000 --workers 4

  worker:
    build: ./app
    command: celery -A lms worker -l info --concurrency=4
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/lms_prod
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis

  db:
    image: postgres:14
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=lms_prod
      - POSTGRES_PASSWORD=password

  redis:
    image: redis:7
    volumes:
      - redis_data:/data

  nginx:
    image: nginx:latest
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./certbot/conf:/etc/letsencrypt
    depends_on:
      - web

volumes:
  postgres_data:
  redis_data:
```

**Kubernetes Deployment**:
```yaml
# lms-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: lms-web
spec:
  replicas: 3
  selector:
    matchLabels:
      app: lms
  template:
    metadata:
      labels:
        app: lms
    spec:
      containers:
      - name: lms
        image: lms:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: lms-secrets
              key: database-url
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5

---
apiVersion: v1
kind: Service
metadata:
  name: lms-service
spec:
  selector:
    app: lms
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer

---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: lms-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: lms-web
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

**Monitoring & Observability**:
```python
import structlog
from prometheus_client import Counter, Histogram, Gauge
import sentry_sdk

# Setup structured logging
logger = structlog.get_logger()

# Prometheus metrics
enrollment_counter = Counter('lms_enrollments_total', 'Total enrollments', ['course_id'])
assignment_submission_time = Histogram('lms_assignment_submission_seconds', 'Assignment submission time')
active_users_gauge = Gauge('lms_active_users', 'Currently active users')

class MonitoringMiddleware:
    """Track LMS metrics for production monitoring."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        import time
        start_time = time.time()

        response = self.get_response(request)

        # Log request with context
        logger.info(
            "request_processed",
            path=request.path,
            method=request.method,
            status_code=response.status_code,
            duration=time.time() - start_time,
            user_id=getattr(request.user, 'id', None)
        )

        return response

class HealthCheckEndpoint:
    """Health checks for load balancers and orchestrators."""

    def liveness_check(self):
        """Is the application running?"""
        return {'status': 'ok', 'timestamp': datetime.utcnow().isoformat()}

    def readiness_check(self):
        """Can the application handle traffic?"""
        checks = {
            'database': self._check_database(),
            'redis': self._check_redis(),
            'storage': self._check_storage()
        }

        all_ready = all(checks.values())

        return {
            'ready': all_ready,
            'checks': checks
        }

    def _check_database(self):
        """Verify database connection."""
        try:
            from django.db import connection
            connection.ensure_connection()
            return True
        except Exception as e:
            logger.error("database_check_failed", error=str(e))
            return False

    def _check_redis(self):
        """Verify Redis connection."""
        try:
            from django.core.cache import cache
            cache.set('health_check', 'ok', 10)
            return cache.get('health_check') == 'ok'
        except Exception as e:
            logger.error("redis_check_failed", error=str(e))
            return False

    def _check_storage(self):
        """Verify S3/storage access."""
        try:
            from django.core.files.storage import default_storage
            return default_storage.exists('.')
        except Exception as e:
            logger.error("storage_check_failed", error=str(e))
            return False
```

**Backup & Disaster Recovery**:
```bash
#!/bin/bash
# backup-lms.sh - Automated backup script

DATE=$(date +%Y-%m-%d_%H-%M-%S)
BACKUP_DIR="/backups/lms"

# Database backup with pg_dump
echo "Backing up database..."
pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME | gzip > "$BACKUP_DIR/db-$DATE.sql.gz"

# Media files backup with rsync
echo "Backing up media files..."
rsync -avz /app/media/ "$BACKUP_DIR/media-$DATE/"

# Upload to S3 for offsite storage
echo "Uploading to S3..."
aws s3 cp "$BACKUP_DIR/db-$DATE.sql.gz" "s3://lms-backups/database/"
aws s3 sync "$BACKUP_DIR/media-$DATE/" "s3://lms-backups/media/$DATE/"

# Retain only last 30 days locally
find $BACKUP_DIR -type f -mtime +30 -delete

echo "Backup completed: $DATE"
```

**Performance Testing**:
```python
from locust import HttpUser, task, between

class LMSUser(HttpUser):
    """Load testing scenarios for LMS performance."""

    wait_time = between(1, 5)

    @task(3)
    def view_course_list(self):
        """Most common action: Browse courses."""
        self.client.get("/courses")

    @task(5)
    def view_course_content(self):
        """View lesson content."""
        self.client.get("/courses/101/modules/1")

    @task(2)
    def submit_quiz(self):
        """Submit quiz answers."""
        self.client.post("/courses/101/quizzes/5/submit", json={
            'answers': {'q1': 'A', 'q2': 'B', 'q3': 'C'}
        })

    @task(1)
    def check_grades(self):
        """View gradebook."""
        self.client.get("/courses/101/grades")

# Run: locust -f locustfile.py --host=https://lms.example.com
```

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
