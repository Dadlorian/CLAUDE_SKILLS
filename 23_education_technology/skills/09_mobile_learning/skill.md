# Mobile Learning & Offline Capabilities Skill

## Purpose

You are an expert in mobile-first educational design, offline-capable learning apps, microlearning, and native mobile development. You build systems that work seamlessly on smartphones and tablets, online and offline, providing engaging learning experiences optimized for small screens and intermittent connectivity. Your expertise spans responsive design, offline-first architecture, and device feature integration.

## Core Competencies

### Mobile-First Design Principles

**Touch Optimization**:
```html
<!-- Minimum touch target size: 44x44px (Apple), 48x48dp (Google) -->
<button class="action-button">
  <!-- Text + icon, both tappable -->
  <svg width="24" height="24" viewBox="0 0 24 24">
    <!-- Icon -->
  </svg>
  <span>Submit Answer</span>
</button>

<style>
  .action-button {
    min-width: 48px;
    min-height: 48px;
    padding: 12px;
    margin: 8px;  /* Space between targets */
  }

  /* Avoid hover-only interactions */
  .action-button {
    cursor: pointer;
  }
  /* No :hover required since touch doesn't hover */

  /* Provide visual feedback for touch */
  .action-button:active {
    background-color: rgba(0, 0, 0, 0.2);
    transform: scale(0.98);
  }
</style>
```

**Thumb-Friendly Navigation**:
```javascript
class MobileNavigation {
  /**
   * Put frequently used items in bottom navigation.
   * Users hold phone with thumb and can naturally reach bottom.
   */

  constructor() {
    this.bottomNavItems = [
      { icon: 'home', label: 'Home', active: true },
      { icon: 'search', label: 'Search', active: false },
      { icon: 'messages', label: 'Messages', active: false },
      { icon: 'profile', label: 'Profile', active: false }
    ];

    // Top of screen has status bar (hard to reach with thumb)
    // Bottom has navigation (easy to reach)
    // Content in middle
  }

  render() {
    return `
      <main style="padding-bottom: 64px;"> <!-- Account for bottom nav -->
        <!-- Main content -->
      </main>

      <nav class="bottom-nav" style="position: fixed; bottom: 0; height: 56px;">
        ${this.bottomNavItems.map(item => `
          <button class="${item.active ? 'active' : ''}">
            <i class="icon-${item.icon}"></i>
            <span>${item.label}</span>
          </button>
        `).join('')}
      </nav>
    `;
  }
}
```

**Responsive Layouts**:
```css
/* Mobile-first: Design for 320px width first, then enhance for larger screens */

body {
  font-size: 16px; /* Minimum for comfortable reading */
  padding: 16px;
}

/* One column on mobile */
.lesson-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.lesson-video { width: 100%; }
.lesson-quiz { width: 100%; }

/* Two columns on tablet (480px+) */
@media (min-width: 480px) {
  .lesson-content {
    flex-direction: row;
  }
  .lesson-video { flex: 1; }
  .lesson-quiz { flex: 1; }
}

/* Three columns on desktop (1024px+) */
@media (min-width: 1024px) {
  .lesson-content {
    grid-template-columns: 1fr 1fr 1fr;
  }
}

/* Readable text widths */
.article { max-width: 65ch; }  /* ~65 characters per line */
```

**Performance Optimization**:
```javascript
class MobilePerformance {
  /**
   * Mobile devices often have:
   * - Slower networks (3G, 4G)
   * - Less CPU/memory than desktop
   * - Battery constraints
   */

  implement_lazy_loading() {
    // Images load only when near viewport
    const images = document.querySelectorAll('img[loading="lazy"]');
    // Browser handles with Intersection Observer API

    // Videos lazy-load poster
    // Actual video stream starts on click
  }

  code_splitting() {
    // Only load code needed for current page
    // Example: Quiz code only when on quiz page
    import('./quiz-module.js').then(module => {
      module.initQuiz();
    });
  }

  optimize_bundle_size() {
    // Large JavaScript slows app load and drains battery
    // Minify: Remove comments, whitespace
    // Tree-shake: Remove unused code
    // Compression: GZIP reduces file size ~70%
    return {
      minified_js: '50KB',
      minified_css: '10KB',
      compressed_total: '30KB'
    };
  }

  battery_aware_features() {
    // Detect low battery mode (iOS), low power mode (Android)
    if ('getBattery' in navigator) {
      navigator.getBattery().then(battery => {
        if (battery.level < 0.2) {
          // Disable video autoplay, reduce animation
          document.body.classList.add('low-battery');
        }
      });
    }
  }
}
```

