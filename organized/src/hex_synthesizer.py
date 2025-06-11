#!/usr/bin/env python3

import os
import time
import threading
import numpy as np
import subprocess
import tempfile

class HexSynthesizer:
    def __init__(self):
        self.sample_rate = 44100
        self.temp_file = 'temp_sound.wav'

    def _binary_to_note(self, binary):
        """Convert binary to frequency with focus on mid-range"""
        value = int(binary[:16], 2)
        # Map to a deep house frequency range (50-400 Hz)
        base_freq = 50 + (value % 350)
        return base_freq

    def generate_waveform(self, params, duration):
        """Generate a waveform with given parameters"""
        sample_rate = 44100
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        if params.get('waveform_type') == 'sine':
            wave = np.sin(2 * np.pi * params['frequency'] * t)
        elif params.get('waveform_type') == 'square':
            wave = np.sign(np.sin(2 * np.pi * params['frequency'] * t))
        elif params.get('waveform_type') == 'sawtooth':
            wave = 2 * (t * params['frequency'] - np.floor(0.5 + t * params['frequency']))
        elif params.get('waveform_type') == 'noise':
            wave = np.random.uniform(-1, 1, len(t))
            # Simple lowpass filter for noise
            wave = np.convolve(wave, np.ones(32)/32, mode='same')
        
        # Apply house-style envelope
        attack = int(0.05 * sample_rate)  # 50ms attack
        decay = int(0.1 * sample_rate)    # 100ms decay
        sustain_level = 0.7
        release = int(0.2 * sample_rate)  # 200ms release
        
        envelope = np.ones(len(wave))
        if len(wave) > attack:
            envelope[:attack] = np.linspace(0, 1, attack)
        if len(wave) > attack + decay:
            envelope[attack:attack+decay] = np.linspace(1, sustain_level, decay)
        if len(wave) > release:
            envelope[-release:] = np.linspace(sustain_level, 0, release)
        
        wave = wave * envelope * params['amplitude']
        
        # Soft clip for warmth
        wave = np.clip(wave * 1.2, -0.9, 0.9)
        
        return np.int16(wave * 32767)

    def play(self, wave_data):
        """Play the wave data through aplay"""
        try:
            # Save wave data to a temporary file
            with open(self.temp_file, 'wb') as f:
                # Write WAV header
                f.write(b'RIFF')
                f.write((36 + len(wave_data) * 2).to_bytes(4, 'little'))
                f.write(b'WAVE')
                f.write(b'fmt ')
                f.write((16).to_bytes(4, 'little'))
                f.write((1).to_bytes(2, 'little'))  # PCM
                f.write((1).to_bytes(2, 'little'))  # Mono
                f.write((44100).to_bytes(4, 'little'))  # Sample rate
                f.write((88200).to_bytes(4, 'little'))  # Byte rate
                f.write((2).to_bytes(2, 'little'))  # Block align
                f.write((16).to_bytes(2, 'little'))  # Bits per sample
                f.write(b'data')
                f.write((len(wave_data) * 2).to_bytes(4, 'little'))
                wave_data.tofile(f)
            
            # Play using aplay
            subprocess.run(['aplay', self.temp_file])
            
            # Clean up
            if os.path.exists(self.temp_file):
                os.remove(self.temp_file)
        except Exception as e:
            print(f"Playback error: {e}")

def play_sequence(synth, hex_strings, sequence_type='beat'):
    try:
        beat_counter = 0
        while True:
            for hex_str in hex_strings:
                binary = bin(int(hex_str, 16))[2:].zfill(256)
                intensity = sum(int(b) for b in binary[:8]) / 8.0
                
                if sequence_type == 'beat':
                    # Deep house beat pattern (4/4 time)
                    if beat_counter % 4 == 0:
                        # Deep kick
                        params = {
                            'frequency': 45,  # Deep sub bass
                            'amplitude': 0.9,
                            'waveform_type': 'sine'
                        }
                        wave = synth.generate_waveform(params, 0.25)
                        synth.play(wave)
                    
                    # Offbeat hi-hats
                    if beat_counter % 2 == 1:
                        params = {
                            'frequency': 5000,
                            'amplitude': 0.2,
                            'waveform_type': 'noise'
                        }
                        wave = synth.generate_waveform(params, 0.05)
                        synth.play(wave)
                    
                    # Clap on 2 and 4
                    if beat_counter % 4 == 2:
                        params = {
                            'frequency': 1000,
                            'amplitude': 0.4,
                            'waveform_type': 'noise'
                        }
                        wave = synth.generate_waveform(params, 0.1)
                        synth.play(wave)
                    
                    time.sleep(0.2)  # 120 BPM
                
                else:  # synth and bass
                    # Deep house bass line
                    if beat_counter % 4 == 0:
                        params = {
                            'frequency': 55,  # Bass A
                            'amplitude': 0.8,
                            'waveform_type': 'sawtooth'
                        }
                        wave = synth.generate_waveform(params, 0.3)
                        synth.play(wave)
                    
                    # Chord stabs on offbeats
                    if beat_counter % 8 == 4:
                        # Am7 chord frequencies
                        chord_freqs = [220, 261.63, 329.63, 392.00]
                        for freq in chord_freqs:
                            params = {
                                'frequency': freq,
                                'amplitude': 0.25,
                                'waveform_type': 'square'
                            }
                            wave = synth.generate_waveform(params, 0.2)
                            synth.play(wave)
                    
                    time.sleep(0.2)  # Sync with beat
                
                beat_counter = (beat_counter + 1) % 16
    
    except KeyboardInterrupt:
        return

def main():
    os.makedirs("audio_output", exist_ok=True)
    
    with open("data/32bHex.txt", 'r') as f:
        hex_strings = [line.strip() for line in f.readlines()]
    
    beat_synth = HexSynthesizer()
    bass_synth = HexSynthesizer()
    
    beat_thread = threading.Thread(target=play_sequence, args=(beat_synth, hex_strings, 'beat'))
    bass_thread = threading.Thread(target=play_sequence, args=(bass_synth, hex_strings, 'synth'))
    
    try:
        beat_thread.start()
        bass_thread.start()
        
        beat_thread.join()
        bass_thread.join()
    except KeyboardInterrupt:
        print("\nStopping sound generation...")
    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    main() 