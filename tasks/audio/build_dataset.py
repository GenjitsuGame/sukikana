import spotipy
import pandas as pd
import numpy as np
from spotipy.oauth2 import SpotifyClientCredentials
import requests
import time
import multiprocessing
import configparser
import sys


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
        res = requests.get(
            'https://api.napster.com/v2.2/search',
            params={'query': query, 'type': 'track', 'per_type_limit': 1},
            headers={'apikey': self.apikey}
        ).json()
        try:
            track = res['search']['data']['tracks'][0]
            return track['id'], track['previewURL'], track['artistName'], track['name'], 'napster'
        except:
            return None, None, None, None, 'napster'


class SpotifyController:
    def __init__(self, sp):
        self.sp = sp

    def search(self, query):
        res = self.sp.search(query, type='track', limit=1)
        try:
            track = res['items'][0]
            return track['id'], track['preview_url'], track['artists'][0]['name'], track['name'], 'spotify'
        except:
            return None, None, None, None, 'spotify'


def tuples_to_df(tups):
    return pd.DataFrame(
        list(tups.values),
        columns=['preview_id', 'remote_preview_url', 'preview_artist', 'preview_title', 'preview_service']
    )


class SearchController:
    def __init__(self, searchers):
        self.searchers = searchers

    def search(self, query):
        for searcher in self.searchers:
            res = searcher.search(query)
            if res[0]:
                return res
        return None, None, None, None, None

def merge_service_df(df1, df2):
    df1


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('../../config.ini')

    data_config = config['DATA']

    sp_config = config['SPOTIFY']
    sp = spotipy.Spotify(
        client_credentials_manager=SpotifyClientCredentials(client_id=sp_config['client_id'], client_secret=sp_config['client_secret']))
    spotify = SpotifyController(sp)

    napster_config = config['NAPSTER']
    napster = NapsterController(napster_config['apikey'])

    search_controller = SearchController([napster, spotify])

    df_taste = pd.read_csv(data_config['taste_path'], sep='\t', names=['user_id', 'song_id', 'play_count'])
    df_msd = pd.read_csv(data_config['msd_path'], sep=',', index_col=0)
    df_msd = df_msd[df_msd.song_id.isin(df_taste.song_id)]
    df_msd = df_msd[~df_msd.title.isna()]

    limit = df_msd.shape[0]
    if sys.argv[1]:
        limit = int(sys.argv[1])

    df_song = df_msd.loc[:, ['artist_name', 'title']][:limit].apply(lambda row: row['artist_name'] + ' ' + row['title'], axis=1)

    df_full = apply_by_multiprocessing(
        df_song,
        search_controller.search,
        workers=14
    )

    df_full.to_csv('napster.csv', sep=';')
