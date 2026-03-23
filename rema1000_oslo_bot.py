#!/usr/bin/env python3
"""Fetch coordinates for REMA 1000 stores in Oslo from OpenStreetMap."""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass

OVERPASS_URL = "https://overpass-api.de/api/interpreter"


@dataclass(frozen=True)
class Store:
    name: str
    latitude: float
    longitude: float


def build_query() -> str:
    return """
[out:json][timeout:25];
area["name"="Oslo"]["boundary"="administrative"]->.searchArea;
(
  node["shop"="supermarket"]["name"~"^REMA 1000", i](area.searchArea);
  way["shop"="supermarket"]["name"~"^REMA 1000", i](area.searchArea);
  relation["shop"="supermarket"]["name"~"^REMA 1000", i](area.searchArea);
);
out center tags;
""".strip()


def fetch_stores() -> list[Store]:
    data = urllib.parse.urlencode({"data": build_query()}).encode("utf-8")
    request = urllib.request.Request(OVERPASS_URL, data=data, method="POST")

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Network error while calling Overpass API: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError("Received invalid JSON from Overpass API.") from exc

    stores: list[Store] = []
    seen: set[tuple[str, float, float]] = set()
    for element in payload.get("elements", []):
        tags = element.get("tags", {})
        name = tags.get("name", "REMA 1000")

        if "lat" in element and "lon" in element:
            lat = element["lat"]
            lon = element["lon"]
        else:
            center = element.get("center")
            if not center:
                continue
            lat = center.get("lat")
            lon = center.get("lon")

        if lat is None or lon is None:
            continue

        key = (name, float(lat), float(lon))
        if key in seen:
            continue
        seen.add(key)
        stores.append(Store(name=name, latitude=float(lat), longitude=float(lon)))

    stores.sort(key=lambda s: (s.name.lower(), s.latitude, s.longitude))
    return stores


def format_csv(stores: list[Store]) -> str:
    lines = ["name,latitude,longitude"]
    for store in stores:
        lines.append(f"{store.name},{store.latitude:.6f},{store.longitude:.6f}")
    return "\n".join(lines)


def format_json(stores: list[Store]) -> str:
    payload = [
        {"name": s.name, "latitude": s.latitude, "longitude": s.longitude}
        for s in stores
    ]
    return json.dumps(payload, indent=2, ensure_ascii=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Get coordinates for REMA 1000 stores in Oslo."
    )
    parser.add_argument(
        "--format",
        choices=("csv", "json"),
        default="csv",
        help="Output format (default: csv).",
    )
    parser.add_argument(
        "--output",
        help="Optional output file path. Prints to stdout when omitted.",
    )
    args = parser.parse_args()

    try:
        stores = fetch_stores()
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    output = format_json(stores) if args.format == "json" else format_csv(stores)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as file_handle:
            file_handle.write(output + "\n")
    else:
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
