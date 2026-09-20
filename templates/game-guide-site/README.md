# Game Guide Site Pipeline Template

Use this template for Roblox, Steam, and other game guide/new-term sites.

## Setup

```bash
cp .env.example .env
```

Fill `.env`, then edit `keywords.json`.

## Commands

```bash
python run.py search --keywords keywords.json
python run.py generate --keywords keywords.json
python audit.py --articles-dir output/<project>/articles/en
```

## Editorial rules

- Prefer official game pages, official announcements, store pages, patch notes, and established gaming publications.
- Treat YouTube, Reddit, TikTok, Discord screenshots, and competitor guide pages as community signals, not final facts.
- Never invent codes, drop rates, map locations, tier rankings, forms, release dates, rewards, or patch data.
- If sources are weak, return `INSUFFICIENT_EVIDENCE` rather than filler.
