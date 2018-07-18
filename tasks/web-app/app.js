var express = require("express");
var app     = express();
var path    = require("path");


app.get('/',function(req,res){
  res.sendFile(path.join(__dirname+'/index.html'));
});

app.listen(3000);



console.log("Running at Port 3000");


/*const http = require('http');
const url = require('url');
const fs = require('fs');

const hostname = '127.0.0.1';
const port = 3000;

const server = http.createServer((req, res) => {
	var page = url.parse(req.url).pathname;
	console.log(page);
	res.statusCode = 200;
	res.setHeader('Content-Type', 'text/html');
	if(page == '/')  {
		fs.readFile('./index.html', function (err, html) {
			if (err) {
				throw err; 
			}
		})
	}
	else {
	  res.statusCode = 404;
	  res.write('la page demandée n\'existe pas');
	}
	res.end();
	
});

server.listen(port, hostname, () => {
  console.log(`Server running at http://${hostname}:${port}/`);
});*/
