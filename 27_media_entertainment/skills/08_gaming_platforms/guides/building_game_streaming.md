# Building a Game Streaming Platform

Complete guide to building cloud gaming and game streaming services like Twitch, Steam, or GeForce NOW, covering low-latency streaming, input handling, matchmaking, and social features.

## Architecture Overview

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│  Game Server    │─────>│  Video Encoder   │─────>│   WebRTC/RTMP   │
│  (Rendering)    │      │  (H.264/H.265)   │      │   Streaming     │
└─────────────────┘      └──────────────────┘      └─────────────────┘
        ▲                                                     │
        │                                                     ▼
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│  Input Handler  │<─────│   Client App     │<─────│   CDN/Edge      │
│  (Gamepad/KB/M) │      │   (Web/Native)   │      │   Distribution  │
└─────────────────┘      └──────────────────┘      └─────────────────┘
```

## Phase 1: Low-Latency Video Streaming

### 1.1 WebRTC Implementation

```typescript
// webrtc_streamer.ts
class GameStreamer {
    private peerConnection: RTCPeerConnection;
    private dataChannel: RTCDataChannel;
    private stream: MediaStream | null = null;

    constructor(private config: StreamConfig) {
        this.peerConnection = new RTCPeerConnection({
            iceServers: [
                { urls: 'stun:stun.l.google.com:19302' },
                {
                    urls: 'turn:turn.example.com:3478',
                    username: 'user',
                    credential: 'pass'
                }
            ]
        });

        this.setupPeerConnection();
    }

    private setupPeerConnection() {
        // Handle incoming streams
        this.peerConnection.ontrack = (event) => {
            this.stream = event.streams[0];
            this.emit('stream-ready', this.stream);
        };

        // Create data channel for input
        this.dataChannel = this.peerConnection.createDataChannel('input', {
            ordered: false,  // Don't wait for packet order
            maxRetransmits: 0  // Don't retransmit - low latency priority
        });

        this.dataChannel.onopen = () => {
            console.log('Data channel opened');
            this.setupInputHandlers();
        };

        // ICE candidate handling
        this.peerConnection.onicecandidate = (event) => {
            if (event.candidate) {
                this.sendToServer({
                    type: 'ice-candidate',
                    candidate: event.candidate
                });
            }
        };

        // Monitor connection state
        this.peerConnection.onconnectionstatechange = () => {
            console.log('Connection state:', this.peerConnection.connectionState);
            this.emit('connection-state', this.peerConnection.connectionState);
        };
    }

