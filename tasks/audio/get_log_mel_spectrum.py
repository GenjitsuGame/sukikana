import boto3
import numpy as np
from tempfile import  NamedTemporaryFile
from librosa.feature import melspectrogram
import librosa

boto_session = boto3.session.Session(region_name='eu-west-3')
s3 = boto_session.resource('s3')
sukikana_bucket = 'sukikana'


def get_logmels(song_id):
    with NamedTemporaryFile('wb+') as download_file:
        s3.Object(sukikana_bucket, song_id).download_fileobj(download_file)
        download_file.seek(0)
        offset = 0  # np.random.randint(26 * 1000) / 1000.0
        duration = 3.0
        y, sr = librosa.load(download_file.name, offset=offset, duration=duration)
        return np.log10(melspectrogram(y=y, sr=sr, n_fft=1024, hop_length=512, power=2))


if __name__ == '__main__':
    song_id = 'SOAAAKE12A8C1397E9'
    feature_sequence = get_logmels(song_id)
