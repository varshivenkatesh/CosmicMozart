"""
Conversion of frequencies to a song using WAV files of piano notes Created by @MAXIMUSSCORP (Mohammmad Zaid Khan)
"""
import numpy as np
import scipy.io.wavfile as wavfile
import os

# Define the standard piano note frequencies (A0 to C8)
A4_freq = 440.0
piano_frequencies = [A4_freq * (2 ** ((n - 49) / 12)) for n in range(1, 89)]  # 88 keys
note_names = [
    'A0', 'Bb0', 'B0', 'C1', 'Db1', 'D1', 'Eb1', 'E1', 'F1', 'Gb1', 'G1', 'Ab1',
    'A1', 'Bb1', 'B1', 'C2', 'Db2', 'D2', 'Eb2', 'E2', 'F2', 'Gb2', 'G2', 'Ab2',
    'A2', 'Bb2', 'B2', 'C3', 'Db3', 'D3', 'Eb3', 'E3', 'F3', 'Gb3', 'G3', 'Ab3',
    'A3', 'Bb3', 'B3', 'C4', 'Db4', 'D4', 'Eb4', 'E4', 'F4', 'Gb4', 'G4', 'Ab4',
    'A4', 'Bb4', 'B4', 'C5', 'Db5', 'D5', 'Eb5', 'E5', 'F5', 'Gb5', 'G5', 'Ab5',
    'A5', 'Bb5', 'B5', 'C6', 'Db6', 'D6', 'Eb6', 'E6', 'F6', 'Gb6', 'G6', 'Ab6',
    'A6', 'Bb6', 'B6', 'C7', 'Db7', 'D7', 'Eb7', 'E7', 'F7', 'Gb7', 'G7', 'Ab7',
    'A7', 'Bb7', 'B7', 'C8'
]

# Array of frequencies to be converted to a song
with open("frequencies.txt") as f:
    input_frequencies = f.readlines()
    input_frequencies = [float(x.strip()) for x in input_frequencies]

# Folder where WAV files for each note are stored (with 'b' for sharps)
wav_folder = "notes_online/"

# Function to find the closest piano note frequency
def closest_piano_note_frequency(freq):
    closest_freq_index = np.argmin([abs(f - freq) for f in piano_frequencies])
    return piano_frequencies[closest_freq_index], note_names[closest_freq_index]

# Function to convert stereo to mono by averaging the channels
def stereo_to_mono(wav_data):
    if len(wav_data.shape) == 2:  # If stereo (2 channels)
        wav_data = np.mean(wav_data, axis=1).astype(wav_data.dtype)  # Average both channels
    return wav_data
notes = []
# Function to create a song by concatenating WAV files
def create_song_from_wav(frequency_array, output_filename):
    combined_wave = np.array([])
    sample_rate = None


    for freq in frequency_array:
        closest_freq, note_name = closest_piano_note_frequency(freq)
        if closest_freq is None:
            continue
        print(f"Input frequency: {freq:.2f} Hz, Closest piano note: {note_name} ({closest_freq:.2f} Hz)")


        wav_file_path = os.path.join(wav_folder, f"{note_name}.wav")
        notes.append(note_name)
        if not os.path.exists(wav_file_path):
            print(f"Warning: WAV file for {note_name} not found.")
            continue


        sr, wav_data = wavfile.read(wav_file_path)
        wav_data = stereo_to_mono(wav_data)

        if sample_rate is None:
            sample_rate = sr

        combined_wave = np.concatenate((combined_wave, wav_data))


    combined_wave = np.int16(combined_wave)
    wavfile.write(output_filename, sample_rate, combined_wave)
    print(f"Song saved as '{output_filename}'")

# Array of arbitrary frequencies
create_song_from_wav(input_frequencies, "song_from_wav_files.wav")
print(notes)