    async startStreaming(sessionId: string) {
        // Get offer from server
        const response = await fetch(`/api/stream/start/${sessionId}`, {
            method: 'POST'
        });

        const { offer } = await response.json();

        // Set remote description
        await this.peerConnection.setRemoteDescription(
            new RTCSessionDescription(offer)
        );

        // Create answer
        const answer = await this.peerConnection.createAnswer();
        await this.peerConnection.setLocalDescription(answer);

        // Send answer to server
        await fetch(`/api/stream/answer/${sessionId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ answer })
        });
    }

    private setupInputHandlers() {
        // Keyboard input
        window.addEventListener('keydown', (e) => {
            this.sendInput({
                type: 'keyboard',
                action: 'down',
                key: e.key,
                code: e.code,
                timestamp: Date.now()
            });
        });

        window.addEventListener('keyup', (e) => {
            this.sendInput({
                type: 'keyboard',
                action: 'up',
                key: e.key,
                code: e.code,
                timestamp: Date.now()
            });
        });

        // Mouse input
        window.addEventListener('mousemove', (e) => {
            this.sendInput({
                type: 'mouse',
                action: 'move',
                x: e.clientX,
                y: e.clientY,
                timestamp: Date.now()
            });
        });

        window.addEventListener('mousedown', (e) => {
            this.sendInput({
                type: 'mouse',
                action: 'down',
                button: e.button,
                x: e.clientX,
                y: e.clientY,
                timestamp: Date.now()
            });
        });

        // Gamepad input
        this.startGamepadPolling();
    }

    private startGamepadPolling() {
        const pollGamepads = () => {
            const gamepads = navigator.getGamepads();

            for (const gamepad of gamepads) {
                if (gamepad) {
                    this.sendInput({
                        type: 'gamepad',
                        index: gamepad.index,
                        buttons: gamepad.buttons.map(b => ({
                            pressed: b.pressed,
                            value: b.value
                        })),
                        axes: Array.from(gamepad.axes),
                        timestamp: Date.now()
                    });
                }
            }

            requestAnimationFrame(pollGamepads);
        };

        requestAnimationFrame(pollGamepads);
    }

    private sendInput(input: any) {
        if (this.dataChannel && this.dataChannel.readyState === 'open') {
            // Serialize input to binary for efficiency
            const buffer = this.serializeInput(input);
            this.dataChannel.send(buffer);
        }
    }

    private serializeInput(input: any): ArrayBuffer {
        // Simple JSON serialization (in production use binary protocol)
        const json = JSON.stringify(input);
        const encoder = new TextEncoder();
        return encoder.encode(json).buffer;
    }

    getLatencyStats() {
        return this.peerConnection.getStats().then(stats => {
            let rtt = 0;
            let jitter = 0;
            let packetsLost = 0;

            stats.forEach(report => {
                if (report.type === 'candidate-pair' && report.state === 'succeeded') {
                    rtt = report.currentRoundTripTime * 1000; // Convert to ms
                }
                if (report.type === 'inbound-rtp' && report.mediaType === 'video') {
                    jitter = report.jitter;
                    packetsLost = report.packetsLost;
                }
            });

            return { rtt, jitter, packetsLost };
        });
    }

    private emit(event: string, data: any) {
        // Event emission logic
    }

    private sendToServer(data: any) {
        // WebSocket communication with signaling server
    }
}
```

### 1.2 Server-Side Game Rendering

```python
# game_server.py
import asyncio
import cv2
import numpy as np
from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack
from av import VideoFrame

class GameRenderer(VideoStreamTrack):
    """
    Captures game video and streams via WebRTC
    """
    kind = "video"

    def __init__(self, game_process):
        super().__init__()
        self.game_process = game_process
        self.frame_rate = 60
        self.width = 1920
        self.height = 1080

    async def recv(self):
        """Generate video frames from game"""

        pts, time_base = await self.next_timestamp()

        # Capture frame from game process (via screen capture or GPU sharing)
        frame = self.capture_game_frame()

        # Convert to VideoFrame
        video_frame = VideoFrame.from_ndarray(frame, format="bgr24")
        video_frame.pts = pts
        video_frame.time_base = time_base

        return video_frame

    def capture_game_frame(self):
        """Capture frame from game rendering"""

        # In production, this would capture from:
        # - GPU frame buffer
        # - Virtual display
        # - Game engine hook

        # Mock frame
        frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        frame[:] = (50, 100, 150)  # Blue-ish background

        return frame


class GameStreamingServer:
    def __init__(self):
        self.peer_connections = {}
        self.game_sessions = {}

    async def create_session(self, session_id, game_id):
        """Create new game streaming session"""

        # Launch game process
        game_process = await self.launch_game(game_id)
        self.game_sessions[session_id] = game_process

        # Create peer connection
        pc = RTCPeerConnection()
        self.peer_connections[session_id] = pc

        # Add video track
        renderer = GameRenderer(game_process)
        pc.addTrack(renderer)

        # Setup data channel for input
        @pc.on("datachannel")
        def on_datachannel(channel):
            @channel.on("message")
            def on_message(message):
                # Handle input from client
                self.handle_input(session_id, message)

        return pc

    async def launch_game(self, game_id):
        """Launch game process"""

        # In production:
        # - Start game executable
        # - Configure virtual display
        # - Setup GPU sharing
        # - Configure audio capture

        return {"game_id": game_id, "pid": 12345}

    def handle_input(self, session_id, input_data):
        """Process input from client"""

        # Deserialize input
        input_event = self.deserialize_input(input_data)

        # Forward to game process via:
        # - Virtual input device
        # - Game engine API
        # - Input injection

        print(f"Input for {session_id}: {input_event}")

    def deserialize_input(self, data):
        """Deserialize input data"""
        import json
        return json.loads(data)

    async def handle_offer(self, session_id, offer):
        """Handle WebRTC offer from client"""

        pc = self.peer_connections.get(session_id)
        if not pc:
            pc = await self.create_session(session_id, "game_123")

        # Set remote description
        await pc.setRemoteDescription(
            RTCSessionDescription(sdp=offer["sdp"], type=offer["type"])
        )

        # Create answer
        answer = await pc.createAnswer()
        await pc.setLocalDescription(answer)

        return {
            "sdp": pc.localDescription.sdp,
            "type": pc.localDescription.type
        }
```

## Phase 2: Matchmaking System

### 2.1 Skill-Based Matchmaking

```python
# matchmaking.py
import asyncio
import time
from typing import List, Dict
from dataclasses import dataclass

@dataclass
class Player:
    id: str
    skill_rating: float
    region: str
    preferred_modes: List[str]
    wait_time: float = 0
    party_id: str = None

class SkillBasedMatchmaking:
    def __init__(self):
        self.queue = {}  # mode -> [players]
        self.matches = []
        self.match_sizes = {
            "1v1": 2,
            "2v2": 4,
            "5v5": 10
        }

    async def add_to_queue(self, player: Player, mode: str):
        """Add player to matchmaking queue"""

        if mode not in self.queue:
            self.queue[mode] = []

        player.wait_time = time.time()
        self.queue[mode].append(player)

        print(f"Player {player.id} joined {mode} queue")

        # Try to find match
        match = await self.find_match(mode)

        return match

    async def find_match(self, mode: str) -> Dict:
        """Find suitable match for players in queue"""

        players = self.queue[mode]
        match_size = self.match_sizes.get(mode, 2)

        if len(players) < match_size:
            return None

        # Sort by wait time (priority to waiting players)
        players.sort(key=lambda p: p.wait_time)

        # Try to create balanced match
        for i in range(len(players) - match_size + 1):
            candidate_players = players[i:i + match_size]

            if self.is_balanced_match(candidate_players):
                # Create match
                match = self.create_match(mode, candidate_players)

                # Remove players from queue
                for p in candidate_players:
                    self.queue[mode].remove(p)

                return match

        return None

    def is_balanced_match(self, players: List[Player]) -> bool:
        """Check if match is balanced"""

        # Calculate skill range
        skills = [p.skill_rating for p in players]
        skill_range = max(skills) - min(skills)

        # Dynamic tolerance based on wait time
        max_wait = max(p.wait_time for p in players)
        wait_duration = time.time() - max_wait

        # Expand tolerance over time
        base_tolerance = 100  # Skill rating points
        time_expansion = wait_duration / 10  # Expand by 1 per 10 seconds
        tolerance = base_tolerance + time_expansion * 50

        # Check region compatibility
        regions = set(p.region for p in players)
        if len(regions) > 2:  # Too many regions
            return False

        return skill_range <= tolerance

    def create_match(self, mode: str, players: List[Player]) -> Dict:
        """Create match from players"""

        match_id = f"match_{int(time.time())}_{len(self.matches)}"

        # Balance teams (for team modes)
        if mode in ["2v2", "5v5"]:
            teams = self.balance_teams(players)
        else:
            teams = {"players": [p.id for p in players]}

        match = {
            "match_id": match_id,
            "mode": mode,
            "teams": teams,
            "players": [p.id for p in players],
            "avg_skill": sum(p.skill_rating for p in players) / len(players),
            "created_at": time.time()
        }

        self.matches.append(match)

        print(f"Created match {match_id} with {len(players)} players")

        return match

    def balance_teams(self, players: List[Player]) -> Dict:
        """Create balanced teams"""

        # Sort by skill
        sorted_players = sorted(players, key=lambda p: p.skill_rating, reverse=True)

        # Alternate assignment (snake draft)
        team1 = []
        team2 = []

        for i, player in enumerate(sorted_players):
            if i % 2 == 0:
                team1.append(player.id)
            else:
                team2.append(player.id)

        return {
            "team1": team1,
            "team2": team2
        }

    async def update_skill_rating(self, player_id: str, match_result: Dict):
        """Update player skill rating after match (ELO-like)"""

        # ELO calculation
        K = 32  # K-factor
        player_rating = match_result["player_rating"]
        opponent_rating = match_result["opponent_avg_rating"]
        won = match_result["won"]

        # Expected score
        expected = 1 / (1 + 10 ** ((opponent_rating - player_rating) / 400))

        # Actual score
        actual = 1.0 if won else 0.0

        # New rating
        new_rating = player_rating + K * (actual - expected)

        return new_rating
```

## Phase 3: Live Streaming Integration

### 3.1 Twitch-Style Broadcasting

```javascript
// broadcast_system.js
class GameBroadcaster {
    constructor() {
        this.mediaRecorder = null;
        this.stream = null;
        this.chunks = [];
        this.websocket = null;
    }

    async startBroadcast(streamKey) {
        // Capture game video + audio + webcam
        const gameStream = await this.captureGameStream();
        const webcamStream = await this.captureWebcam();
        const audioStream = await this.captureAudio();

        // Combine streams
        this.stream = this.combineStreams(gameStream, webcamStream, audioStream);

        // Setup WebSocket to streaming server
        this.websocket = new WebSocket(`wss://stream.example.com/publish/${streamKey}`);

        this.websocket.onopen = () => {
            console.log('Connected to streaming server');
            this.startEncoding();
        };

        this.websocket.onerror = (error) => {
            console.error('Streaming error:', error);
        };
    }

    async captureGameStream() {
        // Capture game window/screen
        return await navigator.mediaDevices.getDisplayMedia({
            video: {
                width: 1920,
                height: 1080,
                frameRate: 60
            },
            audio: true
        });
    }

    async captureWebcam() {
        return await navigator.mediaDevices.getUserMedia({
            video: {
                width: 320,
                height: 240,
                frameRate: 30
            }
        });
    }

    async captureAudio() {
        return await navigator.mediaDevices.getUserMedia({
            audio: {
                echoCancellation: true,
                noiseSuppression: true,
                autoGainControl: true
            }
        });
    }

    combineStreams(gameStream, webcamStream, audioStream) {
        // Combine video tracks
        const canvas = document.createElement('canvas');
        canvas.width = 1920;
        canvas.height = 1080;
        const ctx = canvas.getContext('2d');

        const gameVideo = document.createElement('video');
        gameVideo.srcObject = gameStream;
        gameVideo.play();

        const webcamVideo = document.createElement('video');
        webcamVideo.srcObject = webcamStream;
        webcamVideo.play();

        // Composite video
        const drawFrame = () => {
            // Draw game video
            ctx.drawImage(gameVideo, 0, 0, 1920, 1080);

            // Draw webcam overlay (bottom-right corner)
            ctx.drawImage(webcamVideo, 1920 - 320 - 20, 1080 - 240 - 20, 320, 240);

            requestAnimationFrame(drawFrame);
        };

        requestAnimationFrame(drawFrame);

        // Create stream from canvas
        const compositeStream = canvas.captureStream(60);

        // Add audio tracks
        audioStream.getAudioTracks().forEach(track => {
            compositeStream.addTrack(track);
        });

        return compositeStream;
    }

    startEncoding() {
        // Encode and send to server
        const options = {
            mimeType: 'video/webm; codecs=vp9,opus',
            videoBitsPerSecond: 6000000, // 6 Mbps
            audioBitsPerSecond: 128000   // 128 Kbps
        };

        this.mediaRecorder = new MediaRecorder(this.stream, options);

        this.mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                // Send chunk to server
                this.websocket.send(event.data);
            }
        };

