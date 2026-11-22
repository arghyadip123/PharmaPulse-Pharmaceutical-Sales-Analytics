-- Best selling fictional products, 2026 Jan-Oct.
SELECT p.product_name, p.therapy_area,
       ROUND(SUM(s.net_sales_inr), 2) AS revenue_inr,
       SUM(s.net_units) AS units,
       SUM(s.returned_units) AS returned_units
FROM sales s JOIN products p ON s.product_id=p.product_id
WHERE s.month BETWEEN '2026-01' AND '2026-10'
GROUP BY p.product_id
ORDER BY revenue_inr DESC;
