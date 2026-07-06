# Shared Te Pā footer — embed guide

The Te Pā footer is a **single JavaScript file** hosted from this repo and
served via [jsDelivr](https://www.jsdelivr.com/). Every site that can run
`<script>` uses the same URL. Edit `assets/site-footer.js` here, push to
`main`, and every consumer picks up the change (jsDelivr caches ~12h; bust
with a `?v=YYYYMMDD` query string on the src).

Canonical URL:

```
https://cdn.jsdelivr.net/gh/robertmccallnz/systems-observatory@main/assets/site-footer.js
```

For production, pin a specific tag or commit instead of `@main`, e.g.
`@v1.0.0` or `@1a5a70d`.

---

## 1 — Sites that support `<script>` tags

**Works on:** `systems-observatory` (already wired), other GitHub Pages
repos, Netlify sites, Vercel sites, custom HTML on `te-pa.org` (if you
control the template), any static site you own.

Paste this immediately before `</body>` (or wherever you want the footer
to appear):

```html
<!-- Shared Te Pā footer -->
<div id="tepa-site-footer"></div>
<script
  src="https://cdn.jsdelivr.net/gh/robertmccallnz/systems-observatory@main/assets/site-footer.js"
  defer
></script>
```

That's it. No CSS import needed — the script injects its own styles into
`<head>`.

### Optional attributes

- **Light-theme override.** The footer defaults to the observatory's dark
  palette (`#0a0a0a` background context, cream text, kōura links). If your
  site has a light background, set:
  ```html
  <html data-tepa-theme="light">
  ```
  or on `<body>`. The footer switches to a light-friendly palette.

- **Mark current page in the "Views" links.** Set `data-tepa-page` on
  `<body>`:
  ```html
  <body data-tepa-page="observatory">     <!-- or -->
  <body data-tepa-page="governance">
  <body data-tepa-page="te-pa">
  <body data-tepa-page="kiwi-dialectic">
  ```
  If you omit it, the script auto-detects from the URL.

- **Force a cache bust.** After editing the footer, add a version query:
  ```html
  <script src="https://cdn.jsdelivr.net/gh/robertmccallnz/systems-observatory@main/assets/site-footer.js?v=2026-07-06" defer></script>
  ```

---

## 2 — te-pa.org

**If te-pa.org is a static site (GitHub Pages, Netlify, Vercel, hand-rolled
HTML):** use the `<script>` embed above. Set the light-theme flag if the
site is on a cream/white background.

**If te-pa.org is on a hosted platform (Squarespace, Wix, Webflow):**
- Squarespace: paste the `<script>` block into *Settings → Advanced → Code
  Injection → Footer*.
- Wix: use a **Custom Element / Embed HTML** widget, paste the same block.
- Webflow: paste inside *Project Settings → Custom Code → Footer Code*.

If none of those options is available on your plan, use the **static-HTML
fallback** in §4.

---

## 3 — The Kiwi Dialectic (Substack)

**Substack strips `<script>` tags** on every plan, so the JS include does
not work. Use one of these instead:

### Option A — Paste the static HTML into your "About" page

Substack allows raw HTML inside a post/page in the source view. Copy the
block from §4 into a new *About* page or an evergreen pinned post titled
e.g. "Kaupapa & network". You'll need to re-paste it whenever the shared
footer changes — treat that as an annual chore, not a per-edit one.

### Option B — Add the "Ecosystem" links to Substack's built-in About/Recommendations

Substack's *Settings → Publication details → About* accepts short HTML.
Paste just the Ecosystem block (Te Pā · Kiwi Dialectic · Kōrero · Systems
Observatory) as a bullet list. Cleaner than trying to render the full
footer inside Substack's constrained styling.

---

## 4 — Static-HTML fallback (paste-ready)

Use this only where JavaScript embeds are not allowed. All colours are
inlined; all URLs are absolute. Safe to paste into any HTML editor.

```html
<footer style="max-width:1200px;margin:4rem auto 0;padding:2.5rem 1.25rem 2rem;border-top:1px solid #1e1e1e;background:#0a0a0a;color:#d9d1bd;font-family:'Inter',system-ui,sans-serif;font-size:15px;line-height:1.5;">
  <div style="display:grid;grid-template-columns:1.4fr 1fr 1fr 1fr;gap:1.5rem;">
    <div>
      <h2 style="font-family:'Bebas Neue','Inter',sans-serif;font-size:1.6rem;letter-spacing:0.04em;margin:0 0 0.5rem;color:#f4ecd8;font-weight:400;">Te Pā Systems Observatory</h2>
      <p style="color:#d9d1bd;margin:0 0 0.6rem;">A public systems observatory and governance-audit tool developed as a Te Pā Collective Action Lab artefact, in relation to Te Pā Tūwatawata and The Kiwi Dialectic.</p>
      <p style="color:#d9d1bd;margin:0 0 0.6rem;">Standalone, forkable research artefact. Te Pā remains the kaupapa and charitable-trust anchor; the observatory remains an open technical and pedagogical tool.</p>
    </div>
    <div>
      <h3 style="font-size:0.75rem;text-transform:uppercase;letter-spacing:0.12em;color:#7a7268;margin:0 0 0.75rem;font-weight:600;">Views</h3>
      <ul style="list-style:none;margin:0;padding:0;">
        <li style="margin-bottom:0.5rem;"><a href="https://robertmccallnz.github.io/systems-observatory/" style="color:#e8a83a;text-decoration:none;">Observatory</a></li>
        <li><a href="https://robertmccallnz.github.io/systems-observatory/governance.html" style="color:#e8a83a;text-decoration:none;">Governance Audit</a></li>
      </ul>
    </div>
    <div>
      <h3 style="font-size:0.75rem;text-transform:uppercase;letter-spacing:0.12em;color:#7a7268;margin:0 0 0.75rem;font-weight:600;">Ecosystem</h3>
      <ul style="list-style:none;margin:0;padding:0;">
        <li style="margin-bottom:0.5rem;"><a href="https://te-pa.org" target="_blank" rel="noopener" style="color:#e8a83a;text-decoration:none;">Te Pā</a></li>
        <li style="margin-bottom:0.5rem;"><a href="https://www.kiwidialectic.com/" target="_blank" rel="noopener" style="color:#e8a83a;text-decoration:none;">Kiwi Dialectic</a></li>
        <li><a href="https://github.com/robertmccallnz/systems-observatory/discussions" target="_blank" rel="noopener" style="color:#e8a83a;text-decoration:none;">Kōrero</a></li>
      </ul>
    </div>
    <div>
      <h3 style="font-size:0.75rem;text-transform:uppercase;letter-spacing:0.12em;color:#7a7268;margin:0 0 0.75rem;font-weight:600;">Context</h3>
      <ul style="list-style:none;margin:0;padding:0;">
        <li style="margin-bottom:0.5rem;"><a href="https://github.com/robertmccallnz/systems-observatory/blob/main/docs/LEVERAGE_POINTS.md" target="_blank" rel="noopener" style="color:#e8a83a;text-decoration:none;">Leverage points mapping</a></li>
        <li style="margin-bottom:0.5rem;"><a href="https://github.com/robertmccallnz/systems-observatory/blob/main/docs/GOVERNANCE_AUDIT.md" target="_blank" rel="noopener" style="color:#e8a83a;text-decoration:none;">Governance audit method</a></li>
        <li style="margin-bottom:0.5rem;"><a href="https://github.com/robertmccallnz/systems-observatory/blob/main/reports/governance-audit-report.md" target="_blank" rel="noopener" style="color:#e8a83a;text-decoration:none;">Governance audit report</a></li>
        <li><a href="https://github.com/robertmccallnz/systems-observatory" target="_blank" rel="noopener" style="color:#e8a83a;text-decoration:none;">GitHub repository</a></li>
      </ul>
    </div>
  </div>
  <div style="margin-top:2rem;padding-top:1rem;border-top:1px solid #1e1e1e;color:#7a7268;font-size:0.85rem;">
    <p style="margin:0;">Built under the <a href="https://www.kahuiraraunga.io/" target="_blank" rel="noopener" style="color:#e8a83a;text-decoration:none;">Māori Data Governance Model</a> of Te Kāhui Raraunga. Public, aggregated, non-personal data only.</p>
  </div>
</footer>
```

### Light-background variant

If pasting into a site with a cream/white background (e.g. Substack's
default theme), swap these colour values everywhere:

- `#0a0a0a` → `#ffffff` (background — remove entirely if you prefer transparent)
- `#1e1e1e` → `#d8d1c5` (borders)
- `#f4ecd8` → `#1a1a1a` (H2)
- `#d9d1bd` → `#3a3630` (body text)
- `#7a7268` → `#6d655c` (muted meta / H3)
- `#e8a83a` → `#c1712f` (links)

---

## 5 — Updating the footer

1. Edit `assets/site-footer.js` in this repo (`FOOTER_HTML` and `CSS` are
   both at the top of the file).
2. `git commit && git push`.
3. jsDelivr picks up the change within ~12h automatically. For instant
   propagation on a specific site, bump the `?v=` query string on that
   site's `<script>` tag.
4. Substack + other static-HTML consumers: re-paste from §4.

## 6 — Pinning to a version

For production stability, pin to a git tag:

```bash
git tag v1.0.0
git push origin v1.0.0
```

Then use:

```
https://cdn.jsdelivr.net/gh/robertmccallnz/systems-observatory@v1.0.0/assets/site-footer.js
```
