-- Latest available month only.  Below-threshold inventory needs review.
SELECT i.month, r.region_name, p.product_name, p.therapy_area,
       i.stock_units, p.reorder_level_units,
       (p.reorder_level_units-i.stock_units) AS shortage_units
FROM inventory i
JOIN products p ON i.product_id=p.product_id
JOIN regions r ON i.region_id=r.region_id
WHERE i.month=(SELECT MAX(month) FROM inventory)
  AND i.stock_units < p.reorder_level_units
ORDER BY shortage_units DESC;
