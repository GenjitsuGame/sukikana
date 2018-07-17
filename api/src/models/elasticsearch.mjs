import config from 'config';
import Elasticsearch from 'elasticsearch';

export default new Elasticsearch.Client({
  host: config.elasticsearch.host,
  pingTimeout: 30000,
  maxRetries: 5,
  log: function (config) {
    this.error = console.log.bind(console);
    this.warning = console.log.bind(console);
    this.info = console.log.bind(console);
    this.debug = console.log.bind(console);
    this.trace = (method, requestUrl, body, responseBody, responseStatus) => {
      console.log({
        method,
        requestUrl,
        body,
        responseBody,
        responseStatus
      })
    };
    this.close = function () {
    };
  }
});

