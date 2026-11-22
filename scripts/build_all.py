"""Regenerate synthetic source data, SQL reports and interactive dashboard.

    python scripts/build_all.py
    python scripts/build_all.py --with-excel  # requires artifact_tool installed
"""
import argparse
import subprocess
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent

def main():
    parser=argparse.ArgumentParser(description='Rebuild fictional pharmaceutical analytics demo.')
    parser.add_argument('--with-excel',action='store_true',help='Regenerate Excel workbook (requires optional artifact_tool)')
    args=parser.parse_args()
    steps=['generate_sample_data.py','run_pipeline.py','build_dashboard.py']
    if args.with_excel:
        steps.append('build_excel.py')
    for name in steps:
        print(f'\n>>> Running {name}',flush=True)
        subprocess.run([sys.executable,str(HERE/name)],check=True)
    print('\nProject generation complete. Open dashboard.html in your browser.')

if __name__=='__main__':main()
