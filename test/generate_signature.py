import hmac, hashlib

secret = b"pravinwin4"
with open("test_webhook.json", "rb") as f:
    body = f.read()

signature = "sha256=" + hmac.new(secret, msg=body, digestmod=hashlib.sha256).hexdigest()
print(signature)
