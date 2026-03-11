import pandas as pd, numpy as np, os, warnings
warnings.filterwarnings('ignore')
RAW = 'ml/data/raw/'
 
def divider(title):
    print('\n' + '='*55)
    print(f'  {title}')
    print('='*55)
 
def study(name, filepath, label_col=None):
    divider(name)
    try:
        df = pd.read_csv(filepath)
        print(f'  Rows: {len(df):,}  |  Columns: {df.shape[1]}')
        print(f'  Column names: {df.columns.tolist()}')
        num = df.select_dtypes(include='number')
        print(f'\n  Numeric ranges (min → max):')
        for col in num.columns:
            print(f'    {col:<30} {num[col].min():.3f}  →  {num[col].max():.3f}  (mean: {num[col].mean():.3f})')
        if label_col and label_col in df.columns:
            print(f'\n  Label [{label_col}] counts: {dict(df[label_col].value_counts())}')
        elif label_col is None:
            last = df.columns[-1]
            print(f'\n  Last column [{last}] counts: {dict(df[last].value_counts())}')
    except FileNotFoundError:
        print(f'  FILE NOT FOUND: {filepath}')
    except Exception as e:
        print(f'  ERROR: {e}')
 
# ── Study each dataset ──
study('1. ENGINE DATA (Most Important!)', RAW+'engine_data.csv')
study('2. AI4I 2020',                    RAW+'ai4i2020.csv', 'Machine failure')
study('3. PREDICTIVE MAINTENANCE',       RAW+'predictive_maintenance.csv', 'Target')
study('4. PdM TELEMETRY',               RAW+'PdM_telemetry.csv')
study('5. PdM FAILURES',               RAW+'PdM_failures.csv')
study('6. PdM MAINTENANCE',            RAW+'PdM_maint.csv')
study('7. PdM MACHINES',              RAW+'PdM_machines.csv')
 
# ── CMAPSS special handling ──
divider('8. NASA CMAPSS')
cmapss = RAW + 'CMAPSSData/'
if os.path.exists(cmapss):
    files = sorted(os.listdir(cmapss))
    print(f'  Files: {files}')
    train_files = [f for f in files if 'train' in f.lower() and f.endswith('.txt')]
    if train_files:
        dc = pd.read_csv(cmapss+train_files[0], sep=r'\s+', header=None)
        print(f'  Shape of {train_files[0]}: {dc.shape}')
        dc['RUL'] = dc.groupby(0)[1].transform('max') - dc[1]
        print(f'  RUL (days_until_failure equivalent): 0 → {dc["RUL"].max()}')
        print(f'  Sensor ranges (first 5 cols shown):')
        print(dc.iloc[:,2:7].describe().loc[['min','max']].to_string())
else:
    print('  CMAPSSData/ folder not found')
 
print('\n' + '='*55)
print('  STUDY COMPLETE!')
print('  NOTE DOWN from engine_data.csv:')
print('  → Lub oil pressure  min/max')
print('  → Coolant temp      min/max')
print('  → lub oil temp      min/max')
print('  Use these in SENSOR_RANGES in generate_training_data.py')
print('='*55)