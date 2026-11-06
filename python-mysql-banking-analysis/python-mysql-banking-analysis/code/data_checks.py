"""
Data quality checks on the college banking dataset (Banking.csv).

Checks:
  1. Missing values
  2. Wrong entries (negative or zero amounts, unusual ages)
  3. Repeated Client IDs - are they true duplicates or different people?
"""
import pandas as pd

df = pd.read_csv("Banking.csv", encoding="utf-8-sig")

print("Rows and columns:", df.shape)

# 1. Missing values
print("\nTotal missing values:", int(df.isna().sum().sum()))

# 2. Wrong entries
money_cols = ["Estimated Income", "Bank Loans", "Bank Deposits"]
print("\nNegative amounts:", int((df[money_cols] < 0).sum().sum()))
print("Zero or negative income:", int((df["Estimated Income"] <= 0).sum()))
print("Age range:", df["Age"].min(), "to", df["Age"].max())

# 3. Repeated Client IDs
print("\nCompletely identical rows:", int(df.duplicated().sum()))

repeated = df[df["Client ID"].duplicated(keep=False)]
print("Client IDs that appear more than once:", repeated["Client ID"].nunique())

names_per_id = repeated.groupby("Client ID")["Name"].nunique()
print("Of these, IDs used by different people:", int((names_per_id > 1).sum()))
