import config from 'config';
import mongoose from 'mongoose';
import Song from './song.mjs';

mongoose.connect(`mongodb://${config.mongo.host}:${config.mongo.port}/${config.mongo.database}`, { useNewUrlParser: true });

process.on('SIGINT', function() {
  mongoose.connection.close(function () {
    console.log('Mongoose default connection disconnected through app termination');
    process.exit(0);
  });
});

export {
  Song
};