### Offline-First Architecture

**Service Workers & Caching**:
```javascript
// service-worker.js
const CACHE_VERSION = 'edtech-v1';
const CRITICAL_ASSETS = [
  '/',
  '/index.html',
  '/css/main.css',
  '/js/app.js',
  '/offline.html'
];

// Install: Pre-cache critical assets
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_VERSION)
      .then(cache => cache.addAll(CRITICAL_ASSETS))
      .then(() => self.skipWaiting())
  );
});

// Fetch: Network-first for API, cache-first for assets
self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);

  if (url.pathname.startsWith('/api/')) {
    // API: Try network first, fall back to cache
    event.respondWith(
      fetch(event.request)
        .then(response => {
          // Cache successful responses
          const clone = response.clone();
          caches.open(CACHE_VERSION)
            .then(cache => cache.put(event.request, clone));
          return response;
        })
        .catch(() => {
          // Return cached response if offline
          return caches.match(event.request);
        })
    );
  } else {
    // Assets: Use cache, fall back to network
    event.respondWith(
      caches.match(event.request)
        .then(response => response || fetch(event.request))
    );
  }
});
```

**Offline Data Storage (IndexedDB)**:
```javascript
class OfflineDataManager {
  /**
   * IndexedDB: Client-side database for offline access.
   * Better than localStorage (10MB limit): IndexedDB supports gigabytes.
   */

  async storeOfflineContent(lesson) {
    const db = await this.openDatabase();
    const tx = db.transaction('lessons', 'readwrite');

    tx.objectStore('lessons').put({
      id: lesson.id,
      title: lesson.title,
      content: lesson.content,
      video_blob: lesson.video,  // Can store video blobs
      downloaded_at: Date.now(),
      synced: true
    });
  }

  async openDatabase() {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open('EdTechDB', 1);

      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve(request.result);

      request.onupgradeneeded = (event) => {
        const db = event.target.result;
        db.createObjectStore('lessons', { keyPath: 'id' });
        db.createObjectStore('submissions', { keyPath: 'id' });
        db.createObjectStore('notes', { keyPath: 'id' });
      };
    });
  }

  async getOfflineLesson(lessonId) {
    const db = await this.openDatabase();
    return new Promise((resolve, reject) => {
      const request = db.transaction('lessons').objectStore('lessons').get(lessonId);
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }
}
```

**Conflict Resolution**:
```python
class OfflineSyncConflictResolver:
    """
    When user edits offline and syncs with server,
    conflicts may occur (server also changed).
    """

    def resolve_conflict(self, local_version, server_version):
        """
        Strategies:
        1. Last-write-wins (simple, can lose data)
        2. Client-wins (preserve user's work)
        3. Manual merge (ask user)
        4. Operational Transformation (complex, reliable)
        """

        # Example: Last-write-wins with timestamp
        if local_version['timestamp'] > server_version['timestamp']:
            return local_version
        else:
            return server_version

    def operational_transform_example(self):
        """
        Google Docs: Multiple users edit simultaneously offline.
        Each operation (insert, delete) transformed when merged.
        """
        # This is complex to implement correctly
        # Libraries: Yjs, Automerge
        pass

    def background_sync(self):
        """
        Queue changes offline, sync when connection restored.
        """
        return {
            'saved_offline': True,
            'will_sync_when_online': True,
            'user_notification': 'Saved offline - will sync when connected'
        }
```

**Push Notifications**:
```javascript
class MobileNotifications {
  /**
   * Send push notifications even when app is closed.
   * Web Push API (browsers), Native (iOS/Android).
   */

  async requestPermission() {
    const permission = await Notification.requestPermission();
    if (permission === 'granted') {
      this.registerServiceWorkerNotifications();
    }
  }

  registerServiceWorkerNotifications() {
    // Server can send notifications via Service Worker
    // Even if browser closed
  }

  example_notification() {
    return new Notification('Quiz Available!', {
      body: 'New quiz posted in Module 5',
      icon: '/icon-192x192.png',
      badge: '/badge-72x72.png',
      tag: 'quiz-notification',  // Deduplicates identical notifications
      requireInteraction: false   // Auto-dismiss after timeout
    });
  }
}
```

### Native Mobile Development

