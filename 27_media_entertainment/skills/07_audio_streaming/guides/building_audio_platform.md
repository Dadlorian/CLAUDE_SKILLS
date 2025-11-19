# Building a Music Streaming Platform

Complete guide to building a production music streaming service like Spotify, Apple Music, or Tidal, covering audio pipeline, playback, recommendations, and social features.

## Architecture Overview

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│ Audio Ingest &  │─────>│ Transcoding &    │─────>│  CDN Storage    │
│ Normalization   │      │ Format Variants  │      │  (Multi-codec)  │
└─────────────────┘      └──────────────────┘      └─────────────────┘
                                                              │
                                                              ▼
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│  Client Apps    │<─────│   Streaming API  │─────>│  Playlist &     │
│  (Web/Mobile)   │      │   & Playback     │      │  Metadata DB    │
└─────────────────┘      └──────────────────┘      └─────────────────┘
        │
        ▼
┌─────────────────┐
│  Offline Sync   │
│  & Downloads    │
└─────────────────┘
```

## Phase 1: Audio Ingestion & Processing

### 1.1 Audio Upload & Validation

```python
# audio_ingest.py
import librosa
import soundfile as sf
import numpy as np
from pathlib import Path
import hashlib

class AudioIngestPipeline:
    def __init__(self, config):
        self.config = config
        self.supported_formats = ['mp3', 'wav', 'flac', 'aac', 'm4a', 'ogg']

    def validate_audio_file(self, file_path):
        """Validate uploaded audio file"""

        file_path = Path(file_path)

        # Check extension
        if file_path.suffix[1:].lower() not in self.supported_formats:
            raise ValueError(f"Unsupported format: {file_path.suffix}")

        # Check file size
        file_size = file_path.stat().st_size
        max_size = self.config.get('max_file_size', 500 * 1024 * 1024)  # 500MB
        if file_size > max_size:
            raise ValueError(f"File too large: {file_size} bytes")

        try:
            # Load audio to verify it's valid
            audio, sr = librosa.load(file_path, sr=None, mono=False)

            # Check duration
            duration = librosa.get_duration(y=audio, sr=sr)
            if duration < 5:  # Minimum 5 seconds
                raise ValueError(f"Track too short: {duration}s")

            if duration > 3600:  # Maximum 1 hour
                raise ValueError(f"Track too long: {duration}s")

            # Check sample rate
            if sr < 44100:
                raise ValueError(f"Sample rate too low: {sr} Hz")

            return {
                'valid': True,
                'duration': duration,
                'sample_rate': sr,
                'channels': audio.shape[0] if audio.ndim > 1 else 1,
                'file_size': file_size
            }

        except Exception as e:
            raise ValueError(f"Invalid audio file: {str(e)}")

    def compute_fingerprint(self, file_path):
        """Compute audio fingerprint for duplicate detection"""

        # Load audio
        audio, sr = librosa.load(file_path, sr=22050, mono=True)

        # Extract chromagram features
        chroma = librosa.feature.chroma_cqt(y=audio, sr=sr)

        # Compute hash
        chroma_flat = chroma.flatten()
        fingerprint = hashlib.sha256(chroma_flat.tobytes()).hexdigest()

        return fingerprint

    def normalize_audio(self, input_path, output_path, target_lufs=-14.0):
        """Normalize audio loudness to target LUFS"""

        # Load audio
        audio, sr = librosa.load(input_path, sr=None, mono=False)

        # Compute current loudness
        current_lufs = self.compute_lufs(audio, sr)

        # Calculate gain adjustment
        gain_db = target_lufs - current_lufs
        gain_linear = 10 ** (gain_db / 20)

        # Apply gain
        normalized_audio = audio * gain_linear

        # Prevent clipping
        peak = np.max(np.abs(normalized_audio))
        if peak > 0.99:
            normalized_audio = normalized_audio * (0.99 / peak)

        # Save
        sf.write(output_path, normalized_audio.T, sr)

        return {
            'original_lufs': current_lufs,
            'target_lufs': target_lufs,
            'gain_applied_db': gain_db,
            'peak_after': np.max(np.abs(normalized_audio))
        }

    def compute_lufs(self, audio, sr):
        """Compute integrated loudness (simplified)"""

        # This is simplified - in production use pyloudnorm
        rms = np.sqrt(np.mean(audio ** 2))
        lufs = 20 * np.log10(rms) - 0.691  # Approximate conversion

        return lufs

    def extract_metadata(self, file_path):
        """Extract audio metadata"""

        import mutagen

        audio_file = mutagen.File(file_path)

        if audio_file is None:
            return {}

        metadata = {
            'title': audio_file.get('title', ['Unknown'])[0],
            'artist': audio_file.get('artist', ['Unknown'])[0],
            'album': audio_file.get('album', ['Unknown'])[0],
            'genre': audio_file.get('genre', ['Unknown'])[0],
            'year': audio_file.get('date', ['Unknown'])[0],
            'track_number': audio_file.get('tracknumber', ['Unknown'])[0],
            'duration': audio_file.info.length if hasattr(audio_file, 'info') else 0,
            'bitrate': audio_file.info.bitrate if hasattr(audio_file, 'info') else 0,
            'sample_rate': audio_file.info.sample_rate if hasattr(audio_file, 'info') else 0
        }

        return metadata
