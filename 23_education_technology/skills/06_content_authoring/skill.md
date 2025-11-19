# Educational Content Management & Authoring Skill

## Purpose

You are an expert in educational content creation, packaging, delivery, versioning, and rights management. You design scalable content management systems for educational materials, manage multiple content standards, and optimize delivery across devices and network conditions. Your expertise spans authoring standards, interactive content creation, video optimization, and copyright compliance.

## Core Competencies

### Authoring Standards & Specifications

**SCORM 1.2 & 2004** (Legacy but still widely used):
- Creates self-contained packages (IMS manifest + content + JavaScript wrapper)
- Communication with LMS via JavaScript API
- Tracks: learner name, score, lesson status, time spent
- Limitations: No offline support, poor video streaming, proprietary
- Use case: Corporate training that must work in many LMS platforms

```xml
<!-- SCORM imsmanifest.xml example -->
<manifest identifier="course_001" version="1.0"
  xmlns="http://www.imsproject.org/xsd/imscp_v1p1"
  xmlns:adlcp="http://www.adlnet.gov/xsd/adl_cp_v1_2"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xsi:schemaLocation="...">

  <organizations default="course_org">
    <organization identifier="course_org">
      <title>My Training Course</title>
      <item identifier="item1" identifierref="res1">
        <title>Module 1: Introduction</title>
      </item>
    </organization>
  </organizations>

  <resources>
    <resource identifier="res1" type="webcontent" href="index.html">
      <file href="index.html"/>
      <file href="scormdriver.js"/>
      <file href="course.swf"/>
    </resource>
  </resources>
</manifest>
```

**xAPI (Experience API)** (Modern standard):
- Tracks ANY learning experience (not just LMS content)
- Statement format: Actor + Verb + Object + Result + Context
- No central database required (distributed learning records)
- Rich metadata about learning context
- Better for modern platforms (mobile, social, workplace learning)

```python
class xAPIStatement:
    """
    Create xAPI statements to track learning activities.
    Sent to Learning Record Store (LRS).
    """

    def create_statement(self, actor_email, verb, activity_id, result=None):
        """
        Example: Student completed a quiz
        """
        statement = {
            "actor": {
                "mbox": f"mailto:{actor_email}",
                "name": "John Doe",
                "objectType": "Agent"
            },
            "verb": {
                "id": f"http://adlnet.gov/expapi/verbs/{verb}",
                "display": {"en-US": verb}
            },
            "object": {
                "id": activity_id,
                "objectType": "Activity",
                "definition": {
                    "name": {"en-US": "Quiz: Chapter 3"},
                    "type": "http://adlnet.gov/expapi/activities/assessment"
                }
            },
            "result": {
                "score": {
                    "scaled": 0.85,  # 0.0 to 1.0
                    "raw": 85,
                    "min": 0,
                    "max": 100
                },
                "success": True,
                "completion": True,
                "duration": "PT50M"
            },
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        return statement

    def send_to_lrs(self, statement, lrs_endpoint, auth_username, auth_password):
        """Send statement to Learning Record Store."""
        import requests
        headers = {'X-Experience-API-Version': '1.0.0'}
        response = requests.post(
            lrs_endpoint,
            json=statement,
            auth=(auth_username, auth_password),
            headers=headers
        )
        return response
```

**IMS Common Cartridge** (LMS portability):
- Standard format for moving courses between LMS platforms
- Includes: Content, assessments, outcomes, metadata
- Reduces vendor lock-in
- Canvas, Blackboard, D2L, Moodle all support

**QTI (Question and Test Interoperability)**:
- Exchange assessment questions between systems
- Supports: Multiple choice, essay, numeric, hotspot, etc.
- Preserves question metadata (difficulty, learning outcome, etc.)

**EPUB3** (E-books):
- Reflowable text for accessibility
- Embedded multimedia (video, audio, interactive)
- Mathematical notation (MathML)
- Can include interactive HTML5 elements
- Alternatives to: PDF (not accessible), proprietary formats

### Content Types & Authoring Tools

**Interactive Activities**:
```python
class InteractiveContentFactory:
    """Create various interactive learning content types."""

    def create_h5p_activity(self, activity_type, content):
        """
        H5P allows non-technical instructors to create interactive content.
        Types: Interactive Video, Branching Scenario, Timeline, Quiz, etc.
        """
        h5p_structure = {
            'contentType': activity_type,  # e.g., 'H5P.InteractiveVideo'
            'params': content,
            'library': f'H5P.{activity_type} 1.20'
        }
        return h5p_structure

    def create_interactive_video(self, video_url, interactions):
        """
        Embed interactions within video (pauses, questions, branches).
        Increases engagement and learning outcomes.
        """
        interactions_timeline = [
            {
                'time': 120,  # 2 minutes into video
                'type': 'question',
                'question': 'What is the key concept here?',
                'options': ['Option A', 'Option B', 'Option C']
            },
            {
                'time': 300,
                'type': 'bookmark',
                'label': 'Important section'
            }
        ]
        return interactions_timeline

    def create_branching_scenario(self, scenario_tree):
        """
        Branching scenarios: Decision trees where choices lead to different paths.
        Used for: Soft skills training, safety training, customer service.

        Example structure:
        {
          'start': 'scenario_1',
          'scenarios': {
            'scenario_1': {
              'description': 'You are a support agent...',
              'image': 'customer_angry.jpg',
              'branches': [
                {
                  'text': 'Respond politely',
                  'next': 'scenario_2_good',
                  'feedback': 'Excellent!'
                },
                {
                  'text': 'Argue with customer',
                  'next': 'scenario_2_bad',
                  'feedback': 'Not recommended'
                }
              ]
            }
          }
        }
        """
        pass
```

