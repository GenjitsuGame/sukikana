# Audio processing

### [build_dataset.py](build_dataset.py)

_In progress..._

> Use MSD, Taste datasets and fetch 30 second audio preview to build our training data.

Requires [napster](https://developer.napster.com/developer) and [spotify](https://developer.spotify.com/) api credentials.

`python build_dataset.py limit`

- limit : amount of songs to process

###[get_preview.py](get_preview.py)

> Extract first 30 second preview from audio files.

Requires [pydub](https://github.com/jiaaro/pydub) and either [ffmpeg or libav](https://github.com/jiaaro/pydub#dependencies).

`python get_preview.py input_dir output_dir`

- `input_dir` : directory containing audio files
- `output_dir` : directory to export previews to