```

### 1.2 Audio Transcoding Pipeline

```python
# transcoding.py
import subprocess
import os
from concurrent.futures import ThreadPoolExecutor

class AudioTranscoder:
    def __init__(self, ffmpeg_path='ffmpeg'):
        self.ffmpeg_path = ffmpeg_path

    def transcode_to_formats(self, input_file, output_dir, track_id):
        """Transcode to multiple formats and bitrates"""

        formats = [
            # Format: (codec, bitrate, extension)
            ('aac', '320k', 'aac'),      # High quality AAC
            ('aac', '256k', 'aac'),      # Medium-high AAC
            ('aac', '128k', 'aac'),      # Medium AAC
            ('aac', '96k', 'aac'),       # Low AAC (mobile)
            ('opus', '256k', 'opus'),    # High quality Opus
            ('opus', '128k', 'opus'),    # Medium Opus
            ('opus', '64k', 'opus'),     # Low Opus
            ('mp3', '320k', 'mp3'),      # High quality MP3
            ('mp3', '192k', 'mp3'),      # Medium MP3
            ('mp3', '128k', 'mp3'),      # Low MP3
        ]

        os.makedirs(output_dir, exist_ok=True)

        results = []

        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = []

            for codec, bitrate, ext in formats:
                output_file = os.path.join(
                    output_dir,
                    f"{track_id}_{codec}_{bitrate}.{ext}"
                )

                future = executor.submit(
                    self.transcode_single,
                    input_file,
                    output_file,
                    codec,
                    bitrate
                )
                futures.append((future, output_file, codec, bitrate))

            for future, output_file, codec, bitrate in futures:
                try:
                    result = future.result()
                    results.append({
                        'codec': codec,
                        'bitrate': bitrate,
                        'file': output_file,
                        'size': os.path.getsize(output_file),
                        'success': True
                    })
                except Exception as e:
                    results.append({
                        'codec': codec,
                        'bitrate': bitrate,
                        'error': str(e),
                        'success': False
                    })

        return results

    def transcode_single(self, input_file, output_file, codec, bitrate):
        """Transcode to a single format"""

        codec_map = {
            'aac': 'aac',
            'opus': 'libopus',
            'mp3': 'libmp3lame',
            'vorbis': 'libvorbis'
        }

        ffmpeg_codec = codec_map.get(codec, codec)

        # Build ffmpeg command
        cmd = [
            self.ffmpeg_path,
            '-i', input_file,
            '-c:a', ffmpeg_codec,
            '-b:a', bitrate,
            '-ar', '44100',  # Sample rate
            '-ac', '2',       # Stereo
            '-y',             # Overwrite
            output_file
        ]

        # Run ffmpeg
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if result.returncode != 0:
            raise Exception(f"FFmpeg error: {result.stderr}")

        return output_file
```

## Phase 2: Streaming & Adaptive Bitrate

### 2.1 Adaptive Bitrate Streaming

```javascript
// adaptive_streaming.js
class AdaptiveAudioStreamer {
    constructor(config) {
        this.config = config;
        this.audio = new Audio();
        this.currentQuality = 'medium';
        this.qualityLevels = [
            { name: 'low', bitrate: 64, url: null },
            { name: 'medium', bitrate: 128, url: null },
            { name: 'high', bitrate: 256, url: null },
            { name: 'ultra', bitrate: 320, url: null }
        ];

        this.bandwidthEstimate = 1000; // kbps
        this.bufferLevel = 0;
        this.targetBuffer = 30; // seconds

        this.setupNetworkMonitoring();
    }

    async loadTrack(trackId) {
        // Fetch available quality levels for track
        const response = await fetch(`/api/tracks/${trackId}/variants`);
        const variants = await response.json();

        this.qualityLevels.forEach(level => {
            const variant = variants.find(v => v.bitrate === level.bitrate);
            if (variant) {
                level.url = variant.url;
            }
        });

        // Start with appropriate quality
        const initialQuality = this.selectQuality();
        await this.switchQuality(initialQuality);
    }

