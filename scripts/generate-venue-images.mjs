#!/usr/bin/env node
/**
 * Generate atmospheric imagery for /venues with Gemini, then convert to WebP.
 *
 * Usage (from ~/projects/stagewell/backend, which is Railway-linked and injects GEMINI_API_KEY):
 *   railway run node ~/projects/insert/scripts/generate-venue-images.mjs [--force]
 *
 * Output: ~/projects/insert/assets/venues-*.webp
 */
import { mkdirSync, existsSync, writeFileSync, unlinkSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { execFileSync } from 'node:child_process';

const __dirname = dirname(fileURLToPath(import.meta.url));
const OUT_DIR = resolve(__dirname, '..', 'assets');
const force = process.argv.includes('--force');

const apiKey = process.env.GEMINI_API_KEY;
if (!apiKey) { console.error('GEMINI_API_KEY is not set. Run via `railway run` from the stagewell backend directory.'); process.exit(1); }
const MODEL = process.env.GEMINI_MODEL || 'gemini-3.1-flash-image-preview';
const URL = `https://generativelanguage.googleapis.com/v1beta/models/${MODEL}:generateContent`;

const QUALITY = `Editorial fine-art wedding photograph, shot on medium format film, shallow depth of field, soft grain.
Warm golden-hour light, deep warm shadows, muted champagne and cream tones against near-black darkness, low-key exposure.
Absolutely no people, no faces, no hands, no text, no logos, no watermarks. Not a stock photo: quiet, moody, intimate, understated.`;

const PROMPTS = {
  'venues-hero': {
    aspect: '16:9',
    prompt: 'Long outdoor wedding reception table at dusk on an estate lawn under an old oak, viewed down its length at a low angle. Linen runner, low arrangements of cream garden roses and dried grasses, dozens of taper candles and glass votives glowing gold, string lights softly out of focus in the trees behind. Golden hour fading to deep dusk, the background falls into warm near-black.',
  },
  'venues-florals': {
    aspect: '4:5',
    prompt: 'Close-up detail of a wedding tablescape: cream and blush garden roses, dried wheat and eucalyptus in a low brass vessel, a single lit taper candle in a brass holder, antique gold-rimmed glassware catching the last golden-hour light through a window. Dark linen, very dark warm background, light raking in from one side.',
  },
};

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function generate({ prompt, aspect }, label) {
  const body = (withConfig) => JSON.stringify({
    contents: [{ parts: [{ text: `${prompt}\n\n${QUALITY}` }] }],
    generationConfig: { responseModalities: ['TEXT', 'IMAGE'], ...(withConfig ? { imageConfig: { aspectRatio: aspect } } : {}) },
  });
  let withConfig = true;
  for (let attempt = 0; attempt < 4; attempt++) {
    const res = await fetch(URL, { method: 'POST', headers: { 'x-goog-api-key': apiKey, 'Content-Type': 'application/json' }, body: body(withConfig) });
    const data = await res.json();
    if (!res.ok || data.error) {
      const msg = data.error?.message ?? `HTTP ${res.status}`;
      if (withConfig && res.status === 400 && /image_?config|aspect/i.test(msg)) { console.warn(`[${label}] imageConfig rejected, retrying without it`); withConfig = false; continue; }
      if (res.status === 429 || res.status >= 500) { console.warn(`[${label}] ${res.status} ${msg} - retrying`); await sleep(3000 * (attempt + 1)); continue; }
      throw new Error(`[${label}] ${msg}`);
    }
    if (data.promptFeedback?.blockReason) throw new Error(`[${label}] blocked: ${data.promptFeedback.blockReason}`);
    const img = (data.candidates?.[0]?.content?.parts ?? []).find((p) => p.inlineData?.data);
    if (!img) { console.warn(`[${label}] no image (finishReason=${data.candidates?.[0]?.finishReason}) - retrying`); await sleep(2000); continue; }
    return { buffer: Buffer.from(img.inlineData.data, 'base64'), mime: img.inlineData.mimeType };
  }
  throw new Error(`[${label}] gave up after retries`);
}

mkdirSync(OUT_DIR, { recursive: true });
for (const [name, spec] of Object.entries(PROMPTS)) {
  const png = resolve(OUT_DIR, `${name}.png`);
  if (existsSync(png) && !force) { console.log(`[${name}] exists, skipping (use --force)`); continue; }
  const t = Date.now();
  const { buffer, mime } = await generate(spec, name);
  const raw = resolve(OUT_DIR, `${name}.raw.${mime.includes('jpeg') ? 'jpg' : 'png'}`);
  writeFileSync(raw, buffer);
  // sips: resample to 1600px wide, keep as PNG master; WebP conversion happens in a separate step.
  execFileSync('sips', ['--resampleWidth', '1600', '-s', 'format', 'png', raw, '--out', png], { stdio: 'ignore' });
  unlinkSync(raw);
  console.log(`[${name}] ${(Date.now() - t) / 1000}s -> ${png}`);
}
console.log('done');
