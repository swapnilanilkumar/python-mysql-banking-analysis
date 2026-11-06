# Banking Customer Analysis – Python and MySQL

**College Project | Tools: Python (pandas, SQLAlchemy, matplotlib) and MySQL**

---

## 1. What is this project about?

Banks keep their information in databases, not in single spreadsheets. This project shows the full path from a database to an answer:

1. Customer data from a bank is stored in a **MySQL database**.
2. **Python** connects to that database and pulls the data using an **SQL query**.
3. The data is checked for problems and **cleaned**.
4. The results are summarised and shown as a **chart**.

**Business question answered:**
> How do customers in different loyalty classes (Jade, Silver, Gold, Platinum) compare in the average loans they hold and the average deposits they keep with the bank?

---

## 2. About the data

| Detail | Value |
|---|---|
| Source | Sample banking dataset provided by the college |
| File | `Banking.csv` |
| Customers | **3,000** |
| Columns | **25** |
| Database name | `banking_db` (MySQL) |

**What the data contains for each customer:**
- **Personal details:** client ID, name, age, nationality, occupation
- **Bank relationship:** fee structure (Low, Mid, High), loyalty class (Jade, Silver, Gold, Platinum), join date, banking contact
- **Money details:** estimated income, bank loans, bank deposits, checking and saving accounts, credit card balance, foreign currency account, business lending
- **Other:** number of credit cards, properties owned, risk weighting

A small sample of the data (first 25 rows) is in [`data/Banking_sample_25_rows.csv`](data/Banking_sample_25_rows.csv).

**Customers in each loyalty class:**

| Loyalty class | Customers |
|---|---|
| Jade | 1,331 |
| Silver | 767 |
| Gold | 585 |
| Platinum | 317 |

---

## 3. How the database is organised

The data is stored in MySQL as several **related tables** instead of one big table. Each table holds one kind of information and the tables are linked using ID numbers.

| Table | What it holds |
|---|---|
| `customers` | Customer details such as client code, name, age, income |
| `nationalities` | The list of nationalities |
| `customer_accounts` | Each customer's loans and deposits, linked to a loyalty class and a fee type |
| `loyalty_classes` | The list of loyalty classes (Jade, Silver, Gold, Platinum) |
| `fee_structures` | The list of fee types |

```
nationalities ──┐
                ├── customers ── customer_accounts ──┬── loyalty_classes
                                                     └── fee_structures
```

**Why this is useful:** a nationality or loyalty class name is stored only once and referred to by an ID, so the same text is not repeated thousands of times and it is easier to keep the data consistent.

---

## 4. Data cleaning and checks

Before analysing the data, I checked its quality. The checks can be repeated by running [`code/data_checks.py`](code/data_checks.py).

### Check 1 – Missing values and wrong entries

| Check | Result |
|---|---|
| Missing values in any column | **0** |
| Negative loans, deposits or income | **0** |
| Zero or negative income | **0** |
| Age range | 17 to 85 (all reasonable) |
| Completely identical rows | **0** |

**Result:** the data had no missing values and no impossible numbers, so no rows had to be removed.

### Check 2 – Repeated Client IDs

While checking, I found that **59 Client IDs appear twice**. The question was whether these were duplicate records that should be deleted.

After looking closer, **all 59 repeated IDs belong to two different people each**, with different names and different details. They are not duplicates, so deleting them would have wrongly removed 59 real customers.

**How it was handled:** each customer is identified in the database by a separate `customer_id`, and the original Client ID is kept as `client_code`. This way both people sharing an ID are kept, and nobody is lost.

Output of the checks:

```
Rows and columns: (3000, 25)

Total missing values: 0

Negative amounts: 0
Zero or negative income: 0
Age range: 17 to 85

Completely identical rows: 0
Client IDs that appear more than once: 59
Of these, IDs used by different people: 59
```

---

## 5. Code and explanation

File: [`code/connector.py`](code/connector.py)

### Step 1 – Connect Python to MySQL

