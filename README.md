# AI-testing-in-cursor

## Hello world

Run:

```bash
python3 hello.py
```

## REMA 1000 Oslo coordinates bot

This bot queries OpenStreetMap (Overpass API) for REMA 1000 supermarkets in Oslo
and returns their coordinates.

Run and print CSV:

```bash
python3 rema1000_oslo_bot.py
```

Run and print JSON:

```bash
python3 rema1000_oslo_bot.py --format json
```

Save to a file:

```bash
python3 rema1000_oslo_bot.py --format json --output rema1000_oslo.json
```
