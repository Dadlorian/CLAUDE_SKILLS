# Virtual Classrooms & Synchronous Learning Skill

## Purpose

You are an expert in real-time video conferencing, collaborative learning platforms, WebRTC architecture, and synchronous learning pedagogy. You design virtual classroom systems that support rich real-time interaction, maintain pedagogical engagement, and scale to hundreds of concurrent participants. Your expertise spans video routing architectures, latency optimization, and instructor tools for effective synchronous teaching.

## Core Competencies

### WebRTC Architecture & Topologies

**Mesh Topology** (P2P, small groups <8 participants):
- Each participant sends/receives directly from all others
- Minimal latency (~50-100ms)
- Bandwidth intensive (scales as O(n²))
- Best for small study groups, breakout rooms
- Example implementation: Jitsi Meet (mesh option), peer.js

```javascript
// Simplified mesh WebRTC setup
const peerConnections = {};
const localStream = await navigator.mediaDevices.getUserMedia({
  video: true, audio: true
});

async function initiateP2PConnection(peerId) {
  const peerConnection = new RTCPeerConnection({
    iceServers: [{ urls: ['stun:stun.l.google.com:19302'] }]
  });

  // Add local tracks
  localStream.getTracks().forEach(track => {
    peerConnection.addTrack(track, localStream);
  });

  // Handle remote stream
  peerConnection.ontrack = event => {
    const remoteVideo = document.getElementById(`video-${peerId}`);
    remoteVideo.srcObject = event.streams[0];
  };

  // Create and send offer
  const offer = await peerConnection.createOffer();
  await peerConnection.setLocalDescription(offer);
  signaling.send({ type: 'offer', offer, to: peerId });

  peerConnections[peerId] = peerConnection;
}
```

**SFU Topology** (Selective Forwarding Unit, 8-50 participants):
- Central server receives one stream from each participant
- Server selectively forwards streams to others (not all-to-all)
- Moderate latency (~80-150ms)
- Bandwidth efficient for receiving (only need bandwidth for downloaded streams)
- Used by: Zoom (with some MCU), Google Meet, Jitsi with bridge
- Codec support: Handles simulcast (multiple bitrates)

**MCU Topology** (Multipoint Control Unit, 50+ participants):
- Server receives and **transcodes** all streams
- Server sends single mixed video/audio to participants
- Higher latency (~150-200ms, due to processing)
- Lower bandwidth for clients
- Expensive computationally (per-participant transcoding)
- Used when: Large lectures, standardized output quality needed

```python
# Conceptual SFU/MCU selection logic
def select_topology(num_participants, bandwidth_constraint, latency_requirement):
    if num_participants < 8 and latency_requirement < 100:
        return 'mesh'
    elif num_participants < 50 and bandwidth_constraint == 'high':
        return 'sfu'
    else:
        return 'mcu'

# SFU stream selection algorithm
class SFUStreamSelector:
    """Decide which remote streams to send to each participant."""

    def select_active_speakers(self, participants, num_to_forward=4):
        """
        Forward only the most active speakers to save bandwidth.
        Alternative: speaker-side selection (participant asks for specific streams).
        """
        # Sort by recent speaking activity (audio level)
        active = sorted(
            participants,
            key=lambda p: p.audio_activity_score,
            reverse=True
        )
        return active[:num_to_forward]

    def select_by_attention(self, participants, focus_participant):
        """
        Forward streams participant is looking at (gaze detection or manual selection).
        """
        # Participant can see: their own video, speaker, people they named
        streams_to_send = [
            focus_participant,  # Always see yourself
            self.get_current_speaker(),
            *focus_participant.selected_peers
        ]
        return streams_to_send
```

**Hybrid Topology** (Modern approach):
- MCU for main lecture video (mixed feed)
- SFU for participant highlights and Q&A
- Allows large lectures + rich interaction
- Example: Instructure's Canvas Conferences with Jitsi

### Virtual Classroom Features & Interactions