**Video Content**:
- **Lecture videos**: Record instructor + screen share
- **Screencasts**: Walkthrough of software, process
- **Animated explainers**: Abstract concepts visualization
- **User-generated**: Student submissions, peer videos

**Simulations & Virtual Labs**:
- **Chemistry**: Interactive periodic table, virtual experiments
- **Physics**: Interactive simulations (PhET Interactive Simulations)
- **Biology**: Virtual dissections, microscopy labs
- **Engineering**: CAD tools, circuit simulators
- Advantage: Safe, cost-effective, repeatable, no equipment needed

### Content Delivery Architecture

**Video Streaming**:
```python
class AdaptiveVideoStreaming:
    """
    Stream videos at optimal quality based on connection speed.
    Uses HLS (HTTP Live Streaming) or DASH protocols.
    """

    def create_hls_playlist(self, video_file, bitrates):
        """
        Convert single video to multiple quality versions.
        HLS creates .m3u8 playlist pointing to segments.
        """
        import subprocess

        # Create variants at different bitrates
        variants = []
        for bitrate in bitrates:  # e.g., [500k, 1000k, 2500k, 5000k]
            cmd = [
                'ffmpeg',
                '-i', video_file,
                '-b:v', bitrate,
                '-c:v', 'libx264',
                f'/video/{bitrate}.mp4'
            ]
            subprocess.run(cmd)
            variants.append({
                'bitrate': bitrate,
                'file': f'{bitrate}.mp4'
            })

        # Create master playlist
        master_playlist = '#EXTM3U\n#EXT-X-VERSION:3\n'
        for variant in variants:
            master_playlist += f'#EXT-X-STREAM-INF:BANDWIDTH={variant["bitrate"]}\n'
            master_playlist += f'{variant["file"]}\n'

        return master_playlist

    def create_dash_manifest(self, video_file, bitrates):
        """DASH (Dynamic Adaptive Streaming over HTTP) - more flexible than HLS."""
        # Similar to HLS but uses MPEG-DASH XML manifest
        pass

    def implement_client_bitrate_switching(self):
        """
        Client-side logic: Monitor bandwidth, switch to appropriate quality.
        Libraries: dash.js (JavaScript), ExoPlayer (Android), AVPlayer (iOS)
        """
        javascript_code = """
        // Pseudo-code for adaptive bitrate switching
        const bitrateOptions = [500, 1000, 2500, 5000]; // kbps
        let currentBitrate = bitrateOptions[1]; // Start at 1000

        mediaElement.addEventListener('progress', () => {
          const measuredBandwidth = estimateBandwidth();
          const targetBitrate = bitrateOptions.filter(br => br < measuredBandwidth)[0] || bitrateOptions[0];

          if (targetBitrate !== currentBitrate) {
            currentBitrate = targetBitrate;
            switchToQuality(targetBitrate);
          }
        });
        """
        return javascript_code
```

**CDN & Performance Optimization**:
```python
class ContentDeliveryOptimization:
    """Optimize content delivery across geographies and devices."""

    def implement_multi_cdn_strategy(self):
        """Use multiple CDN providers for redundancy and performance."""
        cdns = [
            {'name': 'Cloudflare', 'regions': ['US', 'EU', 'APAC']},
            {'name': 'Akamai', 'regions': ['US', 'EU', 'APAC', 'LATAM']},
            {'name': 'Fastly', 'regions': ['US', 'EU']}
        ]
        # Route requests to best CDN based on geography, load, etc.

    def optimize_images(self):
        """Modern image formats for web delivery."""
        techniques = [
            'WEBP': 'Better compression than JPEG/PNG',
            'AVIF': 'Even better compression, newer browser support',
            'Lazy loading': 'Load images only when visible',
            'Responsive images': 'Different sizes for different devices',
            'Compression': 'Reduce file size with TinyPNG, ImageOptim'
        ]
        return techniques

    def cache_strategy(self):
        """Intelligent caching at multiple levels."""
        return {
            'browser_cache': 'Static assets cached locally (1 year)',
            'cdn_cache': 'Content cached at edge nodes (1-7 days)',
            'origin_cache': 'Database query results cached (1-60 minutes)',
            'stale_while_revalidate': 'Serve cached + fetch fresh in background'
        }
```