```python
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

url = URL.create(
    drivername="mysql+pymysql",
    username="root",
    password=os.environ["MYSQL_PASSWORD"],
    host="localhost",
    port=3306,
    database="banking_db",
)
engine = create_engine(url)
```

- `SQLAlchemy` and `PyMySQL` are the tools that let Python talk to MySQL.
- The URL tells Python where the database is (`localhost`), which one to open (`banking_db`) and which user to log in as.
- The password is **read from the computer's environment** and not typed in the code, so it is never shared when the code is uploaded to GitHub.

### Step 2 – Join the tables with an SQL query

```python
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
```

- The data is spread across 5 tables, so the query uses **JOIN** to bring it back together, one row per customer.
- `ON ... = ...` tells SQL which ID numbers match between two tables.
- `SELECT` picks only the columns needed for this analysis.
- `pd.read_sql(...)` runs the query and puts the result into a pandas table called `df`.

### Step 3 – Find the average loans and deposits for each loyalty class

```python
order = ["Jade", "Silver", "Gold", "Platinum"]
avg = (df.groupby("loyalty_name")[["bank_loans", "bank_deposits"]]
         .mean().reindex(order))
```

- `groupby("loyalty_name")` groups customers by loyalty class.
- `.mean()` finds the average loans and average deposits in each group.
- `.reindex(order)` places the classes in the order Jade, Silver, Gold, Platinum.

### Step 4 – Draw the chart

```python
ax = avg.plot(kind="bar", figsize=(9, 5.5), width=0.7)
ax.set_title("Average Loans and Deposits by Loyalty Class")
...
plt.savefig("loyalty_chart.png", dpi=150)
```

- A bar chart is drawn with two bars for each class, one for loans and one for deposits.
- Labels such as `606K` are added on top of each bar so values can be read directly.
- The chart is saved as an image file.

---

## 6. Output

![Average Loans and Deposits by Loyalty Class](images/loyalty_chart.png)

| Loyalty class | Average loans | Average deposits |
|---|---|---|
| Jade | 606K | 697K |
| Silver | 591K | 658K |
| Gold | 574K | 664K |
| Platinum | 565K | 612K |

---

## 7. What I understood from the results

- **In every loyalty class, average deposits are higher than average loans.** The bank holds more of its customers' money than it has lent them, in all four classes.
- **Jade customers have the highest averages** for both loans (606K) and deposits (697K).
- **Platinum customers have the lowest averages** for both loans (565K) and deposits (612K), even though Platinum sounds like the top class.
- **Platinum is also the smallest group** with 317 customers, compared with 1,331 in Jade, so its average comes from far fewer people.
- **The gap between deposits and loans is smallest for Platinum** (about 47K) and largest for Jade (about 91K) and Gold (about 90K).

---

## 8. Limitations

- The data is a **sample dataset from the college**, so the findings show how the method works and are not conclusions about a real bank.
- The chart compares **averages only**. It does not show how spread out the amounts are inside each class, and a few very large accounts can pull an average up.
- The analysis does not explain *why* the classes differ, for example how a customer is placed in a loyalty class. That would need more information.

---

## 9. How to run it yourself

1. Install Python and MySQL, and create the `banking_db` database with the banking tables.
2. Install the packages:
   ```
   pip install -r requirements.txt
   ```
3. Set your MySQL password (do not type it inside the code):
   - Windows PowerShell: `$env:MYSQL_PASSWORD = "your_password"`
   - Mac / Linux: `export MYSQL_PASSWORD="your_password"`
4. Run the connector: `python code/connector.py`
5. To repeat the data checks, put `Banking.csv` in the same folder and run `python code/data_checks.py`.

---

## 10. Project structure

```
python-mysql-banking-analysis/
├── README.md
├── requirements.txt
├── code/
│   ├── connector.py
│   └── data_checks.py
├── data/
│   ├── Banking_sample_25_rows.csv
│   └── data_checks_output.txt
└── images/
    └── loyalty_chart.png
```

---

**Tools used:** Python, pandas, SQLAlchemy, PyMySQL, matplotlib, MySQL
**Author:** Swapnil Anilkumar
