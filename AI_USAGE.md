# AI Tools Usage During Development

## AI Tools Used

- **ChatGPT / Claude** — Used for generating boilerplate code, understanding LangChain setup, and writing SQL queries.
- **GitHub Copilot** — Used for code autocompletion while writing Python files.

## How AI Was Used

1. **Project Structure**: Asked AI to suggest a clean folder structure for a Flask + SQLite project.
2. **SQL Queries**: Used AI to generate correct SQL queries for revenue calculations with GROUP BY and aggregations.
3. **LangChain Setup**: Referenced AI suggestions for setting up a basic LangChain prompt template for text-to-SQL conversion.
4. **HTML/CSS**: Used AI to generate the frontend HTML page with styling.
5. **Test Cases**: Asked AI to suggest test scenarios for the query engine.

## Problems Encountered

1. **LangChain API Key**: Could not fully integrate LLM-based text-to-SQL because it requires an OpenAI API key. Implemented keyword matching as a working fallback.
2. **Date Parsing**: The CSV had DD-MM-YYYY format which needed explicit format specification in pandas.
3. **Missing Data**: Row TXN0051 had a missing Unit_price. Added data cleaning to drop such rows.
4. **Import Paths**: Had issues with Python imports across folders. Solved by adding `sys.path` adjustments.

## How I Debugged

- Used `print()` statements to check data loading.
- Tested SQL queries directly in SQLite before putting them in code.
- Ran `pytest -v` to catch errors in the query engine.

## What I Would Improve With Another Day

1. **Full LLM Integration**: Connect OpenAI or Gemini API via LangChain for true natural language to SQL conversion.
2. **Revenue Comparison**: Add ability to compare revenue between two specific months.
3. **Charts**: Add matplotlib or plotly charts in Streamlit for visual trends.
4. **More Question Patterns**: Support more natural language variations.
5. **Better Error Messages**: More helpful guidance when a question is not understood.

