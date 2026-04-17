import sqlite3
import pandas as pd
from pathlib import Path

# Connect to (or create) the database
conn = sqlite3.connect('../chicago_budget.db')
cursor = conn.cursor()

# Run our schema to create the tables
cursor.executescript('''
    CREATE TABLE IF NOT EXISTS departments (
        department_number   INTEGER PRIMARY KEY,
        department_description TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS appropriations (
        id                              INTEGER PRIMARY KEY AUTOINCREMENT,
        fund_type                       TEXT,
        fund_code                       TEXT,
        fund_description                TEXT,
        department_number               INTEGER,
        appropriation_authority         TEXT,
        appropriation_authority_desc    TEXT,
        appropriation_account           TEXT,
        appropriation_account_desc      TEXT,
        amount                          REAL,
        fiscal_year                     INTEGER,
        FOREIGN KEY (department_number) REFERENCES departments(department_number)
    );
''')
conn.commit()

print("Tables created successfully")


# Load the CSV files
df_2024 = pd.read_csv('Budget_-_2024_Budget_Ordinance_-_Appropriations_20260417.csv')
df_2025 = pd.read_csv('Budget_-_2025_Budget_Ordinance_-_Appropriations_20260417.csv')

print(f"2024 rows: {len(df_2024)}")
print(f"2025 rows: {len(df_2025)}")
print(df_2025.columns.tolist())



# Extract unique departments from both years combined
departments = pd.concat([
    df_2024[['DEPARTMENT NUMBER', 'DEPARTMENT DESCRIPTION']],
    df_2025[['DEPARTMENT NUMBER', 'DEPARTMENT DESCRIPTION']]
]).drop_duplicates(subset='DEPARTMENT NUMBER')

# Load departments into the database
for _, row in departments.iterrows():
    cursor.execute('''
        INSERT OR IGNORE INTO departments 
        (department_number, department_description)
        VALUES (?, ?)
    ''', (row['DEPARTMENT NUMBER'], row['DEPARTMENT DESCRIPTION']))

print(f"Departments loaded: {len(departments)}")
conn.commit()



# Load appropriations for both years
def load_appropriations(df, year, amount_column):
    for _, row in df.iterrows():
        cursor.execute('''
            INSERT INTO appropriations (
                fund_type, fund_code, fund_description,
                department_number, appropriation_authority,
                appropriation_authority_desc, appropriation_account,
                appropriation_account_desc, amount, fiscal_year
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            row['FUND TYPE'],
            row['FUND CODE'],
            row['FUND DESCRIPTION'],
            row['DEPARTMENT NUMBER'],
            row['APPROPRIATION AUTHORITY'],
            row['APPROPRIATION AUTHORITY DESCRIPTION'],
            row['APPROPRIATION ACCOUNT'],
            row['APPROPRIATION ACCOUNT DESCRIPTION'],
            float(str(row[amount_column]).replace('$', '').replace(',', '')),
            year
        ))
    conn.commit()
    print(f"{year} appropriations loaded: {len(df)} rows")

load_appropriations(df_2024, 2024, '2024 ORDINANCE (AMOUNT $)')
load_appropriations(df_2025, 2025, '2025 ORDINANCE (AMOUNT $)')

conn.close()
print("Database complete!")




query2 = '''
SELECT
    d.department_description,
    SUM(CASE WHEN a.fiscal_year = 2024 THEN a.amount ELSE 0 END) AS budget_2024,
    SUM(CASE WHEN a.fiscal_year = 2025 THEN a.amount ELSE 0 END) AS budget_2025,
    SUM(CASE WHEN a.fiscal_year = 2025 THEN a.amount ELSE 0 END) -
    SUM(CASE WHEN a.fiscal_year = 2024 THEN a.amount ELSE 0 END) AS variance
FROM appropriations a
JOIN departments d
    ON a.department_number = d.department_number
GROUP BY d.department_description
ORDER BY variance DESC;
'''

df2 = pd.read_sql_query(query2, conn)
df2['budget_2024'] = df2['budget_2024'].apply(lambda x: f"${x:,.0f}")
df2['budget_2025'] = df2['budget_2025'].apply(lambda x: f"${x:,.0f}")
df2['variance'] = df2['variance'].apply(lambda x: f"${x:,.0f}")
print("\nYear over Year Variance:")
print(df2.to_string())