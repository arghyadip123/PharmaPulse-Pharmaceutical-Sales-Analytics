-- Monthly net revenue / units / transactions, all available periods.
SELECT s.month,
       ROUND(SUM(s.net_sales_inr), 2) AS revenue_inr,
       SUM(s.net_units) AS net_units,
       SUM(s.returned_units) AS returned_units,
       COUNT(*) AS transactions
FROM sales s
GROUP BY s.month
ORDER BY s.month;
