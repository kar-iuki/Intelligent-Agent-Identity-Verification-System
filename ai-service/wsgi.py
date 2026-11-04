import os
import hmac
from flask import request, jsonify
from validate_models import app, validate

key = os.environ.get("VERITY_API_KEY", "")
if len(key) < 32:
    raise RuntimeError("Set VERITY_API_KEY to a random secret of at least 32 characters")
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024
validate()


@app.before_request
def require_api_key():
    if request.path == "/health":
        return None
    if not hmac.compare_digest(request.headers.get("X-API-Key", ""), key):
        return jsonify(error="Unauthorized"), 401
