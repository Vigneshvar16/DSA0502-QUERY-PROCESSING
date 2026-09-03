# Safe Comprehensive Data Visualization Project
# Install packages if needed:
# pip install pandas matplotlib openpyxl

import os
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import filedialog

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# -------------------- 1. Safely choose and import dataset --------------------
root = tk.Tk()
root.withdraw()  # Hide the small Tkinter window

file_path = filedialog.askopenfilename(
    title="Select a CSV or Excel dataset",
    filetypes=[
        ("Data files", "*.csv *.xlsx *.xls"),
        ("CSV files", "*.csv"),
        ("Excel files", "*.xlsx *.xls"),
        ("All files", "*.*")
    ]
)

if not file_path:
    print("No file selected. Program stopped safely.")
    raise SystemExit

file_path = Path(file_path)

try:
    if file_path.suffix.lower() == ".csv":
        try:
            df = pd.read_csv(file_path)
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, encoding="latin1")
    elif file_path.suffix.lower() in [".xlsx", ".xls"]:
        df = pd.read_excel(file_path)
    else:
        print("Unsupported file type. Please select a CSV or Excel file.")
        raise SystemExit
except Exception as error:
    print(f"Could not read the file: {error}")
    raise SystemExit

if df.empty:
    print("The selected dataset is empty.")
    raise SystemExit

print("\n" + "=" * 60)
print("DATASET IMPORTED SUCCESSFULLY")
print("=" * 60)

# -------------------- 2. Explore rows, columns, and data types --------------------
print("\nFirst 5 rows:")
print(df.head())

print(f"\nRows and columns: {df.shape}")
print("\nColumn names:")
print(df.columns.tolist())

print("\nData types:")
print(df.dtypes)

print("\nMissing values before cleaning:")
print(df.isnull().sum())

# -------------------- 3. Handle missing values --------------------
numeric_columns = df.select_dtypes(include=np.number).columns.tolist()
category_columns = df.select_dtypes(exclude=np.number).columns.tolist()

for column in numeric_columns:
    df[column] = df[column].fillna(df[column].median())

for column in category_columns:
    mode_value = df[column].mode()
    fill_value = mode_value.iloc[0] if not mode_value.empty else "Unknown"
    df[column] = df[column].fillna(fill_value)

# -------------------- 4. Remove duplicates --------------------
duplicate_count = int(df.duplicated().sum())
df_cleaned = df.drop_duplicates().copy()

print(f"\nDuplicate records removed: {duplicate_count}")
print("\nMissing values after cleaning:")
print(df_cleaned.isnull().sum())

# -------------------- 5. Descriptive statistics --------------------
print("\nDescriptive statistics:")
print(df_cleaned.describe(include="all"))

# -------------------- 6. Identify outliers using IQR --------------------
outlier_summary = {}

for column in numeric_columns:
    q1 = df_cleaned[column].quantile(0.25)
    q3 = df_cleaned[column].quantile(0.75)
    iqr = q3 - q1

    lower_limit = q1 - 1.5 * iqr
    upper_limit = q3 + 1.5 * iqr

    outliers = df_cleaned[
        (df_cleaned[column] < lower_limit) |
        (df_cleaned[column] > upper_limit)
    ]

    outlier_summary[column] = len(outliers)

print("\nOutlier summary:")
for column, count in outlier_summary.items():
    print(f"{column}: {count} outlier(s)")

# -------------------- 7. Correlations --------------------
if len(numeric_columns) >= 2:
    correlation_matrix = df_cleaned[numeric_columns].corr()

    print("\nCorrelation matrix:")
    print(correlation_matrix)

    plt.figure(figsize=(10, 6))
    plt.imshow(correlation_matrix, cmap="coolwarm", aspect="auto")
    plt.colorbar(label="Correlation")
    plt.xticks(range(len(numeric_columns)), numeric_columns, rotation=45, ha="right")
    plt.yticks(range(len(numeric_columns)), numeric_columns)
    plt.title("Correlation Heatmap")
    plt.tight_layout()
    plt.show()

