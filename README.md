# Chicago Budget Analysis Tool

An automated data pipeline that analyzes real City of Chicago budget data, 
identifies year-over-year spending trends, and generates an AI-powered 
executive summary — all with a single command.

## What It Does

1. Loads real Chicago budget data (2024 & 2025) into a SQL database
2. Runs analytical SQL queries to find spending trends and variances
3. Uses the Claude AI API to generate a professional executive summary
4. Exports a formatted Excel report with color-coded insights

## Tech Stack

- **Python** — data pipeline and automation
- **SQL (SQLite)** — relational database design and analytical queries
- **Claude AI API** — automated executive summary generation
- **Excel (xlsxwriter)** — formatted report output
- **Pandas** — data manipulation and transformation

## Key Findings (2024 vs 2025)

- Chicago Department of Transportation: **+37.4%** ($554M increase)
- Chicago Department of Public Health: **-23.5%** ($212M cut)
- Department of Planning and Development: **-34.5%**
- Office of Budget and Management: **-40.5%**

## How To Run

1. Clone the repository
2. Install dependencies: `pip install anthropic pandas xlsxwriter python-dotenv`
3. Add your Anthropic API key to a `.env` file: `ANTHROPIC_API_KEY=your_key`
4. Load the data: `python python/load_data.py`
5. Generate the report: `python python/generate_report.py`

## Data Source

City of Chicago Open Data Portal — Budget Ordinance Appropriations  
https://data.cityofchicago.org