**Audio/Video Management**:
- Adaptive bitrate (simulcast): Send multiple quality versions, client chooses
- Echo cancellation: Remove participant's own voice from audio
- Noise suppression: Filter background noise (especially important for education)
- Voice activity detection: Mute participants automatically when not speaking
- Bandwidth throttling: Graceful degradation when network is poor

```python
class AdaptiveBitrateManager:
    """Manage simulcast streams at different quality levels."""

    ENCODING_PROFILES = [
        {'rid': 'h', 'maxBitrate': 2500000, 'scaleResolutionDownBy': 1},    # High
        {'rid': 'm', 'maxBitrate': 1000000, 'scaleResolutionDownBy': 2},    # Medium
        {'rid': 'l', 'maxBitrate': 300000, 'scaleResolutionDownBy': 4}      # Low
    ]

    def apply_simulcast(self, peer_connection, local_stream):
        """Enable simulcast encoding."""
        transceiver = peer_connection.addTransceiver(local_stream.getVideoTracks()[0], {
            'sendEncodings': self.ENCODING_PROFILES
        })
        return transceiver

    def measure_bandwidth(self):
        """Estimate available bandwidth using REMB (Receiver Estimated Maximum Bitrate)."""
        # Measured from getStats() API
        return {
            'estimated_bitrate': 2500000,  # bits/second
            'available_bitrate': 2000000,
            'used_bitrate': 1800000
        }
```

**Collaborative Tools**:
- **Screen/Application Sharing**:
  - Canvas/Whiteboard: Collaborative drawing (real-time sync)
  - Document Sharing: View/edit together (Google Docs integration)
  - Screen Annotation: Highlight important areas during presentation

- **Hand Raising & Q&A**:
  - Students raise hand to speak (respects turn-taking)
  - Queue-based system (instructor controls order)
  - Chat moderation (prevent off-topic chatter)
  - Anonymous questions (reduce anxiety)

```javascript
class VirtualClassroomInteractions {
  constructor(roomId) {
    this.handRaiseQueue = [];
    this.chatMessages = [];
    this.polls = {};
  }

  raiseHand(studentId) {
    // Prevent duplicate entries
    if (!this.handRaiseQueue.includes(studentId)) {
      this.handRaiseQueue.push(studentId);
      this.broadcastQueueUpdate();
    }
  }

  lowerHand(studentId) {
    this.handRaiseQueue = this.handRaiseQueue.filter(id => id !== studentId);
    this.broadcastQueueUpdate();
  }

  startPoll(question, options) {
    const pollId = Date.now();
    this.polls[pollId] = {
      question,
      options,
      responses: new Map(),
      active: true
    };
    return pollId;
  }

  submitPollResponse(studentId, pollId, optionIndex) {
    this.polls[pollId].responses.set(studentId, optionIndex);
    // Anonymize if needed (don't broadcast individual votes)
  }

  endPoll(pollId) {
    const poll = this.polls[pollId];
    poll.active = false;
    // Show aggregate results (histogram)
    const results = Array(poll.options.length).fill(0);
    poll.responses.forEach(optionIndex => results[optionIndex]++);
    return results;
  }

  sendChatMessage(senderId, text, isPrivate = false, privateReceiverId = null) {
    const message = {
      senderId,
      text,
      timestamp: Date.now(),
      isPrivate,
      privateReceiverId
    };
    this.chatMessages.push(message);
    this.broadcastMessage(message);
  }
}
```

**Breakout Rooms**:
```python
class BreakoutRoomManager:
    """Manage student breakout rooms for group work."""

    def create_breakout_rooms(self, students, num_rooms):
        """Automatically distribute students into breakout rooms."""
        import random
        random.shuffle(students)
        room_size = len(students) // num_rooms
        rooms = {}

        for i in range(num_rooms):
            start = i * room_size
            end = (i + 1) * room_size if i < num_rooms - 1 else len(students)
            rooms[f'room_{i}'] = students[start:end]

        return rooms

    def monitor_breakout_rooms(self, instructor_id):
        """Allow instructor to monitor/visit rooms."""
        # Instructor can:
        # - See list of rooms and participants
        # - Jump into rooms to check progress
        # - Send time warnings (2 min remaining)
        # - End early if groups finish
        pass

    def return_to_main_room(self, students):
        """Bring all students back to main classroom."""
        # Rejoin peer connections to main SFU/MCU
        for student in students:
            self.rejoin_main_room(student)
```

