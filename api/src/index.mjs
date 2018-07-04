import config from 'config';
import http from 'http';
import express from 'express';
import morgan from 'morgan';
import addRequestId from 'express-request-id';
import compress from 'compression';
import cors from 'cors';
import helmet from 'helmet';
import HttpError from 'http-errors';

const app = express()

app.disable('etag');
app.use(morgan(
  ":id :remote-addr - :remote-user [:date[clf]] \":method :url HTTP/:http-version\" :status :body :res[content-length] \":referrer\" \":user-agent\"",
  { "stream": { write: message => console.log(message) } })
);
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: false }));
app.use(cors());
app.use(helmet());
app.use(compress());
app.use(addRequestId());

app.use((err, req, res, next) => {
  if (!err.expose) {
    if (!(err instanceof HttpError.HttpError)) {
      err = new HttpError.InternalServerError();
    }
  }
  res.status(err.status).json(err);
});

port = config.port;
const server = http.createServer(app);
server.listen(port);
console.log('listening on port ' + port);