    selectQuality() {
        // Select quality based on bandwidth and buffer
        const availableBandwidth = this.bandwidthEstimate * 0.8; // Safety margin

        // If buffer is low, choose lower quality for faster buffering
        if (this.bufferLevel < 5) {
            return 'low';
        }

        // Select highest quality that fits bandwidth
        for (let i = this.qualityLevels.length - 1; i >= 0; i--) {
            const level = this.qualityLevels[i];
            if (level.bitrate <= availableBandwidth && level.url) {
                return level.name;
            }
        }

        return 'low'; // Fallback
    }

    async switchQuality(qualityName) {
        const quality = this.qualityLevels.find(q => q.name === qualityName);
        if (!quality || !quality.url) {
            console.warn(`Quality ${qualityName} not available`);
            return;
        }

        const currentTime = this.audio.currentTime;
        const wasPlaying = !this.audio.paused;

        // Switch to new quality
        this.audio.src = quality.url;
        this.audio.currentTime = currentTime;

        if (wasPlaying) {
            await this.audio.play();
        }

        this.currentQuality = qualityName;
        console.log(`Switched to ${qualityName} (${quality.bitrate}kbps)`);
    }

    setupNetworkMonitoring() {
        // Monitor network conditions
        if ('connection' in navigator) {
            navigator.connection.addEventListener('change', () => {
                this.updateBandwidthEstimate();
            });
        }

        // Monitor buffer level
        this.audio.addEventListener('progress', () => {
            this.updateBufferLevel();
            this.adaptQuality();
        });

        // Monitor playback
        this.audio.addEventListener('waiting', () => {
            console.warn('Buffering...');
            // Switch to lower quality if buffering
            this.handleBuffering();
        });
    }

    updateBandwidthEstimate() {
        // Use Network Information API
        if ('connection' in navigator) {
            const connection = navigator.connection;
            if (connection.downlink) {
                this.bandwidthEstimate = connection.downlink * 1000; // Convert to kbps
            }
        }

        // Also measure actual download speed
        this.measureDownloadSpeed();
    }

    async measureDownloadSpeed() {
        const testSize = 100 * 1024; // 100KB
        const startTime = Date.now();

        try {
            const response = await fetch('/api/speedtest', {
                headers: {
                    'Range': `bytes=0-${testSize}`
                }
            });

            await response.arrayBuffer();
            const duration = (Date.now() - startTime) / 1000; // seconds
            const speedKbps = (testSize * 8) / (duration * 1000);

            // Exponential moving average
            this.bandwidthEstimate = 0.8 * this.bandwidthEstimate + 0.2 * speedKbps;

        } catch (error) {
            console.error('Speed test failed:', error);
        }
    }

    updateBufferLevel() {
        if (this.audio.buffered.length > 0) {
            const bufferedEnd = this.audio.buffered.end(this.audio.buffered.length - 1);
            this.bufferLevel = bufferedEnd - this.audio.currentTime;
        }
    }

    adaptQuality() {
        // Adapt quality based on current conditions
        const optimalQuality = this.selectQuality();

        if (optimalQuality !== this.currentQuality) {
            console.log(`Adapting quality: ${this.currentQuality} -> ${optimalQuality}`);
            this.switchQuality(optimalQuality);
        }
    }

    handleBuffering() {
        // If buffering, immediately switch to lower quality
        const currentIndex = this.qualityLevels.findIndex(q => q.name === this.currentQuality);

        if (currentIndex > 0) {
            const lowerQuality = this.qualityLevels[currentIndex - 1];
            console.log('Buffering detected, switching to lower quality');
            this.switchQuality(lowerQuality.name);
        }
    }

    play() {
        return this.audio.play();
    }

    pause() {
        this.audio.pause();
    }

    seek(time) {
        this.audio.currentTime = time;
    }

    getCurrentTime() {
        return this.audio.currentTime;
    }

    getDuration() {
        return this.audio.duration;
    }
}

// Usage
const streamer = new AdaptiveAudioStreamer({ targetBuffer: 30 });
await streamer.loadTrack('track_12345');
await streamer.play();
```

## Phase 3: Offline Playback & Sync

### 3.1 Offline Download Manager

```typescript
// offline_manager.ts
import { openDB, DBSchema, IDBPDatabase } from 'idb';

interface Track {
    id: string;
    title: string;
    artist: string;
    album: string;
    duration: number;
    audioUrl: string;
    coverArtUrl: string;
}

