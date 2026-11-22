# PharmaPulse — Project explanation and interview guide

**30-second project explanation:**

> “I worked with a synthetic pharmaceutical sales dataset to practise the end-to-end analytics workflow. I used Python and Pandas to remove duplicates, standardize source data, validate sales and calculate net revenue. I loaded the cleaned tables into SQLite and wrote queries for monthly revenue, regional performance, product mix, field-force targets and inventory alerts. I also prepared a formula-linked Excel summary and an offline interactive dashboard with region and product filters. The data is fictional and built for learning.”

Only use that explanation after running the project and understanding the key steps. Be transparent about which portions you created or adapted with AI assistance.

## Likely interview questions and talking points

**Q1. What is the difference between gross units and net units?**  
Gross units are the invoiced units before returns; net units subtract returned units. The simplified net revenue then multiplies net units by price after discount.

**Q2. Why did you use SQLite?**  
It is lightweight, SQL-compatible and creates a single portable file. It helped practise joins and business aggregations without operating a database server.

**Q3. How did you handle duplicate records?**  
The raw dataset deliberately contains repeated transaction IDs. The pipeline drops duplicate `transaction_id` values and records how many were removed in the QA audit. A real pipeline should confirm the correct deduplication rule with the data owner.

**Q4. Why do product filters hide target attainment?**  
Targets were assigned by rep and month, not product. Comparing filtered product sales with all-product targets would understate attainment and mislead management.

**Q5. Explain `JOIN` and `GROUP BY` in your project.**  
Sales records store IDs. `JOIN` brings in readable region/product/executive details. `GROUP BY` aggregates sales by month, region, product or representative.

**Q6. How would you make an MIS report automatically?**  
Schedule a script to load validated data, execute SQL aggregations and export standardized CSVs and dashboard files. Add logging, data freshness checks, exception alerts and a review/approval stage for production.

**Q7. How could Excel support this?**  
The included workbook uses `SUMIF`, `COUNTIF`, linked KPI formulas, conditional formatting and charts. Power Query and PivotTables would be logical next steps for real-time refresh and ad hoc exploration; the workbook itself does **not** include native PivotTables.

**Q8. What does Power BI add?**  
Relational tables, reusable DAX measures, slicers, published reporting and controlled refresh. This project includes a model and guide, not a completed `.pbix` file.

**Q9. What would you improve for a real pharmaceutical company?**  
Source-system access controls, price/master-data validation, batch tracking, data lineage, audit logs, daily incremental ingestion, secured access, automated error alerts and stakeholder-defined KPIs.

## Exercises (do these before the interview)

1. Explain each transformation in `scripts/run_pipeline.py` without reading from the file.
2. Run `sql/02_region_performance.sql` and explain why regional target attainment varies.
3. Explain Excel’s `SUMIF` calculation for one region, and distinguish a formula-based summary from a PivotTable.
4. Change the dashboard to the East region and Neurology therapy; explain why attainment shows “N/A”.
5. Rebuild the project with `python scripts/build_all.py` and run all six unit tests.
6. If you have Power BI Desktop, create one report page following `powerbi/POWER_BI_SETUP.md` and save a `.pbix` file before claiming Power BI project experience.

## Resume entry (after verifying/understanding your work)

**PharmaPulse — Pharmaceutical Sales Analytics & Automation**  
*Python, Pandas, SQLite/SQL, Excel, interactive Plotly HTML dashboard*

- Built and tested a synthetic sales analytics pipeline covering 4,996 transactions across 12 products and 5 regions.
- Used Pandas to clean duplicate/incomplete sales records; generated SQL reporting for revenue, targets, field-force productivity and inventory alerts.
- Produced a formula-driven Excel workbook and interactive offline analytics dashboard with regional and therapy filters.

Add “Power BI” **only after creating the actual report in Power BI Desktop**. Do not present synthetic demonstration numbers as actual company financial results.
