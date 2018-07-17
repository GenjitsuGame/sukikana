import mongoose from 'mongoose';

const songSchema = new mongoose.Schema({
  msdId: { type: String, unique: true, sparse: true, index: true},
  title: String,
  artist: String,
  latents: [Number],
  lastfmId: { type: String, unique: true, sparse: true },
  mels: [Number],
  nComponents: Number
});

export default mongoose.model('Song', songSchema)