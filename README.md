# Game Site Content Pipeline

Reusable content research and draft-generation pipeline for fast new-term guide sites.

This repository is intentionally a pipeline template, not a finished website. Copy a template into a site's repository, add a local `.env`, tune `keywords.json` and prompts, then run the pipeline from that site.

## What it does

- Keeps keyword groups in a repeatable JSON format.
- Wraps an installed `seoscout` CLI with site-local prompts and environment variables.
- Validates generated MDX drafts for basic SEO/article-shape requirements.
- Audits draft folders without claiming fact-checking is complete.
- Provides two starter templates:
  - `game-guide-site` for Roblox, Steam, and other game guide sites.
  - `ai-product-site` for AI product/tutorial new-term sites.

## What it does not do

- It does not publish articles automatically.
- It does not deploy websites.
- It does not hide weak evidence. Unsupported drafts should fail with `INSUFFICIENT_EVIDENCE`.
- It does not store secrets. Keep `.env` local and out of Git.

## Quick start for a new site

From the target website repo:

```bash
mkdir -p content-pipeline
cp -R /Users/dugufeng/Desktop/github/game-site-content-pipeline/templates/game-guide-site/. content-pipeline/
cp /Users/dugufeng/Desktop/github/game-site-content-pipeline/core/*.py content-pipeline/
cp content-pipeline/.env.example content-pipeline/.env
```

Then edit:

- `content-pipeline/.env`
- `content-pipeline/keywords.json`
- `content-pipeline/generate-prompt.md`
- `content-pipeline/translate-prompt.md`

Run from `content-pipeline`:

```bash
python run.py search --keywords keywords.json
python run.py generate --keywords keywords.json
python audit.py --articles-dir output/<project>/articles/en
```

Use the generated drafts as editorial inputs. Review sources, facts, links, and site fit before publishing.

## Repository layout

```text
core/
  run.py
  audit.py
  draft_validation.py
templates/
  game-guide-site/
  ai-product-site/
examples/
  aniimo/
  jev/
docs/
  workflow.md
```

## Recommended usage

Use this repository as the central source of truth. Individual websites should only keep a copied `content-pipeline/` folder plus their own site-specific keywords and prompts.
game-site-content-pipeline
