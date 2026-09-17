# ARGONAUT AI — Vercel checklist

This repository is intentionally structured with the Next.js app at the repository root and FastAPI at `api/index.py`.

## Vercel settings

- Framework Preset: Next.js
- Root Directory: `.` (repository root)
- Build Command: leave blank / default (`next build`)
- Output Directory: leave blank / default
- Install Command: leave blank / default (`npm install`)
- Do not set a custom rewrite for `/api`.

## API

The Python entrypoint is `api/index.py` and exposes the FastAPI application as `app`.

## Demo

The application starts with synthetic ARGO-style data so it does not depend on external ocean APIs.
Demo login: `admin` / `argo123`.
