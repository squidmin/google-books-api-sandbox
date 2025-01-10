import os
from werkzeug.security import generate_password_hash

CONTENT_BASE_DIR = os.getenv("CONTENT_BASE_DIR", "/library")

READOPS_ADMIN_PASSWORD = os.getenv("READOPS_ADMIN_PASSWORD", None)
users = {}
if READOPS_ADMIN_PASSWORD:
    users = {
        "admin": generate_password_hash(READOPS_ADMIN_PASSWORD),
    }
else:
    print(
        "WARNING: admin password not configured - catalog will be exposed as public"
    )
