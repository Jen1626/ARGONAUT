# ARGONAUT AI — V3

A Vercel-ready full-stack ocean intelligence dashboard for exploring ARGO-style float observations.

## What is included

- Cinematic ocean-themed login screen
- Demo login: `admin` / `argo123`
- Guest access
- Ocean AI natural-language query engine
- Region-aware filtering for Arabian Sea, Bay of Bengal, Indian Ocean, Atlantic regions and global data
- Float explorer by WMO/platform number
- Temperature, salinity, density and T-S visualizations
- Float trajectory map with React Leaflet + OpenStreetMap
- Nearest-float search from latitude/longitude
- FastAPI backend under `api/index.py`
- Next.js App Router frontend at the repository root
- Local CSV ingestion using the original ARGO-style schema
- Vercel-compatible Python runtime configuration

## Important data note

The project starts with deterministic **synthetic ARGO-style demo observations** so the UI works immediately without depending on an external ocean-data service. The dashboard labels this as `DEMO NETWORK`.

For real observations, add files such as:

```text
backend/data/argo_float_4903775_full_data.csv
```

The engine recognizes these columns (case-insensitive aliases are supported):

```text
TIME, PRES, TEMP, PSAL, PDEN, CYCLE_NUMBER, LATITUDE, LONGITUDE
```

Real-data ingestion is local-file based in this V3 build. A production deployment that downloads large NetCDF/FTP datasets per request should use durable object storage or a dedicated data-processing service instead of doing heavy processing inside a Vercel Function.

## Project structure

```text
argonaut-ai-v3/
├── app/                    # Next.js App Router
│   ├── page.tsx            # Command Center + login
│   ├── explorer/page.tsx
│   ├── visualization/page.tsx
│   ├── trajectory/page.tsx
│   └── help/page.tsx
├── components/
│   ├── Map.tsx
│   ├── Plot.tsx
│   └── OceanBackground.tsx
├── lib/api.ts
├── api/
│   ├── index.py            # Vercel FastAPI entrypoint
│   └── engine.py           # Ocean data processing engine
├── backend/data/            # Optional real ARGO CSV files
├── package.json
├── requirements.txt
├── .python-version
└── vercel.json
```

## Run locally

### 1. Frontend dependencies

From the project root:

```bash
npm install
npm run dev
```

Open:

```text
http://localhost:3000
```

### 2. Test the FastAPI engine directly

Create a Python virtual environment if needed:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Then:

```bash
uvicorn api.index:app --reload --port 8000
```

API examples:

```text
http://localhost:8000/api/health
http://localhost:8000/api/dashboard
http://localhost:8000/api/float/4903775
http://localhost:8000/api/float/4903775/trajectory
http://localhost:8000/api/nearest?lat=12&lon=64
```

The frontend normally uses same-origin `/api`, which is the intended Vercel deployment setup.

## Vercel deployment

1. Put this entire folder in a GitHub repository.
2. Open Vercel and choose **Add New → Project**.
3. Import the GitHub repository.
4. Keep the project root at the repository root.
5. Do not set a separate frontend root directory.
6. Deploy.

Vercel detects the Next.js application from the root `package.json` and the FastAPI application from `api/index.py`.

If you use the CLI:

```bash
npm install -g vercel
vercel
```

For a production deployment:

```bash
vercel --prod
```

## Demo credentials

```text
Username: admin
Password: argo123
```

Google and LinkedIn buttons are intentionally demo entry buttons; they do not perform OAuth authentication.

## Main API routes

| Method | Route | Purpose |
|---|---|---|
| GET | `/api` | API status |
| GET | `/api/health` | Health check |
| GET | `/api/dashboard` | Dashboard metrics |
| POST | `/api/chat` | Natural-language ocean query |
| GET | `/api/float/{wmo}` | Float observations + statistics |
| GET | `/api/float/{wmo}/plot` | Chart-ready data |
| GET | `/api/float/{wmo}/trajectory` | Cycle trajectory |
| GET | `/api/nearest?lat=&lon=` | Nearest demo floats |

## Example queries

```text
Show temperature profiles in the Arabian Sea
Show temperature and salinity profiles in the Arabian Sea
Float 4903775
Show density in the Indian Ocean
What are the nearest ARGO floats to 12N, 64E?
```

## Production upgrade path

For a research/production version, the next layer should be:

1. Real ARGO/Argovis data ingestion
2. Persistent object storage for downloaded NetCDF/CSV data
3. Background data-processing jobs for large datasets
4. Hosted LLM integration instead of local Ollama
5. User authentication/OAuth
6. Cached query results and rate limiting
7. More advanced oceanographic calculations such as mixed-layer depth, thermocline, halocline and stratification

The V3 architecture deliberately keeps the serverless API lightweight enough for a Vercel deployment while leaving the data engine isolated for those upgrades.
