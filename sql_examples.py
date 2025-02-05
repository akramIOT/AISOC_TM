SQL_EXAMPLES = [
    # USER_SESSIONS
    {"input": "List all user sessions.", "query": "SELECT * FROM user_sessions;"},
    {
        "input": "Find all user sessions for the user with ID '12345'.",
        "query": "SELECT * FROM user_sessions WHERE user_id = '12345';",
    },
    {
        "input": "List all sessions with a status of 'active'.",
        "query": "SELECT * FROM user_sessions WHERE status = 'active';",
    },
    {
        "input": "Find the total duration of all user sessions.",
        "query": "SELECT SUM(TIMESTAMPDIFF(SECOND, start_time, end_time)) FROM user_sessions;",
    },
    {
        "input": "List all sessions from the IP address '192.168.1.1'.",
        "query": "SELECT * FROM user_sessions WHERE ip_address = '192.168.1.1';",
    },
    {
        "input": "How many sessions are there for each user?",
        "query": "SELECT user_id, COUNT(*) AS session_count FROM user_sessions GROUP BY user_id;",
    },
    {
        "input": "Find the total number of user sessions.",
        "query": "SELECT COUNT(*) FROM user_sessions;",
    },
    {
        "input": "List all sessions that lasted more than 1 hour.",
        "query": "SELECT * FROM user_sessions WHERE TIMESTAMPDIFF(SECOND, start_time, end_time) > 3600;",
    },
    {
        "input": "Who are the top 5 users by total session duration?",
        "query": "SELECT user_id, SUM(TIMESTAMPDIFF(SECOND, start_time, end_time)) AS total_duration FROM user_sessions GROUP BY user_id ORDER BY total_duration DESC LIMIT 5;",
    },
    {
        "input": "Which sessions started in the year 2023?",
        "query": "SELECT * FROM user_sessions WHERE strftime('%Y', start_time) = '2023';",
    },
    {
        "input": "How many unique users are there",
        "query": 'SELECT COUNT(DISTINCT user_id) FROM user_sessions',
    },
    # APPLICATION_ERRORS
    {"input": "List all application errors.", "query": "SELECT * FROM application_errors;"},
    {
        "input": "Find all errors for the user with ID '12345'.",
        "query": "SELECT * FROM application_errors WHERE user_id = '12345';",
    },
    {
        "input": "List all errors with a severity level of 'critical'.",
        "query": "SELECT * FROM application_errors WHERE severity_level = 'critical';",
    },
    {
        "input": "Find the total number of errors per module.",
        "query": "SELECT module_name, COUNT(*) AS error_count FROM application_errors GROUP BY module_name;",
    },
    {
        "input": "List all errors from the IP address '192.168.1.1'.",
        "query": "SELECT * FROM application_errors WHERE session_id IN (SELECT session_id FROM user_sessions WHERE ip_address = '192.168.1.1');",
    },
    {
        "input": "How many errors are there for each user?",
        "query": "SELECT user_id, COUNT(*) AS error_count FROM application_errors GROUP BY user_id;",
    },
    {
        "input": "Find the total number of application errors.",
        "query": "SELECT COUNT(*) FROM application_errors;",
    },
    {
        "input": "List all errors that occurred after the timestamp '2023-01-01 00:00:00'.",
        "query": "SELECT * FROM application_errors WHERE timestamp > '2023-01-01 00:00:00';",
    },
    {
        "input": "Who are the top 5 users by total error occurrences?",
        "query": "SELECT user_id, COUNT(*) AS error_count FROM application_errors GROUP BY user_id ORDER BY error_count DESC LIMIT 5;",
    },
    {
        "input": "Which errors occurred in the year 2023?",
        "query": "SELECT * FROM application_errors WHERE strftime('%Y', timestamp) = '2023';",
    },
    {
        "input": "How many unique users have reported errors",
        "query": 'SELECT COUNT(DISTINCT user_id) FROM application_errors',
    },
    # SYSTEM_PERFORMANCE
    {"input": "List all system performance metrics.", "query": "SELECT * FROM system_performance;"},
    {
        "input": "Find all metrics for the server with ID '12345'.",
        "query": "SELECT * FROM system_performance WHERE server_id = '12345';",
    },
    {
        "input": "List all metrics with a CPU usage greater than 80%.",
        "query": "SELECT * FROM system_performance WHERE cpu_usage > 80;",
    },
    {
        "input": "Find the average memory usage across all metrics.",
        "query": "SELECT AVG(memory_usage) AS avg_memory_usage FROM system_performance;",
    },
    {
        "input": "List all metrics from the server with IP address '192.168.1.1'.",
        "query": "SELECT * FROM system_performance WHERE server_id IN (SELECT server_id FROM server_details WHERE ip_address = '192.168.1.1');",
    },
    {
        "input": "How many metrics are there for each server?",
        "query": "SELECT server_id, COUNT(*) AS metric_count FROM system_performance GROUP BY server_id;",
    },
    {
        "input": "Find the total number of system performance metrics.",
        "query": "SELECT COUNT(*) FROM system_performance;",
    },
    {
        "input": "List all metrics that have a response time greater than 1 second.",
        "query": "SELECT * FROM system_performance WHERE response_time > 1000;",
    },
    {
        "input": "Who are the top 5 servers by average CPU usage?",
        "query": "SELECT server_id, AVG(cpu_usage) AS avg_cpu_usage FROM system_performance GROUP BY server_id ORDER BY avg_cpu_usage DESC LIMIT 5;",
    },
    {
        "input": "Which metrics occurred in the year 2023?",
        "query": "SELECT * FROM system_performance WHERE strftime('%Y', timestamp) = '2023';",
    },
    {
        "input": "How many unique servers are reporting metrics",
        "query": 'SELECT COUNT(DISTINCT server_id) FROM system_performance',
    },
    # API_REQUESTS
    {"input": "List all API requests.", "query": "SELECT * FROM api_requests;"},
    {
        "input": "Find all requests for the user with ID '12345'.",
        "query": "SELECT * FROM api_requests WHERE user_id = '12345';",
    },
    {
        "input": "List all requests with a response code of '404'.",
        "query": "SELECT * FROM api_requests WHERE response_code = 404;",
    },
    {
        "input": "Find the average response time for each endpoint.",
        "query": "SELECT endpoint, AVG(response_time) AS avg_response_time FROM api_requests GROUP BY endpoint;",
    },
    {
        "input": "List all requests from the IP address '192.168.1.1'.",
        "query": "SELECT * FROM api_requests WHERE session_id IN (SELECT session_id FROM user_sessions WHERE ip_address = '192.168.1.1');"},
    ]