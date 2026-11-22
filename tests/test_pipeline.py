"""Run: python -m unittest discover -s tests -v"""
from pathlib import Path
import json
import sqlite3
import unittest
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'/'processed'
DB=ROOT/'outputs'/'database'/'pharma_analytics.sqlite'
REPORTS=ROOT/'outputs'/'reports'

class TestPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sales=pd.read_csv(DATA/'sales.csv')
        cls.audit=json.loads((DATA/'data_quality_audit.json').read_text())

    def test_unique_clean_transactions(self):
        self.assertEqual(self.sales.transaction_id.nunique(),len(self.sales))
        self.assertEqual(self.audit['clean_transactions'],len(self.sales))
        self.assertEqual(self.audit['duplicate_ids_removed'],28)

    def test_valid_values(self):
        self.assertFalse(self.sales.isna().any().any())
        self.assertTrue((self.sales.units_sold > 0).all())
        self.assertTrue((self.sales.returned_units <= self.sales.units_sold).all())
        self.assertTrue((self.sales.net_sales_inr >= 0).all())
        self.assertTrue(self.sales.discount_pct.between(0,.5).all())

    def test_revenue_matches_sqlite(self):
        with sqlite3.connect(DB) as conn:
            db_total=conn.execute('SELECT SUM(net_sales_inr) FROM sales').fetchone()[0]
            db_ytd=conn.execute("SELECT SUM(net_sales_inr) FROM sales WHERE month BETWEEN '2026-01' AND '2026-10'").fetchone()[0]
        self.assertAlmostEqual(self.sales.net_sales_inr.sum(),db_total,places=2)
        self.assertAlmostEqual(self.audit['net_sales_inr_2026_jan_oct'],db_ytd,places=2)

    def test_monthly_and_region_reports_reconcile(self):
        monthly=pd.read_csv(REPORTS/'01_monthly_sales.csv')
        regions=pd.read_csv(REPORTS/'02_region_performance.csv')
        self.assertAlmostEqual(monthly.revenue_inr.sum(),self.sales.net_sales_inr.sum(),places=2)
        self.assertAlmostEqual(regions.revenue_inr.sum(),self.audit['net_sales_inr_2026_jan_oct'],places=2)
        self.assertEqual(int(regions.transactions.sum()),int(self.sales.month.between('2026-01','2026-10').sum()))

    def test_targets_and_visit_limits(self):
        targets=pd.read_csv(DATA/'targets.csv')
        visits=pd.read_csv(DATA/'visits.csv')
        self.assertEqual(len(targets),22*15)
        self.assertTrue((visits.completed_visits <= visits.planned_visits+8).all())  # extra visits permitted
        self.assertTrue((visits.planned_visits > 0).all())

    def test_inventory_reorder_alerts_correct(self):
        alerts=pd.read_csv(REPORTS/'05_inventory_reorder_alerts.csv')
        self.assertTrue((alerts.stock_units < alerts.reorder_level_units).all())
        self.assertTrue((alerts.shortage_units == alerts.reorder_level_units-alerts.stock_units).all())

if __name__=='__main__':unittest.main()
