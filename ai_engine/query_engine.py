"""
query_engine.py - AI Query Engine
Capabilities:
  1. LangChain SQLDatabase Inspection:
     - Automatically inspects existing database tables and columns using LangChain's SQLDatabase utility
     - Can answer questions like "How are the tables columns", "What tables exist", "Show schema"
  2. LangChain + OpenAI LLM:
     - When OPENAI_API_KEY is configured, translates natural language questions to SQL
  3. Keyword Matching:
     - Deterministic fallback for predefined analytical questions
"""

import os
import re
from database.db_setup import get_connection, DB_PATH

# Try importing LangChain components
try:
    from langchain_community.utilities import SQLDatabase
    LANGCHAIN_DB_AVAILABLE = True
except ImportError:
    LANGCHAIN_DB_AVAILABLE = False


# =====================================================================
#  LANGCHAIN SQLDATABASE SCHEMA INSPECTOR
#  Uses LangChain SQLDatabase utility to inspect tables & columns
# =====================================================================

def get_langchain_sqldb():
    """Returns an instance of LangChain SQLDatabase for the sales DB."""
    if not LANGCHAIN_DB_AVAILABLE:
        return None
    try:
        abs_db_path = os.path.abspath(DB_PATH)
        return SQLDatabase.from_uri(f"sqlite:///{abs_db_path}")
    except Exception as e:
        print(f"[WARN] Failed to load LangChain SQLDatabase: {e}")
        return None


def get_schema_info_from_langchain(question):
    """
    Checks if user is asking about tables, columns, or schema.
    Uses LangChain SQLDatabase to inspect existing tables and columns.
    Returns: (answer, data, sql_query, description) or None
    """
    q = question.lower().strip()

    # Match questions regarding table structure, columns, schema
    schema_keywords = [
        "table", "tables", "column", "columns", "schema", 
        "structure", "fields", "what tables", "list tables"
    ]
    if not any(k in q for k in schema_keywords):
        return None

    # Use LangChain SQLDatabase if available
    db = get_langchain_sqldb()
    if db:
        try:
            tables = db.get_usable_table_names()
            table_info = db.get_table_info()
            
            # Format columns cleanly for table display
            columns_data = []
            conn = get_connection()
            cursor = conn.cursor()
            for t in tables:
                cursor.execute(f"PRAGMA table_info({t});")
                cols = cursor.fetchall()
                for c in cols:
                    columns_data.append({
                        "Table": t,
                        "Column_Name": c[1],
                        "Data_Type": c[2],
                        "Nullable": "Yes" if c[3] == 0 else "No"
                    })
            conn.close()

            table_names_str = ", ".join(tables)
            col_names_str = ", ".join([c["Column_Name"] for c in columns_data])
            answer = f"The database contains table(s) [{table_names_str}] with columns: {col_names_str}."

            return {
                "answer": answer,
                "data": columns_data,
                "sql_query": "PRAGMA table_info(sales);",
                "description": "Database Schema Information inspected via LangChain SQLDatabase",
                "method": "langchain_sqldatabase"
            }
        except Exception as e:
            print(f"[WARN] Error inspecting schema via LangChain: {e}")

    # Fallback to direct sqlite PRAGMA if LangChain isn't available
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        columns_data = []
        for t in tables:
            cursor.execute(f"PRAGMA table_info({t});")
            for c in cursor.fetchall():
                columns_data.append({
                    "Table": t,
                    "Column_Name": c[1],
                    "Data_Type": c[2]
                })
        conn.close()
        return {
            "answer": f"Database has table(s) {tables} with {len(columns_data)} columns.",
            "data": columns_data,
            "sql_query": "PRAGMA table_info(sales);",
            "description": "Database Schema Information",
            "method": "sqlite_schema_inspector"
        }
    except Exception as e:
        return None


# =====================================================================
#  LANGCHAIN LLM SETUP (Optional - activates if OPENAI_API_KEY is set)
# =====================================================================

SQL_PROMPT_TEMPLATE = """You are a SQL expert. Convert the user's question into a SQLite query.

Table name: sales
Columns:
  - Transaction_Id (text)
  - Order_date (date, stored as YYYY-MM-DD)
  - Product (text)       — e.g. Laptop Stand, Wireless Mouse, Monitor, Keyboard, Desk, Office Chair, USB-C Hub
  - Category (text)      — Accessories, Furniture, Electronics
  - Region (text)        — North, South, East, West
  - Sales_channel (text) — Online, Retail
  - Quantity (integer)
  - Unit_price (real)
  - Discount_amount (real)
  - Status (text)        — Completed, Cancelled, Returned
  - Revenue (real)       — pre-calculated as Quantity * Unit_price - Discount_amount

Rules:
  1. Only generate SELECT queries.
  2. Never generate DELETE, DROP, UPDATE, INSERT, ALTER, or TRUNCATE.
  3. For revenue questions, only include rows WHERE Status = 'Completed'.
  4. Use strftime('%Y-%m', Order_date) for monthly grouping.
  5. Return ONLY the SQL query, nothing else. No explanation.

Question: {question}
SQL:"""


