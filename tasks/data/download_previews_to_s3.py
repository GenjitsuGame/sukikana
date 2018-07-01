import boto3
import botocore
import param_utils
import configparser
import os
import pandas as pd
import argparse

import requests

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description='')
    arg_parser.add_argument('-i', '--input', type=str)
    arg_parser.add_argument('--start', type=int, default=0)
    arg_parser.add_argument('--limit', type=int)
    arg_parser.add_argument('-b, --s3_previews_bucket', type=str)
    arg_parser.add_argument('-c', '--config', type=str)
    args = vars(arg_parser.parse_args())

    config = configparser.ConfigParser()
    config_path = os.environ.get('CONFIG', args.get('config'))
    if config_path is not None:
        config.read(config_path)

    boto_session = boto3.session.Session(region_name='eu-west-3')

    paramGetter = param_utils.ParamGetter(boto_session=boto_session, config=config, args=args, env=True)

    df = pd.read_csv(paramGetter.get('input'), sep=';', usecols=['song_id', 'remote_preview_url'])
    df = df[~df.remote_preview_url.isna()]

    start = int(paramGetter.get('start', ssm=False, fallback=0))
    limit = int(paramGetter.get('limit', ssm=False, fallback=df.shape[0]))

    start = min(start, df.shape[0])
    limit = min(start + limit, df.shape[0])

    s3 = boto_session.resource('s3')
    sukikana_bucket = paramGetter.get('s3_previews_bucket', fallback='sukikana')
    for row in df.iloc[start:limit].itertuples():
        song_id = getattr(row, 'song_id')
        preview_url = getattr(row, 'remote_preview_url')
        try:
            s3.Object(sukikana_bucket, song_id).load()
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                # The object does not exist.
                res = requests.get(preview_url)
                if res.status_code == 200:
                    s3 \
                        .Object(sukikana_bucket, song_id) \
                        .put(Body=res.content, StorageClass='STANDARD_IA', ACL='private')