### Recording & Accessibility

**Recording Architecture**:
- **Server-side recording**: Record SFU/MCU stream (CPU intensive but high quality)
- **Client-side recording**: Each participant records locally (less load)
- **Chunked recording**: Record to multiple files (easier to process/store)
- **Post-processing**: Transcode to multiple formats, add captions

```python
class VirtualClassroomRecorder:
    """Record and process virtual classroom sessions."""

    def record_session(self, room_id, participants):
        """
        Record video/audio using FFmpeg with SFU stream.
        Process: SFU -> FFmpeg -> MP4 -> Transcode + Captions
        """
        import subprocess
        import json

        # FFmpeg command to mux video and audio
        cmd = [
            'ffmpeg',
            '-i', f'rtmp://sfu-server/streams/{room_id}_video',  # Video from SFU
            '-i', f'rtmp://sfu-server/streams/{room_id}_audio',  # Audio from SFU
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '23',
            '-c:a', 'aac',
            f'/recordings/{room_id}_recording.mp4'
        ]

        subprocess.run(cmd)

    def add_captions(self, video_path):
        """Generate captions using speech-to-text (AWS Transcribe, Google Cloud)."""
        from google.cloud import speech_v1p1beta1
        from google.cloud.speech_v1p1beta1 import enums

        client = speech_v1p1beta1.SpeechClient()

        with open(video_path, 'rb') as audio_file:
            content = audio_file.read()

        audio = speech_v1p1beta1.RecognitionAudio(content=content)
        config = speech_v1p1beta1.RecognitionConfig(
            encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code='en-US',
            enable_automatic_punctuation=True
        )

        response = client.recognize(config, audio)

        # Generate WebVTT subtitle file
        captions = []
        for result in response.results:
            for alternative in result.alternatives:
                captions.append({
                    'text': alternative.transcript,
                    'confidence': alternative.confidence
                })

        return self.generate_vtt(captions)

    def transcode_for_accessibility(self, video_path):
        """Create multiple versions for different devices/connections."""
        profiles = [
            {'name': '720p', 'bitrate': '2500k', 'scale': '1280:720'},
            {'name': '480p', 'bitrate': '1000k', 'scale': '854:480'},
            {'name': '360p', 'bitrate': '500k', 'scale': '640:360'}
        ]

        for profile in profiles:
            cmd = [
                'ffmpeg', '-i', video_path,
                '-b:v', profile['bitrate'],
                '-vf', f"scale={profile['scale']}",
                f"/processed/{video_path}_{profile['name']}.mp4"
            ]
            subprocess.run(cmd)
```

### Performance Optimization & Scalability

**Latency Optimization**:
- **RTCDataChannel**: For non-media data (hand raises, polls) - lower latency than video
- **Packet Loss Concealment (PLC)**: Interpolate lost audio frames
- **Forward Error Correction (FEC)**: Send redundant packets
- **Adaptive video refresh**: Reduce frame rate if network is congested
- Target: <150ms latency for educational use

**Bandwidth Management**:
- **Temporal Scalability**: Send key frames less frequently under poor network
- **Spatial Scalability**: Reduce resolution under bandwidth constraints
- **TWCC (Transport-Wide Congestion Control)**: Client reports network status to server
- **Jitter Buffer**: Smooth out packet arrival variance

**Scaling to Large Lectures**:
1. **Staged rollout**: Gradually increase participant count
2. **Geographic distribution**: Deploy SFU nodes in multiple regions
3. **Load balancing**: Distribute participants across multiple SFU instances
4. **Monitoring**: Track CPU, memory, network per SFU instance
5. **Auto-scaling**: Spin up additional instances under high load

### Synchronous Learning Pedagogy

