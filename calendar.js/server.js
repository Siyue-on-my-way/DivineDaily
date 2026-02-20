/**
 * 简单的 HTTP 服务器，用于测试日历转换功能
 * 端口: 40080
 */

const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 40080;

const MIME_TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.map': 'application/json; charset=utf-8',
};

const server = http.createServer((req, res) => {
  let filePath = req.url === '/' ? '/test.html' : req.url;
  filePath = path.join(__dirname, filePath);

  // 安全检查：防止路径遍历
  if (!filePath.startsWith(__dirname)) {
    res.writeHead(403, { 'Content-Type': 'text/plain; charset=utf-8' });
    res.end('Forbidden');
    return;
  }

  const ext = path.extname(filePath);
  const contentType = MIME_TYPES[ext] || 'text/plain; charset=utf-8';

  fs.readFile(filePath, (err, data) => {
    if (err) {
      if (err.code === 'ENOENT') {
        res.writeHead(404, { 'Content-Type': 'text/html; charset=utf-8' });
        res.end(`
          <html>
            <head><title>404 - 文件未找到</title></head>
            <body>
              <h1>404 - 文件未找到</h1>
              <p>请求的文件不存在: ${req.url}</p>
              <p><a href="/">返回首页</a></p>
            </body>
          </html>
        `);
      } else {
        res.writeHead(500, { 'Content-Type': 'text/plain; charset=utf-8' });
        res.end('服务器错误: ' + err.message);
      }
    } else {
      res.writeHead(200, { 'Content-Type': contentType });
      res.end(data);
    }
  });
});

server.listen(PORT, () => {
  console.log(`
╔══════════════════════════════════════════════════════════╗
║  中国农历转换测试服务器已启动                            ║
╠══════════════════════════════════════════════════════════╣
║  访问地址: http://localhost:${PORT}                      ║
║  测试页面: http://localhost:${PORT}/test.html            ║
║  原始演示: http://localhost:${PORT}/demo.html            ║
╚══════════════════════════════════════════════════════════╝
  `);
  console.log('按 Ctrl+C 停止服务器\n');
});

