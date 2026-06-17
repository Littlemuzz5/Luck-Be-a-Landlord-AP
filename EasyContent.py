from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


def _package_root() -> Path:
    return Path(__file__).resolve().parent


def _normalise_entry(entry: Dict[str, Any], kind: str, pack_id: str) -> Dict[str, Any]:
    name = str(entry.get("name") or entry.get("display_name") or entry.get("id") or "").strip()
    type_id = str(entry.get("id") or entry.get("type") or name.lower().replace(" ", "_")).strip()
    if not name or not type_id:
        raise ValueError("easy content entries need at least name and id/type")
    rarity = str(entry.get("rarity") or ("essence" if kind == "essence" else "common"))
    data = dict(entry)
    data.update({"name": name, "id": type_id, "type": type_id, "kind": kind, "pack_id": pack_id, "rarity": rarity})
    return data


def _load_manifest(path: Path) -> Dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {"symbols": [], "items": [], "essences": []}
    if not isinstance(data, dict):
        return {"symbols": [], "items": [], "essences": []}
    pack_id = str(data.get("pack_id") or data.get("mod_name") or path.stem)
    out = {"pack_id": pack_id, "symbols": [], "items": [], "essences": []}
    for key, kind in (("symbols", "symbol"), ("items", "item"), ("essences", "essence")):
        values = data.get(key, [])
        if isinstance(values, list):
            for entry in values:
                if isinstance(entry, dict):
                    try:
                        out[key].append(_normalise_entry(entry, kind, pack_id))
                    except Exception:
                        pass
    return out


def load_easy_content() -> Dict[str, Any]:
    root = _package_root() / "mod_content" / "easy_packs"
    packs: List[Dict[str, Any]] = []
    if root.is_dir():
        for path in sorted(root.glob("*.json")):
            if path.name.startswith("example_") or path.name.endswith(".disabled.json"):
                continue
            packs.append(_load_manifest(path))
    symbols: List[Dict[str, Any]] = []
    items: List[Dict[str, Any]] = []
    essences: List[Dict[str, Any]] = []
    for pack in packs:
        symbols.extend(pack.get("symbols", []))
        items.extend(pack.get("items", []))
        essences.extend(pack.get("essences", []))
    return {"packs": packs, "symbols": symbols, "items": items, "essences": essences}


EASY_CONTENT = load_easy_content()
EASY_SYMBOLS = list(EASY_CONTENT.get("symbols", []))
EASY_ITEMS = list(EASY_CONTENT.get("items", []))
EASY_ESSENCES = list(EASY_CONTENT.get("essences", []))
EASY_SYMBOL_NAMES = [entry["name"] for entry in EASY_SYMBOLS]
EASY_ITEM_NAMES = [entry["name"] for entry in EASY_ITEMS]
EASY_ESSENCE_NAMES = [entry["name"] for entry in EASY_ESSENCES]
EASY_NAME_TO_TYPE = {entry["name"]: entry["id"] for entry in EASY_SYMBOLS + EASY_ITEMS + EASY_ESSENCES}
EASY_BY_NAME = {entry["name"]: entry for entry in EASY_SYMBOLS + EASY_ITEMS + EASY_ESSENCES}
EASY_BY_TYPE = {entry["id"]: entry for entry in EASY_SYMBOLS + EASY_ITEMS + EASY_ESSENCES}