interface OfflineTrack extends Track {
    downloadedAt: Date;
    audioBlob: Blob;
    coverArtBlob: Blob;
}

interface MusicDB extends DBSchema {
    'offline-tracks': {
        key: string;
        value: OfflineTrack;
        indexes: { 'by-downloaded': Date };
    };
    'playlists': {
        key: string;
        value: {
            id: string;
            name: string;
            trackIds: string[];
            downloadedAt: Date;
        };
    };
}

class OfflineManager {
    private db: IDBPDatabase<MusicDB> | null = null;
    private downloadQueue: string[] = [];
    private isDownloading: boolean = false;

    async initialize() {
        this.db = await openDB<MusicDB>('music-offline', 1, {
            upgrade(db) {
                // Create stores
                const trackStore = db.createObjectStore('offline-tracks', {
                    keyPath: 'id'
                });
                trackStore.createIndex('by-downloaded', 'downloadedAt');

                db.createObjectStore('playlists', { keyPath: 'id' });
            }
        });
    }

    async downloadTrack(track: Track): Promise<void> {
        if (!this.db) throw new Error('Database not initialized');

        // Check if already downloaded
        const existing = await this.db.get('offline-tracks', track.id);
        if (existing) {
            console.log(`Track ${track.id} already downloaded`);
            return;
        }

        try {
            // Download audio file
            const audioResponse = await fetch(track.audioUrl);
            const audioBlob = await audioResponse.blob();

            // Download cover art
            const coverResponse = await fetch(track.coverArtUrl);
            const coverArtBlob = await coverResponse.blob();

            // Store in IndexedDB
            const offlineTrack: OfflineTrack = {
                ...track,
                audioBlob,
                coverArtBlob,
                downloadedAt: new Date()
            };

            await this.db.put('offline-tracks', offlineTrack);

            console.log(`Downloaded track: ${track.title}`);

            // Emit event
            this.emitDownloadComplete(track.id);

        } catch (error) {
            console.error(`Failed to download track ${track.id}:`, error);
            throw error;
        }
    }

    async downloadPlaylist(playlistId: string, tracks: Track[]): Promise<void> {
        if (!this.db) throw new Error('Database not initialized');

        // Add all tracks to download queue
        for (const track of tracks) {
            if (!await this.isTrackDownloaded(track.id)) {
                this.downloadQueue.push(track.id);
            }
        }

        // Start downloading
        this.processDownloadQueue(tracks);

        // Store playlist info
        await this.db.put('playlists', {
            id: playlistId,
            name: 'Offline Playlist',
            trackIds: tracks.map(t => t.id),
            downloadedAt: new Date()
        });
    }

    private async processDownloadQueue(tracks: Track[]) {
        if (this.isDownloading) return;

        this.isDownloading = true;

        while (this.downloadQueue.length > 0) {
            const trackId = this.downloadQueue.shift()!;
            const track = tracks.find(t => t.id === trackId);

            if (track) {
                try {
                    await this.downloadTrack(track);
                } catch (error) {
                    console.error(`Failed to download ${trackId}:`, error);
                }
            }
        }

        this.isDownloading = false;
    }

    async isTrackDownloaded(trackId: string): Promise<boolean> {
        if (!this.db) return false;

        const track = await this.db.get('offline-tracks', trackId);
        return track !== undefined;
    }

    async getOfflineTrack(trackId: string): Promise<OfflineTrack | null> {
        if (!this.db) return null;

        return await this.db.get('offline-tracks', trackId) || null;
    }

    async getAllOfflineTracks(): Promise<OfflineTrack[]> {
        if (!this.db) return [];

        return await this.db.getAll('offline-tracks');
    }

    async removeTrack(trackId: string): Promise<void> {
        if (!this.db) return;

        await this.db.delete('offline-tracks', trackId);
        console.log(`Removed offline track: ${trackId}`);
    }

    async getStorageUsage(): Promise<{ used: number; quota: number }> {
        if ('storage' in navigator && 'estimate' in navigator.storage) {
            const estimate = await navigator.storage.estimate();
            return {
                used: estimate.usage || 0,
                quota: estimate.quota || 0
            };
        }

        return { used: 0, quota: 0 };
    }

    async clearAllOfflineData(): Promise<void> {
        if (!this.db) return;

        await this.db.clear('offline-tracks');
        await this.db.clear('playlists');

        console.log('Cleared all offline data');
    }

    private emitDownloadComplete(trackId: string) {
        const event = new CustomEvent('track-downloaded', {
            detail: { trackId }
        });
        window.dispatchEvent(event);
    }
}

// Usage
const offlineManager = new OfflineManager();
await offlineManager.initialize();

