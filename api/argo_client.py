"""Server-side client for real Argo profiles served by Argovis."""
from __future__ import annotations
from datetime import datetime, timedelta, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import json
import os
import time

BASE_URL = "https://argovis-api.colorado.edu"
REGION_BOXES = {
    "arabian sea": [[50, 5], [78, 28]],
    "bay of bengal": [[80, 5], [95, 22]],
    "indian ocean": [[20, -40], [120, 30]],
    "north atlantic": [[-80, 0], [20, 70]],
    "south atlantic": [[-70, -60], [20, 0]],
}

class ArgovisError(RuntimeError):
    pass

class ArgovisClient:
    def __init__(self, timeout: int = 22, cache_seconds: int = 600):
        self.api_key = os.getenv("ARGOVIS_API_KEY", "guest").strip() or "guest"
        self.timeout = timeout
        self.cache_seconds = cache_seconds
        self._cache: dict[str, tuple[float, list[dict]]] = {}

    def _get_json(self, params: dict) -> list[dict]:
        url = f"{BASE_URL}/argo?{urlencode(params)}"
        request = Request(url, headers={
            "Accept": "application/json",
            "User-Agent": "ARGONAUT-AI/3.2",
            "x-argokey": self.api_key,
        })
        try:
            with urlopen(request, timeout=self.timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:400]
            if exc.code == 429:
                raise ArgovisError("Argovis rate limit reached. Add a personal API key or retry later.") from exc
            raise ArgovisError(f"Argovis HTTP {exc.code}: {detail}") from exc
        except (URLError, TimeoutError) as exc:
            raise ArgovisError(f"Could not reach Argovis: {exc}") from exc
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ArgovisError("Argovis returned an unreadable response.") from exc
        if not isinstance(payload, list):
            raise ArgovisError("Argovis returned an unexpected response format.")
        return payload

    @staticmethod
    def _flatten_profiles(payload) -> list[dict]:
        """Normalize Argovis responses that may contain nested profile lists."""
        if isinstance(payload, dict):
            return [payload]
        if isinstance(payload, list):
            profiles = []
            for item in payload:
                profiles.extend(ArgovisClient._flatten_profiles(item))
            return profiles
        return []

    @staticmethod
    def _profile_rows(profile: dict) -> list[dict]:
        if not isinstance(profile, dict):
            return []
        data, info = profile.get("data") or [], profile.get("data_info") or []
        if not isinstance(data, list) or not isinstance(info, list):
            return []
        keys = info[0] if info and isinstance(info[0], list) else []
        if not data or not keys:
            return []
        aliases = {
            "pressure": ("pressure", "pres"),
            "temperature": ("temperature", "temp"),
            "salinity": ("salinity", "psal"),
        }
        lower = [str(k).lower() for k in keys]
        indexes = {}
        for name, candidates in aliases.items():
            for candidate in candidates:
                if candidate in lower:
                    indexes[name] = lower.index(candidate)
                    break
        pidx = indexes.get("pressure")
        if pidx is None or pidx >= len(data) or not isinstance(data[pidx], list):
            return []
        pressures = data[pidx]
        geo = (profile.get("geolocation") or {}).get("coordinates") or []
        profile_id = str(profile.get("_id", ""))
        wmo = profile_id.split("_")[0] if profile_id else str(profile.get("platform", "unknown"))
        rows = []
        for i, pressure in enumerate(pressures):
            if pressure is None:
                continue
            row = {
                "wmo": wmo,
                "cycle": profile.get("cycle_number"),
                "time": profile.get("timestamp"),
                "latitude": geo[1] if len(geo) > 1 else None,
                "longitude": geo[0] if geo else None,
                "pressure": pressure,
            }
            for variable in ("temperature", "salinity"):
                idx = indexes.get(variable)
                if idx is not None and idx < len(data) and i < len(data[idx]):
                    row[variable] = data[idx][i]
            rows.append(row)
        return rows

    def fetch(self, wmo: str | None = None, region: str = "global") -> list[dict]:
        cache_key = f"{wmo or 'region'}:{region.lower()}"
        cached = self._cache.get(cache_key)
        if cached and time.time() - cached[0] < self.cache_seconds:
            return cached[1]

        now = datetime.now(timezone.utc)
        params = {
            # Request only good-QC temperature and salinity levels.
            # Pressure is included by Argovis as the vertical coordinate.
            "data": "temperature,1,salinity,1",
            "compression": "minimal",
        }
        if wmo:
            params["platform"] = str(wmo)
            params["startDate"] = (now - timedelta(days=365)).strftime("%Y-%m-%dT%H:%M:%SZ")
            params["endDate"] = now.strftime("%Y-%m-%dT%H:%M:%SZ")
            profiles = self._get_json(params)
        else:
            box = REGION_BOXES.get(region.lower())
            if box:
                params["box"] = json.dumps(box, separators=(",", ":"))
            profiles = None
            last_error = None
            for days in (30, 14, 7, 3):
                params["startDate"] = (now - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
                params["endDate"] = now.strftime("%Y-%m-%dT%H:%M:%SZ")
                try:
                    profiles = self._get_json(params)
                    break
                except ArgovisError as exc:
                    last_error = exc
                    if "HTTP 400" not in str(exc):
                        raise
            if profiles is None:
                raise last_error or ArgovisError("Argovis returned no result.")
        normalized_profiles = self._flatten_profiles(profiles)
        rows = [row for profile in normalized_profiles for row in self._profile_rows(profile)]
        self._cache[cache_key] = (time.time(), rows)
        return rows
