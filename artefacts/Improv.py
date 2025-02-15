# -*- coding: utf-8 -*-
"""
Refactored on Friday Jan 7 13:23:39 2025
# Text2SQL LLM Agentic Tool based approach to Optimize the SQL Queries for Application Health Monitoring
@author: Akram Sheriff
"""
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import ConfigurableField
from langchain_core.tools import tool
from langchain.agents import create_tool_calling_agent, AgentExecutor
from openai import OpenAI
import os, sys
import sqlite3
import streamlit as st
from langchain_community.utilities import SQLDatabase
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
import openai

# Increase recursion limit (temporary solution)
sys.setrecursionlimit(10000)

os.environ["OPENAI_API_KEY"] = ""

# Set up OpenAI API key
OPENAI_API_KEY = ""
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

db_directory = "/Users/akram/Desktop/MOTIFIC_AI/TM"
db_path = os.path.join(db_directory, "database.db")

# Ensure the directory exists
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

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "you're a helpful assistant"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
)

# Define the Agentic SQL tool to detect poorly written SQL queries
@tool
def detect_and_improve_sql(requirement):
    """
    Detects poorly written SQL queries in the input, identifies their issues, and provides improvements.

    Args:
        requirement (str): SQL query or description of the problem

    Returns:
        dict: Original query, identified issues, and improved query
    """
    prompt = f"""You are an SQL expert. Analyze the following SQL query or requirement, detect any issues, and improve it:

Requirement:
{requirement}

Respond with the original query (if present), identified issues, and the improved query."""
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert SQL assistant."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=500,
            temperature=0.0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error detecting and improving SQL query: {e}")
        return None

# Define the Agentic SQL tool for generating queries
@tool
def generate_sql_query(requirement):
    """
       Generates a SQL query based on the given natural language requirement.
       Args:
           requirement (str): Natural language description of the desired SQL query
       Returns:
           str: Generated SQL query based on the requirement
    """
    prompt = f"""You are an expert SQL developer. Convert the following requirement into a well-written SQL query:

{requirement}

SQL Query:"""
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "developer", "content": "You are an expert AI assistant."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=300,
            temperature=0.0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating SQL query: {e}")
        return None

# Define the SQL tool for query execution
@tool
def execute_sql_query(query, conn):
    """
    Executes a SQL query on the given database connection and returns the results.

    Args:
        query (str): The SQL query to execute
        conn: Database connection object

    Returns:
        list: Results of the query if successful
        None: If query execution fails

    Raises:
        sqlite3.Error: If there's an error during query execution
    """
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()  # Good practice to close cursor
        return results
    except sqlite3.Error as e:
        print(f"Error executing SQL query: {e}")
        return None
    finally:
        if cursor:
            cursor.close()

# Create a list of AI Agent or LLM Agent tools
tools = [generate_sql_query, detect_and_improve_sql, execute_sql_query]

llm = ChatOpenAI(model="gpt-4", openai_api_key=OPENAI_API_KEY, temperature=0)

# Create the agent
agent = create_tool_calling_agent(llm, tools, prompt)

# Create the agent executor
agent_executor = AgentExecutor(
    agent=agent, tools=tools, handle_parsing_errors=True, verbose=True
)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Backlog requirements
backlog_requirements = [
    "Create a query to alert when any API endpoint experiences a 50% increase in average response time compared to the previous hour's baseline.",
    "Users have reported unusual account activity. Create monitoring to detect anomalous user session patterns that could indicate account compromise. Consider factors like login frequency, concurrent sessions, and access patterns.",
    "Monitor for scenarios where error rates exceed 5% of total requests per endpoint while also having high response times (>2s) in the last 15 minutes.",
    "The application seems slow during peak hours. Create a query to help us understand what's causing it.",
    "Create proactive monitoring for resource utilization across our microservices. We need early warning when any service is trending towards capacity limits, considering historical usage patterns and growth rates."
]

def main():
    st.title("Product Backlog Requirements and SQL Queries")

    requirement = st.selectbox("Select a Product Backlog requirement", backlog_requirements)

    if requirement:
        try:
            # Call the agent executor with the selected requirement
            result = agent_executor.invoke(
                {"input": requirement},
                additional_context={"conn": conn}
            )
            # Process the result
            if "generated_query" in result:
                generated_query = result["generated_query"]
                st.write("Generated SQL Query:")
                st.code(generated_query, language="sql")

                if "improved_query" in result:
                    improved_query = result["improved_query"]
                    st.write("Improved SQL Query:")
                    st.code(improved_query, language="sql")

                    if st.button("Execute Query"):
                        results = result["query_results"]
                        if results:
                            st.write("Query Results:")
                            st.dataframe(results)
                        else:
                            st.warning("Query execution failed.")

        except openai.APIConnectionError as e:
            st.error("Failed to connect to the OpenAI API: " + str(e))

if __name__ == "__main__":
    main()
