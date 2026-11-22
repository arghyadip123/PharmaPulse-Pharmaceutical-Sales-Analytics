# PharmaPulse — Pharmaceutical Sales Analytics & Automation

**Python • Pandas • SQL (SQLite) • Excel • Interactive HTML/Plotly • Power BI-ready data**

A working, interview-ready **portfolio demonstration** built to explore the sort of commercial analytics work mentioned in the Executive / Management Trainee – Business Analytics & Data Automation job description at Alteus Biogenics. The project is **independent** and **not affiliated with or endorsed by Alteus Biogenics**.

> ⚠️ **All records are completely synthetic**: fictional brands, employees, prices, transactions, returns, targets, geographic sales and inventory. Nothing comes from Alteus, actual customers, doctors, patients, or confidential company systems. Do not present any revenue here as company performance.

## Open the project now

- **`dashboard.html`** — offline interactive browser dashboard. Double-click to open (no server, no internet needed). Filters: period, sales region and therapy area. Includes CSV export.
- **`outputs/reports/Pharma_Sales_Excel_Report.xlsx`** — formula-linked Excel dashboard with charts, monthly trends, regional analysis, product analysis, field-force performance, targets, raw records and data-quality audit.
- **`outputs/database/pharma_analytics.sqlite`** — SQLite database with clean sales/dimension/target/visit/inventory tables and an enriched SQL view.
- **`outputs/reports/`** — seven automatically generated analysis CSVs.
- **`powerbi/import/`** — Power BI-ready clean model tables; build the actual `.pbix` using the accompanying guide.

### Sample reporting scope

| Item | Demo figure |
|---|---:|
| Historical coverage | January 2025 – October 2026 (22 months) |
| Raw transactions | 5,024 (includes intentional duplicates) |
| Clean transactions | 4,996 |
| 2026 Jan–Oct net sales | ₹2,18,95,873.40 |
| 2026 Jan–Oct assigned sales targets | ₹2,61,00,000 |
| 2026 Jan–Oct target attainment | 83.9% |
| Fictional SKUs / regions / executives | 12 / 5 / 15 |
| Inventory reorder alerts (Oct 2026) | 25 |

**Definitions:** Net sales = `(units_sold − returned_units) × unit_price_inr × (1 − discount_pct)`; target attainment = `net sales / assigned sales targets`. A return is modeled as a reversed unit before discount (simplified illustration). Inventory alert = stock below product reorder level. No cost/profit or tax data is modeled.

## Run from scratch (Windows, macOS or Linux)

Requires **Python 3.10+**. Open Terminal/PowerShell in this folder:

```bash
python -m pip install -r requirements.txt
python scripts/build_all.py
python -m unittest discover -s tests -v
```

Then double-click `dashboard.html`. `build_all.py` regenerates sample records using fixed seed `20261122`, cleans and validates sales, rebuilds the SQL database, exports reporting CSVs and refreshes the offline HTML dashboard. It **does not overwrite the included Excel workbook by default**. The `.xlsx` file is an included working snapshot with Excel formulas; rebuilding it programmatically is optional (see next section).

If on Windows `python` does not work, try `py` in its place.

### Refresh the Excel file

The included workbook already has formula-linked summaries built from the 2026 source data and target table. For interactive Excel refreshes, modify the `Sales Data` and `Targets` sheets (preserve the header/column schema) and extend formula references as required. The optional developer script `scripts/build_excel.py` can recreate the workbook from clean CSV files **only in a Python environment with `artifact_tool` installed**. `artifact_tool` is **not included in `requirements.txt`** because availability may vary. The rest of the project does not depend on it.

### Build Power BI dashboard

The project includes Power BI-ready imported tables, a custom theme and a relationship/DAX walkthrough:

**[`powerbi/POWER_BI_SETUP.md`](powerbi/POWER_BI_SETUP.md)**

A native Power BI `.pbix` file is **not included**; create and save it with Microsoft Power BI Desktop on Windows. The supplied HTML dashboard is independently complete and interactive.

