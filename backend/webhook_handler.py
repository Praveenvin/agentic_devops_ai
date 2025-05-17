from flask import request, abort, jsonify
import hmac, hashlib
from db import get_db_connection

GITHUB_SECRET = b"pravinwin4"

def verify_signature(payload_body, received_signature):
    if not received_signature:
        return False
    mac = hmac.new(GITHUB_SECRET, msg=payload_body, digestmod=hashlib.sha256)
    expected_signature = "sha256=" + mac.hexdigest()
    return hmac.compare_digest(expected_signature, received_signature)

def handle_webhook(payload):
    if 'commits' not in payload:
        return

    conn = get_db_connection()
    cursor = conn.cursor()

    for commit in payload['commits']:
        commit_id = commit['id']
        message = commit['message']
        author = commit['author']['name']
        timestamp = commit['timestamp']

        cursor.execute("""
            INSERT INTO commits (commit_id, message, author, timestamp)
            VALUES (%s, %s, %s, %s)
        """, (commit_id, message, author, timestamp))

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Commits saved to database.")
