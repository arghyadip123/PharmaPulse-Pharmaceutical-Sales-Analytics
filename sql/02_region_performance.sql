-- Current reporting period: January–October 2026. Compare regional revenue to targets.
WITH rev AS (
    SELECT s.region_id, ROUND(SUM(s.net_sales_inr), 2) AS revenue_inr,
           SUM(s.net_units) AS units, COUNT(*) AS transactions
    FROM sales s WHERE s.month BETWEEN '2026-01' AND '2026-10'
    GROUP BY s.region_id
), goal AS (
    SELECT x.region_id, SUM(t.target_inr) AS target_inr
    FROM targets t JOIN reps x ON t.rep_id = x.rep_id
    WHERE t.month BETWEEN '2026-01' AND '2026-10'
    GROUP BY x.region_id
)
SELECT r.region_name, rev.revenue_inr, goal.target_inr,
       ROUND(100.0 * rev.revenue_inr / NULLIF(goal.target_inr, 0), 1) AS attainment_pct,
       rev.units, rev.transactions
FROM rev JOIN regions r ON rev.region_id = r.region_id
JOIN goal ON rev.region_id = goal.region_id
ORDER BY rev.revenue_inr DESC;
