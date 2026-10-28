# Architecture Overview

## System Architecture (Simple)

```
┌──────────────────────────────────────────────────┐
│                   User Interface                  │
│         (HTML Frontend / Streamlit App)           │
│                                                    │
│  User types a question in plain English            │
└────────────────────┬─────────────────────────────┘
                     │  HTTP POST /api/ask
                     ▼
┌──────────────────────────────────────────────────┐
│                Flask Backend API                  │
│               (backend/app.py)                    │
│                                                    │
│  - Receives question as JSON                       │
│  - Passes to Query Engine                          │
│  - Returns structured JSON response                │
└────────────────────┬─────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────┐
│             AI Query Engine                       │
│         (ai_engine/query_engine.py)               │
│                                                    │
│  - Keyword matching (working)                      │
│  - LangChain LLM text-to-SQL (partial/TODO)       │
│  - SQL validation (blocks DELETE/DROP etc.)        │
│  - Executes safe SELECT queries                    │
└────────────────────┬─────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────┐
│              SQLite Database                      │
│              (sales.db)                           │
│                                                    │
│  - Loaded from CSV on startup                      │
│  - Cleaned data (missing values handled)           │
│  - Revenue column pre-calculated                   │
└──────────────────────────────────────────────────┘
```

## Data Flow

1. User enters a natural language question
2. Flask API receives the question
3. Query Engine matches keywords to a pre-defined SQL pattern
4. SQL is validated (only SELECT allowed)
5. Query runs against SQLite database
6. Results are returned as JSON with answer + supporting data

## Technology Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.x |
| Backend | Flask |
| Database | SQLite |
| AI/NLP | Keyword matching (LangChain partially set up) |
| Frontend | HTML/CSS/JS + Streamlit |
| Testing | pytest |

