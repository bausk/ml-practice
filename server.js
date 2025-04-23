const http = require('http');

const server = http.createServer((req, res) => {
  res.writeHead(200, {'Content-Type': 'text/plain'});
  res.end('Dummy server running on port 9009\n');
});

server.listen(9009, '127.0.0.1', () => {
  console.log('Server running at http://127.0.0.1:9009/');
}); 