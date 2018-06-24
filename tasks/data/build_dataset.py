import json

import spotipy
import pandas as pd
import numpy as np
from spotipy.oauth2 import SpotifyClientCredentials
import requests
import time
import multiprocessing
import configparser
import sys
import os
from io import StringIO
import argparse
import param_utils
import boto3


def _apply_df(args):
    df, func, kwargs = args
    return df.apply(func, **kwargs)


def apply_by_multiprocessing(df, func, **kwargs):
    workers = kwargs.pop('workers')
    pool = multiprocessing.Pool(processes=workers)
    result = pool.map(_apply_df, [(d, func, kwargs)
                                  for d in np.array_split(df, workers)])
    pool.close()
    return pd.concat(list(result))


class NapsterController():
    def __init__(self, apikey):
        self.count = 0
        self.firstTime = time.time()
        self.apikey = apikey

    def should_download(self):
        if (time.time() - self.firstTime) < 1:
            if self.count >= 499:
                return False
            else:
                self.count += 1
                return True
        else:
            self.count = 0
            self.firstTime = time.time()
            return True

    def search(self, query):
        while not self.should_download():
            pass
        try:
            res = requests.get(
                'https://api.napster.com/v2.2/search',
                params={'query': query, 'type': 'track', 'per_type_limit': 1},
                headers={'apikey': self.apikey},
                timeout=10
            ).json()
            track = res['search']['data']['tracks'][0]
            return track['id'], track['previewURL'], track['artistName'], track['name'], 'napster'
        except:
            return None, None, None, None, 'napster'


class SpotifyController:
    def __init__(self, sp):
        self.sp = sp

    def search(self, query):
        try:
            res = self.sp.search(query, type='track', limit=1)
            track = res['items'][0]
            return track['id'], track['preview_url'], track['artists'][0]['name'], track['name'], 'spotify'
        except:
            return None, None, None, None, 'spotify'


def tuples_to_df(tups):
    return pd.DataFrame(
        list(tups.values),
        columns=['preview_id', 'remote_preview_url', 'preview_artist', 'preview_title', 'preview_service'],
        index=tups.index
    )


class SearchController:
    def __init__(self, searchers, limit):
        self.searchers = searchers
        self.count = 0
        self.limit = limit

    def search(self, query):
        progress = (self.count * 100.) / self.limit
        sys.stdout.write("==== Compiling subset of data...[ {:.2f}% ] ==== \r".format(progress))
        sys.stdout.flush()
        self.count += 1
        for searcher in self.searchers:
            res = searcher.search(query)
            if res[0]:
                return res
        return None, None, None, None, None


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description='')
    arg_parser.add_argument('-c', '--config', type=str)
    arg_parser.add_argument('--start', type=int, default=0)
    arg_parser.add_argument('--limit', type=int)
    arg_parser.add_argument('--output_type', type=str, choices=['LOCAL', 'AWS'])
    arg_parser.add_argument('--msd_relevant_path')
    arg_parser.add_argument('-o', '--output', type=str)
    arg_parser.add_argument('-l', '--instance_label', type=str)
    args = vars(arg_parser.parse_args())

    config = configparser.ConfigParser()
    config_path = os.environ.get('CONFIG', args.get('config'))
    if config_path is not None:
        config.read(config_path)

    boto_session = boto3.session.Session(region_name='eu-west-3')

    paramGetter = param_utils.ParamGetter(boto_session=boto_session, config=config, args=args, env=True)

    sp_client_id = paramGetter.get('spotify_client_id')
    sp_secret = paramGetter.get('spotify_secret')
    sp = spotipy.Spotify(
        client_credentials_manager=SpotifyClientCredentials(client_id=sp_client_id, client_secret=sp_secret),
        requests_timeout=10
    )

    spotify = SpotifyController(sp)

    napster_apikey = paramGetter.get('napster_apikey')
    napster = NapsterController(napster_apikey)

    df_msd = pd.read_csv(paramGetter.get('msd_relevant_path'), sep=';')

    start = int(paramGetter.get('start', ssm=False, fallback=0))
    limit = int(paramGetter.get('LIMIT', ssm=False, fallback=df_msd.shape[0]))

    start = min(start, df_msd.shape[0])
    limit = min(start + limit, df_msd.shape[0])

    df_song = df_msd.loc[:, ['artist_name', 'title']][start:limit].apply(
        lambda row: row['artist_name'] + ' ' + row['title'], axis=1)

    search_controller = SearchController([napster, spotify], limit)

    df_msd = df_msd[start:limit].join(tuples_to_df(df_song.apply(search_controller.search)))

    output_path = paramGetter.get('full_dataset_path', ssm=False, fallback=paramGetter.get('output', ssm=False))

    if output_path is None:
        raise Exception('no output_path specified')

    output_path = output_path.format(start, limit)
    output_type = paramGetter.get('output_type', ssm=False, fallback='LOCAL')
    if output_type == 'AWS':
        buffer_df = StringIO()
        df_msd.to_csv(buffer_df, sep=';', index=False)
        boto_session \
            .resource('s3') \
            .Object(paramGetter.get('sukikana_dataset_bucket'), output_path) \
            .put(Body=buffer_df.getvalue())
    elif output_type == 'LOCAL':
        df_msd.to_csv(output_path, sep=';', index=False)

    instance_label = paramGetter.get('instance_label', ssm=False, config=False)
    instance_id = paramGetter.get('instance_id', ssm=False, config=False, args=False)
    if instance_label:
        sns = boto_session.resource('sns')
        topic = sns.Topic(paramGetter.get('sukikana_processing_topic'))
        topic.publish(MessageAttributes={
            'by': {
                'DataType': 'String',
                'StringValue': 'tag:label'
            },
            'region': {
                'DataType': 'String',
                'StringValue': 'eu-west-3'
            },
            'value': {
                'DataType': 'String',
                'StringValue': instance_label
            }
        }, Message='Build dataset done')
    elif instance_id:
        sns = boto_session.resource('sns')
        topic = sns.Topic(paramGetter.get('sukikana_processing_topic'))
        topic.publish(MessageAttributes={
            'by': {
                'DataType': 'String',
                'StringValue': 'instance-id'
            },
            'region': {
                'DataType': 'String',
                'StringValue': 'eu-west-3'
            },
            'value': {
                'DataType': 'String',
                'StringValue': instance_id
            }
        }, Message='Build dataset done')
