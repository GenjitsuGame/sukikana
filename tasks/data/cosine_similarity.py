import sklearn.metrics as metrics
import pandas as pd

df = pd.read_csv("./song_factors.csv", delimiter=";")
df = df.loc[:, df.columns != 'song_id']
cosine = metrics.pairwise.cosine_similarity(df.T,df.T)

