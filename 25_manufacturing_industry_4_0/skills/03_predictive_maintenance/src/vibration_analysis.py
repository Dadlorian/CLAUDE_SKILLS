"""
Vibration Analysis Module for Predictive Maintenance

This module provides comprehensive vibration analysis capabilities for equipment
condition monitoring, including time-domain and frequency-domain analysis,
bearing fault detection, and envelope analysis.

Author: Industrial AI Team
License: MIT
"""

import numpy as np
import scipy.signal
import scipy.stats
from typing import Dict, Tuple, List, Optional
import warnings


class VibrationAnalyzer:
    """
    Comprehensive vibration analysis for bearing and rotating machinery diagnosis.

    Attributes:
        sampling_rate (float): Data sampling rate in Hz
        signal_data (np.ndarray): Raw vibration signal
        time_array (np.ndarray): Time vector corresponding to signal
    """

    def __init__(self, sampling_rate: float):
        """
        Initialize VibrationAnalyzer.

        Args:
            sampling_rate: Sampling rate in Hz (e.g., 51200 for 51.2 kHz)
        """
        self.sampling_rate = sampling_rate
        self.signal_data = None
        self.time_array = None

    def load_signal(self, signal_data: np.ndarray, duration: Optional[float] = None):
        """
        Load vibration signal data.

        Args:
            signal_data: 1D array of vibration acceleration values (in g or m/s²)
            duration: Duration of signal in seconds (if not provided, calculated from len/sampling_rate)
        """
        self.signal_data = np.asarray(signal_data).flatten()

        if duration is None:
            duration = len(self.signal_data) / self.sampling_rate

        self.time_array = np.linspace(0, duration, len(self.signal_data))

    def time_domain_features(self) -> Dict[str, float]:
        """
        Extract time-domain features from vibration signal.

        Returns:
            Dictionary containing:
            - rms: Root Mean Square vibration amplitude
            - peak: Peak (maximum absolute) value
            - peak_to_peak: Peak-to-peak amplitude
            - crest_factor: Peak/RMS ratio (indicates impulsiveness)
            - kurtosis: 4th moment (indicates fault presence)
            - skewness: 3rd moment (asymmetry indicator)
            - rms_envelope: RMS of impulse envelope (bearing faults)
        """

        if self.signal_data is None:
            raise ValueError("No signal loaded. Call load_signal() first.")

        x = self.signal_data

        # Basic statistics
        rms = np.sqrt(np.mean(x**2))
        peak = np.max(np.abs(x))
        peak_to_peak = np.max(x) - np.min(x)
        mean_val = np.mean(x)
        std_val = np.std(x)

        # Distribution metrics
        crest_factor = peak / rms if rms > 0 else 0
        kurtosis = scipy.stats.kurtosis(x)
        skewness = scipy.stats.skewness(x)

        # Impulse metrics
        rms_envelope = self._compute_envelope_rms()

        features = {
            'rms': float(rms),
            'peak': float(peak),
            'peak_to_peak': float(peak_to_peak),
            'mean': float(mean_val),
            'std': float(std_val),
            'crest_factor': float(crest_factor),
            'kurtosis': float(kurtosis),
            'skewness': float(skewness),
            'rms_envelope': float(rms_envelope),
            'energy': float(np.sum(x**2))
        }

        return features

    def _compute_envelope_rms(self, freq_min: float = 5000, freq_max: float = 40000) -> float:
        """
        Compute RMS of envelope signal (demodulated high-frequency content).

        Args:
            freq_min: Lower frequency limit for bandpass filter (Hz)
            freq_max: Upper frequency limit for bandpass filter (Hz)

        Returns:
            RMS of envelope signal
        """

        # Bandpass filter
        sos = scipy.signal.butter(
            4, [freq_min, freq_max], btype='band',
            fs=self.sampling_rate, output='sos'
        )
        filtered = scipy.signal.sosfilt(sos, self.signal_data)

        # Envelope (magnitude of analytic signal)
        analytic_signal = scipy.signal.hilbert(filtered)
        envelope = np.abs(analytic_signal)

        # RMS of envelope
        envelope_rms = np.sqrt(np.mean(envelope**2))

        return envelope_rms

    def frequency_domain_features(self) -> Dict[str, float]:
        """
        Extract frequency-domain features from vibration signal.

        Returns:
            Dictionary containing spectral features:
            - spectral_centroid: Center of mass of spectrum
            - spectral_energy: Total energy in frequency domain
            - spectral_entropy: Shannon entropy (low for periodic, high for noise)
            - peak_frequency: Frequency with highest power
            - peak_power: Power at peak frequency
        """

        if self.signal_data is None:
            raise ValueError("No signal loaded.")

        # FFT
        fft_result = np.fft.fft(self.signal_data)
        freqs = np.fft.fftfreq(len(self.signal_data), 1/self.sampling_rate)
        power = np.abs(fft_result)**2

        # Use only positive frequencies
        positive_idx = freqs > 0
        freqs = freqs[positive_idx]
        power = power[positive_idx]

        # Spectral features
        spectral_centroid = np.sum(freqs * power) / (np.sum(power) + 1e-10)
        spectral_energy = np.sum(power)

        # Spectral entropy (indicates coherence)
        power_normalized = power / (np.sum(power) + 1e-10)
        spectral_entropy = -np.sum(power_normalized * np.log2(power_normalized + 1e-10))

        peak_idx = np.argmax(power)
        peak_frequency = freqs[peak_idx]
        peak_power = power[peak_idx]

        features = {
            'spectral_centroid': float(spectral_centroid),
            'spectral_energy': float(spectral_energy),
            'spectral_entropy': float(spectral_entropy),
            'peak_frequency': float(peak_frequency),
            'peak_power': float(peak_power)
        }

        return features

    def bearing_fault_frequencies(self, running_speed_hz: float,
                                  num_rolling_elements: int = 16,
                                  ball_diameter_mm: float = 12.7,
                                  pitch_diameter_mm: float = 71.5,
                                  contact_angle_deg: float = 0) -> Dict[str, float]:
        """
        Calculate bearing characteristic fault frequencies.

        Args:
            running_speed_hz: Shaft running speed in Hz (RPM/60)
            num_rolling_elements: Number of rolling elements (balls/rollers)
            ball_diameter_mm: Diameter of rolling elements
            pitch_diameter_mm: Pitch circle diameter
            contact_angle_deg: Contact angle in degrees

        Returns:
            Dictionary with bearing fault frequencies:
            - BPFO: Ball Pass Frequency Outer race
            - BPFI: Ball Pass Frequency Inner race
            - BSF: Ball Spin Frequency
            - FTF: Fundamental Train Frequency
        """

        n = num_rolling_elements
        Bd = ball_diameter_mm
        Pd = pitch_diameter_mm
        phi = np.radians(contact_angle_deg)
        fr = running_speed_hz

        # Bearing fault frequencies
        BPFO = (n/2) * fr * (1 + (Bd/Pd) * np.cos(phi))
        BPFI = (n/2) * fr * (1 - (Bd/Pd) * np.cos(phi))
        BSF = (Pd/(2*Bd)) * fr * (1 - ((Bd/Pd)**2) * (np.cos(phi))**2)
        FTF = 0.5 * (1 - (Bd/Pd) * np.cos(phi)) * fr

        return {
            'BPFO': float(BPFO),
            'BPFI': float(BPFI),
            'BSF': float(BSF),
            'FTF': float(FTF)
        }

    def envelope_analysis(self, freq_min: float = 5000, freq_max: float = 40000,
                         demod_freq_max: float = 500) -> Tuple[np.ndarray, np.ndarray, Dict]:
        """
        Perform envelope analysis (high-frequency demodulation) for bearing fault detection.

        Args:
            freq_min: Lower bandpass frequency limit (Hz)
            freq_max: Upper bandpass frequency limit (Hz)
            demod_freq_max: Upper frequency limit for demodulation filtering (Hz)

        Returns:
            Tuple of:
            - demodulated signal (envelope of filtered signal)
            - frequency array for FFT of demodulated signal
            - features extracted from demodulated signal
        """

        # Step 1: Bandpass filter (5-40 kHz typical)
        sos = scipy.signal.butter(
            4, [freq_min, freq_max], btype='band',
            fs=self.sampling_rate, output='sos'
        )
        filtered = scipy.signal.sosfilt(sos, self.signal_data)

        # Step 2: Envelope (analytic signal magnitude)
        analytic_signal = scipy.signal.hilbert(filtered)
        envelope = np.abs(analytic_signal)

        # Step 3: Low-pass filter envelope (demodulation)
        sos_lp = scipy.signal.butter(
            2, demod_freq_max, btype='low',
            fs=self.sampling_rate, output='sos'
        )
        demod_signal = scipy.signal.sosfilt(sos_lp, envelope)

        # Step 4: FFT of demodulated signal
        fft_demod = np.fft.fft(demod_signal)
        freqs_demod = np.fft.fftfreq(len(demod_signal), 1/self.sampling_rate)

        # Take only positive frequencies
        positive_idx = freqs_demod > 0
        freqs_demod = freqs_demod[positive_idx]
        power_demod = np.abs(fft_demod[positive_idx])**2

        # Extract features from demodulated signal
        features = {
            'envelope_rms': float(np.sqrt(np.mean(demod_signal**2))),
            'envelope_peak': float(np.max(np.abs(demod_signal))),
            'envelope_kurtosis': float(scipy.stats.kurtosis(demod_signal)),
            'demod_power': float(np.sum(power_demod))
        }

        return demod_signal, freqs_demod, features

    def bearing_fault_detection(self, running_speed_hz: float,
                               bearing_params: Optional[Dict] = None,
                               threshold_multiplier: float = 3.0) -> Dict:
        """
        Detect bearing faults by checking for energy at bearing fault frequencies.

        Args:
            running_speed_hz: Shaft speed in Hz
            bearing_params: Dictionary with bearing geometry parameters
            threshold_multiplier: Multiplier for noise floor to set detection threshold

        Returns:
            Dictionary with fault detection results:
            - fault_detected: Boolean indicating if fault likely
            - fault_type: Estimated fault type (if detected)
            - fault_frequencies: Detected frequencies with amplitudes
            - confidence: Confidence score (0-1)
        """

        # Default bearing parameters (standard deep-groove ball bearing)
        if bearing_params is None:
            bearing_params = {
                'num_rolling_elements': 16,
                'ball_diameter_mm': 12.7,
                'pitch_diameter_mm': 71.5,
                'contact_angle_deg': 0
            }

        # Get bearing fault frequencies
        fault_freqs = self.bearing_fault_frequencies(running_speed_hz, **bearing_params)

        # Perform envelope analysis
        _, freqs, _ = self.envelope_analysis()

        # Create frequency resolution
        freq_resolution = freqs[1] - freqs[0] if len(freqs) > 1 else 1.0
        detection_band = 0.1  # ±10% of fault frequency

        # FFT for amplitude
        fft_result = np.fft.fft(self.signal_data)
        freqs_fft = np.fft.fftfreq(len(self.signal_data), 1/self.sampling_rate)
        amplitudes = np.abs(fft_result)**2
        positive_idx = freqs_fft > 0
        freqs_fft = freqs_fft[positive_idx]
        amplitudes = amplitudes[positive_idx]

        # Check for fault frequencies
        detected_faults = {}
        baseline_noise = np.percentile(amplitudes, 50)  # Median as noise floor

        for fault_name, fault_freq in fault_freqs.items():
            # Look for energy ±10% of fault frequency
            freq_min = fault_freq * (1 - detection_band)
            freq_max = fault_freq * (1 + detection_band)

            in_range = (freqs_fft >= freq_min) & (freqs_fft <= freq_max)
            if np.any(in_range):
                peak_amp = np.max(amplitudes[in_range])
                peak_freq = freqs_fft[np.argmax(amplitudes[in_range])]

                # Signal-to-noise ratio
                snr = peak_amp / (baseline_noise + 1e-10)

                if snr > threshold_multiplier:
                    detected_faults[fault_name] = {
                        'frequency': float(peak_freq),
                        'amplitude': float(np.sqrt(peak_amp)),
                        'snr': float(snr)
                    }

        # Determine overall fault status
        fault_detected = len(detected_faults) > 0
        confidence = min(1.0, len(detected_faults) / 2.0) if fault_detected else 0.0

        # Determine fault type based on patterns
        fault_type = "None"
        if 'BPFO' in detected_faults and 'BPFI' not in detected_faults:
            fault_type = "Outer Race Defect"
        elif 'BPFI' in detected_faults:
            fault_type = "Inner Race Defect"
        elif 'BSF' in detected_faults:
            fault_type = "Rolling Element Defect"

        return {
            'fault_detected': bool(fault_detected),
            'fault_type': fault_type,
            'fault_frequencies': detected_faults,
            'confidence': float(confidence),
            'baseline_noise': float(baseline_noise)
        }

    def extract_all_features(self, running_speed_hz: Optional[float] = None,
                            bearing_params: Optional[Dict] = None) -> Dict:
        """
        Extract comprehensive feature set from vibration signal.

        Args:
            running_speed_hz: Optional shaft speed for bearing analysis
            bearing_params: Optional bearing geometry for bearing analysis

        Returns:
            Comprehensive feature dictionary
        """

        features = {}

        # Time-domain features
        time_features = self.time_domain_features()
        features.update({f"time_{k}": v for k, v in time_features.items()})

        # Frequency-domain features
        freq_features = self.frequency_domain_features()
        features.update({f"freq_{k}": v for k, v in freq_features.items()})

        # Bearing fault detection (if speed provided)
        if running_speed_hz is not None:
            bearing_fault = self.bearing_fault_detection(running_speed_hz, bearing_params)
            features['bearing_fault_detected'] = bearing_fault['fault_detected']
            features['bearing_fault_confidence'] = bearing_fault['confidence']
            features['bearing_fault_type'] = bearing_fault['fault_type']

        return features


