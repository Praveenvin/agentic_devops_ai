import json
from db import get_db_connection
from datetime import datetime

# --- Commit Labeler ---
def label_commit(message):
    message = message.lower() if message else ""
    if "fix" in message or "bug" in message:
        return "Bug Fix"
    elif "feature" in message or "add" in message:
        return "Feature"
    elif "refactor" in message:
        return "Refactor"
    return "Other"

# --- Module & Impact Guessing ---
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
    module = ",".join(modules) if modules else None
    impact_area = ",".join(impacts) if impacts else None
    return module, impact_area

# --- Save Commit ---
def save_commit(cursor, commit_id, message, author, timestamp, label, module, impact_area, reviewer, branch_name, repo_name):
    insert_commit_query = """
        INSERT INTO commits (
            commit_id, message, author, timestamp, label,
            module, impact_area, reviewer, branch_name, repo_name
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE message=VALUES(message), timestamp=VALUES(timestamp)
    """
    cursor.execute(insert_commit_query, (
        commit_id, message, author, timestamp, label,
        module, impact_area, reviewer, branch_name, repo_name
    ))

# --- Save File Changes ---
def save_file_changes(cursor, commit_id, added_files, removed_files, modified_files):
    all_files = added_files + removed_files + modified_files
    for file_path in all_files:
        if file_path in added_files:
            change_type = 'added'
        elif file_path in removed_files:
            change_type = 'removed'
        else:
            change_type = 'modified'
        lines_added = 0  # Placeholder
        lines_removed = 0  # Placeholder

        insert_file_query = """
            INSERT INTO file_changes (commit_id, file_path, change_type, lines_added, lines_removed)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(insert_file_query, (commit_id, file_path, change_type, lines_added, lines_removed))

# --- Save AI Summary ---
def save_ai_summary(cursor, commit_id, summary, description, doc_markdown):
    insert_query = """
        INSERT INTO ai_summaries (commit_id, summary, description, doc_markdown)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            summary=VALUES(summary),
            description=VALUES(description),
            doc_markdown=VALUES(doc_markdown)
    """
    cursor.execute(insert_query, (commit_id, summary, description, doc_markdown))

# --- Save Metrics ---
def save_metrics(cursor, commit_id, cyclomatic_complexity=None, lines_of_code=None, test_coverage=None):
    insert_query = """
        INSERT INTO metrics (commit_id, cyclomatic_complexity, lines_of_code, test_coverage)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            cyclomatic_complexity=VALUES(cyclomatic_complexity),
            lines_of_code=VALUES(lines_of_code),
            test_coverage=VALUES(test_coverage)
    """
    cursor.execute(insert_query, (commit_id, cyclomatic_complexity, lines_of_code, test_coverage))

# --- Save Review Comments ---
def save_review_comment(cursor, commit_id, commenter, comment):
    insert_query = """
        INSERT INTO review_comments (commit_id, commenter, comment)
        VALUES (%s, %s, %s)
    """
    cursor.execute(insert_query, (commit_id, commenter, comment))

# --- Save Test Cases ---
def save_test_case(cursor, commit_id, file_path, test_name, test_code, generated_by_ai=False):
    insert_query = """
        INSERT INTO test_cases (commit_id, file_path, test_name, test_code, generated_by_ai)
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(insert_query, (commit_id, file_path, test_name, test_code, int(generated_by_ai)))

# --- Main handler ---
def handle_webhook(request_body):
    payload = json.loads(request_body)
    db_conn = get_connection()
    cursor = db_conn.cursor()

    repo_name = payload.get('repository', {}).get('name')
    ref = payload.get('ref', '')  # e.g. refs/heads/main
    branch_name = ref.split('/')[-1] if ref else None

    commits = payload.get('commits', [])

    for commit in commits:
        commit_id = commit.get('id')
        message = commit.get('message')
        author = commit.get('author', {}).get('name')
        timestamp_str = commit.get('timestamp')
        timestamp = None
        if timestamp_str:
            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))

        added_files = commit.get('added', [])
        removed_files = commit.get('removed', [])
        modified_files = commit.get('modified', [])

        all_files = added_files + removed_files + modified_files

        label = label_commit(message)
        module, impact_area = guess_module_and_impact(all_files)
        reviewer = None  # placeholder, you can add logic here later

        # Save commit & files
        save_commit(cursor, commit_id, message, author, timestamp, label, module, impact_area, reviewer, branch_name, repo_name)
        save_file_changes(cursor, commit_id, added_files, removed_files, modified_files)

        # ======= Save AI Summary =======
        # Stub summary data (replace with real AI integration later)
        summary = f"Summary for commit {commit_id[:7]}"
        description = f"This commit includes changes: {', '.join(all_files)}"
        doc_markdown = f"# Commit {commit_id[:7]}\n\n{message}\n\nChanges:\n" + "\n".join(f"- {f}" for f in all_files)
        save_ai_summary(cursor, commit_id, summary, description, doc_markdown)

        # ======= Save Metrics =======
        # Stub metrics - replace with real metrics if you have tools to analyze code
        cyclomatic_complexity = 5.0  # example static value
        lines_of_code = 100          # example static value
        test_coverage = 75.0         # example static value in percentage
        save_metrics(cursor, commit_id, cyclomatic_complexity, lines_of_code, test_coverage)

        # ======= Save Review Comments =======
        # Example placeholder, no real data in webhook commits
        # You may add parsing for PR review webhook events separately
        # Here we just add a dummy comment for demonstration
        save_review_comment(cursor, commit_id, "reviewer_bot", "Auto review comment placeholder.")

        # ======= Save Test Cases =======
        # Example placeholder test case, replace with actual if available
        for file_path in added_files:
            test_name = f"Test for {file_path.split('/')[-1]}"
            test_code = f"# Test code stub for {file_path}"
            generated_by_ai = True
            save_test_case(cursor, commit_id, file_path, test_name, test_code, generated_by_ai)

    db_conn.commit()
    cursor.close()
    db_conn.close()
    return "OK"
