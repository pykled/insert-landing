# Insert — PROJECT.md

**Last Updated:** 2026-08-25
**Status:** Active / Early Stage — site live, first clients not yet signed
**Owner:** Dillon
**Discord:** #insert
**Live Site:** https://insert-landing-production.up.railway.app

---

## What Is Insert?

Insert is an **AI consulting business** that helps local businesses eliminate repetitive, manual work by implementing custom AI workflows. We go into businesses — primarily real estate brokerages, property managers, and operators — audit where their team's time is actually going, and build the automations that give it back.

**The pitch:** Your team wasn't hired to do busywork. Stop paying them to.

**Business model:** Project-based consulting fees. We scope the problem, quote the engagement, build the solution, and hand it off. No retainer required, though ongoing support and expansion are options.

**Key insight:** Most small businesses are drowning in tasks that could be automated — but they don't know what's possible, don't have technical staff, and don't have time to figure it out. Insert bridges that gap. We come in, translate their pain into automation, and build it.

---

## Target Customer

**Primary:** Real estate brokerages, property managers, commercial RE operators
- Writing/syndicating listings
- Updating statuses across platforms
- Scheduling, follow-ups, lead routing
- Document generation (leases, offers, disclosures)

**Open to:** Any local service business with repetitive operational work
- Legal/insurance offices, med spas, contractors, logistics, etc.

**Not targeting:** Enterprise, Fortune 500, or companies with in-house technical teams

---

## Services We Offer

1. **AI Workflow Audit** — We map their current process and identify what can be automated
2. **Custom Workflow Build** — We build the actual solution (n8n, Claude API, custom scripts, integrations)
3. **Staff Training** — We make sure their team can actually use what we built
4. **Ongoing Tuning** — Optional — we monitor, expand, and iterate post-launch

---

## What's Built

### Landing Page
- **URL:** https://insert-landing-production.up.railway.app
- **GitHub:** https://github.com/pykled/insert-landing
- Palantir-dark aesthetic, IBM Plex Mono, fully responsive
- Sections: Hero, Stats, Problem, Services, How It Works, Who We Serve, Why Insert, Testimonials, Contact
- Contact section: Calendly booking embed + contact form

### Contact Form (Resend)
- POST `/api/contact` → Resend API → pykledd@gmail.com
- No third-party dependency beyond Resend (free tier, 3k/mo)

### Analytics (Self-Hosted)
- POST `/api/track` → Railway Postgres
- Dashboard at `/analytics?p=insert2026`
- Tracks: page views, unique visitors, referrers, device type
- Zero cookies, zero third parties

### Calendly
- Booking embed: `calendly.com/dilldjie/free-consultation`
- 30-min free consultation

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Static HTML/CSS/JS (no framework) |
| Server | Node.js + Express on Railway |
| Email | Resend API |
| Analytics DB | Railway Postgres |
| Booking | Calendly embed |
| Repo | github.com/pykled/insert-landing |

---

## Environment Variables (Railway)

| Variable | Purpose |
|----------|---------|
| `RESEND_API_KEY` | Contact form email delivery |
| `DATABASE_URL` | Postgres for analytics (auto-injected by Railway) |
| `ANALYTICS_PASSWORD` | Dashboard password (default: `insert2026`) |

---

## Deploy

```bash
cd ~/projects/insert
railway up --service insert-landing
```

---

## Current State

### ✅ Done
- Landing page live on Railway
- Contact form wired to Resend → pykledd@gmail.com
- Calendly booking embed (dilldjie/free-consultation)
- Self-hosted analytics with Postgres dashboard
- Privacy policy page
- GitHub repo: pykled/insert-landing

### 🔲 Pending
- [ ] Buy `useinsert.com` domain (~$12) and wire DNS to Railway
- [ ] Update OG tags and canonical URLs once domain is live
- [ ] Set up `hello@useinsert.com` once domain purchased
- [ ] Update Resend "from" address from `onboarding@resend.dev` to branded domain email
- [ ] First client signed

### 🚧 Open Questions
- Final business name: "Insert" is a placeholder that stuck — still evaluating
- Niche focus: starting with real estate, may expand based on first clients

---

## Vision

Build a lean consulting business where AI does the heavy lifting — fast discovery, fast builds, high margins. The goal isn't a big agency. It's a small, high-signal operation that moves faster than any traditional IT shop and charges accordingly.

Long-term: productize the most common workflows into repeatable packages. Sell the same real estate workflow to 20 brokerages instead of custom-building 20 times.

---

## Team

- **Dillon** — Founder, sole operator
- AI agents (via OpenClaw) — build and maintain the technical stack
