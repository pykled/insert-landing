const express = require('express');
const path = require('path');
const { Resend } = require('resend');
const { Pool } = require('pg');
const crypto = require('crypto');

const app = express();
const PORT = process.env.PORT || 3000;
const resend = new Resend(process.env.RESEND_API_KEY);
const ANALYTICS_PASSWORD = process.env.ANALYTICS_PASSWORD || 'insert2026';

const db = new Pool({ connectionString: process.env.DATABASE_URL });

async function initDb() {
  await db.query(`
    CREATE TABLE IF NOT EXISTS page_views (
      id SERIAL PRIMARY KEY,
      ts TIMESTAMPTZ DEFAULT NOW(),
      page TEXT,
      referrer TEXT,
      device TEXT,
      visitor_hash TEXT
    )
  `);
}
initDb().catch(console.error);

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// --- Contact form ---
app.post('/api/contact', async (req, res) => {
  const { name, email, business, message } = req.body;
  if (!name || !email) return res.status(400).json({ error: 'Name and email are required.' });
  try {
    await resend.emails.send({
      from: 'Insert Contact <onboarding@resend.dev>',
      to: 'pykledd@gmail.com',
      reply_to: email,
      subject: `New consultation request — ${name}`,
      html: `
        <h2>New message from Insert landing page</h2>
        <p><strong>Name:</strong> ${name}</p>
        <p><strong>Email:</strong> ${email}</p>
        <p><strong>Business type:</strong> ${business || '—'}</p>
        <p><strong>Message:</strong><br>${message ? message.replace(/\n/g, '<br>') : '—'}</p>
      `,
    });
    res.json({ ok: true });
  } catch (err) {
    console.error('Resend error:', err);
    res.status(500).json({ error: 'Failed to send message. Please try again.' });
  }
});

// --- Analytics tracking ---
app.post('/api/track', async (req, res) => {
  try {
    const { page, referrer, device } = req.body;
    const ip = req.headers['x-forwarded-for']?.split(',')[0] || req.socket.remoteAddress || '';
    const ua = req.headers['user-agent'] || '';
    const visitor_hash = crypto.createHash('sha256').update(ip + ua).digest('hex').slice(0, 16);
    await db.query(
      'INSERT INTO page_views (page, referrer, device, visitor_hash) VALUES ($1, $2, $3, $4)',
      [page || '/', referrer || '', device || 'unknown', visitor_hash]
    );
    res.json({ ok: true });
  } catch (err) {
    console.error('Track error:', err);
    res.status(500).json({ ok: false });
  }
});

