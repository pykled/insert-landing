# Venue content schema (consumed by build.py)

One JSON file per venue under `factory/content/<slug>.json`. Every statement that will appear on the page must be
traceable to the venue's own site: facts carry a `source` URL, spaces carry a `source` URL, FAQs carry a `source` URL,
photos carry the source URL in the referenced manifest. The generator never invents a number, a phone, an address line
or a capacity; if a field is null the templates say so ("Capacity on request") or omit the element.

| Key | Type | Notes |
|---|---|---|
| `slug`, `name`, `short_name`, `legal_name` | string | `short_name` is the wordmark; `legal_name` is the copyright line |
| `tagline_facts` | object | `locality`, `region`, `state`, `acres`, `space_count`, `max_guests`, `events_per_day`, `uses[]` — the numbers every hero draws on |
| `website` | url | used in JSON-LD `url` and `@id` |
| `contact` | object | `email`, `email_note`, `phone` (null allowed), `phone_note`, `address_line`, `address_note`, `hours`, `source` |
| `facts[]` | `{id, text, source}` | the verified fact ledger; not rendered directly, kept for audit |
| `story` | object | `kicker`, `lead`, `paragraphs[]`, `credit`, `timeline[] {year, text, source}`, `photo`, `source` |
| `numbers[]` | `{value, label, source}` | 3-4 big figures (acres, spaces, events per day, a date) |
| `spaces[]` | object | `id`, `name`, `photo`, `capacity` (int or null), `capacity_label`, `capacity_kind`, optional `capacity_ceremony`, `use`, `blurb`, `features[]`, `journey_step`, `source` |
| `journey` | object | `note` (how the order was derived from stated uses), `steps[]` of space ids |
| `day` | object | `rental_hours`, `gates_open`, `event_end`, `breakdown_end`, `included[]`, `requirement`, `spaces_per_event`, `source` |
| `faqs[]` | `{q, a, source}` | verbatim or lightly paraphrased from the venue's FAQ |
| `featured_in[]` | string | plain text names only; never logo files |
| `photos` | object | `source_dir`, `manifest` (both relative to the content file), `credit`, `items{name: {alt, focal, light, tags[]}}` |
| `preview` | object | `private` (true = noindex meta + disclaimer chip), `disclaimer`, `meta_description` |
| `copy_overrides` | object (optional) | voice slot -> string, applied after the voice preset; the human taste pass lives here |

Photo manifest (`img/real/manifest.json`, written by the crawl/convert step): `name`, `source_url`, `source_page`,
`native [w,h]`, `crop [w,h]`, `kept_copy`, `kept_copy_size`. The QA gate reads `crop` as the never-exceed width.

Personality is not in the content file: it is a build input (`--personality`), so one content file can produce many
sites. Forced choices (`--force hero=frame`) and the lead photo (`--lead`) are build inputs too, and are recorded in
`build-meta.json` next to the output.
