import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),  # updated from DB_PASSWORD to DB_PASS
        database=os.getenv("DB_NAME")
    )


def insert_commit(commit):
    conn = get_connection()
    cursor = conn.cursor()
    query = """
    INSERT IGNORE INTO commits (
        commit_id, message, author, timestamp,
        label, module, impact_area, reviewer,
        branch_name, repo_name
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(query, (
        commit['commit_id'], commit['message'], commit['author'],
        commit['timestamp'], commit['label'], commit['module'],
        commit['impact_area'], commit['reviewer'],
        commit['branch_name'], commit['repo_name']
    ))
    conn.commit()
    cursor.close()
    conn.close()

def insert_file_change(change):
    conn = get_connection()
    cursor = conn.cursor()
    query = """
    INSERT INTO file_changes (
        commit_id, file_path, change_type, lines_added, lines_removed,
        file_extension, file_size_before, file_size_after,
        is_binary, diff_summary, change_complexity_score
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(query, (
        change['commit_id'], change['file_path'], change['change_type'],
        change['lines_added'], change['lines_removed'],
        change['file_extension'], change['file_size_before'],
        change['file_size_after'], change['is_binary'],
        change['diff_summary'], change['change_complexity_score']
    ))
    conn.commit()
    cursor.close()
    conn.close()