**Engagement Strategies**:
- **Regular interaction**: Polls, hand raises, chat every 5-10 minutes
- **Breakout rooms**: Small group discussions (proven effective for retention)
- **Shared documents**: Collaborative note-taking
- **Gamification**: Leaderboards for participation, badges for engagement
- **Recording + availability**: Record for those who can't attend live

**Accessibility Considerations**:
- Captions for deaf/hard of hearing students
- Audio descriptions for visual content
- Large fonts for low-vision students
- Keyboard navigation support
- High color contrast (WCAG AA minimum)

### Technologies & Platforms

**Open Source**:
- **Jitsi Meet**: Full-featured, self-hostable, uses SFU
- **BigBlueButton**: Education-focused, built on Kurento SFU
- **Mattermost**: Team communication with video support

**Commercial SaaS**:
- **Zoom**: Market leader, uses mixture of P2P/SFU/MCU
- **Microsoft Teams**: Integrated with Office 365
- **Google Meet**: Simple, integrated with Google Classroom
- **Cisco Webex**: Enterprise-grade, reliable

**Infrastructure**:
- **WebRTC Libraries**: libwebrtc (Chromium), Pion (Go), mediasoup (Node.js)
- **SFU Implementations**: mediasoup, Janus, SRS, Kurento
- **Signaling**: WebSocket, Socket.io, MQTT
- **Video Processing**: FFmpeg, GStreamer
- **STN Servers**: STUN (session traversal), TURN (relay) for NAT traversal

### Best Practices

1. **Test before class**: Verify audio, video, lighting, background noise
2. **Clear communication**: Explain hand-raise protocol, chat expectations
3. **Breakout rooms for engagement**: Even for larger classes
4. **Record lectures**: Provide for those who can't attend live
5. **Minimize latency**: Use local SFU when possible
6. **Accessibility first**: Captions and alt text essential
7. **Technical support**: Have backup plan for connection failures

### Troubleshooting & Production Issues

**Common WebRTC Issues**:
```python
class WebRTCTroubleshooting:
    """Diagnose and fix common WebRTC problems."""

    def diagnose_connection_failure(self, peer_connection):
        """
        Common causes:
        1. Firewall blocking UDP (use TURN)
        2. Symmetric NAT (requires TURN relay)
        3. ICE candidates not exchanged properly
        4. Certificate errors (HTTPS required)
        """
        diagnostics = {
            'ice_connection_state': peer_connection.iceConnectionState,
            'ice_gathering_state': peer_connection.iceGatheringState,
            'connection_state': peer_connection.connectionState,
            'signaling_state': peer_connection.signalingState
        }

        if diagnostics['ice_connection_state'] == 'failed':
            return {
                'issue': 'ICE connection failed',
                'solution': 'Enable TURN server, check firewall settings',
                'turn_config': {
                    'urls': 'turn:turn.example.com:3478',
                    'username': 'user',
                    'credential': 'password'
                }
            }

        return diagnostics

    def fix_audio_echo(self):
        """
        Audio echo issues and solutions.
        """
        return {
            'constraints': {
                'audio': {
                    'echoCancellation': True,
                    'noiseSuppression': True,
                    'autoGainControl': True
                }
            },
            'tips': [
                'Use headphones (prevents speaker -> mic feedback)',
                'Enable browser echo cancellation',
                'Mute when not speaking',
                'Test with getUserMedia constraints'
            ]
        }

    def optimize_poor_video_quality(self):
        """
        Video quality troubleshooting.
        """
        return {
            'check_bandwidth': 'Run network speed test (need 1-5 Mbps per stream)',
            'reduce_resolution': 'Lower video resolution (720p -> 480p)',
            'reduce_framerate': 'Lower framerate (30fps -> 15fps)',
            'disable_video': 'Audio-only mode for very poor connections',
            'use_simulcast': 'Send multiple quality levels, receiver chooses best'
        }

    def handle_high_cpu_usage(self):
        """
        CPU usage optimization for video processing.
        """
        return {
            'hardware_acceleration': 'Enable GPU video encoding/decoding',
            'codec_selection': 'Use VP9 or H.264 (hardware accelerated)',
            'resolution_limits': 'Cap at 720p for standard meetings',
            'background_blur_off': 'Disable CPU-intensive background blur',
            'participant_limit': 'Reduce visible participants (show 4-6 max)'
        }
```

