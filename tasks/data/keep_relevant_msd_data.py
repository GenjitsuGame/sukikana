import pandas as pd
import configparser
import os

if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read(os.environ['CONFIG'])

    df_taste = pd.read_csv(os.environ.get('TASTE_URL', config['DATA']['taste_path']), sep='\t',
                           names=['user_id', 'song_id', 'play_count'])
    df_msd = pd.read_csv(os.environ.get('FULL_MSD_URL', config['DATA']['msd_path']), sep=';')
    df_msd = df_msd[df_msd.song_id.isin(df_taste.song_id)]
    df_msd = df_msd[~df_msd.title.isna()]

    df_msd.to_csv(os.environ.get('RELEVANT_MSD_URL', config['DATA']['msd_relevant_path']), sep=';', index=False)
