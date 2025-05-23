import hmac
import hashlib

secret = b"pravinwin4"

with open("test_webhook.json", "rb") as f:
    body = f.read()

# Generate the HMAC SHA256 signature
signature = "sha256=" + hmac.new(secret, msg=body, digestmod=hashlib.sha256).hexdigest()

# Print the result (for debugging or testing)
print("Generated Signature for Webhook Payload:")
print(signature)
