import config from 'config';
import http from 'http';
import express from 'express';
import restify from 'express-restify-mongoose';
import morgan from 'morgan';
import addRequestId from 'express-request-id';
import bodyParser from 'body-parser';
import compress from 'compression';
import cors from 'cors';
import helmet from 'helmet';
import HttpError from 'http-errors';
import { Song } from './models/index';

const app = express()

morgan.token('id', req => req.id);
morgan.token('body', req => req.method === 'POST' ? JSON.stringify(req.body) : '');

app.disable('etag');
app.use(morgan(":id :remote-addr - :remote-user [:date[clf]] \":method :url HTTP/:http-version\" :status :res[content-length] \":referrer\" \":user-agent\""));

app.use(bodyParser.urlencoded({ limit: '50mb', extended: false }));
app.use(bodyParser.json({limit:1024102420, type:'application/json'}));
app.use(cors());
app.use(helmet());
app.use(compress());
app.use(addRequestId());

//app.use('/songs', Songs);

const restifyRouter = express.Router();

restify.serve(restifyRouter, Song, { name: 'songs', lean: true, limit: 50 });

app.use(restifyRouter);

app.use((err, req, res, next) => {
  console.log(err);
  if (!err.expose) {
    if (!(err instanceof HttpError.HttpError)) {
      err = new HttpError.InternalServerError();
    }
  }
  res.status(err.status).json(err);
});

const port = process.env.PORT || config.port;
const server = http.createServer(app);
server.listen(port);
console.log('listening on port ' + port);