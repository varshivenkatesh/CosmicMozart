"""
This script generates a WAV file based on the pixel intensities of an image.
Algorithm created by @Varshiiii (Varshitha Venkatesh) from the .ipynb file
"""
from flask import Flask, render_template, request, send_file, url_for
import os
from werkzeug.utils import secure_filename
import cv2
import numpy as np
from scipy.io.wavfile import write

# Initialize the Flask app
app = Flask(__name__)

# Define the upload folder
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp'}

def allowed_file(filename):
    """
    Check if the file has a valid extension.

    Args:
        filename (str): The name of the file to check.

    Returns:
        bool: True if the file has an allowed extension, False otherwise.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """
    Render the index page.

    Returns:
        str: The rendered HTML of the index page.
    """
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """
    Handle file upload and process the image to generate a WAV file.

    Returns:
        str: The rendered HTML of the index page with the WAV file URL.
    """
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Process the image and generate the wav file
        wav_filepath = process_image_to_wav(filepath)

        # Send the WAV file as a downloadable file
        wav_url = url_for('static', filename=f'uploads/{os.path.basename(wav_filepath)}')
        return render_template('index.html', wav_url=wav_url)

def process_image_to_wav(image_path):
    """
    Process the uploaded image and generate a WAV file based on the image's pixel intensities.

    Args:
        image_path (str): The path to the uploaded image.

    Returns:
        str: The path to the generated WAV file.
    """
    # Load the image
    img = cv2.resize(cv2.imread(image_path), (250, 250))

    if img is None:
        raise ValueError("Image not found or unable to load the image.")

    # Get image dimensions and convert to grayscale
    image_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    height, width = image_gray.shape

    # Frequency settings
    fbase = 600
    fmax = 1000
    f_array = []
    freq_array = []

    # Calculate frequencies based on image intensities
    for x in range(min(width, 250)):
        max_intensity = 0
        for y in range(min(height, 250)):
            intensity = image_gray[y, x]
            if intensity > max_intensity:
                max_intensity = intensity

        f = fbase + (max_intensity / 255) * (fmax - fbase)
        f_array.append(f)

    for i in range(0, len(f_array), 2):
        if i+1 < len(f_array):
            new_freq = np.min([f_array[i], f_array[i+1]])
            freq_array.append(new_freq)
        else:
            freq_array.append(f_array[i])
    print(len(freq_array))
    print(freq_array)

    with open('frequencies.txt', 'w') as f:
        for item in freq_array:
            f.write("%s\n" % item)

    def generate_sine_wave(frequency, duration, sample_rate=44100):
        """
        Generate a sine wave for a given frequency and duration.

        Args:
            frequency (float): The frequency of the sine wave.
            duration (float): The duration of the sine wave in seconds.
            sample_rate (int, optional): The sample rate. Defaults to 44100.

        Returns:
            np.ndarray: The generated sine wave.
        """
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        tone = np.sin(2 * np.pi * frequency * t)
        return tone

    total_duration = 20
    duration_wave_1 = total_duration / len(freq_array)

    # Harmonics
    num_harmonics = 3
    harmonic_amplitude_scale = 0.5

    combined_wave = np.array([])

    for frequency in freq_array:
        frequency /= 3

        sine_wave_1 = generate_sine_wave(frequency, duration_wave_1)

        for harmonic in range(2, num_harmonics + 1):
            harmonic_freq = frequency * harmonic
            sine_wave_1 += harmonic_amplitude_scale * generate_sine_wave(harmonic_freq, duration_wave_1)

        combined_wave = np.concatenate((combined_wave, sine_wave_1))

    # Normalize
    combined_wave /= np.max(np.abs(combined_wave))

    def wave_shaper(combined_wave):
        """
        Apply a wave shaping function to the combined wave.

        Args:
            combined_wave (np.ndarray): The combined wave to shape.

        Returns:
            np.ndarray: The shaped wave.
        """
        shaped_wave = np.tanh(combined_wave * 5)  # Soft clipping using a tanh function
        return shaped_wave

    shaped_wave = wave_shaper(combined_wave)

    # Save the generated sound as a .wav file
    wav_filename = os.path.splitext(os.path.basename(image_path))[0] + ".wav"
    wav_filepath = os.path.join(app.config['UPLOAD_FOLDER'], wav_filename)
    write(wav_filepath, 44100,  (shaped_wave * 32767).astype(np.int16))

    return wav_filepath

if __name__ == '__main__':
    app.run(debug=True)