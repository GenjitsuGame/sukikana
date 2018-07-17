import boto3
import botocore
import param_utils
import configparser
import os
import pandas as pd
import argparse
from tempfile import  NamedTemporaryFile
from librosa.feature import melspectrogram
import librosa
import numpy as np
import requests
import json

def get_logmels(s3, song_id):
    with NamedTemporaryFile('wb+') as download_file:
        s3.Object(sukikana_bucket, song_id).download_fileobj(download_file)
        download_file.seek(0)
        offset = 0
        y, sr = librosa.load(download_file.name, offset=offset, sr=22050)
        mels = melspectrogram(y=y, sr=sr, n_fft=1024, hop_length=512, power=2)
        min_mel = np.min(mels[np.where(mels != 0)])
        mels[np.where(mels == 0)] = min_mel / 10
        return np.log10(mels)

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description='')
    arg_parser.add_argument('--meta', type=str)
    arg_parser.add_argument('--latent', type=str)
    arg_parser.add_argument('--start', type=int, default=0)
    arg_parser.add_argument('--limit', type=int)
    arg_parser.add_argument('-b, --s3_previews_bucket', type=str)
    arg_parser.add_argument('--check', action='store_true')
    arg_parser.add_argument('-c', '--config', type=str)
    arg_parser.add_argument('--host', type=str)
    args = vars(arg_parser.parse_args())

    config = configparser.ConfigParser()
    config_path = os.environ.get('CONFIG', args.get('config'))
    if config_path is not None:
        config.read(config_path)

    boto_session = boto3.session.Session(region_name='eu-west-3')

    paramGetter = param_utils.ParamGetter(boto_session=boto_session, config=config, args=args, env=True)

    api = 'http://{}/api/v1/songs'.format(paramGetter.get('host'))

    df_meta = pd.read_csv(paramGetter.get('meta'), index_col='song_id', sep=';')
    df_latent = pd.read_csv(paramGetter.get('latent'), index_col='song_id', sep=';')

    start = int(paramGetter.get('start', ssm=False, fallback=0))
    limit = int(paramGetter.get('limit', ssm=False, fallback=df_meta.shape[0]))

    start = min(start, df_meta.shape[0])
    limit = min(start + limit, df_meta.shape[0])

    s3 = boto_session.resource('s3')
    sukikana_bucket = paramGetter.get('s3_previews_bucket', fallback='sukikana')

    i = 0
    for song_id, record in df_meta.iloc[start:limit].iterrows():
        print(i)
        i += 1
        try:
            req_get = requests.get(api, params={'query': json.dumps({'msdId': song_id})}, timeout=5)
            req_get.raise_for_status()
            res_get = req_get.json()
            print(res_get)
            if len(res_get) != 0:
                print('already indexed {}'.format(song_id))
            else:
                mels = get_logmels(s3, song_id)
                data = {
                    'msdId': song_id,
                    'artist': record['artist_name'],
                    'title': record['title'],
                    'latents': df_latent.loc[song_id].values.tolist(),
                    'mels': mels.reshape(-1).tolist(),
                    'nComponents': mels.shape[0]
                }
                req_post = requests.post(api, json=data)
                req_post.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(e)
            print('error on {}'.format(song_id))
        except ValueError as e:
            print(e)
            print('error on {}'.format(song_id))