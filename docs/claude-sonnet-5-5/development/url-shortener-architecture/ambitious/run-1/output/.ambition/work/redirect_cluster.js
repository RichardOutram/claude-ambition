// N worker processes sharing one port (node cluster). usage: node redirect_cluster.js <workers>
const cluster = require('cluster'), http = require('http');
const W = parseInt(process.argv[2] || '2');
if (cluster.isPrimary) { for (let i = 0; i < W; i++) cluster.fork(); console.log('ready'); }
else {
  const cache = new Map();
  for (let i = 0; i < 200_000; i++) cache.set('c' + i, 'https://example.com/long/path/' + i + '?utm=' + 'x'.repeat(100));
  http.createServer((req, res) => {
    const u = cache.get(req.url.slice(1));
    if (u) { res.writeHead(302, { Location: u, 'Cache-Control': 'max-age=60' }); res.end(); } else { res.writeHead(404); res.end(); }
  }).listen(8098);
}