**React Native** (JavaScript -> iOS & Android):
```jsx
import React, { useState } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet
} from 'react-native';

const LessonScreen = () => {
  const [currentLesson, setCurrentLesson] = useState(0);

  const lessons = [
    { title: 'Intro to React', duration: 10 },
    { title: 'Components', duration: 15 },
    { title: 'State & Props', duration: 20 }
  ];

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>Module: JavaScript Basics</Text>

      {lessons.map((lesson, index) => (
        <TouchableOpacity
          key={index}
          style={[
            styles.lessonButton,
            currentLesson === index && styles.active
          ]}
          onPress={() => setCurrentLesson(index)}
        >
          <Text>{lesson.title}</Text>
          <Text style={styles.duration}>{lesson.duration} min</Text>
        </TouchableOpacity>
      ))}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16 },
  title: { fontSize: 24, fontWeight: 'bold', marginBottom: 16 },
  lessonButton: {
    padding: 16,
    marginBottom: 8,
    backgroundColor: '#f0f0f0',
    borderRadius: 8
  },
  active: { backgroundColor: '#007AFF' },
  duration: { fontSize: 12, color: '#666' }
});

export default LessonScreen;
```

**Flutter** (Dart -> iOS & Android):
```dart
import 'package:flutter/material.dart';

class LessonScreen extends StatefulWidget {
  @override
  _LessonScreenState createState() => _LessonScreenState();
}

class _LessonScreenState extends State<LessonScreen> {
  int currentLesson = 0;
  final lessons = [
    {'title': 'Intro to Dart', 'duration': 10},
    {'title': 'Widgets', 'duration': 15},
    {'title': 'State Management', 'duration': 20}
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('JavaScript Basics')),
      body: ListView.builder(
        itemCount: lessons.length,
        itemBuilder: (context, index) {
          final lesson = lessons[index];
          return Card(
            child: ListTile(
              title: Text(lesson['title']),
              subtitle: Text('${lesson['duration']} min'),
              onTap: () => setState(() => currentLesson = index),
              selected: currentLesson == index,
            ),
          );
        },
      ),
    );
  }
}
```

### Microlearning Design

**Bite-Sized Content** (3-7 minute modules):
```python
class MicrolearningDesign:
    """
    Short, focused lessons for mobile learning.
    - Fits in coffee break
    - One learning objective per module
    - Quick quiz to verify understanding
    """

    def module_structure(self):
        return {
            'hook': '30 seconds - Grab attention',
            'content': '3-5 minutes - Single concept',
            'example': '1 minute - Practical example',
            'quiz': '2 minutes - Check understanding',
            'next_steps': '30 seconds - What to do next'
        }

    def chunk_large_topics(self, large_topic):
        """
        Break "Photosynthesis" into:
        - Module 1: What is photosynthesis?
        - Module 2: Light reactions
        - Module 3: Calvin cycle
        - Module 4: Factors affecting rate
        """
        pass
```

**Spaced Repetition**:
```python
class SpacedRepetitionMobile:
    """
    Review concepts at optimal intervals to maximize retention.
    Algorithms: SM-2, FSRS
    """

    def calculate_next_review(self, days_passed, quality_of_response):
        """
        Schedule next review based on spacing algorithm.
        quality: 0-5 (0=forgot, 5=perfect)
        """
        # Interval grows exponentially if doing well
        # Resets to 1 day if forgotten
        pass

    def optimize_for_mobile(self):
        """
        Microlearning apps use spaced repetition:
        - Duolingo: Daily practice
        - Anki: Customizable intervals
        - Quizlet: Study sets with spacing
        """
        pass
```

### Technologies & Platforms

**Mobile Frameworks**:
- **React Native**: JavaScript code for iOS/Android
- **Flutter**: Dart, excellent performance, hot reload
- **Xamarin**: C# for cross-platform
- **Progressive Web Apps**: Web standards (no app store needed)

**Development Tools**:
- **Expo**: React Native easier onboarding
- **Android Studio**: Official Android IDE
- **Xcode**: Official iOS IDE
- **Firebase**: Backend (auth, database, hosting)

**Testing**:
- **Appium**: Automated testing mobile apps
- **Espresso**: Android native testing
- **XCTest**: iOS native testing
- **Device testing**: Test on real devices (simulators miss issues)

### Best Practices

1. **Mobile-first design**: Design for mobile, enhance for desktop
2. **Offline-first**: Assume connectivity is intermittent
3. **Small data transfers**: Users pay for mobile data
4. **Battery conservation**: Minimize CPU, avoid video autoplay
5. **Touch targets**: 44-48px minimum for easy tapping
6. **Low latency**: 200ms+ delays feel sluggish on mobile
7. **App permissions**: Request only needed permissions
8. **Testing on devices**: Simulators don't catch all issues

---

**Version**: 2.0
**Last Updated**: 2025-11-19
**Maintained by**: CLAUDE_SKILLS Education Technology Domain
