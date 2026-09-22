/* =========================================================
   export-frames.mjs — export a complete frame sequence from the FILM for encoding.

   Scope: this tool drives the film's own seek contract in a browser. It renders
   frames from the composition. To extract frames from an already-rendered video
   FILE (for review or defect checks), use ffmpeg instead, for example:
     "$(tools/ffmpeg.sh)" -i clip.mp4 -vf fps=1 review/f_%03d.png

   Difference from shots.mjs: instead of a list of individual times, this walks
   the ENTIRE frame grid (25 fps x duration) and writes one image per frame.

   Determinism rests on the film's seek contract: each frame is seeked to its
   exact time and, when the film exposes `seekAsync`, we wait for changed image
   frames to decode before capturing. Otherwise we seek, wait two animation
   frames, and seek again so that onUpdate work (blur, dash offsets) settles
   before the screenshot.

   Note: this tool uses Date.now() for progress reporting only. Film sources
   must never use it — tools/verify.sh enforces that separately.

   Usage:
     PUPPETEER_CACHE_DIR="$PWD/.puppeteer-cache" TMPDIR="$PWD/.tmp" \
     URL="file://$PWD/index.html?clean=1" \
     node tools/export-frames.mjs frames 25 60 --size 1920x1080 --format jpeg --quality 96
   ========================================================= */
import puppeteer from 'puppeteer';
import { pathToFileURL } from 'node:url';
import { mkdir, readdir, writeFile } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import path from 'node:path';

/* --- arguments ------------------------------------------------------------ */
const argv = process.argv.slice(2);
const positional = [];
const opt = { size: '1920x1080', format: 'jpeg', quality: 96, url: null };
for (let i = 0; i < argv.length; i++) {
  const a = argv[i];
  if (a === '--size') opt.size = argv[++i];
  else if (a === '--format') opt.format = argv[++i];
  else if (a === '--quality') opt.quality = Number(argv[++i]);
  else if (a === '--url') opt.url = argv[++i];
  else positional.push(a);
}

const OUT = positional[0] || 'frames';
const FPS = Number(positional[1] || 25);
const DUR = Number(positional[2] || 60);
const TOTAL = Math.round(FPS * DUR);
const [W, H] = opt.size.split('x').map(Number);
const FORMAT = opt.format === 'png' ? 'png' : 'jpeg';
const EXT = FORMAT === 'png' ? 'png' : 'jpg';

if (!Number.isFinite(FPS) || !Number.isFinite(DUR) || TOTAL <= 0) {
  console.log('usage: node tools/export-frames.mjs <outDir> <fps> <seconds> [--size WxH] [--format jpeg|png] [--quality N]');
  process.exit(1);
}

/* Full Chrome can fail with "Requesting main frame too early!"; the headless
   shell runs cleanly and is the right tool for capture. */
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
  return undefined;   // fall back to the Puppeteer default
}

await mkdir(OUT, { recursive: true });
const userDataDir = path.resolve('.tmp/chrome-profile-export');
await mkdir(userDataDir, { recursive: true });

const shellPath = await resolveShell();
const browser = await puppeteer.launch({
  executablePath: shellPath,
  headless: 'shell',
  args: [
    '--enable-gpu', '--use-gl=angle', '--enable-webgl', '--ignore-gpu-blocklist',
    '--no-first-run', '--no-default-browser-check', '--disable-dev-shm-usage',
    '--no-sandbox', '--disable-crashpad', '--disable-breakpad',
    '--allow-file-access-from-files',
  ],
  userDataDir,
});
console.log('browser:', await browser.version(), shellPath ? '(chrome-headless-shell)' : '(default)');

const pages = await browser.pages();
const page = pages.length ? pages[0] : await browser.newPage();
await new Promise((r) => setTimeout(r, 300));

const problems = [];
page.on('pageerror', (e) => problems.push('PAGEERROR ' + e.message));
page.on('console', (m) => { if (m.type() === 'error') problems.push('CONSOLE ' + m.text()); });
page.on('requestfailed', (r) => problems.push('REQFAIL ' + r.url() + ' ' + (r.failure()?.errorText || '')));

const URL_ = opt.url || process.env.URL || pathToFileURL(process.cwd()).href + '/index.html?clean=1';
await page.goto(URL_, { waitUntil: 'networkidle0', timeout: 60000 });
await page.waitForFunction(
  'window.OPENER && window.OPENER.ready && (!window.OPENER.clipsReady || window.OPENER.clipsReady())',
  { timeout: 60000 },
);
await page.setViewport({ width: W, height: H, deviceScaleFactor: 1 });

const t0 = Date.now();
for (let i = 0; i < TOTAL; i++) {
  const t = i / FPS;
  await page.evaluate(async (time) => {
    if (window.OPENER.seekAsync) { await window.OPENER.seekAsync(time); return; }
    window.OPENER.seek(time);
    await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
    window.OPENER.seek(time);
  }, t);
  const name = 'f_' + String(i).padStart(5, '0') + '.' + EXT;
  const shot = { path: path.join(OUT, name), type: FORMAT };
  if (FORMAT === 'jpeg') shot.quality = opt.quality;
  await page.screenshot(shot);
  if (i % 100 === 0 || i === TOTAL - 1) {
    const el = (Date.now() - t0) / 1000;
    process.stdout.write(`${i + 1}/${TOTAL} (${el.toFixed(0)}s, ${(el / (i + 1)).toFixed(2)}s/frame)\n`);
  }
}
await browser.close();

await writeFile(path.join(OUT, '_manifest.json'), JSON.stringify({
  fps: FPS, duration: DUR, total: TOTAL, width: W, height: H,
  format: FORMAT, quality: FORMAT === 'jpeg' ? opt.quality : null, url: URL_,
}, null, 2));

console.log('frames written:', OUT, '| total', TOTAL);
if (problems.length) {
  console.log('PAGE PROBLEMS (' + problems.length + '):');
  for (const p of [...new Set(problems)].slice(0, 12)) console.log('  • ' + p);
} else {
  console.log('no page errors');
}
