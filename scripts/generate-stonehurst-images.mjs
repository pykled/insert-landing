#!/usr/bin/env node
/**
 * Generate illustrative garden-estate imagery for the private Stonehurst homepage concept
 * (previews/stonehurst). Native 2K output, no resampling here; WebP conversion happens in
 * scripts/convert-stonehurst-images.py. No people, faces, text or logos in any image.
 *
 * Usage (from ~/projects/stagewell/backend, Railway-linked, injects GEMINI_API_KEY):
 *   RAILWAY_API_TOKEN="$(tr -d '[:space:]' < ~/projects/scripts/railway.token)" railway run \
 *     node ~/projects/insert/scripts/generate-stonehurst-images.mjs [outDir] [only,keys]
 */
import { writeFileSync, mkdirSync, existsSync } from 'node:fs';
import { join } from 'node:path';

const apiKey = process.env.GEMINI_API_KEY;
if (!apiKey) { console.error('GEMINI_API_KEY not set'); process.exit(1); }
const MODEL = process.env.GEMINI_MODEL || 'gemini-3.1-flash-image-preview';
const URL = `https://generativelanguage.googleapis.com/v1beta/models/${MODEL}:generateContent`;
const outDir = process.argv[2] || '/tmp/stonehurst-raw';
const only = process.argv[3] ? process.argv[3].split(',') : null;
mkdirSync(outDir, { recursive: true });

const STYLE = `Editorial fine-art wedding venue photograph, medium format film look, natural light, fine grain, razor sharp focus, high detail, restrained luxury, warm neutral tones with soft green foliage. Absolutely no people, no faces, no hands, no text, no signage, no logos, no watermarks.`;

const IMAGES = [
  { key: 'hero', ratio: '21:9', prompt: `Ultra-wide golden-hour view across a private nine-acre garden estate in the Southern California foothills: a hand-laid stone pathway curving between mature trees, yucca and agave beds, a dark weathered wood barn roofline half-hidden in the distance, strings of warm cafe lights catching the last light, soft rolling hills behind. Empty, quiet, just before guests arrive. ${STYLE}` },
  { key: 'greenhouse', ratio: '4:3', prompt: `Interior of a bright working greenhouse set for a wedding reception: floor-to-ceiling glass panes, original dark timber beams overhead with trailing greenery and loose white florals hung from them, long empty wooden tables with linen runners and taper candles, soft diffused daylight. ${STYLE}` },
  { key: 'barn', ratio: '4:3', prompt: `Interior of a historic wooden barn prepared for a candlelit reception: original dark-stained wood walls and rafters, three cascading crystal chandeliers hanging in a row down the centre, natural light falling from an open barn door, round tables with cream linens and low florals, empty chairs. ${STYLE}` },
  { key: 'bamboo', ratio: '4:3', prompt: `A secret bamboo garden ceremony space: tall dense bamboo of several varieties forming green walls on all sides, a narrow stone path leading to a small clearing with a few rows of empty wooden ceremony chairs, dappled light, a single woven lantern hanging overhead. Intimate, private, hushed. ${STYLE}` },
  { key: 'flower-garden', ratio: '4:3', prompt: `Outdoor ceremony under one enormous old fig tree with a wide spreading canopy: rows of empty wooden cross-back chairs on hand-laid stone paving, lush flowering garden beds and greenery wrapping fully around, two low floral arrangements flanking the aisle, late afternoon light through the leaves. ${STYLE}` },
  { key: 'bungalow', ratio: '4:3', prompt: `Exterior of a small private mid-century bungalow tucked into a garden: low-pitched dark roof, stone-clad porch base, two steps up to a shaded porch, potted plants, a single wooden chair, ivy and mature trees around it, morning light. Calm, a quiet place to get ready. ${STYLE}` },
  { key: 'terrace', ratio: '4:3', prompt: `A grand open-air stone terrace at dusk looking out over a small desert garden of cacti, agave and yucca with foothills beyond; terracotta and stone paving, a long empty cocktail table with glassware, strings of warm lights overhead, sky fading from apricot to blue. ${STYLE}` },
  { key: 'detail', ratio: '3:2', prompt: `Close detail of a wedding tablescape in a garden at golden hour: cream garden roses, dried grasses and eucalyptus in a low stone vessel, taper candles in brass holders, linen napkins, hand-laid stone pathway softly out of focus behind. ${STYLE}` },
];

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function gen({ key, ratio, prompt }) {
  let size = '2K';
  for (let attempt = 0; attempt < 5; attempt++) {
    const res = await fetch(URL, { method: 'POST', headers: { 'x-goog-api-key': apiKey, 'Content-Type': 'application/json' }, body: JSON.stringify({
      contents: [{ parts: [{ text: prompt }] }],
      generationConfig: { responseModalities: ['TEXT', 'IMAGE'], imageConfig: size ? { aspectRatio: ratio, imageSize: size } : { aspectRatio: ratio } },
    }) });
    const data = await res.json();
    if (!res.ok || data.error) {
      const msg = data.error?.message ?? `HTTP ${res.status}`;
      console.warn(`${key} attempt ${attempt}: ${res.status} ${msg}`);
      if (res.status === 400 && /imageSize|image_size/i.test(msg) && size) { size = null; continue; }
      await sleep(3000 * (attempt + 1)); continue;
    }
    const img = (data.candidates?.[0]?.content?.parts ?? []).find((p) => p.inlineData?.data);
    if (!img) { console.warn(`${key}: no image, retrying`); await sleep(2000); continue; }
    const ext = img.inlineData.mimeType.includes('jpeg') ? 'jpg' : 'png';
    const file = join(outDir, `${key}.${ext}`);
    writeFileSync(file, Buffer.from(img.inlineData.data, 'base64'));
    console.log(`wrote ${file} (${img.inlineData.mimeType}, imageSize=${size})`);
    return true;
  }
  console.error(`${key}: gave up`);
  return false;
}

let failed = 0;
for (const im of IMAGES) {
  if (only && !only.includes(im.key)) continue;
  if (!only && existsSync(join(outDir, `${im.key}.png`))) { console.log(`skip ${im.key} (exists)`); continue; }
  if (!(await gen(im))) failed++;
}
process.exit(failed ? 1 : 0);
