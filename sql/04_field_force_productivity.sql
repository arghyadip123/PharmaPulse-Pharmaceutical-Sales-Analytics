-- 2026 YTD field productivity: sales, sales goal, and customer coverage.
WITH rev AS (
    SELECT rep_id, SUM(net_sales_inr) AS revenue_inr
    FROM sales WHERE month BETWEEN '2026-01' AND '2026-10'
    GROUP BY rep_id
), goal AS (
    SELECT rep_id, SUM(target_inr) AS target_inr
    FROM targets WHERE month BETWEEN '2026-01' AND '2026-10'
    GROUP BY rep_id
), coverage AS (
    SELECT rep_id, SUM(planned_visits) AS planned_visits,
           SUM(completed_visits) AS completed_visits
    FROM visits WHERE month BETWEEN '2026-01' AND '2026-10'
    GROUP BY rep_id
)
SELECT r.rep_id, r.rep_name, g.region_name,
       ROUND(rev.revenue_inr, 2) AS revenue_inr,
       goal.target_inr,
       ROUND(100.0 * rev.revenue_inr / NULLIF(goal.target_inr, 0), 1) AS target_attainment_pct,
       coverage.planned_visits, coverage.completed_visits,
       ROUND(100.0 * coverage.completed_visits / NULLIF(coverage.planned_visits, 0), 1) AS visit_completion_pct
FROM reps r JOIN regions g ON r.region_id = g.region_id
JOIN rev ON rev.rep_id=r.rep_id
JOIN goal ON goal.rep_id=r.rep_id
JOIN coverage ON coverage.rep_id=r.rep_id
ORDER BY target_attainment_pct DESC;
