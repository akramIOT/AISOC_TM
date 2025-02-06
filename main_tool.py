import os
import sqlite3
import streamlit as st
from typing import List, Dict
from langchain import SQLDatabase, FewShotPromptTemplate, PromptTemplate, LLMChain
from langchain.llms import OpenAI
from langchain.agents import initialize_agent
from langchain.tools import Tool

# OpenAI API Key Configuration
os.environ["OPENAI_API_KEY"] = ""

# Database Setup
DB_DIRECTORY = "/Users/akram/Desktop/MOTIFIC_AI/TM"
DB_PATH = os.path.join(DB_DIRECTORY, "database.db")
os.makedirs(DB_DIRECTORY, exist_ok=True)

if not os.path.exists(DB_PATH):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sample_table (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT
        )
    """)
    cursor.execute("INSERT INTO sample_table (name, description) VALUES ('Test Item', 'Sample Description')")
    conn.commit()
    conn.close()
print("Database setup complete.")

# Connect to the database
db = SQLDatabase.from_uri(f"sqlite:///{DB_PATH}")

# Define LLM
llm = OpenAI(model="gpt-4", temperature=0)

# Define FewShotPromptTemplate for SQL Examples
examples = [
    {"input": "Get all items", "query": "SELECT * FROM sample_table;"},
    {"input": "Find item by name", "query": "SELECT * FROM sample_table WHERE name = 'Test Item';"}
]

prompt_template = FewShotPromptTemplate(
    examples=examples,
    example_prompt=PromptTemplate(
        input_variables=["input", "query"],
        template="Input: {input}\nQuery: {query}\n"
    ),
    prefix="You are a SQL expert. Convert the following inputs into SQL queries:\n",
    suffix="\nInput: {input}\nQuery:",
    input_variables=["input"]
)

# Define tools correctly
generate_sql_query_tool = Tool(
    name="Generate SQL Query",
    func=lambda requirement: LLMChain(llm=llm, prompt=prompt_template).run(requirement),
    description="Generates SQL query from requirements."
)

execute_sql_query_tool = Tool(
    name="Execute SQL Query",
    func=lambda query: db.run(query) if db else {"error": "Database not connected."},
    description="Executes SQL query and returns results."
)

optimize_sql_query_tool = Tool(
    name="Optimize SQL Query",
    func=lambda query: LLMChain(
        llm=llm,
        prompt=PromptTemplate(
            input_variables=["query"],
            template="You are an SQL optimization expert. Improve the following SQL query:\n\n{query}\n\nOptimized Query:"
        )
    ).run(query),
    description="Optimizes SQL query for performance."

# Initialize Agent
tools = [generate_sql_query, execute_sql_query, optimize_sql_query]
agent = initialize_agent(tools=tools, llm=llm, verbose=True)

# Streamlit App
def main():
    st.title("Automated SQL Query Generation and Optimization")

    requirement = st.selectbox(
        "Select a Requirement",
        [
            "Fetch all records from the table.",
            "Find an item with a specific name.",
            "Fetch records with a description containing 'Sample'."
        ]
    )

    if requirement:
        st.write("Generating SQL Query...")
        sql_query = agent.run({"input": requirement})
        st.code(sql_query, language="sql")

        if st.button("Optimize Query"):
            optimized_query = optimize_sql_query(sql_query)
            st.code(optimized_query, language="sql")

        if st.button("Execute Query"):
            results = execute_sql_query(sql_query)
            st.write(results)

if __name__ == "__main__":
    main()
