"""The Price Edit: reproducible, entirely synthetic retail pricing simulation."""
import csv
import json
import random
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "outputs"
DASH = ROOT / "dashboard"
for folder in (DATA, OUT, DASH):
    folder.mkdir(parents=True, exist_ok=True)

CATEGORIES = {
    "Skincare": (46, .41, -1.85),
    "Fragrance": (112, .47, -1.32),
    "Makeup": (33, .36, -2.25),
    "Haircare": (38, .38, -1.68),
    "Accessories": (64, .48, -1.48),
}
MULTIPLIERS = [.80,.85,.90,.95,1.00,1.05,1.10,1.15,1.20]
SEED = 20261117

def dollars(value):
    return round(value + 1e-9, 2)

def units_at_price(base_units, price, base_price, elasticity):
    """Constant-elasticity simulation, NOT empirically estimated demand."""
    return max(0, base_units * (price / base_price) ** elasticity)

def select_optimum(options):
    """Choose gross-profit maximum satisfying margin and competitor guardrails."""
    qualified = [x for x in options if x["gross_margin_pct"] >= 30 and x["price"] <= x["competitor_price"] * 1.12 + 1e-8]
    return max(qualified, key=lambda x: (x["weekly_gross_profit"], -abs(x["price_change_pct"]))) if qualified else None

def save_csv(path, rows):
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

def main():
    rng = random.Random(SEED)
    catalog, scenarios, recommendations = [], [], []
    for category_idx, (category, (anchor, cost_ratio, elasticity)) in enumerate(CATEGORIES.items()):
        for n in range(12):
            sku = f"PE-{category_idx+1:02d}-{n+1:03d}"
            base_price = dollars(anchor * (.76 + n * .043) * (1 + rng.uniform(-.05, .05)))
            unit_cost = dollars(base_price * (cost_ratio + rng.uniform(-.035, .035)))
            competitor_price = dollars(base_price * (1 + rng.uniform(-.09, .12)))
            base_units = round(52 + rng.randint(0, 140) * (1.05 - .01 * n), 1)
            own_elasticity = round(elasticity + rng.uniform(-.24, .24), 2)
            product = dict(sku=sku, category=category, product_name=f"{category} Studio {n+1:02d}", base_price=base_price, unit_cost=unit_cost, competitor_price=competitor_price, baseline_weekly_units=base_units, assumed_elasticity=own_elasticity)
            catalog.append(product)
            product_scenarios = []
            for multiplier in MULTIPLIERS:
                price = dollars(base_price * multiplier)
                estimated_units = units_at_price(base_units, price, base_price, own_elasticity)
                revenue = price * estimated_units
                gross_profit = (price - unit_cost) * estimated_units
                margin = 100 * gross_profit / revenue if revenue else 0
                scenario = dict(sku=sku, category=category, price=price, price_change_pct=round((price / base_price - 1) * 100, 2), competitor_price=competitor_price, assumed_elasticity=own_elasticity, modeled_weekly_units=round(estimated_units, 3), weekly_revenue=dollars(revenue), weekly_gross_profit=dollars(gross_profit), gross_margin_pct=round(margin, 2), eligible=int(margin >= 30 and price <= competitor_price * 1.12 + 1e-8))
                product_scenarios.append(scenario)
                scenarios.append(scenario)
            baseline = next(x for x in product_scenarios if abs(x["price_change_pct"]) < .01)
            best = select_optimum(product_scenarios)
            if best is None:
                raise RuntimeError(f"No feasible pricing scenario for {sku}")
            recommendations.append(dict(sku=sku, category=category, baseline_price=base_price, recommended_price=best["price"], price_change_pct=best["price_change_pct"], assumed_elasticity=own_elasticity, baseline_weekly_units=base_units, modeled_weekly_units=best["modeled_weekly_units"], baseline_weekly_revenue=baseline["weekly_revenue"], modeled_weekly_revenue=best["weekly_revenue"], baseline_weekly_gross_profit=baseline["weekly_gross_profit"], modeled_weekly_gross_profit=best["weekly_gross_profit"], modeled_profit_lift=dollars(best["weekly_gross_profit"] - baseline["weekly_gross_profit"]), modeled_profit_lift_pct=round(100 * (best["weekly_gross_profit"] / baseline["weekly_gross_profit"] - 1), 2), recommended_margin_pct=best["gross_margin_pct"]))

    save_csv(DATA / "synthetic_product_catalog.csv", catalog)
    save_csv(DATA / "synthetic_price_scenarios.csv", scenarios)
    save_csv(OUT / "sku_recommendations.csv", recommendations)

    database = sqlite3.connect(OUT / "pricing_analysis.sqlite")
    for table_name, rows in [("products", catalog), ("price_scenarios", scenarios), ("recommendations", recommendations)]:
        database.execute(f"DROP TABLE IF EXISTS {table_name}")
        fields = list(rows[0])
        types = []
        for field in fields:
            value = rows[0][field]
            dtype = "INTEGER" if isinstance(value, int) else "REAL" if isinstance(value, float) else "TEXT"
            types.append(f'"{field}" {dtype}')
        database.execute(f'CREATE TABLE {table_name} ({", ".join(types)})')
        database.executemany(f'INSERT INTO {table_name} VALUES ({", ".join("?" for _ in fields)})', [[r[field] for field in fields] for r in rows])
    database.commit()
    database.close()

    p0 = sum(x["baseline_weekly_gross_profit"] for x in recommendations)
    p1 = sum(x["modeled_weekly_gross_profit"] for x in recommendations)
    r0 = sum(x["baseline_weekly_revenue"] for x in recommendations)
    r1 = sum(x["modeled_weekly_revenue"] for x in recommendations)
    category_data = []
    for category in CATEGORIES:
        rows = [r for r in recommendations if r["category"] == category]
        category_p0 = sum(x["baseline_weekly_gross_profit"] for x in rows)
        category_p1 = sum(x["modeled_weekly_gross_profit"] for x in rows)
        category_data.append(dict(category=category, skus=len(rows), baseline_profit=dollars(category_p0), modeled_profit=dollars(category_p1), modeled_lift_pct=round((category_p1 / category_p0 - 1) * 100, 2)))
    metrics = dict(synthetic=True, sku_count=len(catalog), scenario_count=len(scenarios), weekly_baseline_revenue=dollars(r0), weekly_modeled_revenue=dollars(r1), weekly_baseline_gross_profit=dollars(p0), weekly_modeled_gross_profit=dollars(p1), modeled_weekly_profit_lift=dollars(p1 - p0), modeled_profit_lift_pct=round((p1 / p0 - 1) * 100, 2), price_changes_count=sum(x["price_change_pct"] != 0 for x in recommendations), margin_floor_pct=30, competitor_price_cap_multiple=1.12, category_summary=category_data)
    (OUT / "summary.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    payload = json.dumps(dict(metrics=metrics, recommendations=recommendations), ensure_ascii=True).replace("</", "<\\/")
    template = (DASH / "template.html").read_text(encoding="utf-8")
    (DASH / "index.html").write_text(template.replace("/*DATA_PAYLOAD*/", payload), encoding="utf-8")
    print(json.dumps({k: v for k, v in metrics.items() if k != "category_summary"}, indent=2))

if __name__ == "__main__":
    main()
