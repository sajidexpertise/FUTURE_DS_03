"""Deterministic, explicitly simulated marketing funnel data for a portfolio demo."""
import csv
import json
import random
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCES = {
    "Paid Search": (380, .37, .42, .165, .39, 1.7),
    "Organic Search": (260, .34, .38, .145, .39, .35),
    "Paid Social": (310, .31, .34, .104, .35, 1.05),
    "Email": (110, .48, .38, .205, .43, .48),
    "Display": (210, .25, .30, .090, .32, .68),
}
DEVICES = {"Desktop": 1.1, "Mobile": .78, "Tablet": .87}
FIELDS = ["date", "source", "device", "campaign", "impressions", "clicks", "leads", "qualified_leads", "customers", "spend_pkr"]


def make_rows():
    rng = random.Random(50326)
    rows = []
    for offset in range(90):  # February–April 2024; March is April's comparator.
        day = date(2024, 2, 1) + timedelta(days=offset)
        for source, (base, ctr, lead_rate, qualify_rate, close_rate, cpc) in SOURCES.items():
            for device, factor in DEVICES.items():
                impressions = round(base * {"Desktop": 1.0, "Mobile": 1.5, "Tablet": .28}[device] * rng.uniform(.75, 1.25) * (1.05 if day.month == 4 else 1))
                clicks = max(0, min(impressions, round(impressions * ctr * factor * rng.uniform(.87, 1.13))))
                leads = max(0, min(clicks, round(clicks * lead_rate * rng.uniform(.80, 1.20))))
                qualified = max(0, min(leads, round(leads * qualify_rate * rng.uniform(.72, 1.28))))
                customers = max(0, min(qualified, round(qualified * close_rate * rng.uniform(.74, 1.26))))
                rows.append([day.isoformat(), source, device, source + " / " + device, impressions, clicks, leads, qualified, customers, round(clicks * cpc * 100, 2)])
    return rows


def main():
    rows = make_rows()
    with (ROOT / "data" / "campaign_funnel.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(FIELDS)
        writer.writerows(rows)
    records = [dict(zip(FIELDS, row)) for row in rows]
    (ROOT / "dashboard" / "data.js").write_text("window.FUNNEL_DATA = " + json.dumps(records, separators=(",", ":")) + ";\n", encoding="utf-8")
    print(f"Generated {len(rows):,} simulated daily campaign segments in data/campaign_funnel.csv and dashboard/data.js")


if __name__ == "__main__":
    main()
