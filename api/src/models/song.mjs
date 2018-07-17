import config from 'config';
import mongoose from 'mongoose';
import elasticsearch from './elasticsearch';

const songSchema = new mongoose.Schema({
  msdId: { type: String, unique: true, sparse: true, index: true },
  title: String,
  artist: String,
  latents: [Number],
  lastfmId: { type: String, unique: true, sparse: true },
  mels: [Number],
  nComponents: Number
});

songSchema.post('save', async song => {
  try {
    await elasticsearch.index({
      index: config.elasticsearch.index,
      type: 'songs',
      id: song._id.toString(),
      body: {
        title: song.title,
        artist: song.artist,
        msdId: song.msdId
      }
    });
  } catch (e) {
    console.log(e);
  }
});

export default mongoose.model('Song', songSchema)