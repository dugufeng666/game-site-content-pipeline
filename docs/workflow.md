# Reusable Content Pipeline Workflow

This workflow is for fast new-term sites where the goal is to collect enough source-backed material to publish useful guide pages quickly.

## 1. Choose the site template

- Use `templates/game-guide-site` for Roblox, Steam, and game wiki/guide sites.
- Use `templates/ai-product-site` for AI tools, model launches, API tutorials, and product comparison sites.

Copy the template and `core/*.py` into the target site's `content-pipeline/` directory.

## 2. Build the keyword file

Start with one main entity in `topic_name`. Put all page ideas under `categories`.

Good category groups for game sites:

- `guide`
- `wiki`
- `creatures` / `items` / `maps`
- `codes`
- `tier-list`
- `builds`

Good category groups for AI product sites:

- `guide`
- `api`
- `model`
- `integrations`
- `comparison`
- `community`

If short titles often omit the full phrase, use a shorter `topic_name` but keep individual keywords specific. Example: `topic_name: "jev"` with keywords like `jev ai tutorial`.

## 3. Collect sources

Run:

```bash
python run.py search --keywords keywords.json
```

Prefer high-signal sources:

- official websites
- official docs
- official announcements
- store pages
- GitHub repositories
- established publications
- YouTube only as community/context evidence unless the video content is available and source-backed

## 4. Generate drafts

Run:

```bash
python run.py generate --keywords keywords.json
```

The prompt should force `INSUFFICIENT_EVIDENCE` when sources are too thin. Do not weaken this gate to get more pages.

## 5. Audit article shape

Run:

```bash
python audit.py --articles-dir output/<project>/articles/en
```

The audit checks metadata, word count, H2 count, table count, keyword presence, and refusal markers. It does not fact-check.

## 6. Publish only after editorial review

Before moving any draft into the website:

- Verify source links.
- Remove unsupported claims.
- Ensure the page matches the site structure.
- Add internal links only when actual routes exist.
- Keep a changelog of which keyword/page was published.

## 7. Reuse rule

Do not let one site's emergency script become the new generic standard. If a change is reusable, move it back to this repository. If a change is site-specific, keep it in that site's `content-pipeline/`.
