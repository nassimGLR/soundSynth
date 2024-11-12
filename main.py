from flask import Flask, jsonify, request
from pydub import AudioSegment
import numpy as np
import os

app = Flask(__name__)

def process_mp3_to_json(file_path, sample_rate=10):
    """Processes an MP3 file to extract amplitude data at regular intervals."""
    audio = AudioSegment.from_file(file_path, format="mp3")

    # Convert to mono and get raw samples
    audio = audio.set_channels(1)
    samples = np.array(audio.get_array_of_samples())

    # Sample at regular intervals to reduce the data size
    sample_points = np.linspace(0, len(samples), int(len(samples) / sample_rate), endpoint=False, dtype=int)
    sample_data = samples[sample_points]

    # Normalize the amplitude values and convert them to JSON-compatible data
    max_amp = np.max(np.abs(sample_data))
    sound_data = [
        {
            "time": i / (1000 / sample_rate),  # time in seconds
            "volume": float(np.abs(sample) / max_amp),  # normalized volume (0 to 1)
            "pitch": 1.0  # Static pitch (you could expand this with further processing)
        }
        for i, sample in enumerate(sample_data)
    ]

    return sound_data

@app.route('/upload-mp3', methods=['POST'])
def upload_mp3():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    file_path = os.path.join("uploads", file.filename)
    file.save(file_path)

    # Process the MP3 file to extract sound data
    sound_data = process_mp3_to_json(file_path)
    
    # Clean up uploaded file after processing
    os.remove(file_path)

    return jsonify(sound_data)

if __name__ == '__main__':
    # Create uploads directory if it doesn't exist
    os.makedirs("uploads", exist_ok=True)
    app.run(debug=True)