// Download single track
await offlineManager.downloadTrack(track);

// Download playlist
await offlineManager.downloadPlaylist('playlist_123', tracks);

// Check storage
const storage = await offlineManager.getStorageUsage();
console.log(`Using ${storage.used} / ${storage.quota} bytes`);
```

## Phase 4: Audio Features & Analysis

### 4.1 Audio Feature Extraction

```python
# audio_features.py
import librosa
import numpy as np

class AudioFeatureExtractor:
    def extract_all_features(self, audio_file):
        """Extract comprehensive audio features"""

        # Load audio
        y, sr = librosa.load(audio_file, sr=22050, mono=True)

        features = {}

        # Tempo and beats
        tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
        features['tempo'] = float(tempo)
        features['num_beats'] = len(beats)

        # Key and mode (major/minor)
        chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
        key = self.estimate_key(chroma)
        features['key'] = key['key']
        features['mode'] = key['mode']

        # Energy and loudness
        features['rms_energy'] = float(np.mean(librosa.feature.rms(y=y)))
        features['loudness'] = float(librosa.amplitude_to_db(np.abs(y).mean()))

        # Spectral features
        spec_cent = librosa.feature.spectral_centroid(y=y, sr=sr)
        features['spectral_centroid'] = float(np.mean(spec_cent))

        spec_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
        features['spectral_rolloff'] = float(np.mean(spec_rolloff))

        # Timbre (MFCCs)
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        features['mfccs'] = mfccs.mean(axis=1).tolist()

        # Danceability (beat strength)
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        features['danceability'] = float(np.mean(onset_env))

        # Valence (happiness) - approximate using spectral features
        features['valence'] = self.estimate_valence(y, sr)

        # Acousticness - estimate using spectral features
        features['acousticness'] = self.estimate_acousticness(y, sr)

        return features

    def estimate_key(self, chroma):
        """Estimate musical key"""

        # Krumhansl-Schmuckler key-finding algorithm
        major_profile = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09,
                                   2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
        minor_profile = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53,
                                   2.54, 4.75, 3.98, 2.69, 3.34, 3.17])

        chroma_mean = chroma.mean(axis=1)

        # Compute correlation with each key
        keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        major_cors = []
        minor_cors = []

        for i in range(12):
            major_cors.append(np.corrcoef(chroma_mean, np.roll(major_profile, i))[0, 1])
            minor_cors.append(np.corrcoef(chroma_mean, np.roll(minor_profile, i))[0, 1])

        major_key = keys[np.argmax(major_cors)]
        minor_key = keys[np.argmax(minor_cors)]

        if max(major_cors) > max(minor_cors):
            return {'key': major_key, 'mode': 'major'}
        else:
            return {'key': minor_key, 'mode': 'minor'}

    def estimate_valence(self, y, sr):
        """Estimate valence (happiness) of track"""

        # Use spectral features as proxy
        # Higher spectral centroid and more harmonics suggest happier sound

        spec_cent = librosa.feature.spectral_centroid(y=y, sr=sr)
        harmonic, percussive = librosa.effects.hpss(y)

        harmonic_ratio = np.mean(np.abs(harmonic)) / (np.mean(np.abs(y)) + 1e-6)

        valence = (np.mean(spec_cent) / 5000) * harmonic_ratio

        return float(np.clip(valence, 0, 1))

    def estimate_acousticness(self, y, sr):
        """Estimate acousticness of track"""

        # Lower spectral complexity suggests more acoustic

        spec_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)
        spec_flatness = librosa.feature.spectral_flatness(y=y)

        # Lower bandwidth and flatness = more acoustic
        acousticness = 1.0 - (np.mean(spec_flatness) + np.mean(spec_bandwidth) / 10000) / 2

        return float(np.clip(acousticness, 0, 1))
```

## Best Practices

1. **Use adaptive bitrate streaming** to handle varying network conditions
2. **Normalize audio** to -14 LUFS for consistent loudness
3. **Support offline playback** for mobile users
4. **Extract audio features** for recommendations and discovery
5. **Implement crossfade** between tracks for seamless listening
6. **Cache frequently played** tracks locally
7. **Preload next track** for instant playback
8. **Monitor bandwidth** and adapt quality in real-time
9. **Support gapless playback** for albums
10. **Implement EQ and audio effects** for personalization

## Performance Targets

- **Initial playback latency**: < 500ms
- **Buffer target**: 30 seconds
- **Adaptive switching time**: < 100ms
- **Offline download speed**: > 1MB/s
- **Audio quality**: AAC 256kbps or Opus 128kbps
- **Storage efficiency**: < 5MB per track average
