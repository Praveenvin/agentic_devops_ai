import json
from datetime import datetime
from db import get_db_connection

def label_commit(message):
    message = message.lower() if message else ""
    if "fix" in message or "bug" in message:
        return "Bug Fix"
    elif "feature" in message or "add" in message:
        return "Feature"
    elif "refactor" in message:
        return "Refactor"
    return "Other"

def guess_module_and_impact(file_paths):
    modules = set()
    impacts = set()
    for f in file_paths:
        if f.startswith("backend/"):
            modules.add("backend")
            impacts.add("backend")
        elif f.startswith("test/"):
            modules.add("test")
            impacts.add("test")
        elif f.endswith(".py"):
            modules.add("python")
        elif f.endswith(".js") or f.endswith(".jsx"):
            modules.add("frontend")
            impacts.add("frontend")
    return ",".join(modules), ",".join(impacts)

def save_commits_and_files(payload):
    db_conn = get_db_connection()
    cursor = db_conn.cursor()

    repo_name = payload.get('repository', {}).get('name')
    branch_name = payload.get('ref', '').split('/')[-1]

    for commit in payload.get('commits', []):
        commit_id = commit.get('id')
        message = commit.get('message')
        author = commit.get('author', {}).get('name')
        timestamp_str = commit.get('timestamp')
        timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))

        added = commit.get('added', [])
        removed = commit.get('removed', [])
        modified = commit.get('modified', [])
        all_files = added + removed + modified

        label = label_commit(message)
        module, impact_area = guess_module_and_impact(all_files)
        reviewer = None

        # Insert into commits
        cursor.execute("""
            INSERT INTO commits (
                commit_id, message, author, timestamp, label,
                module, impact_area, reviewer, branch_name, repo_name
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE message=VALUES(message)
        """, (
            commit_id, message, author, timestamp, label,
            module, impact_area, reviewer, branch_name, repo_name
        ))

        for file_path in all_files:
            change_type = (
                'added' if file_path in added else
                'removed' if file_path in removed else
                'modified'
            )

            cursor.execute("""
                INSERT INTO file_changes (
                    commit_id, file_path, change_type, lines_added, lines_removed
                ) VALUES (%s, %s, %s, %s, %s)
            """, (commit_id, file_path, change_type, 0, 0))  # You can compute real lines later

    db_conn.commit()
    cursor.close()
    db_conn.close()

def handle_webhook(request_body):
    payload = json.loads(request_body)
    save_commits_and_files(payload)
