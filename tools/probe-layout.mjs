/* =========================================================
   probe-layout.mjs — measure text geometry for every beat.

   Why: frame capture plus pixel checks can say "something overflows" but never
   "which line, by how many pixels". This probe reads real
   getBoundingClientRect values from the browser, so type-size and safe-area
   decisions are made from measurements rather than guesses.

   DOM contract (override with flags if your film differs):
     #stage    the scaled stage element (scale is derived from its width)
     .scene    scene containers; hidden ones are skipped
     .hero     text blocks whose glyph boxes are measured

   Glyph boxes come from Range.getClientRects(), not the block box, so the
   measurement reflects real ink bounds regardless of text alignment.

   Usage:
     PUPPETEER_CACHE_DIR="$PWD/.puppeteer-cache" TMPDIR="$PWD/.tmp" \
     node tools/probe-layout.mjs 1.2 4.8 7.6 10.8

     node tools/probe-layout.mjs --safe 0.08 --selector .hero --scene .scene 0 12 30
   ========================================================= */
import puppeteer from 'puppeteer';
import { pathToFileURL } from 'node:url';
import { readdir, mkdir } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import path from 'node:path';

/* --- tiny flag parser: flags before the positional time list --------------- */
const argv = process.argv.slice(2);
const opt = { safe: 0.08, stage: '#stage', scene: '.scene', selector: '.hero', url: null, w: 1920, h: 1080 };
const times = [];
for (let i = 0; i < argv.length; i++) {
  const a = argv[i];
  if (a === '--safe') opt.safe = Number(argv[++i]);
  else if (a === '--stage') opt.stage = argv[++i];
  else if (a === '--scene') opt.scene = argv[++i];
  else if (a === '--selector') opt.selector = argv[++i];
  else if (a === '--url') opt.url = argv[++i];
  else if (a === '--size') { const [w, h] = argv[++i].split('x').map(Number); opt.w = w; opt.h = h; }
  else times.push(Number(a));
}
if (!times.length) {
  console.log('usage: node tools/probe-layout.mjs [--safe 0.08] [--selector .hero] <seconds> ...');
  process.exit(1);
}

const SAFE = {
  x0: Math.round(opt.w * opt.safe),
  y0: Math.round(opt.h * opt.safe),
  x1: Math.round(opt.w * (1 - opt.safe)),
  y1: Math.round(opt.h * (1 - opt.safe)),
};

async function resolveShell() {
  const cache = process.env.PUPPETEER_CACHE_DIR || path.resolve('.puppeteer-cache');
  const root = path.join(cache, 'chrome-headless-shell');
  if (existsSync(root)) {
    for (const d of await readdir(root)) {
      const candidates = [
        path.join(root, d, 'chrome-headless-shell-mac-arm64', 'chrome-headless-shell'),
        path.join(root, d, 'chrome-headless-shell-mac-x64', 'chrome-headless-shell'),
        path.join(root, d, 'chrome-headless-shell-linux64', 'chrome-headless-shell'),
      ];
      for (const p of candidates) if (existsSync(p)) return p;
    }
  }
}

const userDataDir = path.resolve('.tmp/chrome-profile');
await mkdir(userDataDir, { recursive: true });

const browser = await puppeteer.launch({
  executablePath: await resolveShell(), headless: 'shell',
  args: ['--no-sandbox', '--disable-crashpad', '--disable-breakpad', '--allow-file-access-from-files'],
  userDataDir,
});
const [page] = await browser.pages();
const url = opt.url || pathToFileURL(process.cwd() + '/index.html').href + '?clean=1';
await page.goto(url, { waitUntil: 'networkidle0', timeout: 60000 });
await page.waitForFunction('window.OPENER && window.OPENER.ready', { timeout: 60000 });
await page.setViewport({ width: opt.w, height: opt.h, deviceScaleFactor: 1 });

console.log('safe area: x %d..%d, y %d..%d  (%dx%d, %s%%)\n',
  SAFE.x0, SAFE.x1, SAFE.y0, SAFE.y1, opt.w, opt.h, (opt.safe * 100).toFixed(0));
let bad = 0;
for (const t of times) {
  const info = await page.evaluate(async (time, sel) => {
    if (window.OPENER.seekAsync) { await window.OPENER.seekAsync(time); }
    else {
      window.OPENER.seek(time);
      await new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)));
    }
    const stage = document.querySelector(sel.stage);
    const s = stage.getBoundingClientRect().width / sel.w;   // scale (normally 1)
    const out = [];
    document.querySelectorAll(sel.scene).forEach(sc => {
      const cs = getComputedStyle(sc);
      if (cs.visibility === 'hidden' || Number(cs.opacity) < 0.02) return;
      sc.querySelectorAll(sel.selector).forEach(h => {
        /* Real glyph boxes, not the block box: Range.getClientRects() returns
           the ink bounds of each line regardless of alignment. */
        const rg = document.createRange();
        rg.selectNodeContents(h);
        const rects = [...rg.getClientRects()].filter(r => r.width > 1 && r.height > 1);
        if (!rects.length) return;
        const left = Math.min(...rects.map(r => r.left)), right = Math.max(...rects.map(r => r.right));
        const top = Math.min(...rects.map(r => r.top)), bottom = Math.max(...rects.map(r => r.bottom));
        out.push({
          scene: sc.id, text: h.textContent.replace(/\s+/g, ' ').trim(),
          x: Math.round(left / s), y: Math.round(top / s),
          w: Math.round((right - left) / s), hh: Math.round((bottom - top) / s),
          right: Math.round(right / s), bottom: Math.round(bottom / s),
          lines: rects.length,
          fs: getComputedStyle(h).fontSize,
        });
      });
    });
    return out;
  }, t, { stage: opt.stage, scene: opt.scene, selector: opt.selector, w: opt.w });

  console.log(`t=${t.toFixed(2)}s`);
  if (!info.length) console.log('   (no visible text)');
  for (const r of info) {
    const over = [];
    if (r.x < SAFE.x0) over.push(`left ${SAFE.x0 - r.x}px`);
    if (r.right > SAFE.x1) over.push(`right ${r.right - SAFE.x1}px`);
    if (r.y < SAFE.y0) over.push(`top ${SAFE.y0 - r.y}px`);
    if (r.bottom > SAFE.y1) over.push(`bottom ${r.bottom - SAFE.y1}px`);
    if (over.length) bad++;
    console.log(`   ${r.scene} ${r.fs.padEnd(6)} x=${String(r.x).padStart(4)} ` +
      `right=${String(r.right).padStart(4)} w=${String(r.w).padStart(4)} ` +
      `y=${r.y}..${r.bottom}  ${over.length ? 'OVERFLOW: ' + over.join(', ') : 'ok'}`);
    console.log(`      "${r.text}"`);
  }
  console.log('');
}
console.log(bad ? `${bad} overflowing text block(s)` : 'all text inside the safe area');
await browser.close();
