import spotipy
import pandas as pd
import numpy as np
from spotipy.oauth2 import SpotifyClientCredentials
import requests
import time
import multiprocessing
import configparser
import os


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


class NapsterRateController():
    def __init__(self):
        self.count = 0
        self.firstTime = time.time()

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


n = NapsterRateController()
i = 0


def napster_search(query):
    while (not n.should_download()):
        pass
    res = requests.get(
        'https://api.napster.com/v2.2/search',
        params={'query': query, 'type': 'track', 'per_type_limit': 1},
        headers={'apikey': 'MGMwM2NmOGEtZjJmYi00MzU3LThhM2MtMjkyNzViYzVjNWNm'}
    ).json()
    try:
        track = res['search']['data']['tracks'][0]
        return track['id'], track['previewURL'], track['artistName'], track['name'], 'napster'
    except:
        return None, None, None, None, 'napster'


sp = spotipy.Spotify(
    client_credentials_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))


def spotify_search(query):
    res = sp.search(query, type='track', limit=1)
    if not res['total']:
        return None, None, None, None, 'spotify'
    track = res['items'][0]
    return track['id'], track['preview_url'], track['artists'][0]['name'], track['name'], 'spotify'


def tuples_to_df(tups):
    return pd.DataFrame(
        list(tups.values),
        columns=['preview_id', 'remote_preview_url', 'preview_artist', 'preview_title', 'preview_service']
    )


def merge_service_df(df1, df2):
    df1


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('../../config.ini')

    data_config = config['DATA']

    df_taste = pd.read_csv(data_config['taste_path'], sep='\t', names=['user_id', 'song_id', 'play_count'])
    df_msd = pd.read_csv(data_config['msd_path'], sep=',', index_col=0)
    df_msd = df_msd[df_msd.song_id.isin(df_taste.song_id)]
    df_msd = df_msd[~df_msd.title.isna()]

    df_napster = apply_by_multiprocessing(
        df_msd
            .loc[:, ['artist_name', 'title']]
            .apply(lambda row: row['artist_name'] + ' ' + row['title'], axis=1),
        napster_search,
        workers=14
    )

    df_napster.to_csv('napster.csv', sep=';')