def _setup_langchain():
    """Sets up LangChain with OpenAI LLM if OPENAI_API_KEY is present."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return None

    try:
        from langchain.prompts import PromptTemplate
        from langchain_community.llms import OpenAI

        prompt = PromptTemplate(
            input_variables=["question"],
            template=SQL_PROMPT_TEMPLATE,
        )
        llm = OpenAI(
            temperature=0,
            model="gpt-3.5-turbo-instruct",
            max_tokens=200,
            openai_api_key=api_key,
        )
        return prompt | llm
    except Exception as e:
        print(f"[WARN] LangChain setup failed: {e}")
        return None


langchain_chain = _setup_langchain()


def get_sql_from_langchain(question):
    """Uses LangChain LLM to convert a question to SQL."""
    if langchain_chain is None:
        return None, None
    try:
        raw_output = langchain_chain.invoke({"question": question})
        sql = raw_output.strip().replace("```sql", "").replace("```", "").strip()
        if sql:
            return sql, f"AI-generated query for: {question}"
    except Exception as e:
        print(f"[WARN] LangChain query failed: {e}")
    return None, None


# =====================================================================
#  KEYWORD MATCHING (Deterministic Fallback)
# =====================================================================

def get_keyword_query(question):
    """Maps recognized question patterns to deterministic SQL queries."""
    question_lower = question.lower().strip()

    # Q1: Total revenue
    if "total revenue" in question_lower or "total sales" in question_lower:
        sql = """
            SELECT ROUND(SUM(Revenue), 2) as total_revenue 
            FROM sales 
            WHERE Status = 'Completed'
        """
        return sql, "Total revenue from all completed transactions"

    # Q2: Highest revenue product
    if ("highest revenue" in question_lower and "product" in question_lower) or \
       "best selling" in question_lower or "top product" in question_lower:
        sql = """
            SELECT Product, ROUND(SUM(Revenue), 2) as total_revenue 
            FROM sales 
            WHERE Status = 'Completed'
            GROUP BY Product 
            ORDER BY total_revenue DESC 
            LIMIT 1
        """
        return sql, "Product with the highest total revenue"

    # Q3: Monthly revenue trend
    if "monthly" in question_lower and ("revenue" in question_lower or "trend" in question_lower):
        sql = """
            SELECT strftime('%Y-%m', Order_date) as month, 
                   ROUND(SUM(Revenue), 2) as monthly_revenue 
            FROM sales 
            WHERE Status = 'Completed'
            GROUP BY month 
            ORDER BY month
        """
        return sql, "Monthly revenue trend"

    # Q4: Region with highest sales
    if "region" in question_lower and ("highest" in question_lower or "most" in question_lower or "top" in question_lower):
        sql = """
            SELECT Region, ROUND(SUM(Revenue), 2) as total_revenue 
            FROM sales 
            WHERE Status = 'Completed'
            GROUP BY Region 
            ORDER BY total_revenue DESC 
            LIMIT 1
        """
        return sql, "Region with highest sales"

    # Q5: Revenue by region (all regions)
    if "region" in question_lower and "revenue" in question_lower:
        sql = """
            SELECT Region, ROUND(SUM(Revenue), 2) as total_revenue 
            FROM sales 
            WHERE Status = 'Completed'
            GROUP BY Region 
            ORDER BY total_revenue DESC
        """
        return sql, "Revenue breakdown by region"

    return None, None


# =====================================================================
#  SQL VALIDATION
# =====================================================================

def validate_sql(sql):
    """Blocks non-SELECT or destructive SQL commands."""
    sql_upper = sql.strip().upper()
    dangerous_keywords = ["DELETE", "DROP", "UPDATE", "INSERT", "ALTER", "TRUNCATE"]
    for keyword in dangerous_keywords:
        if keyword in sql_upper:
            return False, f"Blocked: {keyword} operation is not allowed"

    if not (sql_upper.startswith("SELECT") or sql_upper.startswith("PRAGMA")):
        return False, "Only SELECT and schema inspection queries are allowed"

    return True, "Query is safe"


# =====================================================================
#  MAIN EXECUTION FUNCTION
# =====================================================================

def execute_query(question):
    """
    Takes natural language question, checks schema queries via LangChain,
    attempts LLM text-to-SQL if configured, or falls back to keyword matching.
    """
    result = {
        "question": question,
        "answer": None,
        "sql_query": None,
        "data": None,
        "description": None,
        "error": None,
        "method": "keyword_matching"
    }

    # --- Step 1: Check if question asks about tables / columns / schema via LangChain ---
    schema_result = get_schema_info_from_langchain(question)
    if schema_result:
        result.update(schema_result)
        return result

    sql = None
    description = None

    # --- Step 2: Try LangChain LLM if API key configured ---
    if langchain_chain is not None:
        sql, description = get_sql_from_langchain(question)
        if sql:
            result["method"] = "langchain_llm"

    # --- Step 3: Fall back to keyword matching ---
    if sql is None:
        sql, description = get_keyword_query(question)

    if sql is None:
        result["error"] = "Sorry, I could not understand your question. Try asking about total revenue, top products, monthly trends, regional sales, or table columns."
        return result

    # --- Step 4: Validate SQL query ---
    is_safe, message = validate_sql(sql)
    if not is_safe:
        result["error"] = message
        return result

    # --- Step 5: Execute SQL ---
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(sql)
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        conn.close()

        result["sql_query"] = sql.strip()
        result["description"] = description
        result["data"] = [dict(zip(columns, row)) for row in rows]

        if len(rows) == 1 and len(columns) == 1:
            result["answer"] = f"{description}: {rows[0][0]}"
        elif len(rows) == 1:
            result["answer"] = f"{description}: {', '.join(str(v) for v in rows[0])}"
        else:
            result["answer"] = f"{description} ({len(rows)} results found)"

    except Exception as e:
        result["error"] = f"Database error: {str(e)}"

    return result
