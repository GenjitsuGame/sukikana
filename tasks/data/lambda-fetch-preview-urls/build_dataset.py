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
import boto_utils


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


def main(event=None, context=None):
    if event is None:
        event = dict()

    config = configparser.ConfigParser()
    config_path = os.environ.get('CONFIG')
    if config_path is not None:
        config.read(config_path)

    sp_client_id = os.environ.get('SP_CLIENT_ID', config['SPOTIFY']['client_id'])
    sp_secret = os.environ.get('SP_SECRET', config['SPOTIFY']['client_secret'])
    sp = spotipy.Spotify(
        client_credentials_manager=SpotifyClientCredentials(client_id=sp_client_id, client_secret=sp_secret),
        requests_timeout=10
    )

    spotify = SpotifyController(sp)

    napster_apikey = os.environ.get('NAPSTER_APIKEY', config['NAPSTER']['apikey'])
    napster = NapsterController(napster_apikey)

    df_msd = pd.read_csv(os.environ.get('MSD_RELEVANT_URL', config['DATA']['msd_relevant_path']), sep=';')

    start = int(os.environ.get('START', event.get('start', 0)))
    limit = int(os.environ.get('LIMIT', event.get('limit', df_msd.shape[0])))

    df_song = df_msd.loc[:, ['artist_name', 'title']][start:limit].apply(
        lambda row: row['artist_name'] + ' ' + row['title'], axis=1)

    search_controller = SearchController([napster, spotify], limit)

    df_msd = df_msd[start:limit].join(tuples_to_df(df_song.apply(search_controller.search)))

    output_path = os.environ.get('FULL_DATASET_NAME', event.get('full_dataset_name', config['DATA']['full_dataset_path']))
    output_path = '{}-{}_{}'.format(start, limit, output_path)
    output_type = os.environ.get('OUTPUT_TYPE', event.get('output_type', 'LOCAL'))
    if output_type == 'AWS':
        buffer_df = StringIO()
        df_msd.to_csv(buffer_df, sep=';', index=False)
        boto_utils \
            .get_session() \
            .resource('s3') \
            .Object(os.environ.get('S3_DATASETS_BUCKET', config['AWS']['s3_datasets_bucket']), output_path) \
            .put(Body=buffer_df.getvalue())
    elif output_type == 'LOCAL':
        df_msd.to_csv(output_path, sep=';', index=False)


if __name__ == '__main__':
    main()