**Monitoring & Alerting**:
```javascript
class VirtualClassroomMonitoring {
  /**
   * Track quality metrics in production.
   * Alert instructors when students have connection issues.
   */

  constructor() {
    this.qualityThresholds = {
      minBitrate: 300000,  // 300 kbps
      maxPacketLoss: 5,    // 5%
      maxJitter: 30,       // 30ms
      maxRTT: 300          // 300ms round-trip time
    };
  }

  async monitorConnectionQuality(peerConnection, studentId) {
    const stats = await peerConnection.getStats();

    const metrics = this.parseWebRTCStats(stats);

    // Check for quality issues
    if (metrics.packetLossRate > this.qualityThresholds.maxPacketLoss) {
      this.alertInstructor({
        studentId,
        issue: 'high_packet_loss',
        value: metrics.packetLossRate,
        recommendation: 'Student may have poor connection - consider audio-only mode'
      });
    }

    if (metrics.currentBitrate < this.qualityThresholds.minBitrate) {
      this.alertInstructor({
        studentId,
        issue: 'low_bitrate',
        value: metrics.currentBitrate,
        recommendation: 'Bandwidth constrained - video may freeze'
      });
    }

    // Log metrics to analytics
    this.logMetrics({
      studentId,
      timestamp: Date.now(),
      ...metrics
    });

    return metrics;
  }

  parseWebRTCStats(stats) {
    let inboundRTP = null;
    let outboundRTP = null;

    stats.forEach(report => {
      if (report.type === 'inbound-rtp' && report.mediaType === 'video') {
        inboundRTP = report;
      }
      if (report.type === 'outbound-rtp' && report.mediaType === 'video') {
        outboundRTP = report;
      }
    });

    return {
      packetsReceived: inboundRTP?.packetsReceived || 0,
      packetsLost: inboundRTP?.packetsLost || 0,
      packetLossRate: (inboundRTP?.packetsLost / inboundRTP?.packetsReceived) * 100 || 0,
      jitter: inboundRTP?.jitter || 0,
      currentBitrate: outboundRTP?.bitrate || 0,
      frameRate: inboundRTP?.framesPerSecond || 0
    };
  }

  alertInstructor(alert) {
    // Send real-time alert to instructor dashboard
    console.warn('Connection quality alert:', alert);
    // Could send via WebSocket, notification API, etc.
  }
}
```

**SFU Server Configuration (Janus)**:
```bash
# /etc/janus/janus.jcfg - Production Janus config

general: {
    configs_folder = "/etc/janus"
    plugins_folder = "/usr/lib/janus/plugins"
    transports_folder = "/usr/lib/janus/transports"
    events_folder = "/usr/lib/janus/events"

    # Performance tuning
    session_timeout = 0
    rtp_port_range = "20000-40000"

    # Enable IPv4 only (or add IPv6 if needed)
    ipv6 = false

    # Enable debug level logging
    debug_level = 4
}

nat: {
    # STUN server for NAT traversal
    stun_server = "stun.l.google.com"
    stun_port = 19302

    # TURN server for relaying (when peer-to-peer fails)
    turn_server = "turn.example.com"
    turn_port = 3478
    turn_type = "udp"
    turn_user = "username"
    turn_pwd = "password"

    # Public IP for server reflexive candidates
    nat_1_1_mapping = "YOUR_PUBLIC_IP"
}

# VideoRoom plugin for SFU mode
plugins: {
    videoroom: {
        bitrate = 2048000  # Max bitrate per publisher (2 Mbps)
        record = true      # Enable recording
        rec_dir = "/var/janus/recordings"
    }
}
```

---

**Version**: 2.0
**Last Updated**: 2025-11-19
**Maintained by**: CLAUDE_SKILLS Education Technology Domain
