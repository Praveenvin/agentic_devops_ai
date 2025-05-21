import json
from db import get_db_connection

def save_commits_and_files(payload):
    db_conn = get_db_connection()
    cursor = db_conn.cursor()

    commits = payload.get('commits', [])
    for commit in commits:
        commit_id = commit.get('id')
        message = commit.get('message')
        author = commit.get('author', {}).get('name')
        timestamp = commit.get('timestamp')

        # Insert into commits table
        cursor.execute("""
            INSERT INTO commits (id, message, author, timestamp)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE message=VALUES(message), author=VALUES(author), timestamp=VALUES(timestamp)
        """, (commit_id, message, author, timestamp))

        # Insert file changes
        for file_path in commit.get('added', []):
            cursor.execute("""
                INSERT INTO file_changes (commit_id, file_path, change_type)
                VALUES (%s, %s, 'added')
            """, (commit_id, file_path))

        for file_path in commit.get('modified', []):
            cursor.execute("""
                INSERT INTO file_changes (commit_id, file_path, change_type)
                VALUES (%s, %s, 'modified')
            """, (commit_id, file_path))

        for file_path in commit.get('removed', []):
            cursor.execute("""
                INSERT INTO file_changes (commit_id, file_path, change_type)
                VALUES (%s, %s, 'removed')
            """, (commit_id, file_path))

    db_conn.commit()
    cursor.close()
    db_conn.close()

def save_additional_info(payload):
    db_conn = get_db_connection()
    cursor = db_conn.cursor()

    commits = payload.get('commits', [])
    for commit in commits:
        commit_id = commit.get('id')

        # Insert dummy AI summary
        cursor.execute("""
            INSERT INTO ai_summaries (commit_id, summary, description, doc_markdown)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE summary=VALUES(summary)
        """, (commit_id, "Dummy summary", "Dummy description", "# Dummy Markdown"))

        # Insert dummy metrics
        cursor.execute("""
            INSERT INTO metrics (commit_id, cyclomatic_complexity, lines_of_code, test_coverage)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE cyclomatic_complexity=VALUES(cyclomatic_complexity)
        """, (commit_id, 1.0, 100, 75.0))

        # Insert dummy review comment
        cursor.execute("""
            INSERT INTO review_comments (commit_id, commenter, comment)
            VALUES (%s, %s, %s)
        """, (commit_id, "Reviewer 1", "Looks good!"))

        # Insert dummy test case
        cursor.execute("""
            INSERT INTO test_cases (commit_id, file_path, test_name, test_code, generated_by_ai)
            VALUES (%s, %s, %s, %s, %s)
        """, (commit_id, "backend/app.py", "test_dummy", "assert True", 1))

    db_conn.commit()
    cursor.close()
    db_conn.close()

def handle_webhook(request_body):
    payload = json.loads(request_body)
    save_commits_and_files(payload)
    save_additional_info(payload)
    return "OK"
