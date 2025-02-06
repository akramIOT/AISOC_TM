from langchain_core.prompts import FewShotPromptTemplate, PromptTemplate
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import ConfigurableField
from pydantic import BaseModel, Field
from langchain_core.tools import tool

from langchain.agents import initialize_agent
from langchain.tools import Tool
from langchain.llms import OpenAI
from sql_examples import SQL_EXAMPLES

import os
import sys
import sqlite3
import streamlit as st
from langchain_community.utilities import SQLDatabase
from langchain_openai import ChatOpenAI
from typing import Dict, List, Optional, Any

# Temporary increase of recursion limit
sys.setrecursionlimit(10000)

# OpenAI API key configuration
os.environ["OPENAI_API_KEY"] = "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"

# Database setup
db_directory = "/Users/akram/Desktop/MOTIFIC_AI/TM"
db_path = os.path.join(db_directory, "database.db")
os.makedirs(db_directory, exist_ok=True)

# Create and initialize the database
if not os.path.exists(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create a sample table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sample_table (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT
            )
        """)

        # Insert some sample data
        cursor.execute("""
            INSERT INTO sample_table (name, description)
            VALUES ('Test Item', 'This is a test description')
        """)

        conn.commit()
        conn.close()
        print("Database initialized with sample table")
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise

try:
    # Connect using SQLDatabase
    db_uri = f"sqlite:///{db_path}"
    db = SQLDatabase.from_uri(db_uri)
    print("Successfully connected to the database")
    print(f"Dialect: {db.dialect}")
    print(f"Available tables: {db.get_usable_table_names()}")

except Exception as e:
    print(f"Error connecting to database: {e}")

# SQL Database with Few Shot Examples
class SQLDatabaseFewShot(SQLDatabase):
    def __init__(self, db_uri: str, examples: List[Dict[str, str]]):
        super().__init__(db_uri)
        self.examples = examples

    def run(self, query: str) -> str:
        few_shot_examples = "\n".join(f"Input: {example['input']}\nQuery: {example['query']}" for example in self.examples)
        prompt = f"""{few_shot_examples}

Input: {query}
Query:"""
        try:
            response = ChatOpenAI().generate(prompt)
            return response.strip()
        except Exception as e:
            print(f"Error generating SQL query: {e}")
            return None

# SQL Query Generation Tool
@tool
def generate_sql_query(requirement: str) -> str:
    """Generate a SQL query based on a natural language requirement."""
    prompt = f"""You are an expert SQL developer. Convert the following requirement into a well-written SQL query:

{requirement}

SQL Query:"""
    try:
        response = ChatOpenAI().generate(prompt)
        return response.strip()
    except Exception as e:
        print(f"Error generating SQL query: {e}")
        return None

# SQL Query Optimization Tool
@tool
def improve_sql_query(query: str) -> str:
    """Improve and optimize a SQL query for better performance and readability."""
    prompt = f"""You are an SQL optimization expert. Improve the following SQL query for readability, efficiency, and performance:

{query}

Improved SQL Query:"""
    try:
        response = ChatOpenAI().generate(prompt)
        return response.strip()
    except Exception as e:
        print(f"Error improving SQL query: {e}")
        return None

# SQL Query Execution Tool
@tool
def execute_sql_query(query: str) -> List:
    """Execute a SQL query and return the results."""
    try:
        db_uri = f"sqlite:///{db_path}"
        db = SQLDatabaseFewShot(db_uri, examples=SQL_EXAMPLES)
        result = db.run(query)
        return result
    except sqlite3.Error as e:
        print(f"Error executing SQL query: {e}")
        return None

# SQL Query Checker Tool
@tool
def check_sql_query(query: str) -> str:
    """Check a SQL query for common mistakes using an LLM."""
    prompt = f"""You are a SQL syntax checker expert. Check the following SQL query for common mistakes and provide feedback:

{query}

Feedback:"""
    try:
        response = ChatOpenAI().generate(prompt)
        return response.strip()
    except Exception as e:
        print(f"Error checking SQL query: {e}")
        return None

# SQL Query Response Formatter Tool
@tool
def format_sql_query_response(results: List) -> str:
    """Format the results of a SQL query into a human-readable response."""
    prompt = f"""You are a SQL response formatter. Format the following results into a clear and concise response:

{results}

Formatted Response:"""
    try:
        response = ChatOpenAI().generate(prompt)
        return response.strip()
    except Exception as e:
        print(f"Error formatting SQL query response: {e}")
        return None

# Create LLM
llm = ChatOpenAI(model="gpt-4", openai_api_key=os.environ["OPENAI_API_KEY"], temperature=0)

# Create the tool-calling agent
agent = initialize_agent(
    tools=[generate_sql_query, improve_sql_query, execute_sql_query, check_sql_query, format_sql_query_response],
    llm=llm,
    verbose=True
)

# Main Streamlit app
def main():
    st.title("Product Backlog Requirements and SQL Queries")

    requirement = st.selectbox(
        "Select a Product Backlog requirement",
        [
            "Create a query to alert when any API endpoint experiences a 50% increase in average response time compared to the previous hour's baseline.",
            "Users have reported unusual account activity. Create monitoring to detect anomalous user session patterns that could indicate account compromise. Consider factors like login frequency, concurrent sessions, and access patterns.",
            "Monitor for scenarios where error rates exceed 5% of total requests per endpoint while also having high response times (>2s) in the last 15 minutes.",
            "The application seems slow during peak hours. Create a query to help us understand what's causing it.",
            "Create proactive monitoring for resource utilization across our microservices. We need early warning when any service is trending towards capacity limits, considering historical usage patterns and growth rates.",
        ],
    )

    if requirement:
        result = agent.run({"input": requirement})
        st.write(result)


if __name__ == "__main__":
    main()