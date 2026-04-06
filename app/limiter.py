import os
from flask import request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


def get_request_email_key():
    data = request.get_json(silent=True) or {}
    email = data.get('email', '').lower().strip()
    return f"email:{email}" if email else get_remote_address()


limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=os.getenv("RATELIMIT_STORAGE_URI", "memory://"),
    default_limits=[],
)
