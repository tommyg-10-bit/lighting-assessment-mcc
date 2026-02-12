#!/usr/bin/env python3
"""
Fixture report generator runner.
Processes all fixture groups and generates PDF reports with OpenAI summaries.
"""
import os
import sys

# Add JPG folder to path so we can import the module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'JPG'))

from SekonicMeasurementReportGenerator import create_fixture_report

def main():
    os.chdir(os.path.join(os.path.dirname(__file__), 'JPG'))
    files = [f for f in os.listdir('.') if 'SL_' in f]
    
    if not files:
        print('No SL_ files found in JPG folder.')
        return
    
    # Group files by fixture ID
    groups = {}
    for f in files:
        idx = f.find('SL_') + 3
        fid = f[idx:idx+13]
        groups.setdefault(fid, []).append(f)
    
    print(f'Found {len(groups)} fixture groups.')
    
    # Process all fixture groups
    total = len(groups)
    for i, (fid, flist) in enumerate(sorted(groups.items()), 1):
        print(f'\n[{i}/{total}] Processing group {fid} with {len(flist)} files...')
        try:
            create_fixture_report(fid, [os.path.join('.', f) for f in flist])
            print(f'  ✓ SUCCESS')
        except Exception as e:
            print(f'  ✗ FAILED: {e}')

if __name__ == '__main__':
    main()
