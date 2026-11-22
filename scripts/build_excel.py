"""Optional workbook builder using artifact_tool, run in environment with artifact_tool installed.

Input: generated CSVs and quality audit. Output: outputs/reports/Pharma_Sales_Excel_Report.xlsx
"""
from pathlib import Path
import json
import pandas as pd
from artifact_tool import Workbook, SpreadsheetFile

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs'/'reports'/'Pharma_Sales_Excel_Report.xlsx'
PROC=ROOT/'data'/'processed'
RAW=ROOT/'data'/'raw'

NAVY='#12263C'; NAVY_DARK='#0C1D30'; TEAL='#007F7A'; WHITE='#FFFFFF'; LT='#EAF4F7'; GRAY='#5C6C7D'; PALE='#F3F7FB'; AMBER='#FDF1DC'; GREEN='#DCFCE7'

def styler(sheet, end_col):
    sheet.get_range(f'A1:{end_col}1').format={'fill':NAVY,'font':{'color':WHITE,'bold':True},'row_height':27,'vertical_alignment':'center'}
    sheet.freeze_panes.freeze_rows(1)

def main():
    sales=pd.read_csv(PROC/'sales_enriched.csv')
    sales=sales[(sales.month>='2026-01')&(sales.month<='2026-10')].copy()
    # Large Excel source table contains ALL transactions for the selected YTD period.
    sales=sales[['transaction_id','sale_date','month','region_name','rep_name','product_name','therapy_area',
                 'units_sold','returned_units','net_units','unit_price_inr','discount_pct','net_sales_inr']]
    sales.columns=['Transaction ID','Date','Month','Region','Executive','Product','Therapy Area',
                   'Units Sold','Returned Units','Net Units','Unit Price (INR)','Discount','Net Revenue (INR)']
    targets=pd.read_csv(PROC/'targets.csv')
    visits=pd.read_csv(PROC/'visits.csv')
    reps=pd.read_csv(PROC/'reps.csv')[['rep_id','rep_name','region_id']]
    regions=pd.read_csv(PROC/'regions.csv')[['region_id','region_name']]
    targets=targets.merge(visits,on=['month','rep_id'],validate='one_to_one').merge(reps,on='rep_id').merge(regions,on='region_id')
    targets=targets[(targets.month>='2026-01')&(targets.month<='2026-10')].copy()
    targets=targets[['month','rep_name','region_name','target_inr','planned_visits','completed_visits']]
    targets.columns=['Month','Executive','Region','Target (INR)','Planned Visits','Completed Visits']
    audit=json.loads((PROC/'data_quality_audit.json').read_text(encoding='utf-8'))

    wb=Workbook.create()
    dashboard=wb.worksheets.add('Dashboard')
    monthly=wb.worksheets.add('Monthly Trend')
    region=wb.worksheets.add('Region Performance')
    product=wb.worksheets.add('Product Performance')
    field=wb.worksheets.add('Field Force')
    quality=wb.worksheets.add('Data Quality')
    src=wb.worksheets.add('Sales Data')
    goal=wb.worksheets.add('Targets')
    row_end=len(sales)+1; target_end=len(targets)+1
    sales_rows=[list(sales.columns)]+[list(r) for r in sales.itertuples(index=False,name=None)]
    src.get_range_by_indexes(0,0,len(sales_rows),13).values=sales_rows
    styler(src,'M')
    src.get_range(f'A2:A{row_end}').format.column_width=18
    src.get_range(f'B2:C{row_end}').format.column_width=13
    src.get_range(f'D2:F{row_end}').format.column_width=21
    src.get_range(f'G2:G{row_end}').format.column_width=22
    src.get_range(f'H2:J{row_end}').format.column_width=15
    src.get_range(f'K2:M{row_end}').format.column_width=18
    src.get_range(f'K2:K{row_end}').set_number_format('₹#,##0.00')
    src.get_range(f'L2:L{row_end}').set_number_format('0.0%')
    src.get_range(f'M2:M{row_end}').set_number_format('₹#,##0.00')
    try:
        src.tables.add(f'A1:M{row_end}',True,'SalesTransactions')
    except Exception as e:
        print('Sales data table styling skipped:',str(e)[:120])
    goalrows=[list(targets.columns)]+[list(r) for r in targets.itertuples(index=False,name=None)]
    goal.get_range_by_indexes(0,0,len(goalrows),6).values=goalrows
    styler(goal,'F')
    goal.get_range('A1:C151').format.column_width=21
    goal.get_range('D1:F151').format.column_width=20
    goal.get_range(f'D2:D{target_end}').set_number_format('₹#,##0')
    try:
        goal.tables.add(f'A1:F{target_end}',True,'SalesTargets')
    except Exception as e:
        print('Target table styling skipped:',str(e)[:120])

    month_names=sorted(sales.Month.unique())
    monthly.get_range('A1:E1').values=[['Month','Net Revenue (INR)','Sales Target (INR)','Target Attainment','Transactions']]
    monthly.get_range('A2:A11').values=[[v] for v in month_names]
    monthly.get_range('B2:E11').formulas=[[
        f'=SUMIF(\'Sales Data\'!$C$2:$C${row_end},A{i},\'Sales Data\'!$M$2:$M${row_end})',
        f'=SUMIF(Targets!$A$2:$A${target_end},A{i},Targets!$D$2:$D${target_end})',
        f'=IFERROR(B{i}/C{i},0)',
        f'=COUNTIF(\'Sales Data\'!$C$2:$C${row_end},A{i})'
    ] for i in range(2,12)]
    styler(monthly,'E')
    monthly.get_range('A1:E11').format.column_width=23
    monthly.get_range('B2:C11').set_number_format('₹#,##0')
    monthly.get_range('D2:D11').set_number_format('0.0%')
    monthly.get_range('D2:D11').conditional_formats.add_color_scale({'minColor':'#FCE8E6','midColor':'#FFF2C2','maxColor':'#C9F3DF'})

    reg_names=sorted(sales.Region.unique())
    region.get_range('A1:E1').values=[['Region','Net Revenue (INR)','Target (INR)','Attainment','Transactions']]
    region.get_range('A2:A6').values=[[v] for v in reg_names]
    region.get_range('B2:E6').formulas=[[
        f'=SUMIF(\'Sales Data\'!$D$2:$D${row_end},A{i},\'Sales Data\'!$M$2:$M${row_end})',
        f'=SUMIF(Targets!$C$2:$C${target_end},A{i},Targets!$D$2:$D${target_end})',
        f'=IFERROR(B{i}/C{i},0)',
        f'=COUNTIF(\'Sales Data\'!$D$2:$D${row_end},A{i})'
    ] for i in range(2,7)]
    styler(region,'E')
    region.get_range('A1:E6').format.column_width=23
    region.get_range('B2:C6').set_number_format('₹#,##0')
    region.get_range('D2:D6').set_number_format('0.0%')
    region.get_range('D2:D6').conditional_formats.add_data_bar({'color':'#06B6A7','gradient':True})

    product_names=sorted(sales.Product.unique())
    product.get_range('A1:D1').values=[['Product','Therapy Area','Net Revenue (INR)','Units Sold (Net)']]
    product.get_range('A2:A13').values=[[v] for v in product_names]
    pmap=dict(zip(sales.Product,sales['Therapy Area']))
    product.get_range('B2:B13').values=[[pmap[n]] for n in product_names]
    product.get_range('C2:D13').formulas=[[
        f'=SUMIF(\'Sales Data\'!$F$2:$F${row_end},A{i},\'Sales Data\'!$M$2:$M${row_end})',
        f'=SUMIF(\'Sales Data\'!$F$2:$F${row_end},A{i},\'Sales Data\'!$J$2:$J${row_end})'
    ] for i in range(2,14)]
    styler(product,'D')
    product.get_range('A1:D13').format.column_width=25
    product.get_range('C2:C13').set_number_format('₹#,##0')
    product.get_range('C2:C13').conditional_formats.add_data_bar({'color':'#007F7A','gradient':True})

    rep_names=sorted(sales.Executive.unique())
    field.get_range('A1:G1').values=[['Executive','Region','Net Revenue (INR)','Target (INR)','Attainment','Planned Visits','Completed Visits']]
    field.get_range('A2:A16').values=[[v] for v in rep_names]
    rmap=dict(zip(targets.Executive,targets.Region))
    field.get_range('B2:B16').values=[[rmap[n]] for n in rep_names]
    field.get_range('C2:G16').formulas=[[
        f'=SUMIF(\'Sales Data\'!$E$2:$E${row_end},A{i},\'Sales Data\'!$M$2:$M${row_end})',
        f'=SUMIF(Targets!$B$2:$B${target_end},A{i},Targets!$D$2:$D${target_end})',
        f'=IFERROR(C{i}/D{i},0)',
        f'=SUMIF(Targets!$B$2:$B${target_end},A{i},Targets!$E$2:$E${target_end})',
        f'=SUMIF(Targets!$B$2:$B${target_end},A{i},Targets!$F$2:$F${target_end})'
    ] for i in range(2,17)]
    styler(field,'G')
    field.get_range('A1:G16').format.column_width=23
    field.get_range('C2:D16').set_number_format('₹#,##0')
    field.get_range('E2:E16').set_number_format('0.0%')
    field.get_range('E2:E16').conditional_formats.add_color_scale({'minColor':'#FCE8E6','midColor':'#FFF2C2','maxColor':'#D3F9E7'})

    # Audit indicates what source-system quality issues the Python pipeline corrected.
    qualrows=[
        ['DATA QUALITY & DEFINITIONS','Value'],
        ['Synthetic dataset', 'Fictional demonstration, NOT Alteus operational information'],
        ['Source sales rows',audit['source_transactions_including_duplicates']],
        ['Duplicates removed',audit['duplicate_ids_removed']],
        ['Missing discounts defaulted to 0',audit['missing_discounts_defaulted_to_zero']],
        ['Region IDs normalized',audit['region_ids_normalized']],
        ['Invalid records dropped',audit['invalid_rows_dropped']],
        ['Valid cleaned rows, all months',audit['clean_transactions']],
        ['Excel reporting period','Jan 2026 – Oct 2026'],
        ['Net revenue definition','(Units sold – returned units) × unit price × (1 – discount)'],
        ['Target metric','Net revenue / sum of targets for same scope'],
        ['Inventory threshold','Available stock below fictional SKU reorder threshold'],
        ['Excel refresh','Rerun Python pipeline, regenerate workbook using build_excel.py'],
        ['Source', 'Programmatically generated with fixed random seed 20261122']
    ]
    quality.get_range_by_indexes(0,0,len(qualrows),2).values=qualrows
    styler(quality,'B')
    quality.get_range('A1:A15').format.column_width=34
    quality.get_range('B1:B15').format.column_width=85
    quality.get_range('A2:B2').format.fill=AMBER
    quality.get_range('B2:B14').format.wrap_text=True

    # Dashboard — two formula-linked KPI cards and two useful Excel charts.
    dashboard.merge_cells('A1:V2')
    dashboard.get_range('A1').values=[['PHARMA SALES | EXECUTIVE PERFORMANCE']]
    dashboard.get_range('A1:V2').format={'fill':NAVY_DARK,'font':{'color':WHITE,'bold':True,'size':19},'row_height':25,'vertical_alignment':'center'}
    dashboard.merge_cells('A3:V3')
    dashboard.get_range('A3').values=[['JAN – OCT 2026  •  ALL REGIONS  •  FICTIONAL PORTFOLIO DEMONSTRATION']]
    dashboard.get_range('A3:V3').format={'fill':LT,'font':{'color':NAVY,'bold':True},'row_height':28,'vertical_alignment':'center'}
    for label_range,value_range,label,formula,num_fmt in [
        ('A5:E5','A6:E7','NET REVENUE (₹)',f'=SUM(\'Sales Data\'!M2:M{row_end})','₹#,##0'),
        ('G5:K5','G6:K7','NET UNITS SOLD',f'=SUM(\'Sales Data\'!J2:J{row_end})','#,##0'),
        ('M5:Q5','M6:Q7','RETURNED UNITS',f'=SUM(\'Sales Data\'!I2:I{row_end})','#,##0'),
        ('S5:V5','S6:V7','TARGET ATTAINMENT',f'=IFERROR(A6/SUM(Targets!D2:D{target_end}),0)','0.0%')]:
        dashboard.merge_cells(label_range)
        dashboard.merge_cells(value_range)
        top=label_range.split(':')[0]
        cell=value_range.split(':')[0]
        dashboard.get_range(top).values=[[label]]
        dashboard.get_range(cell).formulas=[[formula]]
        dashboard.get_range(label_range).format={'fill':TEAL,'font':{'color':WHITE,'bold':True,'size':10},'row_height':26,'vertical_alignment':'center','horizontal_alignment':'center'}
        dashboard.get_range(value_range).format={'fill':PALE,'font':{'color':NAVY,'bold':True,'size':19},'row_height':25,'vertical_alignment':'center','horizontal_alignment':'center'}
        dashboard.get_range(cell).set_number_format(num_fmt)
    dashboard.merge_cells('A9:K9'); dashboard.get_range('A9').values=[['MONTHLY REVENUE']]
    dashboard.merge_cells('M9:V9'); dashboard.get_range('M9').values=[['REVENUE BY REGION']]
    for area in ['A9:K9','M9:V9']:
        dashboard.get_range(area).format={'fill':NAVY,'font':{'color':WHITE,'bold':True},'row_height':27}
    dashboard.merge_cells('A26:V26'); dashboard.get_range('A26').values=[['Use the other tabs for live Excel formula-based analysis, filters and data-quality notes.']]
    dashboard.get_range('A26:V26').format={'fill':LT,'font':{'color':NAVY},'row_height':26}
    dashboard.merge_cells('A28:V28'); dashboard.get_range('A28').values=[['Disclaimer: All sales, targets, inventory, employees and products are synthetic. Not affiliated with Alteus Biogenics.']]
    dashboard.get_range('A28:V28').format={'font':{'color':GRAY,'italic':True},'row_height':23}
    dashboard.get_range('A1:V30').format.column_width=9.5
    dashboard.get_range('A1:V30').format.row_height=22

    try:
        mchart=dashboard.charts.add('ColumnClustered',{'title':'Monthly Net Revenue (INR)','has_legend':False})
        ms=mchart.series.add('Net revenue')
        ms.category_formula="'Monthly Trend'!$A$2:$A$11"
        ms.formula="'Monthly Trend'!$B$2:$B$11"
        mchart.set_position('A10','L24')
        rchart=dashboard.charts.add('bar',{'title':'Revenue by Region (INR)','has_legend':False})
        rchart.bar_options.direction='bar'
        rs=rchart.series.add('Net revenue')
        rs.category_formula="'Region Performance'!$A$2:$A$6"
        rs.formula="'Region Performance'!$B$2:$B$6"
        rchart.set_position('M10','W24')
        print('Added two Excel dashboard charts')
    except Exception as e:
        print('Chart creation warning:',repr(e))

    try:
        print('Inspect dashboard:',wb.inspect({'kind':'table','range':'Dashboard!A5:S7','include':'values,formulas','table_max_rows':3,'table_max_cols':19}).ndjson[:1400])
        print('Formula check:',wb.inspect({'kind':'match','search_term':'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A','options':{'use_regex':True,'max_results':20}}).ndjson[:600])
    except Exception as e:
        print('Inspection warning:',repr(e))
    SpreadsheetFile.export_xlsx(wb).save(str(OUT))
    print(f'Exported {OUT} ({OUT.stat().st_size/1e6:.2f} MB)')

if __name__=='__main__':main()
