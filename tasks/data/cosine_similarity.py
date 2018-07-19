import sklearn.metrics as metrics
import pandas as pd
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

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description='')
    arg_parser.add_argument('-i', '--input', type=str)
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

    df = pd.read_csv(paramGetter.get('input'), index_col='song_id', sep=';')


    start = int(paramGetter.get('start', ssm=False, fallback=0))
    limit = int(paramGetter.get('limit', ssm=False, fallback=df.shape[0]))

    start = min(start, df.shape[0])
    limit = min(start + limit, df.shape[0])

    cosines = metrics.pairwise.cosine_similarity(df.iloc[start:limit].values, df.values)

    # s3 = boto_session.resource('s3')
    # sukikana_bucket = paramGetter.get('s3_previews_bucket', fallback='sukikana')

