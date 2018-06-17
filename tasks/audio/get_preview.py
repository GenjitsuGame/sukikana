import os
from pydub import AudioSegment
import sys

def get_preview(filepath):
    return AudioSegment.from_file(filepath)[:30000]

def save_audio(audio, path, **kwargs):
    audio.export(path, **kwargs)

if __name__ == '__main__':
    args = sys.argv
    input_dir = args[1]
    output_dir = args[2]
    os.makedirs(output_dir, exist_ok=True)
    for file in os.listdir(input_dir):
        save_audio(get_preview(os.path.join(input_dir, file)), os.path.join(output_dir, 'preview_' + file), format='mp3')
