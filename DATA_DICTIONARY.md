# Data dictionary & calculation notes

All values are synthetic. Generated with `scripts/generate_sample_data.py` (fixed seed `20261122`). Date coverage: 2025-01 through 2026-10 inclusive. Currency: Indian Rupees (INR). All example products and employees are fabricated.

## Source files

| File | Grain | Important columns |
|---|---|---|
| `data/raw/products.csv` | One row per product | `product_id`, `product_name`, `therapy_area`, `list_price_inr`, `reorder_level_units` |
| `data/raw/regions.csv` | One row per region | `region_id`, `region_name`, `city_1`, `city_2` |
| `data/raw/sales_reps.csv` | One row per field employee | `rep_id`, `rep_name`, `region_id`, `role` |
| `data/raw/raw_sales.csv` | Raw transaction rows, including duplicates | `transaction_id`, `sale_date`, `rep_id`, `region_id`, `product_id`, `units_sold`, `unit_price_inr`, `discount_pct`, `returned_units` |
| `data/raw/targets.csv` | One row per month & rep | `month`, `rep_id`, `target_inr` |
| `data/raw/field_visits.csv` | One row per month & rep | `month`, `rep_id`, `planned_visits`, `completed_visits` |
| `data/raw/inventory.csv` | One row per month, product & region | `month`, `region_id`, `product_id`, `stock_units` |

## Cleaned fact tables

`data/processed/sales.csv` includes the original transaction keys plus:

| Column | Definition |
|---|---|
| `month` | Calendar month `YYYY-MM` derived from sale_date |
| `net_units` | `units_sold - returned_units` |
| `net_sales_inr` | `ROUND(net_units × unit_price_inr × (1 − discount_pct), 2)` |

`data/processed/sales_enriched.csv` adds readable labels for region, representative, product and therapy (helpful for a flat Excel sheet / HTML dashboard).

## Quality and assumptions

- Remove duplicate transaction IDs, retaining the first raw occurrence. Raw input is deterministic; if a real pipeline needs late-arriving corrections, choose a documented latest-update rule instead.
- Trim and uppercase `region_id` so ` r01 ` maps to `R01`.
- Replace missing discounts with `0`. This is a **fictional exercise rule**, not universal business practice. For genuine data, request business-owner approval for imputation.
- Reject rows with invalid dates, unknown IDs, zero/negative sold units or prices, returned units above sold units, and discounts outside 0–50%.
- Reject any sale assigned to a region that does not match the representative's registered region.
- Target attainment is only appropriate for all products combined within the corresponding time/rep/region scope. Product/therapy targets are not present.
- Returns are handled as unit adjustments in the net-sales formula; no refunds, tax or shipment timing is modeled.
- Inventory is a synthetic month-end snapshot, not a reconciled stock ledger. Low stock means `stock_units < reorder_level_units`.
- A planned visit count is not a doctor/customer name or personal record. Visit completion is `completed_visits / planned_visits`; completed visits can exceed plan slightly where a field employee schedules extra visits.

## Reconciliation targets

- Clean data has exactly 4,996 transactions, and all transaction IDs are unique.
- 2026 Jan–Oct `SUM(net_sales_inr)` = **₹21,895,873.40**.
- 2026 Jan–Oct target sum = **₹26,100,000.00**.
- 2026 Jan–Oct net units = **136,380**.
- Dashboard, SQL summary, Excel KPI and Python should agree within rounding tolerance.

## SQL report files

`01_monthly_sales.sql`, `02_region_performance.sql`, `03_product_performance.sql`, `04_field_force_productivity.sql`, `05_inventory_reorder_alerts.sql`, `06_therapy_mix.sql`, `07_monthly_targets.sql`. Each query runs in SQLite and is exported as a CSV under `outputs/reports/`.
