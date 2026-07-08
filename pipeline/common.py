"""Shared helpers for the NYC AI Hiring Atlas pipeline."""

from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent


def load_env() -> None:
    """Load repo-root `.env` into os.environ (does not override existing vars)."""
    env_path = ROOT / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


load_env()
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
CACHE_DIR = ROOT / "data" / "cache"

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
)

HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

REQUEST_DELAY_SECONDS = 0.6


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def polite_get(url: str, session: requests.Session | None = None, **kwargs) -> requests.Response:
    """GET with browser-like headers and a politeness delay."""
    time.sleep(REQUEST_DELAY_SECONDS)
    sess = session or requests
    headers = {**HEADERS, **kwargs.pop("headers", {})}
    return sess.get(url, headers=headers, timeout=30, **kwargs)


def save_raw(name: str, payload) -> Path:
    """Save a raw payload to data/raw with a collection timestamp."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    path = RAW_DIR / name
    if isinstance(payload, (dict, list)):
        path.write_text(json.dumps({"collected_at": now_iso(), "data": payload}, indent=1))
    else:
        path.write_text(payload)
    return path


def load_raw(name: str):
    path = RAW_DIR / name
    if not path.exists():
        return None
    blob = json.loads(path.read_text())
    return blob.get("data")