## Folder layout

```text
alteus_pharma_analytics/
├── dashboard.html                 # Working, self-contained interactive dashboard
├── README.md                      # You are here
├── requirements.txt
├── data/
│   ├── raw/                       # Seven fictional source CSV files
│   └── processed/                 # Clean CSVs, enriched fact + QA audit
├── outputs/
│   ├── database/pharma_analytics.sqlite
│   └── reports/                  # Excel report + seven SQL outputs
├── scripts/
│   ├── generate_sample_data.py    # Deterministic fictional data
│   ├── run_pipeline.py            # ETL, validation, SQLite + reports
│   ├── build_dashboard.py         # Offline responsive HTML dashboard
│   ├── build_excel.py             # Optional Excel workbook refresh
│   └── build_all.py               # One-command rebuild
├── sql/                           # Seven SQLite analytics queries
├── powerbi/
│   ├── POWER_BI_SETUP.md
│   ├── theme.json
│   └── import/                    # Clean tables for Power BI
├── tests/
│   └── test_pipeline.py           # Reconciliation and QA unit tests
├── DATA_DICTIONARY.md
└── INTERVIEW_GUIDE.md
```

## ETL process

```text
Fictional raw CSV data
    → Deduplicate transaction IDs
    → Normalize region keys
    → Fill absent discounts with documented zero default
    → Validate quantities, returns, prices and relationships
    → Calculate net units and revenue
    → Build SQLite tables / SQL view
    → Run monthly/region/SKU/field-force/inventory SQL reports
    → Update offline HTML dashboard + Power BI import tables
    → Show formula-linked KPI, trend and performance Excel workbook
```

Source quality controls: 28 duplicated transaction IDs are removed; 24 missing discounts are defaulted to 0; 32 region keys are normalized. These are deliberately injected defects so the ETL does something demonstrable. Document missing-value policies carefully when using real data.

## Practical analyst findings (demo only)

1. **Target gap:** Jan–Oct 2026 sales were **₹2.19 crore** against **₹2.61 crore** in targets (**83.9% attainment**). Sales target coverage is below 100% and merits regional investigation.
2. **Regional variation:** Central had the highest example revenue at roughly **₹45.12 lakh**, while East had approximately **₹42.19 lakh**. Central target attainment was **86.4%** versus East's **80.8%**.
3. **Product contribution:** The highest revenue product in the demo was **Nervixa 100**, at approximately **₹28.47 lakh** for Jan–Oct 2026.
4. **Inventory:** The latest stock snapshot contained **25 low-stock combinations** (SKU × region). A purchasing/logistics team could prioritize shortages using `sql/05_inventory_reorder_alerts.sql`.

These observations are **not** about a real employer or their sales, patients, or products. The synthetic data was designed to support SQL and dashboard practice, not predictions.

## Limitations & future enhancements

- The sample uses simplified invoice-level sales and does not model tax, costs, profit, batches, expiry, returns authorization or regulated product tracking.
- There is no customer-/doctor-level identity or patient information. Field visit totals are aggregate counts only.
- Excel workbook summarizes the included Jan–Oct 2026 data; it does not use native Excel PivotTable objects. The summary sheets provide pivot-style reports using Excel `SUMIF`, `COUNTIF` and formulas.
- Power BI setup files are provided but the native `.pbix` must be created in Power BI Desktop.
- Possible extensions: Power Query refresh, forecasting with validated time-series methodology, alerts, user authentication and actual ERP/API ingestion.

## Project ownership and resume advice

You may study, run, modify and upload this demonstration project to your own GitHub repository. Before claiming hands-on expertise on your resume, you should be able to explain and demonstrate how its Python cleaning steps, SQL joins, Excel summaries and dashboard filters work. A good truthful bullet after you have run and understood it is: “Customized and validated a synthetic pharmaceutical sales analytics project using Python, SQL and Excel, including automated data-cleaning checks and interactive reporting.”
