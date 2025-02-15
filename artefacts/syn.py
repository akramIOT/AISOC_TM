
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
    prompt = f"Convert the following requirement into a well-written SQL query:\n\n{requirement}\n\nSQL Query:"
    response = client.chat.completions.create(model="gpt-3.5-turbo",
    messages=[{"role": "system", "content": prompt}],
    max_tokens=200,
    temperature=0.7)
    return response.choices[0].message.content.strip()

def improve_sql_query(query):
    prompt = f"Improve the following SQL query:\n\n{query}\n\nImproved SQL Query:"
    response = client.chat.completions.create(model="gpt-3.5-turbo",
    messages=[{"role": "system", "content": prompt}],
    max_tokens=200,
    temperature=0.7)
    return response.choices[0].message.content.strip()

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

    generated_query = generate_sql_query(requirement)
    st.write("Generated SQL Query:")
    st.code(generated_query, language="sql")

    improved_query = improve_sql_query(generated_query)
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