def calculate_health_indicator(features: Dict[str, float],
                              baseline_healthy: Dict[str, float],
                              baseline_critical: Dict[str, float],
                              weights: Optional[Dict[str, float]] = None) -> float:
    """
    Calculate normalized health indicator (0=healthy, 1=failure) from features.

    Args:
        features: Current feature values
        baseline_healthy: Feature values at healthy state
        baseline_critical: Feature values at failure state
        weights: Optional weights for each feature (defaults to equal weighting)

    Returns:
        Health indicator value (0-1)
    """

    feature_names = ['rms', 'crest_factor', 'kurtosis', 'peak']

    if weights is None:
        weights = {name: 1.0 for name in feature_names}

    # Normalize features
    feature_health = {}
    total_weight = 0

    for feature_name in feature_names:
        if feature_name not in features:
            continue

        current = features.get(f'time_{feature_name}', features.get(feature_name))
        healthy = baseline_healthy.get(feature_name, 0)
        critical = baseline_critical.get(feature_name, 1)

        if current is None or healthy is None or critical is None:
            continue

        # Normalize to 0-1 range
        if critical != healthy:
            normalized = (current - healthy) / (critical - healthy)
            normalized = np.clip(normalized, 0, 1)
        else:
            normalized = 0

        weight = weights.get(feature_name, 1.0)
        feature_health[feature_name] = normalized * weight
        total_weight += weight

    # Weighted average
    if total_weight > 0:
        health_indicator = sum(feature_health.values()) / total_weight
    else:
        health_indicator = 0.0

    return float(np.clip(health_indicator, 0, 1))


