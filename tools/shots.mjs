/* =========================================================
   shots.mjs — capture still frames at exact times.

   Why this is its own file rather than a copy of the skill's snap.mjs: the
   shipped capture scripts open a browser without a userDataDir, which leaves
   the profile in a location the process may not be allowed to write, and some
   Puppeteer/Chrome combinations fail with "Requesting main frame too early!".
   This wrapper:
     • prefers chrome-headless-shell, which is the right tool for frame capture
     • keeps userDataDir and TMPDIR inside the project
     • prints page errors (pageerror/console/requestfailed) so failures are
       never silent

   Usage:
     PUPPETEER_CACHE_DIR="$PWD/.puppeteer-cache" TMPDIR="$PWD/.tmp" \
     URL="file://$PWD/index.html?clean=1" \
     node tools/shots.mjs shots 1.5 12.0 26.0
   ========================================================= */
import puppeteer from 'puppeteer';
import { pathToFileURL } from 'node:url';
import { mkdir, readdir } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import path from 'node:path';

/* Full Chrome can fail with "Requesting main frame too early!" while
   chrome-headless-shell runs cleanly on the same version — and it is the
   correct tool for frame capture anyway. */
async function resolveShell(){
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

const [outDir, ...times] = process.argv.slice(2);
if (!outDir || !times.length) {
  console.log('usage: node tools/shots.mjs <outDir> <seconds> [<seconds> ...]');
  process.exit(1);
}
const URL_ = process.env.URL || pathToFileURL(process.cwd()).href + '/index.html?clean=1';
await mkdir(outDir, { recursive: true });

const launchArgs = [
  '--enable-gpu', '--use-gl=angle', '--enable-webgl', '--ignore-gpu-blocklist',
  '--autoplay-policy=no-user-gesture-required',
  '--no-first-run', '--no-default-browser-check', '--disable-dev-shm-usage',
];
const userDataDir = path.resolve('.tmp/chrome-profile');
await mkdir(userDataDir, { recursive: true });

const shellPath = await resolveShell();
const browser = await puppeteer.launch({
  executablePath: shellPath,
  headless: 'shell',
  args: [...launchArgs, '--no-sandbox', '--disable-crashpad', '--disable-breakpad',
         '--allow-file-access-from-files'],
  userDataDir,
});
console.log('browser:', await browser.version(), shellPath ? '(chrome-headless-shell)' : '(default)');

// Launch already opens a blank tab — reuse it. Calling newPage() and then
// navigating immediately triggers "Requesting main frame too early".
const pages = await browser.pages();
const page = pages.length ? pages[0] : await browser.newPage();
await new Promise(r => setTimeout(r, 300));   // let the main frame attach
const problems = [];
page.on('pageerror', e => problems.push('PAGEERROR ' + e.message));
page.on('console', m => { if (m.type() === 'error') problems.push('CONSOLE ' + m.text()); });
page.on('requestfailed', r => problems.push('REQFAIL ' + r.url() + ' ' + (r.failure()?.errorText || '')));

await page.goto(URL_, { waitUntil: 'networkidle0', timeout: 60000 });
await page.waitForFunction(
  'window.OPENER && window.OPENER.ready && (!window.OPENER.clipsReady || window.OPENER.clipsReady())',
  { timeout: 60000 },
);
await page.setViewport({ width: 1920, height: 1080, deviceScaleFactor: 1 });

for (const ts of times) {
  const t = Number(ts);
  await page.evaluate(async (time) => {
    // seekAsync resolves only once changed image frames have decoded; a plain
    // seek can screenshot a stale frame.
    if (window.OPENER.seekAsync) { await window.OPENER.seekAsync(time); return; }
    window.OPENER.seek(time);
    await new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)));
    window.OPENER.seek(time);
  }, t);
  const name = `t${t.toFixed(2).replace('.', '_')}.png`;
  await page.screenshot({ path: `${outDir}/${name}` });
  process.stdout.write(`${t} `);
}
await browser.close();

console.log('\nframes written:', outDir);
if (problems.length) {
  console.log('\nPAGE PROBLEMS (' + problems.length + '):');
  for (const p of [...new Set(problems)].slice(0, 12)) console.log('  • ' + p);
} else {
  console.log('no page errors');
}
