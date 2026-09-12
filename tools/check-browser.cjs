#!/usr/bin/env node
/* Optional runner for an existing Node + puppeteer-core + Chromium installation. */
'use strict';
const fs = require('node:fs'), path = require('node:path'), http = require('node:http');
const { parseArgs } = require('node:util');

async function main() {
  const { values, positionals } = parseArgs({ allowPositionals: true, options: {
    browser: { type: 'string' }, module: { type: 'string' }, root: { type: 'string' },
    output: { type: 'string' }, screenshots: { type: 'string' }, 'no-sandbox': { type: 'boolean', default: false },
    help: { type: 'boolean', default: false }
  }});
  if (values.help || positionals.length !== 1) {
    console.log('node tools/check-browser.cjs deck.html --browser /path/to/chrome [--root assets-base] [--module puppeteer-core-path] [--output report.json] [--screenshots directory] [--no-sandbox]');
    return values.help ? 0 : 2;
  }
  const file = fs.realpathSync(positionals[0]), root = fs.realpathSync(values.root || path.dirname(file));
  if (!values.browser) throw new Error('--browser is required (use an existing Chromium executable).');
  const puppeteer = require(values.module || 'puppeteer-core');
  const types = { '.html': 'text/html; charset=utf-8', '.css': 'text/css', '.svg': 'image/svg+xml', '.woff': 'font/woff', '.png': 'image/png', '.jpg': 'image/jpeg', '.js': 'text/javascript' };
  const server = http.createServer((req, res) => {
    try {
      const url = new URL(req.url, 'http://localhost');
      const name = decodeURIComponent(url.pathname);
      const resource = name === '/index.html' ? file : fs.realpathSync(path.resolve(root, '.' + name));
      if (resource !== file && (path.relative(root, resource).startsWith('..' + path.sep) || path.relative(root, resource) === '..' || path.isAbsolute(path.relative(root, resource)))) {
        res.writeHead(403).end(); return;
      }
      const data = fs.readFileSync(resource);
      res.writeHead(200, { 'Content-Type': types[path.extname(resource)] || 'application/octet-stream' }); res.end(data);
    } catch { res.writeHead(404).end(); }
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  let browser;
  try {
    browser = await puppeteer.launch({ executablePath: values.browser, headless: true, args: values['no-sandbox'] ? ['--no-sandbox'] : [] });
    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 720 });
    await page.goto(`http://127.0.0.1:${server.address().port}/index.html`, { waitUntil: 'networkidle0', timeout: 60000 });
    await page.addScriptTag({ path: path.join(__dirname, 'check-rendered.js') });
    const report = await page.evaluate(() => window.aizomeCheck());
    if (values.screenshots) {
      fs.mkdirSync(values.screenshots, { recursive: true });
      // Hide presentation controls in screenshots only, not during measurements.
      await page.addStyleTag({ content: '.bespoke-marp-osc { display: none !important; }' });
      for (let n = 1; n <= report.slides; n++) {
        await page.evaluate(n => { location.hash = String(n); }, n);
        await new Promise(resolve => setTimeout(resolve, 80));
        await page.screenshot({ path: path.join(values.screenshots, `slide-${String(n).padStart(3, '0')}.png`) });
      }
    }
    const json = JSON.stringify(report, null, 2) + '\n';
    if (values.output) fs.writeFileSync(values.output, json);
    console.log(json);
    return report.errors ? 1 : 0;
  } finally {
    if (browser) await browser.close();
    await new Promise(resolve => server.close(resolve));
  }
}
main().then(code => { process.exitCode = code; }).catch(error => { console.error(error.message); process.exitCode = 2; });
