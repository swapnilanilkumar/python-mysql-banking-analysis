"""
Connects Python to the MySQL banking database, joins the tables,
and draws a chart of average loans and deposits by loyalty class.

Before running, set your MySQL password as an environment variable
(so it is never written inside the code):
    Windows (PowerShell):  $env:MYSQL_PASSWORD = "your_password"
    Mac / Linux:           export MYSQL_PASSWORD="your_password"
"""
import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)

# ---------- 1. Connect to MySQL ----------
url = URL.create(
    drivername="mysql+pymysql",
    username="root",
    password=os.environ["MYSQL_PASSWORD"],   # read from environment, not typed here
    host="localhost",
    port=3306,
    database="banking_db",
)
engine = create_engine(url)

# ---------- 2. Join the tables into one dataset ----------
query = """
SELECT c.client_code, c.full_name, c.age, c.estimated_income,
       n.nationality_name, l.loyalty_name, f.fee_name,
       a.bank_loans, a.bank_deposits
FROM customers c
JOIN nationalities n     ON n.nationality_id = c.nationality_id
JOIN customer_accounts a ON a.customer_id = c.customer_id
JOIN loyalty_classes l   ON l.loyalty_id = a.loyalty_id
JOIN fee_structures f    ON f.fee_id = a.fee_id
ORDER BY c.customer_id
"""
df = pd.read_sql(query, engine)

# ---------- 3. Chart: average loans and deposits by loyalty class ----------
order = ["Jade", "Silver", "Gold", "Platinum"]
avg = (df.groupby("loyalty_name")[["bank_loans", "bank_deposits"]]
         .mean().reindex(order))

ax = avg.plot(kind="bar", figsize=(9, 5.5), width=0.7)
ax.set_title("Average Loans and Deposits by Loyalty Class")
ax.set_xlabel("Loyalty class")
ax.set_ylabel("Average amount")
ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x/1000:,.0f}K"))
ax.legend(["Avg loans", "Avg deposits"], loc="upper center",
          bbox_to_anchor=(0.5, -0.12), ncol=2, frameon=False)

for container in ax.containers:
    ax.bar_label(container, labels=[f"{v/1000:,.0f}K" for v in container.datavalues],
                 fontsize=8, padding=2)

plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig("loyalty_chart.png", dpi=150)
plt.show()

# ---------- 4. Quick look at the data ----------
print(df.head(5))
print(df.shape)
print(df.describe())
print(df.groupby("loyalty_name")[["bank_loans", "bank_deposits"]].mean().round(2))

engine.dispose()