// --- Analytics dashboard ---
app.get('/analytics', async (req, res) => {
  if (req.query.p !== ANALYTICS_PASSWORD) {
    return res.status(401).send(`
      <html><body style="background:#0a0a0a;color:#f2f2f0;font-family:monospace;display:flex;align-items:center;justify-content:center;height:100vh;margin:0">
        <form method="GET">
          <input name="p" type="password" placeholder="Password" autofocus
            style="background:#111;border:1px solid #333;color:#f2f2f0;padding:10px 14px;font-family:monospace;margin-right:8px">
          <button type="submit" style="background:#f2f2f0;color:#0a0a0a;border:none;padding:10px 18px;font-family:monospace;cursor:pointer">Enter</button>
        </form>
      </body></html>
    `);
  }

  const pw = req.query.p;
  const [today, week, total, uniq, topRefs, recent] = await Promise.all([
    db.query(`SELECT COUNT(*) FROM page_views WHERE ts > NOW() - INTERVAL '1 day'`),
    db.query(`SELECT COUNT(*) FROM page_views WHERE ts > NOW() - INTERVAL '7 days'`),
    db.query(`SELECT COUNT(*) FROM page_views`),
    db.query(`SELECT COUNT(DISTINCT visitor_hash) FROM page_views WHERE ts > NOW() - INTERVAL '7 days'`),
    db.query(`SELECT referrer, COUNT(*) as c FROM page_views WHERE referrer != '' AND ts > NOW() - INTERVAL '7 days' GROUP BY referrer ORDER BY c DESC LIMIT 8`),
    db.query(`SELECT ts, page, referrer, device FROM page_views ORDER BY ts DESC LIMIT 20`),
  ]);

  const stat = (label, val) => `
    <div style="background:#111;border:1px solid #1e1e1e;padding:20px 24px;border-radius:4px">
      <div style="font-size:2rem;font-weight:600;letter-spacing:-0.02em">${val}</div>
      <div style="color:#666;font-size:0.75rem;margin-top:4px;text-transform:uppercase;letter-spacing:0.08em">${label}</div>
    </div>`;

  const refRows = topRefs.rows.map(r =>
    `<tr><td style="padding:8px 0;color:#aaa">${r.referrer || 'direct'}</td><td style="padding:8px 0;text-align:right">${r.c}</td></tr>`
  ).join('') || '<tr><td colspan="2" style="color:#444;padding:8px 0">No referrers yet</td></tr>';

  const recentRows = recent.rows.map(r => {
    const t = new Date(r.ts).toLocaleString('en-US', { month:'short', day:'numeric', hour:'numeric', minute:'2-digit' });
    return `<tr>
      <td style="padding:6px 0;color:#666;font-size:0.8rem">${t}</td>
      <td style="padding:6px 0">${r.page}</td>
      <td style="padding:6px 0;color:#666;font-size:0.8rem">${r.referrer || '—'}</td>
      <td style="padding:6px 0;color:#666;font-size:0.8rem">${r.device}</td>
    </tr>`;
  }).join('') || '<tr><td colspan="4" style="color:#444;padding:8px 0">No visits yet</td></tr>';

  res.send(`<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Insert Analytics</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&display=swap" rel="stylesheet">
</head>
<body style="background:#0a0a0a;color:#f2f2f0;font-family:'IBM Plex Mono',monospace;margin:0;padding:40px 32px;min-height:100vh">
  <div style="max-width:900px;margin:0 auto">
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:40px">
      <div>
        <div style="font-size:0.7rem;color:#444;letter-spacing:0.1em;margin-bottom:4px">INSERT</div>
        <h1 style="margin:0;font-size:1.4rem;font-weight:600">Analytics</h1>
      </div>
      <div style="font-size:0.75rem;color:#444">${new Date().toLocaleDateString('en-US',{weekday:'long',month:'long',day:'numeric'})}</div>
    </div>

    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:40px">
      ${stat('Today', today.rows[0].count)}
      ${stat('This week', week.rows[0].count)}
      ${stat('All time', total.rows[0].count)}
      ${stat('Unique (7d)', uniq.rows[0].count)}
    </div>

    <div style="display:grid;grid-template-columns:1fr 2fr;gap:24px;margin-bottom:40px">
      <div>
        <div style="font-size:0.7rem;color:#444;letter-spacing:0.08em;margin-bottom:12px">TOP REFERRERS — 7D</div>
        <table style="width:100%;border-collapse:collapse">
          ${refRows}
        </table>
      </div>
      <div>
        <div style="font-size:0.7rem;color:#444;letter-spacing:0.08em;margin-bottom:12px">RECENT VISITS</div>
        <table style="width:100%;border-collapse:collapse;font-size:0.85rem">
          ${recentRows}
        </table>
      </div>
    </div>

    <div style="font-size:0.7rem;color:#333;text-align:right">
      <a href="/analytics?p=${pw}" style="color:#444;text-decoration:none">↻ refresh</a>
      &nbsp;·&nbsp; no cookies · no third parties
    </div>
  </div>
</body></html>`);
});

app.use(express.static(path.join(__dirname), { maxAge: '1d', etag: true }));

app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'index.html'));
});

app.listen(PORT, () => {
  console.log(`Insert landing page running on port ${PORT}`);
});