        // Record in small chunks for low latency
        this.mediaRecorder.start(1000); // 1 second chunks
    }

    stopBroadcast() {
        if (this.mediaRecorder) {
            this.mediaRecorder.stop();
        }

        if (this.websocket) {
            this.websocket.close();
        }

        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
        }
    }

    getStats() {
        return {
            bitrate: this.getCurrentBitrate(),
            droppedFrames: this.getDroppedFrames(),
            latency: this.getStreamLatency()
        };
    }

    getCurrentBitrate() {
        // Calculate actual bitrate
        return 6000; // kbps
    }

    getDroppedFrames() {
        // Get dropped frames count
        return 0;
    }

    getStreamLatency() {
        // Measure stream latency
        return 2000; // ms
    }
}

// Usage
const broadcaster = new GameBroadcaster();
await broadcaster.startBroadcast('stream_key_12345');
```

## Best Practices

1. **Minimize latency**: Target < 100ms glass-to-glass latency
2. **Use WebRTC for interactivity**: Lower latency than RTMP/HLS
3. **Implement adaptive bitrate**: Adjust quality based on network
4. **Buffer input locally**: Predict movement for smoother experience
5. **Use UDP data channels**: Unreliable but low-latency for input
6. **Optimize encoding**: H.265 for better quality at lower bitrate
7. **Deploy edge servers**: Reduce distance to players
8. **Implement skill-based matchmaking**: Balanced games
9. **Monitor latency metrics**: Track RTT, jitter, packet loss
10. **Support offline mode**: Download and play locally

## Performance Targets

- **Video latency**: < 100ms glass-to-glass
- **Input lag**: < 50ms
- **Frame rate**: 60 FPS minimum
- **Bitrate**: 10-15 Mbps for 1080p60
- **Matchmaking time**: < 30 seconds average
- **Server tick rate**: 64-128 ticks/second
