import streamlit as st
from openai import OpenAI

client = OpenAI(api_key="")
import sqlite3

# Set up OpenAI API key

# SQLite connection
conn = sqlite3.connect("your_database.db")
cursor = conn.cursor()

# Backlog requirements
backlog_requirements = [
    "Create a query to alert when any API endpoint experiences a 50% increase in average response time compared to the previous hour's baseline.",
    "Users have reported unusual account activity. Create monitoring to detect anomalous user session patterns that could indicate account compromise. Consider factors like login frequency, concurrent sessions, and access patterns.",
    "Monitor for scenarios where error rates exceed 5% of total requests per endpoint while also having high response times (>2s) in the last 15 minutes.",
    "The application seems slow during peak hours. Create a query to help us understand what's causing it.",
    "Create proactive monitoring for resource utilization across our microservices. We need early warning when any service is trending towards capacity limits, considering historical usage patterns and growth rates."
]

def generate_sql_query(requirement):
    prompt = f"""You are an expert SQL developer. Convert the following requirement into a well-written SQL query:

{requirement}

SQL Query:"""
    try:
        response = client.chat.completions.create(model="gpt-4",
        messages=[{"role": "developer", "content": "You are an expert assistant."},
                  {"role": "user", "content": prompt}],
        max_tokens=300,
        temperature=0.5)
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"Error generating SQL query: {e}")
        return None

def improve_sql_query(query):
    prompt = f"""You are an SQL optimization expert. Improve the following SQL query for readability, efficiency, and performance:

{query}

Improved SQL Query:"""
    try:
        response = client.chat.completions.create(model="gpt-4",
        messages=[{"role": "system", "content": "You are an expert assistant."},
                  {"role": "user", "content": prompt}],
        max_tokens=300,
        temperature=0.5)
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"Error improving SQL query: {e}")
        return None

def execute_sql_query(query):
    try:
        cursor.execute(query)
        results = cursor.fetchall()
        return results
    except sqlite3.Error as e:
        st.error(f"Error executing SQL query: {e}")
        return None

def main():
    st.title("Backlog Requirements and SQL Queries")

    requirement = st.selectbox("Select a backlog requirement", backlog_requirements)

    if requirement:
        generated_query = generate_sql_query(requirement)
        if generated_query:
            st.write("Generated SQL Query:")
            st.code(generated_query, language="sql")
            improved_query = improve_sql_query(generated_query)
            if improved_query:
                st.write("Improved SQL Query:")
                st.code(improved_query, language="sql")

                if st.button("Execute Query"):
                    results = execute_sql_query(improved_query)
                    if results:
                        st.write("Query Results:")
                        st.dataframe(results)
                    else:
                        st.warning("Query execution failed.")

if __name__ == "__main__":
    main()
