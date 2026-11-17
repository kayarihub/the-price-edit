<div align="center">

# 🎀 The Price Edit
### Beauty Retail Pricing & Margin Optimization 💗

**Python · SQL · Price Elasticity · Gross Margin · Retail Analytics**

*Chic pricing decisions, measurable business logic.* ✨

</div>

## 🩷 Project overview

**The Price Edit** is a reproducible portfolio simulation evaluating **540 candidate prices across 60 fictional retail products** in Skincare, Fragrance, Makeup, Haircare, and Accessories. The project models how pricing changes could affect weekly demand, revenue, and **gross profit**, subject to minimum margin and competitive positioning constraints.

> **All data, demand assumptions, price elasticities, and results are synthetic.** A modeled result is not actual revenue, profit, or validated customer behavior.

## 💗 Results of the pricing simulation

| KPI | Modeled result |
|---|---:|
| Products evaluated | **60** |
| Candidate pricing scenarios | **540** |
| Baseline weekly gross profit | $241,146.30 |
| Recommended modeled weekly gross profit | $252,161.30 |
| Modeled weekly gross profit improvement | **$11,015 / 4.57%** |
| Highest category percentage improvement | **Makeup: 11.86%** |

## 💻 Reproduce it

Python 3.9+ and **standard library only**.

```bash
python3 src/analyze.py
python3 -m unittest discover -s tests
open dashboard/index.html
```

The generator creates a fictional product catalog, 540 scenario rows, SKU recommendations, a SQLite database, JSON summary, and interactive HTML dashboard.

## 🌸 Pricing method

We simulate nine candidate prices per SKU, ranging from **−20% to +20%** in 5-point increments. Price elasticity is an **assumed parameter**, not an empirical estimate.

```text
modeled_units = baseline_units × (candidate_price / baseline_price) ^ assumed_elasticity
modeled_revenue = candidate_price × modeled_units
modeled_gross_profit = (candidate_price − unit_cost) × modeled_units
```

For each product, choose the candidate with the largest modeled weekly gross profit that meets both constraints:

- **Gross margin ≥ 30%**
- **Candidate price ≤ 112% of fictional competitor price**

## ⭐ STAR interview explanation

**Situation:** A fictional retail assortment needed a pricing strategy balancing customer price sensitivity, competitive positioning, and profitability.

**Task:** Find the best modeled price per SKU without violating margin and competitor constraints.

**Action:** Built a Python scenario simulation, analyzed pricing recommendations with SQL, and visualized category opportunities in an interactive dashboard.

**Result:** Identified recommendations associated with a **4.57% modeled weekly gross-profit uplift ($11,015)**. This is a synthetic scenario finding, not realized business impact.

## 🎀 Files

- [Python pricing model](src/analyze.py)
- [SQL pricing analyses](sql/pricing_analysis.sql)
- [Automated tests](tests/test_analyze.py)
- [Interactive dashboard source](dashboard/template.html)

Generated files include `data/synthetic_product_catalog.csv`, `data/synthetic_price_scenarios.csv`, `outputs/sku_recommendations.csv`, `outputs/summary.json`, `outputs/pricing_analysis.sqlite`, and `dashboard/index.html`.

## ⚠️ Analytical limitations

This is not an observed business case. The constant-elasticity model omits inventory, promotions, taxes, returns, seasonality, and competitor response. Gross profit excludes all costs beyond modeled unit product cost. Actual pricing decisions would require empirical elasticity estimates and controlled tests.

*Made for portfolio learning and communication.* 🎀
