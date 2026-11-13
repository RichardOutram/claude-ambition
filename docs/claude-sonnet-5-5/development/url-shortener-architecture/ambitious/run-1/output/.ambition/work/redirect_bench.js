// Minimal redirect hot path: parse code, in-process Map lookup, 302. One process = one core.
// usage: node redirect_bench.js   (listens on 8099)
const http = require('http');
const cache = new Map();
for (let i = 0; i < 1_000_000; i++) cache.set('c' + i, 'https://example.com/long/path/' + i + '?utm=' + 'x'.repeat(100));
http.createServer((req, res) => {
  const url = cache.get(req.url.slice(1));
  if (url) { res.writeHead(302, { Location: url, 'Cache-Control': 'max-age=60' }); res.end(); }
  else { res.writeHead(404); res.end(); }
}).listen(8099, () => console.log('ready'));
