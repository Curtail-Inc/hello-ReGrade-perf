"""Load and validate the video beat script."""
import json
from dataclasses import dataclass


@dataclass(frozen=True)
class Beat:
    id: str
    clip: str
    vo: str


def load_script(path: str) -> list[Beat]:
    with open(path) as f:
        data = json.load(f)
    beats, seen = [], set()
    for raw in data.get("beats", []):
        for field in ("id", "clip", "vo"):
            if field not in raw or not raw[field]:
                raise ValueError(f"beat missing '{field}': {raw}")
        if raw["id"] in seen:
            raise ValueError(f"duplicate beat id: {raw['id']}")
        seen.add(raw["id"])
        beats.append(Beat(id=raw["id"], clip=raw["clip"], vo=raw["vo"]))
    if not beats:
        raise ValueError("no beats in script")
    return beats
