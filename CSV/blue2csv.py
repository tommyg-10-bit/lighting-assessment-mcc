import pandas as pd
import glob
import os

# Get all CSV files
files = glob.glob('*.csv')

for file in files:
    # Load the CSV
    df: pd.DataFrame = pd.read_csv(file, on_bad_lines='skip')

    # 1. Delete rows 530 through 550 (inclusive)
    # No headers, so index 530-550 corresponds to row 530-550
    df = df.drop(df.index[530:550])

    # 2. Make cell a3="% BLUE" 
    # Assumes 'a3' means 3rd row, 1st column (index 2, column 0)
    df.iloc[1, 0] = "% BLUE"

    # 3. Calculate formula and put it in cell A3 (Assuming 'a3' was a label)
    # Let's say B is the second column (index 1)
    try:
        # Sums b149 to b248 and divides by sum of b149 to b529
        # Python index is 0-based, so B149 is index 148
        numerator = df.iloc[148:247, 1].astype(float).sum()
        denominator = df.iloc[148:528, 1].astype(float).sum()
        formula_result = 100 * numerator / denominator if denominator != 0 else 0
        
        # Placing the formula result in another cell, or updating A3
        # If A3 must contain both "% BLUE" and the formula, this needs adjustment.
        # Assuming you want to add the result to a different cell or format it:
        df.iloc[1, 1] = f"{formula_result:.4f}"
    except IndexError:
        print(f"File {file} too short, skipping formula.")

    # Save the modified file, potentially in a new folder
    df.to_csv(f"updated_{os.path.basename(file)}", index=False)

print("Processing complete.")