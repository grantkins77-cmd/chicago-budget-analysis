import sqlite3
import pandas as pd

conn = sqlite3.connect('../chicago_budget.db')

query = '''
SELECT 
    d.department_description,
    SUM(a.amount) AS total_budget
FROM appropriations a
JOIN departments d 
    ON a.department_number = d.department_number
WHERE a.fiscal_year = 2025
GROUP BY d.department_description
ORDER BY total_budget DESC;
'''

df = pd.read_sql_query(query, conn)
df['total_budget'] = df['total_budget'].apply(lambda x: f"${x:,.0f}")
print(df.to_string())



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



query3 = '''
SELECT
    d.department_description,
    SUM(CASE WHEN a.fiscal_year = 2024 THEN a.amount ELSE 0 END) AS budget_2024,
    SUM(CASE WHEN a.fiscal_year = 2025 THEN a.amount ELSE 0 END) AS budget_2025,
    ROUND(
        (SUM(CASE WHEN a.fiscal_year = 2025 THEN a.amount ELSE 0 END) -
         SUM(CASE WHEN a.fiscal_year = 2024 THEN a.amount ELSE 0 END)) /
        SUM(CASE WHEN a.fiscal_year = 2024 THEN a.amount ELSE 0 END) * 100
    , 1) AS pct_change
FROM appropriations a
JOIN departments d
    ON a.department_number = d.department_number
GROUP BY d.department_description
ORDER BY pct_change DESC;
'''

df3 = pd.read_sql_query(query3, conn)
df3['budget_2024'] = df3['budget_2024'].apply(lambda x: f"${x:,.0f}")
df3['budget_2025'] = df3['budget_2025'].apply(lambda x: f"${x:,.0f}")
df3['pct_change'] = df3['pct_change'].apply(lambda x: f"{x:+.1f}%")
print("\nBudget % Change 2024 to 2025:")
print(df3.to_string())

conn.close()