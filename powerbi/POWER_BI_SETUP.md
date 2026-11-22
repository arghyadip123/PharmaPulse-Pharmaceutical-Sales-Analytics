# Build the Power BI report (Power BI Desktop, Windows)

**Important:** The download contains real, working Python/SQL/Excel/HTML deliverables plus ready-to-import Power BI tables. It does **not** contain a `.pbix` file because creating a native `.pbix` report requires Power BI Desktop and must be done in that application. Do not claim the Power BI report exists until you create it.

## Import

1. Install Microsoft Power BI Desktop. Open **Get data > Text/CSV**.
2. From `powerbi/import/`, import these 7 cleaned datasets: `sales.csv`, `products.csv`, `regions.csv`, `reps.csv`, `targets.csv`, `visits.csv`, `inventory.csv`.
3. Ensure `net_sales_inr`, `target_inr` and `unit_price_inr` are Decimal Number; units/visits are Whole Number; `month` remains Text with `YYYY-MM` (lexically sortable). The sale date can be Date.
4. In Model view, create the relationships below. All arrows should be **single-direction**, from dimension / lookup to fact. Do not add additional direct Region→Sales or Region→Targets links; that can introduce ambiguous filter paths.

| One (dimension) | Many (detail table) |
|---|---|
| `regions[region_id]` | `reps[region_id]` |
| `regions[region_id]` | `inventory[region_id]` |
| `reps[rep_id]` | `sales[rep_id]` |
| `reps[rep_id]` | `targets[rep_id]` |
| `reps[rep_id]` | `visits[rep_id]` |
| `products[product_id]` | `sales[product_id]` |
| `products[product_id]` | `inventory[product_id]` |

### Common month slicer

Click **Modeling > New table** and paste:

```dax
DimMonth =
DISTINCT (
    UNION (
        SELECTCOLUMNS ( sales, "Month", sales[month] ),
        SELECTCOLUMNS ( targets, "Month", targets[month] )
    )
)
```

Relate `DimMonth[Month]` (one side) to each of these (many side): `sales[month]`, `targets[month]`, `visits[month]`, `inventory[month]`. Use this dimension, not fact-table month fields, for slicers. The `YYYY-MM` strings sort chronologically. Set the page filter to months `2026-01` through `2026-10` for consistency with the workbook.

## DAX measures

Create these measures (in `sales` or a dedicated Measures table):

```dax
Net Revenue INR = SUM ( sales[net_sales_inr] )

Net Units = SUM ( sales[net_units] )

Returned Units = SUM ( sales[returned_units] )

Return Rate % =
DIVIDE ( [Returned Units], SUM ( sales[units_sold] ) )

Target INR = SUM ( targets[target_inr] )

Target Attainment % =
IF (
    ISCROSSFILTERED ( products ),
    BLANK (),
    DIVIDE ( [Net Revenue INR], [Target INR] )
)

Planned Visits = SUM ( visits[planned_visits] )

Completed Visits = SUM ( visits[completed_visits] )

Visit Completion % =
DIVIDE ( [Completed Visits], [Planned Visits] )

Inventory Shortage Units =
SUMX (
    inventory,
    VAR Threshold = RELATED ( products[reorder_level_units] )
    RETURN MAX ( 0, Threshold - inventory[stock_units] )
)

Low Stock Rows =
COUNTROWS (
    FILTER (
        inventory,
        inventory[stock_units] < RELATED ( products[reorder_level_units] )
    )
)
```

Format currency measures as INR (₹), rates as Percentage (1 decimal), volumes as whole numbers.

**Why blank attainment on therapy filters?** Targets exist by executive and month, not by product/therapy. If you select a product, overall targets would otherwise be compared to product-only sales and become misleading. Either clear the product filter or first create a defensible target allocation model.

## Suggested report layout

Use `powerbi/theme.json` via **View > Themes > Browse for themes**.

**Page 1: Executive overview**

- Cards: Net Revenue INR, Net Units, Return Rate %, Target Attainment %.
- Line chart: `DimMonth[Month]` on X; `Net Revenue INR` on Y.
- Clustered bar chart: `regions[region_name]` on axis; Net Revenue INR as value.
- Treemap or stacked bar: `products[therapy_area]` and Net Revenue INR.
- Slicers: `DimMonth[Month]`, `regions[region_name]`, `products[therapy_area]`.

**Page 2: Field force performance**

- Matrix rows: `reps[rep_name]`; values: Net Revenue INR, Target INR, Target Attainment %, Planned Visits, Completed Visits, Visit Completion %.
- Bar chart: `reps[rep_name]` vs Net Revenue INR.

**Page 3: Inventory risk**

- Set month slicer to `2026-10` (latest snapshot).
- Table: product, region, stock_units, reorder_level_units, Inventory Shortage Units.
- Add a visual-level filter on shortage units greater than zero.

Save it yourself as `PharmaPulse_PowerBI.pbix`, then add a screenshot to your GitHub README if useful.

## Integrity note

These are fictional products, employees, targets, invoices, and inventory snapshots. No real company, pharmacy, clinic, customer, or patient data is included.
