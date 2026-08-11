from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from .models import Dimension, Entity

MAX_BYTES = 10 * 1024 * 1024
SUPPORTED_ADAPTERS = {"ct", "dns", "repo", "package", "oauth", "analytics", "asn", "openapi", "mobile"}


def _read(path: Path) -> str:
    if not path.is_file() or path.is_symlink():
        raise ValueError("collector input must be a regular non-symlink file")
    if path.stat().st_size > MAX_BYTES:
        raise ValueError(f"collector input exceeds {MAX_BYTES} byte limit")
    return path.read_text(encoding="utf-8", errors="replace")


def _eid(adapter: str, value: str) -> str:
    return "ENT-" + hashlib.sha256(f"{adapter}:{value}".encode()).hexdigest()[:14].upper()


def _entity(adapter: str, value: str, entity_type: str, dimension: Dimension, path: Path) -> Entity:
    return Entity(entity_id=_eid(adapter, value), entity_type=entity_type, value=value, dimension=dimension, source=f"adapter:{adapter}", metadata={"artifact": path.name, "adapter": adapter, "source_group": adapter})


def collect_passive(path: Path, adapter: str) -> list[Entity]:
    """Normalize explicit local source exports. No implicit Internet-wide collection occurs."""
    adapter = adapter.lower().strip()
    if adapter not in SUPPORTED_ADAPTERS:
        raise ValueError(f"unsupported passive adapter: {adapter}")
    text = _read(path)
    out: dict[str, Entity] = {}

    if adapter == "openapi":
        openapi_payload = json.loads(text)
        paths = openapi_payload.get("paths", {}) if isinstance(openapi_payload, dict) else {}
        for value in sorted(paths) if isinstance(paths, dict) else []:
            ent = _entity(adapter, str(value), "api_endpoint", Dimension.API, path); out[ent.entity_id] = ent
        return list(out.values())

    if adapter in {"ct", "dns", "oauth", "asn", "analytics"}:
        payload: Any = json.loads(text); serialized = json.dumps(payload, ensure_ascii=False); patterns: list[tuple[str, Dimension, str]] = []
        if adapter in {"ct", "dns"}: patterns.append((r"(?:[A-Za-z0-9-]+\.)+[A-Za-z]{2,63}", Dimension.INFRASTRUCTURE, "domain"))
        if adapter == "oauth": patterns.append((r"https?://[^\s\"']+", Dimension.IDENTITY, "oauth_issuer"))
        if adapter == "asn": patterns.append((r"\bAS\d{1,10}\b", Dimension.INFRASTRUCTURE, "asn"))
        if adapter == "analytics": patterns.append((r"\b(?:UA-\d+-\d+|G-[A-Z0-9]+|GTM-[A-Z0-9]+)\b", Dimension.DEVELOPER, "analytics_id"))
        for pattern, dimension, etype in patterns:
            for value in sorted(set(re.findall(pattern, serialized, flags=re.I))):
                normalized = value.lower() if etype == "domain" else value
                ent = _entity(adapter, normalized, etype, dimension, path); out[ent.entity_id] = ent
        return list(out.values())

    urls = sorted(set(re.findall(r"https?://[^\s\"'<>]+", text)))
    domains = sorted(set(re.findall(r"(?<![@\w.-])(?:[A-Za-z0-9-]+\.)+[A-Za-z]{2,63}(?![\w.-])", text)))
    values = urls if adapter == "repo" else domains + urls
    etype, dimension = ({"repo": ("repository_reference", Dimension.DEVELOPER), "package": ("package_reference", Dimension.SOFTWARE), "mobile": ("mobile_reference", Dimension.API)}).get(adapter, ("reference", Dimension.DEVELOPER))
    for value in values:
        ent = _entity(adapter, value, etype, dimension, path); out[ent.entity_id] = ent
    return list(out.values())
