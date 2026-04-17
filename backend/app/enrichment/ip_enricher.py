from __future__ import annotations

import ipaddress
import json
import threading
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import httpx

from app.core.config import EnrichmentConfig
from app.models.event import LogEvent
from app.storage.sqlite import SQLiteStorage

try:
    import geoip2.database
except ImportError:  # pragma: no cover - optional dependency during partial installs
    geoip2 = None


@dataclass(slots=True)
class EnrichmentRecord:
    country: str | None = None
    is_malicious: bool = False
    reputation_score: int | None = None
    source: str | None = None


_LOOKUP_EXECUTOR = ThreadPoolExecutor(max_workers=2, thread_name_prefix="0xchou00-intel")


class IPEnrichmentService:
    """Apply local and cached IP context without blocking the ingestion path."""

    def __init__(
        self,
        storage: SQLiteStorage | None = None,
        config: EnrichmentConfig | None = None,
    ) -> None:
        self.storage = storage or SQLiteStorage()
        self.config = config or EnrichmentConfig()
        self._blacklist = self._load_static_blacklist(self.config.static_blacklist_path)
        self._reader = self._open_geoip_reader(self.config.geoip_db_path)
        self._pending_lookups: dict[str, Future[Any]] = {}
        self._pending_lock = threading.Lock()

    def enrich(self, event: LogEvent) -> LogEvent:
        if not event.source_ip:
            return event

        ip = event.source_ip
        if ip in self._blacklist:
            event.country = event.country or self._lookup_country(ip) or "unknown"
            event.is_malicious = True
            event.reputation_score = max(int(event.reputation_score or 0), 100)
            event.enrichment_source = "static_blacklist"
            return event

        if self._is_private_or_reserved(ip):
            event.country = event.country or "private"
            event.enrichment_source = event.enrichment_source or "local"
            return event

        cached = self.storage.get_enrichment_cache(ip)
        country = cached.get("country") if cached else None
        is_malicious = bool(cached.get("is_malicious")) if cached else False
        reputation_score = cached.get("reputation_score") if cached else None
        source = cached.get("source") if cached else None

        geo_country = self._lookup_country(ip)
        if geo_country and not country:
            country = geo_country
            source = source or "geoip"

        if not cached and self.config.abuseipdb_api_key:
            self._schedule_external_lookup(ip)

        event.country = country
        event.is_malicious = is_malicious
        event.reputation_score = reputation_score
        event.enrichment_source = source
        return event

    def _schedule_external_lookup(self, ip: str) -> None:
        with self._pending_lock:
            future = self._pending_lookups.get(ip)
            if future and not future.done():
                return
            self._pending_lookups[ip] = _LOOKUP_EXECUTOR.submit(self._refresh_external_intel, ip)

    def _refresh_external_intel(self, ip: str) -> None:
        try:
            payload = self._lookup_abuseipdb(ip)
            if payload is None:
                return

            merged = {
                "country": payload.get("country") or self._lookup_country(ip),
                "is_malicious": payload.get("is_malicious", False),
                "reputation_score": payload.get("reputation_score"),
                "source": payload.get("source", "abuseipdb"),
                "payload": payload,
                "expires_at": (
                    datetime.now(timezone.utc) + timedelta(seconds=self.config.cache_ttl_seconds)
                ).isoformat(),
            }
            self.storage.upsert_enrichment_cache(ip, merged)
        finally:
            with self._pending_lock:
                self._pending_lookups.pop(ip, None)

    def _lookup_abuseipdb(self, ip: str) -> dict[str, Any] | None:
        if not self.config.abuseipdb_api_key:
            return None

        try:
            with httpx.Client(timeout=self.config.abuseipdb_timeout_seconds) as client:
                response = client.get(
                    self.config.abuseipdb_url,
                    params={"ipAddress": ip, "maxAgeInDays": 90},
                    headers={
                        "Accept": "application/json",
                        "Key": self.config.abuseipdb_api_key,
                    },
                )
                response.raise_for_status()
        except Exception:
            return None

        body = response.json()
        data = body.get("data", {})
        score = int(data.get("abuseConfidenceScore") or 0)
        return {
            "country": data.get("countryCode"),
            "is_malicious": score >= self.config.malicious_score_threshold,
            "reputation_score": score,
            "source": "abuseipdb",
            "payload": data,
        }

    def _lookup_country(self, ip: str) -> str | None:
        if self._reader is None:
            return None

        try:
            city = self._reader.city(ip)
        except Exception:
            return None
        return city.country.iso_code or city.country.name

    def _open_geoip_reader(self, path: Path):
        if geoip2 is None or not path.exists():
            return None
        try:
            return geoip2.database.Reader(str(path))
        except Exception:
            return None

    def _load_static_blacklist(self, path: Path) -> set[str]:
        if not path.exists():
            return set()
        return {
            line.strip()
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.strip().startswith("#")
        }

    def _is_private_or_reserved(self, value: str) -> bool:
        try:
            address = ipaddress.ip_address(value)
        except ValueError:
            return False
        return (
            address.is_private
            or address.is_loopback
            or address.is_reserved
            or address.is_multicast
            or address.is_link_local
        )
