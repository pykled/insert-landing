#!/usr/bin/env node
/**
 * Generate the wide /venues interlude banner at native 2K+ resolution (no resampling),
 * then write it to /tmp for WebP conversion.
 *
 * Usage (from ~/projects/stagewell/backend, Railway-linked, injects GEMINI_API_KEY):
 *   RAILWAY_API_TOKEN="$(tr -d '[:space:]' < ~/projects/scripts/railway.token)" railway run node ~/projects/insert/scripts/generate-venue-banner.mjs [out.png]
 */
import { writeFileSync } from 'node:fs';
const apiKey = process.env.GEMINI_API_KEY;
if (!apiKey) { console.error('GEMINI_API_KEY not set'); process.exit(1); }
const MODEL = process.env.GEMINI_MODEL || 'gemini-3.1-flash-image-preview';
const URL = `https://generativelanguage.googleapis.com/v1beta/models/${MODEL}:generateContent`;
const out = process.argv[2] || '/tmp/venues-banner.raw';
const prompt = `Ultra-wide panoramic detail of a wedding tablescape at golden hour. Left third: a single lit cream taper candle in a brass holder, soft window light, quiet dark negative space in the lower left. Center and right: cream and blush garden roses, dried wheat and eucalyptus in a low brass vessel, antique gold-rimmed glassware catching the last warm light. Dark linen, very dark warm background, light raking in from the left.
Editorial fine-art wedding photograph, medium format film, shallow depth of field, fine grain, razor sharp focus on the roses and candle flame, high detail.
Warm champagne and cream tones against near-black, low-key exposure. Absolutely no people, no faces, no hands, no text, no logos, no watermarks.`;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let size = '2K';
for (let attempt = 0; attempt < 5; attempt++) {
  const res = await fetch(URL, { method: 'POST', headers: { 'x-goog-api-key': apiKey, 'Content-Type': 'application/json' }, body: JSON.stringify({
    contents: [{ parts: [{ text: prompt }] }],
    generationConfig: { responseModalities: ['TEXT', 'IMAGE'], imageConfig: { aspectRatio: '21:9', imageSize: size } },
  }) });
  const data = await res.json();
  if (!res.ok || data.error) {
    const msg = data.error?.message ?? `HTTP ${res.status}`;
    console.warn(`attempt ${attempt}: ${res.status} ${msg}`);
    if (res.status === 400 && /imageSize|image_size/i.test(msg) && size) { size = null; continue; }
    await sleep(3000 * (attempt + 1)); continue;
  }
  const img = (data.candidates?.[0]?.content?.parts ?? []).find((p) => p.inlineData?.data);
  if (!img) { console.warn('no image, retrying'); await sleep(2000); continue; }
  const ext = img.inlineData.mimeType.includes('jpeg') ? 'jpg' : 'png';
  writeFileSync(`${out}.${ext}`, Buffer.from(img.inlineData.data, 'base64'));
  console.log(`wrote ${out}.${ext} (${img.inlineData.mimeType}, imageSize=${size})`);
  process.exit(0);
}
console.error('gave up'); process.exit(1);
