import streamlit as st
from openai import OpenAI

client = OpenAI(api_key="")
import sqlite3

# Set up OpenAI API key


# Create an OpenAI client
client = openai.Completion.create

completion = client.completions.create(
    model="gpt-3.5-turbo-instruct",
    prompt={backlog_requirements},
    temperature=0,
    max_tokens=500
)

print(completion.choices[0].text)

#AZURE_OPENAI_ENDPOINT = "https://eco-poc-gpt.openai.azure.com"

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

# SQL queries
sql_queries = {
    "Alert on API endpoint response time increase": """
        SELECT endpoint, AVG(response_time) AS avg_response_time,
               AVG(response_time) / (SELECT AVG(response_time) FROM api_requests 
                                    WHERE timestamp >= DATE('now', '-1 hour')
                                    AND timestamp < DATE('now', '-30 minutes')) AS ratio
        FROM api_requests
        WHERE timestamp >= DATE('now', '-30 minutes')
        GROUP BY endpoint
        HAVING ratio > 1.5;
    """,
    "Anomaly detection for user sessions": """
        SELECT user_id, COUNT(*) AS total_sessions,
               COUNT(*) / (SELECT COUNT(*) FROM user_sessions 
                            WHERE start_time >= DATE('now', '-1 day')) AS ratio
        FROM user_sessions
        WHERE start_time >= DATE('now', '-1 day')
        GROUP BY user_id
        HAVING ratio > 0.1;
    """,
    "Error rate and response time anomalies": """
        SELECT endpoint, COUNT(*) AS total_requests,
               COUNT(*) / (SELECT COUNT(*) FROM api_requests 
                            WHERE timestamp >= DATE('now', '-15 minutes')) AS ratio,
               AVG(response_time) AS avg_response_time
        FROM api_requests
        WHERE timestamp >= DATE('now', '-15 minutes')
        GROUP BY endpoint
        HAVING ratio > 0.05 AND avg_response_time > 2;
    """,
    "Slow application monitoring": """
        SELECT endpoint, AVG(response_time) AS avg_response_time,
               COUNT(*) AS total_requests
        FROM api_requests
        WHERE timestamp >= DATE('now', '-1 hour')
        GROUP BY endpoint
        ORDER BY avg_response_time DESC
        LIMIT 10;
    """,
    "Resource utilization monitoring": """
        SELECT resource_type, server_id, current_usage, max_capacity,
               (current_usage / max_capacity * 100) AS usage_percentage
        FROM resource_utilization
        WHERE usage_percentage > 80
        ORDER BY usage_percentage DESC;
    """
}

def generate_sql_query(requirement):
    prompt = f"Convert the following requirement into a well-written SQL query:\n\n{requirement}\n\nSQL Query:"
    response = client.completions.create(engine="text-davinci-002",
    prompt=prompt,
    max_tokens=200,
    n=1,
    stop=None,
    temperature=0.7)
    return response.choices[0].text.strip()

def improve_sql_query(query):
    prompt = f"Improve the following SQL query:\n\n{query}\n\nImproved SQL Query:"
    response = client.completions.create(engine="text-davinci-002",
    prompt=prompt,
    max_tokens=200,
    n=1,
    stop=None,
    temperature=0.7)
    return response.choices[0].text.strip()

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
