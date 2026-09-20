# AI Product Site Pipeline Template

Use this template for AI product, model, API, and tutorial new-term sites.

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

- Prefer official docs, official blogs, GitHub repositories, release notes, and provider documentation.
- Treat social posts and YouTube videos as community signals unless they contain verifiable primary-source details.
- Never invent pricing, rate limits, benchmarks, API parameters, model capabilities, release dates, or working code.
- If sources are weak, return `INSUFFICIENT_EVIDENCE` rather than filler.