# -------------------- 8. Grouping --------------------
if category_columns and numeric_columns:
    category_column = category_columns[0]
    numeric_column = numeric_columns[0]

    grouped_data = (
        df_cleaned.groupby(category_column)[numeric_column]
        .agg(["count", "mean", "sum", "min", "max"])
        .sort_values("mean", ascending=False)
    )

    print(f"\nGrouped analysis: {numeric_column} by {category_column}")
    print(grouped_data)

# -------------------- 9. Visualizations --------------------
# Chart 1: Histogram
if numeric_columns:
    first_numeric = numeric_columns[0]

    plt.figure(figsize=(8, 5))
    plt.hist(df_cleaned[first_numeric].dropna(), bins=20,
             color="skyblue", edgecolor="black")
    plt.title(f"Distribution of {first_numeric}")
    plt.xlabel(first_numeric)
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.show()

# Chart 2: Boxplot
if numeric_columns:
    plt.figure(figsize=(8, 5))
    plt.boxplot(df_cleaned[first_numeric].dropna(), vert=False)
    plt.title(f"Boxplot of {first_numeric}")
    plt.xlabel(first_numeric)
    plt.tight_layout()
    plt.show()

# Chart 3: Bar chart
if category_columns:
    first_category = category_columns[0]
    category_counts = df_cleaned[first_category].value_counts().head(10)

    plt.figure(figsize=(10, 5))
    category_counts.plot(kind="bar", color="seagreen")
    plt.title(f"Top Categories in {first_category}")
    plt.xlabel(first_category)
    plt.ylabel("Number of Records")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.show()

# Optional Chart 4: Scatter plot
if len(numeric_columns) >= 2:
    plt.figure(figsize=(8, 5))
    plt.scatter(
        df_cleaned[numeric_columns[0]],
        df_cleaned[numeric_columns[1]],
        alpha=0.6,
        color="purple"
    )
    plt.title(f"{numeric_columns[0]} vs {numeric_columns[1]}")
    plt.xlabel(numeric_columns[0])
    plt.ylabel(numeric_columns[1])
    plt.tight_layout()
    plt.show()

# -------------------- 10. Five observations --------------------
print("\n" + "=" * 60)
print("FIVE OBSERVATIONS")
print("=" * 60)

print(f"1. The cleaned dataset contains {df_cleaned.shape[0]} rows and "
      f"{df_cleaned.shape[1]} columns.")

print(f"2. {duplicate_count} duplicate record(s) were found and removed.")

if numeric_columns:
    highest_average_column = df_cleaned[numeric_columns].mean().idxmax()
    highest_average = df_cleaned[highest_average_column].mean()
    print(f"3. '{highest_average_column}' has the highest average value: "
          f"{highest_average:.2f}.")
else:
    print("3. The dataset has no numeric columns for average-value analysis.")

if outlier_summary:
    most_outlier_column = max(outlier_summary, key=outlier_summary.get)
    print(f"4. '{most_outlier_column}' has the most outliers: "
          f"{outlier_summary[most_outlier_column]}.")
else:
    print("4. No numeric columns were available for outlier detection.")

if category_columns:
    most_common_category = df_cleaned[category_columns[0]].value_counts().idxmax()
    most_common_count = df_cleaned[category_columns[0]].value_counts().max()
    print(f"5. The most common '{category_columns[0]}' value is "
          f"'{most_common_category}' with {most_common_count} record(s).")
else:
    print("5. No categorical columns were available for category analysis.")

# -------------------- 11. Save cleaned dataset safely --------------------
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_file = file_path.parent / f"cleaned_{file_path.stem}_{timestamp}.csv"

df_cleaned.to_csv(output_file, index=False)

print("\n" + "=" * 60)
print(f"Cleaned dataset saved safely as:\n{output_file}")
print("=" * 60)