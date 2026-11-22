"""Clean sales data, validate keys, build SQLite database, export reports/Power BI CSVs.

Run from any directory: python scripts/run_pipeline.py
Synthetic example only, not financial / operational data from any real company.
"""
from pathlib import Path
import json
import sqlite3
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data' / 'raw'
PROCESSED = ROOT / 'data' / 'processed'
REPORTS = ROOT / 'outputs' / 'reports'
DBDIR = ROOT / 'outputs' / 'database'
PBI = ROOT / 'powerbi' / 'import'
for folder in [PROCESSED, REPORTS, DBDIR, PBI]:
    folder.mkdir(parents=True, exist_ok=True)


def month_range_filter(series, start='2026-01', end='2026-10'):
    return (series >= start) & (series <= end)


def main():
    dims = {name: pd.read_csv(RAW / file) for name, file in {
        'products': 'products.csv', 'regions': 'regions.csv', 'reps': 'sales_reps.csv',
        'targets': 'targets.csv', 'visits': 'field_visits.csv', 'inventory': 'inventory.csv'
    }.items()}
    raw = pd.read_csv(RAW / 'raw_sales.csv', dtype={'transaction_id': 'string'})
    num_raw = len(raw)
    duplicate_count = int(raw.transaction_id.duplicated().sum())
    blank_discount_count = int(raw.discount_pct.isna().sum())
    region_normalization_count = int((raw.region_id != raw.region_id.astype(str).str.strip().str.upper()).sum())
    sales = raw.drop_duplicates(subset='transaction_id', keep='first').copy()
    sales['region_id'] = sales.region_id.astype(str).str.strip().str.upper()
    sales['discount_pct'] = sales.discount_pct.fillna(0)
    sales['sale_date'] = pd.to_datetime(sales.sale_date, format='%Y-%m-%d', errors='coerce')
    for col in ['units_sold', 'unit_price_inr', 'returned_units', 'discount_pct']:
        sales[col] = pd.to_numeric(sales[col], errors='coerce')
    valid = (sales.sale_date.notna() & sales.rep_id.isin(dims['reps'].rep_id) &
             sales.region_id.isin(dims['regions'].region_id) &
             sales.product_id.isin(dims['products'].product_id) &
             sales.units_sold.gt(0) & sales.unit_price_inr.gt(0) &
             sales.returned_units.ge(0) & (sales.returned_units <= sales.units_sold) &
             sales.discount_pct.between(0, .5))
    invalid_count = int((~valid).sum())
    sales = sales.loc[valid].copy()
    rep_regions = dims['reps'].set_index('rep_id')['region_id']
    region_mismatch = (sales.region_id != sales.rep_id.map(rep_regions))
    cross_region_count = int(region_mismatch.sum())
    sales = sales.loc[~region_mismatch].copy()
    sales['month'] = sales.sale_date.dt.strftime('%Y-%m')
    sales['net_units'] = sales.units_sold - sales.returned_units
    sales['net_sales_inr'] = (sales.net_units * sales.unit_price_inr *
                               (1 - sales.discount_pct)).round(2)
    sales['sale_date'] = sales.sale_date.dt.strftime('%Y-%m-%d')
    sales = sales.sort_values(['sale_date', 'transaction_id']).reset_index(drop=True)

    # Keep operational tables normalized for SQL joins and Power BI relationships.
    for table, frame in dims.items():
        frame.to_csv(PROCESSED / (table + '.csv'), index=False)
        frame.to_csv(PBI / (table + '.csv'), index=False)
    sales.to_csv(PROCESSED / 'sales.csv', index=False)
    sales.to_csv(PBI / 'sales.csv', index=False)

    enriched = (sales.merge(dims['reps'][['rep_id','rep_name']], on='rep_id', validate='many_to_one')
               .merge(dims['regions'][['region_id','region_name']], on='region_id', validate='many_to_one')
               .merge(dims['products'][['product_id','product_name','therapy_area']], on='product_id', validate='many_to_one'))
    enriched = enriched[['transaction_id','sale_date','month','region_name','rep_name','product_name',
                         'therapy_area','units_sold','returned_units','net_units','unit_price_inr',
                         'discount_pct','net_sales_inr','rep_id','region_id','product_id']]
    enriched.to_csv(PROCESSED / 'sales_enriched.csv', index=False)

    with sqlite3.connect(DBDIR / 'pharma_analytics.sqlite') as conn:
        conn.execute('PRAGMA foreign_keys = OFF')
        for table, frame in dims.items():
            frame.to_sql(table, conn, index=False, if_exists='replace')
        sales.to_sql('sales', conn, index=False, if_exists='replace')
        conn.executescript('''
        CREATE INDEX IF NOT EXISTS idx_sales_month ON sales(month);
        CREATE INDEX IF NOT EXISTS idx_sales_region ON sales(region_id);
        CREATE INDEX IF NOT EXISTS idx_sales_rep ON sales(rep_id);
        CREATE INDEX IF NOT EXISTS idx_sales_product ON sales(product_id);
        CREATE VIEW IF NOT EXISTS v_sales_enriched AS
        SELECT s.*, r.region_name, p.product_name, p.therapy_area, x.rep_name
        FROM sales s JOIN regions r ON s.region_id = r.region_id
        JOIN products p ON s.product_id = p.product_id
        JOIN reps x ON s.rep_id = x.rep_id;
        ''')
        qdir = ROOT / 'sql'
        for filename in sorted(qdir.glob('*.sql')):
            out = pd.read_sql_query(filename.read_text(encoding='utf-8'), conn)
            out.to_csv(REPORTS / (filename.stem + '.csv'), index=False)

    audit = {
        'dataset_type': '100% synthetic and fictional; does not represent Alteus Biogenics',
        'source_transactions_including_duplicates': num_raw,
        'duplicate_ids_removed': duplicate_count,
        'missing_discounts_defaulted_to_zero': blank_discount_count,
        'region_ids_normalized': region_normalization_count,
        'invalid_rows_dropped': invalid_count,
        'rep_region_mismatches_dropped': cross_region_count,
        'clean_transactions': len(sales),
        'net_sales_inr_all_months': round(float(sales.net_sales_inr.sum()), 2),
        'net_sales_inr_2026_jan_oct': round(float(sales.loc[month_range_filter(sales.month), 'net_sales_inr'].sum()), 2),
        'units_returned': int(sales.returned_units.sum()),
        'distinct_products': int(sales.product_id.nunique()),
        'distinct_regions': int(sales.region_id.nunique()),
        'distinct_reps': int(sales.rep_id.nunique()),
    }
    (PROCESSED / 'data_quality_audit.json').write_text(json.dumps(audit, indent=2), encoding='utf-8')
    print(json.dumps(audit, indent=2))
    print(f'SQLite database: {DBDIR / "pharma_analytics.sqlite"}')
    print(f'Reports: {REPORTS} ({len(list(REPORTS.glob("*.csv")))} CSV files)')


if __name__ == '__main__':
    main()