# Example usage
if __name__ == "__main__":
    # Generate synthetic vibration signal with bearing fault
    fs = 51200  # 51.2 kHz sampling rate
    duration = 10  # 10 seconds
    t = np.linspace(0, duration, int(fs * duration))

    # Normal vibration (1X running speed at 1500 RPM = 25 Hz)
    running_speed = 25  # Hz
    signal = 0.5 * np.sin(2*np.pi*running_speed*t)

    # Add bearing fault signature (BPFO harmonics)
    bearing_params = {
        'num_rolling_elements': 16,
        'ball_diameter_mm': 12.7,
        'pitch_diameter_mm': 71.5,
        'contact_angle_deg': 0
    }

    analyzer = VibrationAnalyzer(fs)
    fault_freqs = analyzer.bearing_fault_frequencies(running_speed, **bearing_params)
    bpfo = fault_freqs['BPFO']

    # Add BPFO and harmonics (indicates outer race fault)
    signal += 0.2 * np.sin(2*np.pi*bpfo*t)
    signal += 0.1 * np.sin(2*np.pi*2*bpfo*t)
    signal += 0.05 * np.sin(2*np.pi*3*bpfo*t)

    # Add noise
    signal += 0.05 * np.random.normal(0, 1, len(signal))

    analyzer.load_signal(signal)

    # Extract features
    time_feats = analyzer.time_domain_features()
    print("Time-domain features:")
    for k, v in time_feats.items():
        print(f"  {k}: {v:.4f}")

    # Bearing fault detection
    fault_result = analyzer.bearing_fault_detection(running_speed, bearing_params)
    print(f"\nBearing fault detection:")
    print(f"  Fault detected: {fault_result['fault_detected']}")
    print(f"  Fault type: {fault_result['fault_type']}")
    print(f"  Confidence: {fault_result['confidence']:.2%}")

    # Calculate health indicator
    baseline_healthy = {'rms': 0.6, 'crest_factor': 3.0, 'kurtosis': 3.0, 'peak': 2.0}
    baseline_critical = {'rms': 5.0, 'crest_factor': 10.0, 'kurtosis': 15.0, 'peak': 15.0}

    hi = calculate_health_indicator(time_feats, baseline_healthy, baseline_critical)
    print(f"\nHealth Indicator: {hi:.2f} (0=healthy, 1=failure)")
