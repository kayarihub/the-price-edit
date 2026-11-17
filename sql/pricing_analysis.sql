-- THE PRICE EDIT | SQLite pricing and modeled margin analysis
-- Run python3 src/analyze.py first; open outputs/pricing_analysis.sqlite

-- 1. Portfolio summary: modeled gross profit improvement (not observed results)
SELECT COUNT(*) AS skus,
       ROUND(SUM(baseline_weekly_gross_profit),2) AS baseline_weekly_profit,
       ROUND(SUM(modeled_weekly_gross_profit),2) AS modeled_weekly_profit,
       ROUND(100.0*(SUM(modeled_weekly_gross_profit)/SUM(baseline_weekly_gross_profit)-1),2) AS modeled_profit_lift_pct
FROM recommendations;

-- 2. Largest modeled profit opportunities
SELECT sku, category, baseline_price, recommended_price,
       price_change_pct, modeled_profit_lift, modeled_profit_lift_pct
FROM recommendations
ORDER BY modeled_profit_lift DESC LIMIT 10;

-- 3. Scenario performance by category
SELECT category, COUNT(*) AS skus,
       ROUND(SUM(baseline_weekly_revenue),2) AS baseline_revenue,
       ROUND(SUM(modeled_weekly_revenue),2) AS modeled_revenue,
       ROUND(SUM(modeled_profit_lift),2) AS modeled_profit_lift
FROM recommendations GROUP BY category ORDER BY modeled_profit_lift DESC;

-- 4. Check every recommended price is an eligible scenario
SELECT r.sku, r.recommended_price, s.eligible, s.gross_margin_pct
FROM recommendations r JOIN price_scenarios s
  ON r.sku=s.sku AND r.recommended_price=s.price
WHERE s.eligible=0;
