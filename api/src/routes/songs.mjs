import express from 'express';
import Check from 'express-validator/check';
import Filter from 'express-validator/filter';
import { Song } from '../models/index';
import HttpError from 'http-errors';

const router = express.Router();

const { matchedData } = Filter;
const { validationResult, body } = Check;


router
  .route('/')
  .post([
    body('msdId')
      .exists(),
    body('title')
      .exists(),
    body('artist')
      .exists(),
    body('latents')
      .isArray()
  ], (req, res, next) => {
    (async () => {
      const errors = validationResult(req);
      if (!errors.isEmpty()) {
        throw new HttpError.BadRequest({ errors: errors.mapped() });
      }

      let song = matchedData(req);

      if (await Song.findOne({msdId: song.msdId})) {
        throw new HttpError.BadRequest('Song already exist');
      }

      song = await Song.create(song);

      return res.status(201).json(song);
    })().catch(next);
  });

export default router;
