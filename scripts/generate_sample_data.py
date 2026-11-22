"""Create deterministic, completely fictional pharmaceutical commercial data.

Run: python scripts/generate_sample_data.py
Uses no identifiable real patients, doctors or company records.
"""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data' / 'raw'
RAW.mkdir(parents=True, exist_ok=True)
SEED = 20261122


def main():
    rng = np.random.default_rng(SEED)
    regions = pd.DataFrame([
        ('R01', 'East', 'Kolkata', 'Bhubaneswar'),
        ('R02', 'North', 'Delhi', 'Jaipur'),
        ('R03', 'West', 'Mumbai', 'Pune'),
        ('R04', 'South', 'Bengaluru', 'Chennai'),
        ('R05', 'Central', 'Bhopal', 'Indore'),
    ], columns=['region_id', 'region_name', 'city_1', 'city_2'])
    # Illustrative placeholder products; no real pharmaceutical brand or prescribing data.
    products = pd.DataFrame([
        ('P001', 'Neurovia 10', 'CNS', 140, 320),
        ('P002', 'Neurovia 20', 'CNS', 220, 280),
        ('P003', 'Mindora 5', 'Psychiatry', 165, 300),
        ('P004', 'Mindora 10', 'Psychiatry', 205, 260),
        ('P005', 'Nervixa 50', 'Neurology', 180, 290),
        ('P006', 'Nervixa 100', 'Neurology', 260, 250),
        ('P007', 'Cardava 5', 'Cardio-Metabolic', 120, 360),
        ('P008', 'Cardava 10', 'Cardio-Metabolic', 170, 330),
        ('P009', 'Glucora 500', 'Cardio-Metabolic', 95, 420),
        ('P010', 'Glucora XR', 'Cardio-Metabolic', 155, 350),
        ('P011', 'Gastrel 20', 'Gastroenterology', 105, 390),
        ('P012', 'Respira 10', 'Respiratory', 185, 300),
    ], columns=['product_id', 'product_name', 'therapy_area', 'list_price_inr', 'reorder_level_units'])
    reps = pd.DataFrame([
        (f'E{i:03}', f'Field Executive {i:02}', f'R{((i-1)//3)+1:02}', 'Field Executive')
        for i in range(1, 16)
    ], columns=['rep_id', 'rep_name', 'region_id', 'role'])
    periods = pd.period_range('2025-01', '2026-10', freq='M')
    target_rows, visit_rows, inventory_rows, sale_rows = [], [], [], []
    sale_no = 1
    for p in periods:
        month = str(p)
        year_factor = 1.09 if p.year == 2026 else 1.00
        season = 1 + 0.11*np.sin((p.month-1)*2*np.pi/12) + 0.06*np.cos(p.month*2*np.pi/12)
        for ridx, (_, rep) in enumerate(reps.iterrows()):
            rep_id, region_id = rep['rep_id'], rep['region_id']
            target = int(round((145000 + (ridx % 3)*14000) * year_factor * season / 1000)*1000)
            target_rows.append((month, rep_id, target))
            planned = int(rng.integers(75, 100))
            completed = max(0, min(planned + 8, int(planned*rng.uniform(.77, 1.03))))
            visit_rows.append((month, rep_id, planned, completed))
            order_count = int(rng.integers(12, 19))
            for _ in range(order_count):
                product = products.iloc[int(rng.integers(0, len(products)))]
                units = int(rng.integers(28, 95))
                returns = int(rng.integers(0, 5)) if rng.random() < .16 else 0
                day = int(rng.integers(1, p.days_in_month + 1))
                date = f'{month}-{day:02d}'
                discount = float(rng.choice([0.0, .03, .05, .07, .10], p=[.30,.20,.25,.15,.10]))
                sale_rows.append((f'T{sale_no:06}', date, rep_id, region_id, product['product_id'], units, float(product['list_price_inr']), discount, returns))
                sale_no += 1
        for _, region in regions.iterrows():
            for _, product in products.iterrows():
                base_stock = int(rng.integers(170, 1050))
                if rng.random() < .19:
                    base_stock = int(rng.integers(30, int(product['reorder_level_units']) + 1))
                inventory_rows.append((month, region['region_id'], product['product_id'], base_stock))

    sales = pd.DataFrame(sale_rows, columns=['transaction_id','sale_date','rep_id','region_id','product_id','units_sold','unit_price_inr','discount_pct','returned_units'])
    # Purposeful source-system imperfections to demonstrate a real cleaning and QA workflow:
    extra = sales.sample(n=28, random_state=SEED).copy()
    sales = pd.concat([sales, extra], ignore_index=True)
    dirty_index = rng.choice(len(sales), size=32, replace=False)
    sales.loc[dirty_index, 'region_id'] = ' ' + sales.loc[dirty_index, 'region_id'].astype(str).str.lower() + ' '
    missing_discount = rng.choice(len(sales), size=24, replace=False)
    sales.loc[missing_discount, 'discount_pct'] = np.nan  # documented rule: missing discount -> 0
    sales = sales.sample(frac=1, random_state=SEED).reset_index(drop=True)

    frames = {
        'regions.csv': regions, 'products.csv': products, 'sales_reps.csv': reps,
        'raw_sales.csv': sales,
        'targets.csv': pd.DataFrame(target_rows, columns=['month','rep_id','target_inr']),
        'field_visits.csv': pd.DataFrame(visit_rows, columns=['month','rep_id','planned_visits','completed_visits']),
        'inventory.csv': pd.DataFrame(inventory_rows, columns=['month','region_id','product_id','stock_units']),
    }
    for name, frame in frames.items():
        frame.to_csv(RAW / name, index=False)
    print(f'Sample data created: {len(sales):,} raw sales rows ({sales.transaction_id.nunique():,} unique transactions).')


if __name__ == '__main__':
    main()
