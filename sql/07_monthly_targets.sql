-- Aggregate monthly targets versus actual net sales.
WITH a AS (SELECT month, SUM(net_sales_inr) AS revenue_inr FROM sales GROUP BY month),
     t AS (SELECT month, SUM(target_inr) AS target_inr FROM targets GROUP BY month)
SELECT a.month, ROUND(a.revenue_inr, 2) AS revenue_inr, t.target_inr,
       ROUND(100.0 * a.revenue_inr / NULLIF(t.target_inr, 0), 1) AS attainment_pct
FROM a JOIN t ON a.month=t.month ORDER BY a.month;
