
import os
import sqlite3
import sys
import streamlit as st
from typing import List, Dict
from langchain.agents import initialize_agent
from langchain.llms import OpenAI
from langchain_core.prompts import FewShotPromptTemplate, PromptTemplate
from langchain_core.tools import tool
from langchain_community.utilities import SQLDatabase

# Temporary increase of recursion limit
sys.setrecursionlimit(10000)

# OpenAI API key configuration
os.environ["OPENAI_API_KEY"] = "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"

# Database setup
db_directory = "/Users/akram/Desktop/MOTIFIC_AI/TM"
db_path = os.path.join(db_directory, "database.db")
os.makedirs(db_directory, exist_ok=True)

if not os.path.exists(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create a sample table for demonstration
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS api_logs (
                id INTEGER PRIMARY KEY,
                api_endpoint TEXT NOT NULL,
                response_time REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Insert mock data
        cursor.execute("""
            INSERT INTO api_logs (api_endpoint, response_time)
            VALUES ('/api/test', 200), ('/api/test', 300), ('/api/login', 150)
        """)
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error initializing database: {e}")

# Connect to the SQLite database
db_uri = f"sqlite:///{db_path}"
try:
    db = SQLDatabase.from_uri(db_uri)
except Exception as e:
    print(f"Error connecting to database: {e}")
    db = None


# Define tools
@tool
def generate_sql_query(requirement: str) -> str:
    """Generate a SQLite-compatible SQL query based on a requirement."""
    few_shot_prompt = FewShotPromptTemplate(
        examples=[
            {
                "input": "Create a query to alert when API response times increase significantly.",
                "query": """
                    SELECT api_endpoint, AVG(response_time) AS avg_response_time
                    FROM api_logs
                    WHERE timestamp >= DATETIME('now', '-1 hour')
                    GROUP BY api_endpoint
                    HAVING avg_response_time > (
                        SELECT AVG(response_time) * 1.5
                        FROM api_logs
                        WHERE timestamp BETWEEN DATETIME('now', '-2 hours') AND DATETIME('now', '-1 hour')
                    )
                """,
            }
        ],
        example_prompt=PromptTemplate(
            input_variables=["input", "query"],
            template="Input: {input}\nQuery: {query}",
        ),
        prefix="You are a SQL expert. Generate SQLite-compatible queries for the following requirements:\n",
        suffix="\nInput: {input}\nQuery:",
        input_variables=["input"],
    )
    try:
        prompt = few_shot_prompt.format(input=requirement)
        llm = OpenAI(temperature=0)
        response = llm(prompt)
        return response.strip()
    except Exception as e:
        return f"Error generating SQL query: {e}"


@tool
def execute_sql_query(query: str) -> List:
    """Execute a SQL query and return the results."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        conn.close()
        return result
    except sqlite3.Error as e:
        return [f"Error executing SQL query: {e}"]


# Initialize agent
llm = OpenAI(model="gpt-4", openai_api_key=os.environ["OPENAI_API_KEY"], temperature=0)
agent = initialize_agent(
    tools=[generate_sql_query, execute_sql_query],
    llm=llm,
    verbose=True,
)

# Main Streamlit app
def main():
    st.title("Automated SQL Query Generator (SQLite Compatible)")

    requirement = st.selectbox(
        "Select a Product Backlog Requirement",
        [
            "Create a query to alert when any API endpoint experiences a 50% increase in average response time compared to the previous hour's baseline.",
            "Users have reported unusual account activity. Create monitoring to detect anomalous user session patterns.",
            "Monitor error rates exceeding 5% with high response times (>2s) in the last 15 minutes.",
            "The application is slow during peak hours. Create a query to understand the cause.",
            "Proactive monitoring for resource utilization across microservices.",
        ],
    )

    if requirement:
        st.write("Generating SQL Query...")
        sql_query = agent.run({"input": requirement})
        st.code(sql_query, language="sql")

        if st.button("Execute SQL Query"):
            st.write("Executing SQL Query...")
            results = execute_sql_query(sql_query)
            if results:
                st.write("Results:")
                st.write(results)
            else:
                st.write("No results found or an error occurred.")

if __name__ == "__main__":
    main()
