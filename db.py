# -*- coding: utf-8 -*-
"""
Created on Friday Jan 3 13:23:39 2025
#To store the results of the SQL queries with sample Outputs in a flat file database (e.g., CSV files),
we can use Python's sqlite3 to execute the queries and pandas to handle the data and export it to CSV files.
This below code is to setup the DB, execute the queries, and store the results:

@author: Akram Sheriff
"""

import sqlite3
import pandas as pd

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Create tables
cursor.executescript('''
CREATE TABLE IF NOT EXISTS user_sessions (
    session_id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36),
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    ip_address VARCHAR(45),
    browser_type VARCHAR(100),
    device_type VARCHAR(50),
    status VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS application_errors (
    error_id VARCHAR(36) PRIMARY KEY,
    timestamp TIMESTAMP,
    error_code VARCHAR(50),
    error_message VARCHAR(500),
    severity_level VARCHAR(20),
    module_name VARCHAR(100),
    user_id VARCHAR(36),
    session_id VARCHAR(36),
    FOREIGN KEY (session_id) REFERENCES user_sessions(session_id)
);

CREATE TABLE IF NOT EXISTS system_performance (
    metric_id VARCHAR(36) PRIMARY KEY,
    timestamp TIMESTAMP,
    cpu_usage DECIMAL(5,2),
    memory_usage DECIMAL(5,2),
    disk_usage DECIMAL(5,2),
    response_time DECIMAL(10,3),
    active_connections INTEGER,
    server_id VARCHAR(36)
);

CREATE TABLE IF NOT EXISTS api_requests (
    request_id VARCHAR(36) PRIMARY KEY,
    timestamp TIMESTAMP,
    endpoint VARCHAR(200),
    method VARCHAR(10),
    response_code INTEGER,
    response_time DECIMAL(10,3),
    user_id VARCHAR(36),
    session_id VARCHAR(36),
    payload_size INTEGER,
    FOREIGN KEY (session_id) REFERENCES user_sessions(session_id)
);

CREATE TABLE IF NOT EXISTS resource_utilization (
    resource_id VARCHAR(36) PRIMARY KEY,
    timestamp TIMESTAMP,
    resource_type VARCHAR(50),
    current_usage DECIMAL(10,2),
    max_capacity DECIMAL(10,2),
    server_id VARCHAR(36),
    status VARCHAR(20)
);
''')

# Define queries
queries = {
    "Monitor failed API requests": """
        SELECT COUNT(*) as error_count, endpoint, response_code
        FROM api_requests
        WHERE response_code >= 400
        AND timestamp >= datetime('now', '-5 minutes')
        GROUP BY endpoint, response_code
        HAVING error_count > 10;
    """,
    "Check system performance": """
        SELECT * FROM system_performance
        WHERE (cpu_usage > 50 OR memory_usage > 50 OR disk_usage > 50)
        AND timestamp > datetime('now', '-1 hour');
    """,
    "Track user session anomalies": """
        SELECT user_id, COUNT(*) as session_count
        FROM user_sessions
        WHERE start_time >= datetime('now', '-1 hour')
        GROUP BY user_id
        HAVING session_count > 20;
    """,
    "Error monitoring": """
        SELECT e.*, s.browser_type, s.device_type, 
               COUNT(*) OVER (PARTITION BY e.error_code) as error_count
        FROM application_errors e
        LEFT JOIN user_sessions s ON e.session_id = s.session_id
        WHERE e.timestamp > datetime('now', '-24 hours')
        ORDER BY e.timestamp DESC;
    """,
    "Resource capacity warning": """
        SELECT resource_type, server_id, 
               (current_usage / max_capacity * 100) as usage_percentage
        FROM resource_utilization
        WHERE timestamp >= datetime('now', '-15 minutes')
        AND (current_usage / max_capacity * 100) > 85;
    """,
    "API performance": """
        SELECT endpoint, 
               AVG(response_time) as avg_time,
               COUNT(*) as total_requests
        FROM api_requests
        WHERE timestamp >= datetime('now', '-1 hour')
        GROUP BY endpoint
        HAVING COUNT(*) > 0;
    """,
    "Critical error spike detection": """
        SELECT COUNT(*) as critical_errors, module_name
        FROM application_errors
        WHERE severity_level = 'CRITICAL'
        AND timestamp >= datetime('now', '-10 minutes')
        GROUP BY module_name
        HAVING critical_errors > 5;
    """,
    "Session tracking": """
        SELECT * FROM user_sessions
        WHERE status = 'active' AND end_time IS NULL
        AND start_time < datetime('now');
    """,
    "Concurrent user load monitoring": """
        SELECT COUNT(DISTINCT user_id) as active_users,
               COUNT(*) as total_sessions
        FROM user_sessions
        WHERE status = 'active'
        AND start_time >= datetime('now', '-5 minutes');
    """,
    "Resource check": """
        SELECT resource_type, current_usage, max_capacity 
        FROM resource_utilization 
        WHERE status != 'optimal';
    """
}

# Execute queries and save results to CSV files
for name, query in queries.items():
    try:
        df = pd.read_sql_query(query, conn)
        df.to_csv(f'{name.replace(" ", "_").lower()}.csv', index=False)
        print(f'Successfully saved results of "{name}" to CSV.')
    except Exception as e:
        print(f'Failed to execute query "{name}": {e}')

# Close the database connection
conn.close()