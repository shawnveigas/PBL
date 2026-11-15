import os
import argparse
import numpy as np
from pydub import AudioSegment

def mp3_to_pwl(mp3_path, pwl_output_path, duration_sec=1.0, target_sr=44100, peak_voltage=1.0):
    """Converts an MP3 file into a SPICE-compatible PWL text file."""
    if not os.path.exists(mp3_path):
        raise FileNotFoundError(f"Input file not found: {mp3_path}")

    print(f"[+] Loading audio file: {mp3_path}")
    audio = AudioSegment.from_file(mp3_path)

    # 1. Convert stereo to mono
    audio = audio.set_channels(1)

    # 2. Clip duration to avoid SPICE simulation slowdowns
    max_ms = int(duration_sec * 1000)
    audio = audio[:max_ms]

    # 3. Resample to target sampling rate
    audio = audio.set_frame_rate(target_sr)

    # Extract raw samples as normalized floating-point numpy array
    samples = np.array(audio.get_array_of_samples(), dtype=np.float64)
    max_int = float(1 << (8 * audio.sample_width - 1))
    samples = samples / max_int

    # 4. Normalize and scale peak voltage
    current_peak = np.max(np.abs(samples))
    if current_peak > 0:
        samples = (samples / current_peak) * peak_voltage

    # 5. Generate time array and format space-delimited time/voltage pairs
    time_array = np.linspace(0.0, len(samples) / target_sr, num=len(samples), endpoint=False)

    print(f"[+] Writing PWL file: {pwl_output_path} ({len(samples)} points)")
    with open(pwl_output_path, 'w') as f:
        for t, v in zip(time_array, samples):
            f.write(f"{t:.8e} {v:.8e}\n")

    print("[+] PWL conversion complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert MP3 audio to SPICE PWL format.")
    parser.add_argument("-i", "--input", required=True, help="Path to input MP3 file")
    parser.add_argument("-o", "--output", default="audio_input.pwl", help="Path for output PWL file")
    parser.add_argument("-d", "--duration", type=float, default=1.0, help="Duration in seconds (default: 1.0)")
    parser.add_argument("-r", "--rate", type=int, default=44100, help="Target sample rate in Hz (default: 44100)")
    parser.add_argument("-v", "--voltage", type=float, default=1.0, help="Peak voltage scaling in Volts (default: 1.0)")
    args = parser.parse_args()

    mp3_to_pwl(args.input, args.output, args.duration, args.rate, args.voltage)