const http = require('http');

const PORT = 5000;

const server = http.createServer((req, res) => {
    // Set standard JSON headers
    res.setHeader('Content-Type', 'application/json');
    res.setHeader('Access-Control-Allow-Origin', '*');

    if (req.url === '/api/v1/verify' && (req.method === 'GET' || req.method === 'POST')) {
        res.writeHead(200);
        res.end(JSON.stringify({
            status: "authorized",
            gateway_secure: true,
            node: "Secure B2B Ingestion Node",
            msg: "Lagos Secure Identity Verification Module Active (Native Engine)"
        }));
    } else if (req.url === '/health') {
        res.writeHead(200);
        res.end(JSON.stringify({ status: "online" }));
    } else {
        res.writeHead(404);
        res.end(JSON.stringify({ error: "Not Found" }));
    }
});

server.listen(PORT, '0.0.0.0', () => {
    console.log(`[+] Initializing Secure B2B Ingestion Node on Port ${PORT}...`);
});
