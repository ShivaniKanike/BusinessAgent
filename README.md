# 📊 Mini BI Assistant

A simple AI-powered Business Intelligence assistant that lets users ask questions about sales data in plain English and get answers backed by real database queries.

> **Status**: Work in Progress — Core functionality works. LLM-based natural language processing via LangChain is partially set up.

---

## 🚀 Features (What Works)

- ✅ CSV data loaded into SQLite database with data cleaning
- ✅ Flask REST API to accept questions and return answers
- ✅ Keyword-based question matching → SQL query generation
- ✅ SQL validation (blocks DELETE, DROP, UPDATE, etc.)
- ✅ Simple HTML frontend with clickable suggestions
- ✅ Streamlit frontend (alternative UI)
- ✅ Basic test suite (6 test cases)

### Supported Questions

| # | Question | Status |
|---|----------|--------|
| 1 | What is the total revenue? | ✅ Working |
| 2 | Which product generated the highest revenue? | ✅ Working |
| 3 | What is the monthly revenue trend? | ✅ Working |
| 4 | Which region generated the highest sales? | ✅ Working |
| 5 | How did revenue change between two months? | ❌ Not implemented yet |

---

## 🔧 Not Yet Implemented (TODO)

- ❌ Full LLM integration via LangChain (prompt template is set up, but needs API key)
- ❌ Revenue comparison between two months
- ❌ Charts and visualizations in Streamlit
- ❌ File upload for custom CSV data
- ❌ Caching of repeated queries

---

## 📁 Project Structure

```
mini-bi-assistant/
├── data/
│   └── sales_data.csv          # Sales transaction data (51 records)
├── database/
│   └── db_setup.py             # Loads CSV into SQLite, data cleaning
├── ai_engine/
│   └── query_engine.py         # Keyword matching + LangChain setup (partial)
├── backend/
│   └── app.py                  # Flask REST API
├── frontend/
│   └── streamlit_app.py        # Streamlit UI
├── static/
│   └── index.html              # Simple HTML frontend
├── tests/
│   └── test_basic.py           # 6 test cases
├── requirements.txt
├── ARCHITECTURE.md             # Architecture diagram and explanation
├── AI_USAGE.md                 # How AI tools were used during development
└── README.md                   # This file
```

---

## ⚙️ Setup & Installation

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)

### Step 1: Clone the repository

```bash
git clone <your-repo-url>
cd mini-bi-assistant
```

### Step 2: Create a virtual environment (recommended)

```bash
python3 -m venv venv
source venv/bin/activate        # On Mac/Linux
# venv\Scripts\activate         # On Windows
```

### Step 3: Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Set up the database

```bash
python database/db_setup.py
```

This loads `data/sales_data.csv` into a SQLite database (`sales.db`).

---

## ▶️ Running the Application

### Option A: Flask API + HTML Frontend

```bash
python backend/app.py
```

Then open **http://localhost:5001** in your browser.

### Option B: Streamlit Frontend

```bash
streamlit run frontend/streamlit_app.py
```

Then open **http://localhost:8501** in your browser.

---

## 🧪 Running Tests

```bash
pytest tests/test_basic.py -v
```

### Test Cases

| # | Test | What It Checks |
|---|------|----------------|
| 1 | `test_total_revenue` | Total revenue returns a valid positive number |
| 2 | `test_top_product` | Top product query returns exactly one product |
| 3 | `test_monthly_trend` | Monthly trend returns at least 3 months |
| 4 | `test_invalid_question` | Unrecognized question returns an error message |
| 5 | `test_sql_validation_blocks_delete` | DELETE queries are blocked |
| 6 | `test_empty_question` | Empty string input returns an error |

---

## 🔌 API Usage

### POST `/api/ask`

**Request:**
```json
{
    "question": "What is the total revenue?"
}
```

**Response:**
```json
{
    "question": "What is the total revenue?",
    "answer": "Total revenue from all completed transactions: 812345.0",
    "sql_query": "SELECT ROUND(SUM(Revenue), 2) as total_revenue FROM sales WHERE Status = 'Completed'",
    "data": [{"total_revenue": 812345.0}],
    "description": "Total revenue from all completed transactions",
    "method": "keyword_matching",
    "error": null
}
```

### GET `/api/health`

Returns `{"status": "ok"}` if API is running.

---

## 🧠 AI Integration Approach

### Current (Working): Keyword Matching
The app uses simple keyword matching to identify question intent and map it to pre-defined SQL queries. This is deterministic and reliable but limited to known question patterns.

### Planned (Partial): LangChain + LLM
A LangChain prompt template is set up in `ai_engine/query_engine.py` for LLM-based text-to-SQL conversion. To enable it:
1. Set `OPENAI_API_KEY` in your environment
2. Uncomment the LLM chain code in `query_engine.py`

### Safety Measures
- All generated SQL is validated before execution
- Only `SELECT` statements are allowed
- `DELETE`, `DROP`, `UPDATE`, `INSERT`, `ALTER`, `TRUNCATE` are blocked

---

## ⚠️ Known Limitations

1. Only understands 4 specific question patterns (keyword-based)
2. Cannot compare revenue between two specific months
3. No charts or visual output
4. LangChain LLM integration requires an API key (not included)
5. No authentication or rate limiting on the API
6. Streamlit and Flask run as separate apps (not unified)

---

## 📖 Documentation

- [Architecture Diagram](ARCHITECTURE.md)
- [AI Tools Usage](AI_USAGE.md)

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.x |
| Backend | Flask |
| Database | SQLite |
| AI Framework | LangChain (partial) |
| Frontend | HTML/CSS/JS, Streamlit |
| Testing | pytest |

