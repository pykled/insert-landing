#!/usr/bin/env node
/**
 * Generate the /venues rehaul photographs (venues2-*) at native 4K (falls back to 2K), no resampling.
 * Same recipe as generate-venue-banner.mjs. Run from ~/projects/stagewell/backend (injects GEMINI_API_KEY):
 *   RAILWAY_API_TOKEN="$(tr -d '[:space:]' < ~/projects/scripts/railway.token)" railway run node ~/projects/insert/scripts/generate-venues2-images.mjs <name> [outdir]
 */
import { writeFileSync } from 'node:fs';
const apiKey = process.env.GEMINI_API_KEY;
if (!apiKey) { console.error('GEMINI_API_KEY not set'); process.exit(1); }
const MODEL = process.env.GEMINI_MODEL || 'gemini-3.1-flash-image-preview';
const URL = `https://generativelanguage.googleapis.com/v1beta/models/${MODEL}:generateContent`;
const STYLE = `Editorial fine-art wedding photograph, shot on medium format film, natural light only, fine grain, crisp focus, high detail, calm and unhurried. Warm ivory, soft olive green and muted bronze tones; gentle contrast, nothing oversaturated, not glossy, not stock-looking. Absolutely no people, no faces, no hands, no silhouettes, no text, no lettering, no signage, no logos, no watermarks.`;
const SHOTS = {
  hero: ['16:9', `Wide view through a pair of tall open French doors of an old limestone estate house at blue hour, looking out to a long wooden table set for a wedding dinner on a lawn beneath old oak trees. Many small candles glowing on the table, ivory linen, low arrangements of white garden roses and olive branches, simple glassware. Warm lamplight spills across a worn stone floor in the foreground; the doors and their painted frames softly frame the scene. Quiet, generous negative space in the dusky sky.`],
  table: ['3:2', `Close still life on a long linen-covered wedding table in late afternoon window light: a folded ivory linen napkin tied with a sprig of olive, an antique brass candlestick with an unlit cream taper, a gold-rimmed wine glass, a small low bowl of white garden roses and trailing greenery. Soft shadows, shallow depth of field, the background falls into warm blurred garden light.`],
  path: ['3:2', `A gravel path between clipped boxwood hedges leading through a walled garden toward the open arched wooden door of an old stone barn at golden hour. Climbing white roses on the stone wall, a few lanterns on the ground along the path, long soft shadows, warm light catching the stone.`],
};
const name = process.argv[2]; const outdir = process.argv[3] || '/tmp/rehaul';
const [aspectRatio, subject] = SHOTS[name] || [];
if (!subject) { console.error('unknown shot', name); process.exit(1); }
const prompt = `${subject}\n${STYLE}`;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const sizes = ['4K', '2K'];
let si = 0;
for (let attempt = 0; attempt < 6; attempt++) {
  const size = sizes[si];
  const res = await fetch(URL, { method: 'POST', headers: { 'x-goog-api-key': apiKey, 'Content-Type': 'application/json' }, body: JSON.stringify({
    contents: [{ parts: [{ text: prompt }] }],
    generationConfig: { responseModalities: ['TEXT', 'IMAGE'], imageConfig: { aspectRatio, imageSize: size } },
  }) });
  const data = await res.json().catch(() => ({}));
  if (!res.ok || data.error) {
    const msg = data.error?.message ?? `HTTP ${res.status}`;
    console.warn(`attempt ${attempt} (${size}): ${res.status} ${msg.slice(0, 160)}`);
    if (res.status === 400 && si < sizes.length - 1) { si++; continue; }
    await sleep(3000 * (attempt + 1)); continue;
  }
  const img = (data.candidates?.[0]?.content?.parts ?? []).find((p) => p.inlineData?.data);
  if (!img) { console.warn('no image, retrying'); await sleep(2000); continue; }
  const ext = img.inlineData.mimeType.includes('jpeg') ? 'jpg' : 'png';
  const file = `${outdir}/venues2-${name}-${Date.now()}.${ext}`;
  writeFileSync(file, Buffer.from(img.inlineData.data, 'base64'));
  console.log(`wrote ${file} (${img.inlineData.mimeType}, imageSize=${size})`);
  process.exit(0);
}
console.error('gave up'); process.exit(1);
