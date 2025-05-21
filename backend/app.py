from flask import Flask, request, abort, jsonify
from webhook_handler import handle_webhook
import hmac
import hashlib
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

app = Flask(__name__)
GITHUB_SECRET = os.getenv("GITHUB_SECRET", "pravinwin4").encode()

def verify_signature(data, signature):
    mac = hmac.new(GITHUB_SECRET, msg=data, digestmod=hashlib.sha256)
    expected_signature = 'sha256=' + mac.hexdigest()
    return hmac.compare_digest(expected_signature, signature)

@app.route('/webhook', methods=['POST'])
def webhook():
    signature = request.headers.get('X-Hub-Signature-256')
    if not signature:
        abort(400, 'Missing signature')

    data = request.get_data()
    if not verify_signature(data, signature):
        abort(400, 'Invalid signature')

    print("✅ Webhook received and verified.")
    handle_webhook(data.decode())
    return jsonify({"status": "success"}), 200

@app.route('/')
def index():
    return "✅ Flask server is running!"

if __name__ == '__main__':
    app.run(debug=True, port=5000)