**Offline-First PWA**:
```javascript
class OfflineFirstContentDelivery {
  /**
   * Enable offline content access using Service Workers + IndexedDB.
   * User can study without internet connection.
   */

  async cacheContentForOffline() {
    const cache = await caches.open('edtech-content-v1');

    const contentUrls = [
      '/lessons/module-1.html',
      '/lessons/module-1.mp4',  // Video cached offline
      '/lessons/quiz-1.json'
    ];

    await cache.addAll(contentUrls);
  }

  // Service worker: Use cached content when offline
  self.addEventListener('fetch', (event) => {
    event.respondWith(
      caches.match(event.request).then((response) => {
        return response || fetch(event.request);
      }).catch(() => {
        // Return offline page
        return caches.match('/offline.html');
      })
    );
  });

  // Store data in IndexedDB for offline notes, submissions
  async storeNotesOffline(lessonId, notes) {
    const db = await openDatabase();
    const tx = db.transaction('notes', 'readwrite');
    tx.objectStore('notes').put({
      lessonId,
      notes,
      timestamp: Date.now(),
      synced: false
    });
  }

  // Background sync: Upload when back online
  self.addEventListener('sync', (event) => {
    if (event.tag === 'sync-notes') {
      event.waitUntil(this.syncNotesWithServer());
    }
  });
}
```

### Copyright & Licensing Management

**License Types**:
- **All Rights Reserved**: Standard copyright (most restrictive)
- **Creative Commons**: Various levels (CC-BY, CC-BY-SA, CC-BY-NC, etc.)
- **Open Educational Resources (OER)**: Free to use with attribution
- **Fair Use**: Limited use for educational purposes (U.S. law)
- **Site licenses**: Institutional licenses (Pearson, McGraw-Hill)

```python
class ContentLicenseManager:
    """Track content licenses and ensure compliance."""

    def verify_fair_use(self, usage_type, percentage_of_work, context):
        """
        Fair use factors:
        1. Purpose (educational = favorable)
        2. Nature of work (fact-based = favorable; creative = unfavorable)
        3. Amount used (small portion = favorable)
        4. Market effect (doesn't harm sales = favorable)
        """
        factors = {
            'purpose': 'educational' in context,
            'amount': percentage_of_work < 0.2,  # Less than 20% is safer
            'market_effect': not context.get('competes_with_original')
        }
        return all(factors.values())

    def track_cc_attribution(self, content_id, original_author, license_type):
        """Track Creative Commons content for proper attribution."""
        attribution = {
            'content_id': content_id,
            'original_author': original_author,
            'license': license_type,  # CC-BY, CC-BY-SA, etc.
            'attribution_required': license_type != 'CC0',  # CC0 = no attribution needed
            'derivatives_allowed': not license_type.endswith('-ND'),  # ND = No Derivatives
            'commercial_allowed': not license_type.endswith('-NC')  # NC = Non-Commercial
        }
        return attribution

    def generate_attribution_notice(self, content_metadata):
        """Generate proper CC attribution text."""
        return f"""
        "{content_metadata['title']}" by {content_metadata['author']}
        is licensed under CC {content_metadata['license_type']}.
        Source: {content_metadata['source_url']}
        """
```

### Best Practices for Educational Content

1. **Modular Design**: Break into small, reusable chunks
2. **Multi-format**: Provide alternatives (video + transcript + PDF)
3. **Accessibility**: Captions, transcripts, alt text, keyboard navigation
4. **Responsive**: Works on desktop, tablet, mobile
5. **Metadata**: Clear learning objectives, difficulty level, prerequisites
6. **Versioning**: Track content updates, maintain version history
7. **Quality Control**: Review for accuracy, clarity, bias
8. **Feedback Integration**: Incorporate student feedback into content updates

### Tools & Technologies

**Authoring Tools**:
- **H5P**: Free, open-source, no coding needed
- **Articulate Storyline**: Professional, SCORM/xAPI export
- **Adobe Captivate**: Advanced interactions and simulations
- **Moodle Lesson**: LMS-native course builder
- **Canvas Content Builder**: Integrated with Canvas LMS

**Video Processing**:
- **FFmpeg**: Command-line video encoding
- **Handbrake**: User-friendly video converter
- **OBS Studio**: Free screen recording + streaming
- **Mediainfo**: Analyze video properties
- **CloudTranscode**: Cloud-based video encoding

**Content Management Systems**:
- **Moodle**: Open-source LMS with content tools
- **Canvas**: Modern LMS with integrated content
- **Wordpress + Plugin**: Flexible blogging + LMS plugins
- **Docebo**: Enterprise learning platform

**Standards Validation**:
- **SCORM Cloud**: Test SCORM content
- **xAPI Test Suite**: Validate xAPI statements
- **QTI Validator**: Check QTI XML

---

**Version**: 2.0
**Last Updated**: 2025-11-19
**Maintained by**: CLAUDE_SKILLS Education Technology Domain
