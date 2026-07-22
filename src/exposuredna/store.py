from __future__ import annotations
import json
from pathlib import Path
from typing import Any, cast


class JsonStore:
    def __init__(self, workspace: Path) -> None:
        self.workspace = workspace.resolve()
        if not (self.workspace / "workspace.json").is_file():
            raise FileNotFoundError("workspace.json not found")
        self.path = self.workspace / "exposuredna.json"
        if not self.path.exists():
            self.save({"schema_version": "0.1", "organization": None, "entities": [], "relationships": [], "resolution_queue": [], "resolution_decisions": [], "external_correlations": []})

    def load(self) -> dict[str, Any]:
        data = cast(dict[str, Any], json.loads(self.path.read_text(encoding="utf-8")))
        data.setdefault("resolution_decisions", [])
        data.setdefault("external_correlations", [])
        return data

    def save(self, data: dict[str, Any]) -> None:
        t = self.path.with_suffix(".tmp")
        t.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
        t.replace(self.path)
