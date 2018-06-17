# SUKIKANA

Content based music recommendation system

## Configuration

Copy the [sample configuration file](config.example.ini) at the root of the repository :

`cp config.example.ini config.ini`

and edit it with your own settings.

## Project structure

### [msdvis](msdvis)

Repository (submodule) allowing to easily manipulate the Million Song Dataset and building a `csv` out of it.
(`hdf5` -> `csv`)

### [tasks](tasks)

Python scripts to perform various tasks related to the project


## Resources :

### Papers
- [Aaron van den Oord, Sander Dieleman, Benjamin Schrauwen. Deep content-based music recommendation](https://papers.nips.cc/paper/5004-deep-content-based-music-recommendation.pdf)
- [Yifan Hu, Yehuda Koren, Chris Volinsky. Collaborative Filtering for Implicit Feedback Datasets](http://yifanhu.net/PUB/cf.pdf)

### Tutorial
- [Mel Frequency Cepstral Coefficient (MFCC) tutorial](http://practicalcryptography.com/miscellaneous/machine-learning/guide-mel-frequency-cepstral-coefficients-mfccs/)