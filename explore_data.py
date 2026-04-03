import os
import pandas as pd

print("Exploring OBD-II Dataset Files...\n")

# List all files in data folder
data_files = os.listdir('OBD-II-Dataset')

# Separate by type
csv_files = [f for f in data_files if f.endswith('.csv')]

print("=" * 70)
print(f"FILES FOUND IN OBD-II-Dataset/ FOLDER:")
print("=" * 70)

print(f"\n📊 CSV Files ({len(csv_files)}):")
for i, f in enumerate(csv_files[:10], 1):
    size = os.path.getsize(f'OBD-II-Dataset/{f}') / (1024 * 1024)
    print(f"  {i}. {f} ({size:.2f} MB)")
if len(csv_files) > 10:
    print(f"  ... and {len(csv_files) - 10} more files")


# Pick first data file to analyze
first_file = None
if csv_files:
    first_file = csv_files[0]
    file_type = 'CSV'

if first_file:
    print(f"\n{'=' * 70}")
    print(f"ANALYZING FIRST FILE: {first_file}")
    print("=" * 70)

    try:
        # Read file
        if first_file.endswith('.csv'):
            df = pd.read_csv(f'OBD-II-Dataset/{first_file}')
        else:
            df = pd.read_excel(f'OBD-II-Dataset/{first_file}')

        print(f"\n✓ Successfully loaded!")
        print(f"  Format: {file_type}")
        print(f"  Rows: {len(df):,}")
        print(f"  Columns: {len(df.columns)}")

        print("\n📋 COLUMN NAMES:")
        for i, col in enumerate(df.columns, 1):
            dtype = df[col].dtype
            non_null = df[col].notna().sum()
            print(f"  {i}. {col} ({dtype}) - {non_null:,} non-null values")

        print(f"\n{'=' * 70}")
        print("FIRST 5 ROWS:")
        print("=" * 70)
        print(df.head())

        print(f"\n{'=' * 70}")
        print("DATA STATISTICS:")
        print("=" * 70)
        print(df.describe())

        print(f"\n{'=' * 70}")
        print("MISSING VALUES:")
        print("=" * 70)
        missing = df.isnull().sum()
        if missing.sum() > 0:
            print(missing[missing > 0])
        else:
            print("✓ No missing values!")

        # Save column info
        with open('OBD-II-Dataset/COLUMN_INFO.txt', 'w') as f:
            f.write("OBD-II DATASET COLUMN INFORMATION\n")
            f.write("=" * 70 + "\n\n")
            f.write(f"File: {first_file}\n")
            f.write(f"Total Rows: {len(df):,}\n")
            f.write(f"Total Columns: {len(df.columns)}\n\n")
            f.write("COLUMNS:\n")
            f.write("-" * 70 + "\n")
            for i, col in enumerate(df.columns, 1):
                f.write(f"{i}. {col} ({df[col].dtype})\n")

        print(f"\n✓ Column info saved to: OBD-II-Dataset/COLUMN_INFO.txt")
        print("\n⚠️  READ THAT FILE TO UNDERSTAND YOUR DATA!")

    except Exception as e:
        print(f"\n✗ Error reading file: {e}")
        print("\nTrying with different encoding...")
        try:
            df = pd.read_csv(f'OBD-II-Dataset/{first_file}', encoding='latin1')
            print("✓ Loaded with latin1 encoding")
        except Exception as e2:
            print(f"✗ Still failed: {e2}")
            print("\n⚠️  Please check the file format manually")

else:
    print("\n⚠️  NO DATA FILES FOUND!")
    print("Please make sure you extracted the .tar file correctly")
    print("and copied the files to the data/ folder")

print("\n" + "=" * 70)
print("NEXT STEPS:")
print("=" * 70)
print("1. Read data/COLUMN_INFO.txt to see column names")
print("2. We'll create a script to load this into your database")
print("3. Map OBD-II columns to your Vehicle model")