"""Recompute source-independent funnel statistics and validation report from CSV."""
import csv
import json
from collections import defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
METRICS = ("impressions", "clicks", "leads", "qualified_leads", "customers", "spend_pkr")


def aggregate(rows):
    return {key: round(sum(float(row[key]) for row in rows), 2) for key in METRICS}


def load_rows():
    with (ROOT / "data" / "campaign_funnel.csv").open(encoding="utf-8", newline="") as stream:
        records = list(csv.DictReader(stream))
    assert records, "CSV must contain records"
    for row in records:
        date.fromisoformat(row["date"])
        funnel = [int(row[key]) for key in METRICS[:5]]
        assert all(a >= b >= 0 for a, b in zip(funnel, funnel[1:])), f"Invalid funnel: {row}"
        assert float(row["spend_pkr"]) >= 0
    return records


def main():
    rows = load_rows()
    april = [r for r in rows if r["date"].startswith("2024-04")]
    march = [r for r in rows if r["date"].startswith("2024-03")]
    now, previous = aggregate(april), aggregate(march)
    source = {s: aggregate([r for r in april if r["source"] == s]) for s in sorted({r["source"] for r in rows})}
    stages = METRICS[:5]
    losses = [{"from": stages[i], "to": stages[i + 1], "lost": int(now[stages[i]] - now[stages[i + 1]]), "drop_off_pct": round((1 - now[stages[i + 1]] / now[stages[i]]) * 100, 2)} for i in range(4)]
    # A large absolute loss can occur at a different stage than the highest percentage drop.
    biggest = max(losses, key=lambda x: x["lost"])
    result = {"notice": "SIMULATED portfolio data; no actual business performance is implied", "records": len(rows), "period": "2024-04-01 to 2024-04-30", "previous_period": "2024-03-01 to 2024-03-31", "current": now, "previous": previous, "sources": source, "stage_losses": losses, "biggest_absolute_loss": biggest, "overall_conversion_pct": round(now["customers"] / now["impressions"] * 100, 4)}
    (ROOT / "reports" / "analysis.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    lines = ["# Marketing Funnel & Conversion Performance — analysis", "", "**Data:** deterministic simulation for training. Figures describe the synthetic dataset, not real customers or verified campaign results.", "", f"April 2024: **{int(now['impressions']):,}** impressions → **{int(now['clicks']):,}** clicks → **{int(now['leads']):,}** leads → **{int(now['qualified_leads']):,}** qualified leads → **{int(now['customers']):,}** customers. Overall conversion: **{result['overall_conversion_pct']:.2f}%**.", "", "## Stage losses", "", "| From → To | Lost | Drop-off |", "|---|---:|---:|"]
    for loss in losses:
        lines.append(f"| {loss['from'].replace('_', ' ').title()} → {loss['to'].replace('_', ' ').title()} | {loss['lost']:,} | {loss['drop_off_pct']:.1f}% |")
    lines += ["", f"Largest absolute loss: **{biggest['from'].replace('_', ' ').title()} → {biggest['to'].replace('_', ' ').title()}**, losing **{biggest['lost']:,}**. This is a volume comparison; examine the rates as well.", "", "## Channel performance", "", "| Source | Impressions | Customers | Conversion |", "|---|---:|---:|---:|"]
    for name, numbers in sorted(source.items(), key=lambda pair: pair[1]["customers"], reverse=True):
        lines.append(f"| {name} | {int(numbers['impressions']):,} | {int(numbers['customers']):,} | {numbers['customers'] / numbers['impressions'] * 100:.2f}% |")
    lines += ["", "## Suggested follow-up experiments", "", "1. Test alternative creative and audience segments at the first stage; compare click-through rate and downstream customers before increasing spend.", "2. Audit landing page speed, message and lead-form friction with an A/B test; compare qualified leads and customers, not clicks alone.", "3. Test follow-up timing and lead qualification rules, while checking whether any changes affect lead quality.", "", "**Caution:** These are hypotheses to test. Observed funnel counts cannot establish that a specific intervention caused a change. No revenue or ROI claims are made.", ""]
    (ROOT / "reports" / "analysis.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"Validated {len(rows):,} rows; April customers: {int(now['customers']):,}; overall conversion: {result['overall_conversion_pct']:.2f}%")


if __name__ == "__main__":
    main()
