import pandas as pd
import configparser
import os

if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read(os.environ['CONFIG'])

    df_taste = pd.read_csv(os.environ.get('TASTE_URL', config['DATA']['taste_path']), sep='\t',
                           names=['user_id', 'song_id', 'play_count'])
    df_msd = pd.read_csv(os.environ.get('RELEVANT_MSD_URL', config['DATA']['msd_relevant_path']), sep=';')

    limit = int(os.environ.get('LIMIT', df_msd.shape[0]))

    df_taste_msd = df_taste.merge(df_msd[:limit], left_on='song_id', right_on='song_id', how='inner')

    df_taste_msd.to_csv(os.environ.get('FULL_TASTE_URL', config['DATA']['full_taste_path']), sep=';')
