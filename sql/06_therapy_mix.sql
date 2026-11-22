-- Therapy mix of sample net sales for 2026 Jan-Oct.
SELECT p.therapy_area, ROUND(SUM(s.net_sales_inr), 2) AS revenue_inr,
       ROUND(100.0 * SUM(s.net_sales_inr) /
       (SELECT SUM(net_sales_inr) FROM sales WHERE month BETWEEN '2026-01' AND '2026-10'), 1) AS share_pct
FROM sales s JOIN products p ON s.product_id=p.product_id
WHERE s.month BETWEEN '2026-01' AND '2026-10'
GROUP BY p.therapy_area
ORDER BY revenue_inr DESC;
