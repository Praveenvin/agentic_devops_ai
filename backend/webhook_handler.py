from db import get_db_connection
from datetime import datetime

def classify_commit(message):
    message_lower = message.lower()
    if "fix" in message_lower or "bug" in message_lower:
        return "Bug Fix"
    elif "add" in message_lower or "feature" in message_lower:
        return "Feature"
    elif "refactor" in message_lower:
        return "Refactor"
    else:
        return "Other"

def handle_webhook(payload):
    if 'commits' not in payload:
        print("⚠️ No commits found in payload.")
        return

    conn = get_db_connection()
    cursor = conn.cursor()

    for commit in payload['commits']:
        commit_id = commit.get('id')
        message = commit.get('message')
        author = commit.get('author', {}).get('name')
        timestamp_raw = commit.get('timestamp')
        timestamp = datetime.strptime(timestamp_raw, "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d %H:%M:%S")
        label = classify_commit(message)

        cursor.execute("""
            INSERT INTO commits (commit_id, message, author, timestamp, label)
            VALUES (%s, %s, %s, %s, %s)
        """, (commit_id, message, author, timestamp, label))

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Commits saved to database.")
