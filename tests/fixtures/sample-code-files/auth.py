"""Sample auth module for testing file reader with Python files."""

import os
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from flask import Request, Response, g

JWT_SECRET = os.environ.get("JWT_SECRET", "default-secret")


def authenticate_token(request: Request) -> Optional[Response]:
    """Authenticate a JWT token from the Authorization header."""
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return Response("Unauthorized", status=401)

    parts = auth_header.split(" ")
    if len(parts) != 2:
        return Response("Unauthorized", status=401)

    token = parts[1]

    try:
        decoded = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        g.user_id = decoded.get("userId")
        return None  # Continue to next handler
    except jwt.InvalidTokenError:
        return Response("Forbidden", status=403)


def generate_token(user_id: str) -> str:
    """Generate a JWT token for a user."""
    payload = {
        "userId": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(hours=24),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")
