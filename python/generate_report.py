import sqlite3
import pandas as pd
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

conn = sqlite3.connect('../chicago_budget.db')
client = Anthropic()

print("Pulling data from database...")

# Query 1 - 2025 budget by department
q1 = '''
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

# Query 2 - Year over year variance
q2 = '''
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

df1 = pd.read_sql_query(q1, conn)
df2 = pd.read_sql_query(q2, conn)

print("Data pulled successfully")
print(f"Departments analyzed: {len(df1)}")




print("Sending data to Claude for analysis...")

# Prepare data summary to send to Claude
summary_data = df2.to_string()

message = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": f"""You are a financial analyst writing an executive summary for a consulting client.
            
Below is Chicago's budget data comparing 2024 vs 2025 spending by department, including percentage change:

{summary_data}

Write a professional 3-4 paragraph executive summary highlighting:
1. The biggest budget increases and what they might signal
2. The biggest budget cuts and what they might signal  
3. Overall takeaways about Chicago's spending priorities

Write it in plain English as if presenting to a non-technical executive."""
        }
    ]
)

ai_summary = message.content[0].text
print("\n--- AI EXECUTIVE SUMMARY ---\n")
print(ai_summary)





#Excel Report
print("\nGenerating Excel report...")

output_path = '../output/chicago_budget_report.xlsx'

with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
    wb = writer.book

    # Formats
    header_fmt = wb.add_format({'bold': True, 'bg_color': '#1F3864', 
                                 'font_color': 'white', 'border': 1})
    currency_fmt = wb.add_format({'num_format': '$#,##0', 'border': 1})
    text_fmt = wb.add_format({'border': 1})
    green_fmt = wb.add_format({'num_format': '$#,##0', 'font_color': '#375623', 'border': 1})
    red_fmt = wb.add_format({'num_format': '$#,##0', 'font_color': '#C00000', 'border': 1})
    pct_green_fmt = wb.add_format({'num_format': '0.0"%"', 'font_color': '#375623', 'border': 1})
    pct_red_fmt = wb.add_format({'num_format': '0.0"%"', 'font_color': '#C00000', 'border': 1})

    # Sheet 1 - 2025 Budget
    df1.to_excel(writer, sheet_name='2025 Budget', index=False)
    ws1 = writer.sheets['2025 Budget']
    ws1.set_column('A:A', 45)
    ws1.set_column('B:B', 20)
    for col, header in enumerate(df1.columns):
        ws1.write(0, col, header, header_fmt)
    for row in range(len(df1)):
        ws1.write(row+1, 0, df1.iloc[row]['department_description'], text_fmt)
        ws1.write(row+1, 1, df1.iloc[row]['total_budget'], currency_fmt)

    # Sheet 2 - Year over Year
    df2.to_excel(writer, sheet_name='Year over Year', index=False)
    ws2 = writer.sheets['Year over Year']
    ws2.set_column('A:A', 45)
    ws2.set_column('B:D', 20)
    for col, header in enumerate(df2.columns):
        ws2.write(0, col, header, header_fmt)
    for row in range(len(df2)):
        ws2.write(row+1, 0, df2.iloc[row]['department_description'], text_fmt)
        ws2.write(row+1, 1, df2.iloc[row]['budget_2024'], currency_fmt)
        ws2.write(row+1, 2, df2.iloc[row]['budget_2025'], currency_fmt)
        pct = df2.iloc[row]['pct_change']
        fmt = pct_green_fmt if pct >= 0 else pct_red_fmt
        ws2.write(row+1, 3, pct, fmt)

    # Sheet 3 - AI Summary
    import re
    clean_summary = re.sub(r'\*+', '', ai_summary).replace('#', '').strip()
    ws3 = wb.add_worksheet('AI Summary')
    ws3.set_column('A:A', 100)
    ws3.write(0, 0, 'Executive Summary', header_fmt)
    wrap_fmt = wb.add_format({'text_wrap': True, 'valign': 'top', 'border': 1})
    ws3.set_row(1, 400)
    ws3.write(1, 0, clean_summary, wrap_fmt)

print(f"Report saved to {output_path}")
conn.close()