"""
test_basic.py - Basic Test Cases
Tests for the query engine and data validation.
Run with: pytest tests/test_basic.py -v
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from database.db_setup import create_database, get_connection
from ai_engine.query_engine import execute_query, validate_sql


# --- Setup: create database before tests ---
@pytest.fixture(autouse=True)
def setup_db():
    """Create the database before each test."""
    create_database()


# TEST 1: Total revenue question returns a valid number
def test_total_revenue():
    result = execute_query("What is the total revenue?")
    assert result["error"] is None
    assert result["data"] is not None
    assert len(result["data"]) == 1
    assert result["data"][0]["total_revenue"] > 0
    print(f"Total revenue: {result['data'][0]['total_revenue']}")


# TEST 2: Top product question returns exactly one product
def test_top_product():
    result = execute_query("Which product generated the highest revenue?")
    assert result["error"] is None
    assert len(result["data"]) == 1
    assert "Product" in result["data"][0]
    print(f"Top product: {result['data'][0]['Product']}")


# TEST 3: Monthly trend returns multiple months
def test_monthly_trend():
    result = execute_query("What is the monthly revenue trend?")
    assert result["error"] is None
    assert len(result["data"]) >= 3  # At least 3 months of data
    print(f"Months found: {len(result['data'])}")


# TEST 4: Invalid question returns error message
def test_invalid_question():
    result = execute_query("What is the meaning of life?")
    assert result["error"] is not None
    assert "could not understand" in result["error"].lower()


# TEST 5: SQL validation blocks dangerous queries
def test_sql_validation_blocks_delete():
    is_safe, msg = validate_sql("DELETE FROM sales")
    assert is_safe is False
    assert "DELETE" in msg


# EDGE CASE: Empty question
def test_empty_question():
    result = execute_query("")
    assert result["error"] is not None

