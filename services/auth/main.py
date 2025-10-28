"""Authentication service for JobSense.

Provides local email/password auth and OAuth flows for Google and LinkedIn.
Uses JWTs for stateless sessions and a simple SQLite store for users.
Note: Passwords are stored in plain text in this dev sample — always hash
and salt passwords in production (e.g., bcrypt).
"""

# Standard library imports
import datetime
from functools import wraps
from typing import Callable, Any

# Third-party imports
import jwt
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

# Local application imports
from models import db, User
import common

# Flask app initialization
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Allow the frontend origin used during development
CORS(app, origins=["http://localhost:5173"])

# Initialize DB (creates tables on first run)
db.init_app(app)
with app.app_context():
    db.create_all()


# Utility: create JWT token for a user id
def create_token(user_id: int) -> str:
    """Return a JWT for the given user id that expires in 24 hours."""
    payload = {
        "user_id": user_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24),
    }
    token = jwt.encode(payload, common.SECRET_KEY, algorithm="HS256")
    return token


# Decorator to protect routes that require authentication
def token_required(f: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator that validates a JWT passed in the Authorization header.

    The wrapped function receives the current_user as its first argument.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        # Extract token from Authorization header (expects "Bearer <token>")
        auth_header = request.headers.get("Authorization", "")
        token = auth_header.replace("Bearer ", "").strip()
        if not token:
            return jsonify({"error": "Token missing"}), 401

        try:
            data = jwt.decode(token, common.SECRET_KEY, algorithms=["HS256"])
            current_user = User.query.get(data.get("user_id"))
            if not current_user:
                return jsonify({"error": "User not found"}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        return f(current_user, *args, **kwargs)

    return decorated


# === EMAIL/PASSWORD AUTHENTICATION ===
@app.route("/api/auth/register", methods=["POST"])
def register():
    """Register a new user with email and password.

    Returns a JWT and basic user info on success.
    """
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "User already exists"}), 400

    # WARNING: For demo only. Hash passwords in production.
    user = User(email=email, password_hash=password, provider="local")
    db.session.add(user)
    db.session.commit()

    token = create_token(user.id)
    return jsonify({"token": token, "user": {"email": user.email, "id": user.id}})


@app.route("/api/auth/login", methods=["POST"])
def login():
    """Authenticate a user using email and password and return a JWT."""
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()
    if not user or user.password_hash != password:
        return jsonify({"error": "Invalid credentials"}), 401

    token = create_token(user.id)
    return jsonify({"token": token, "user": {"email": user.email, "id": user.id}})


# === GOOGLE OAUTH ===
@app.route("/api/auth/oauth/google", methods=["POST"])
def google_oauth():
    """Exchange an OAuth code for tokens, fetch user info, and return a JWT."""
    code = (request.json or {}).get("code")
    if not code:
        return jsonify({"error": "Code required"}), 400

    token_url = "https://oauth2.googleapis.com/token"
    payload = {
        "code": code,
        "client_id": common.GOOGLE_CLIENT_ID,
        "client_secret": common.GOOGLE_CLIENT_SECRET,
        "redirect_uri": "http://localhost:5173",
        "grant_type": "authorization_code",
    }

    try:
        response = requests.post(token_url, data=payload, timeout=10)
        response.raise_for_status()
    except requests.RequestException:
        return jsonify({"error": "Google auth failed"}), 400

    access_token = response.json().get("access_token")
    if not access_token:
        return jsonify({"error": "Google did not return access token"}), 400

    user_info = requests.get(
        "https://www.googleapis.com/oauth2/v2/userinfo",
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=10,
    )
    user_data = user_info.json()

    email = user_data.get("email")
    if not email:
        return jsonify({"error": "Unable to retrieve email from Google"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(
            email=email,
            provider="google",
            name=user_data.get("name"),
        )
        db.session.add(user)
        db.session.commit()

    token = create_token(user.id)
    return jsonify(
        {"token": token, "user": {"email": user.email, "name": user.name, "id": user.id}}
    )


# === LINKEDIN OAUTH ===
@app.route("/api/auth/oauth/linkedin", methods=["POST"])
def linkedin_oauth():
    """Exchange LinkedIn OAuth code, fetch profile/email, and return a JWT."""
    code = (request.json or {}).get("code")
    if not code:
        return jsonify({"error": "Code required"}), 400

    token_url = "https://www.linkedin.com/oauth/v2/accessToken"
    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": "http://localhost:5173",
        "client_id": common.LINKEDIN_CLIENT_ID,
        "client_secret": common.LINKEDIN_CLIENT_SECRET,
    }

    try:
        response = requests.post(token_url, data=payload, timeout=10)
        response.raise_for_status()
    except requests.RequestException:
        return jsonify({"error": "LinkedIn auth failed"}), 400

    access_token = response.json().get("access_token")
    if not access_token:
        return jsonify({"error": "LinkedIn did not return access token"}), 400

    profile = requests.get(
        "https://api.linkedin.com/v2/me",
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=10,
    )
    email_res = requests.get(
        "https://api.linkedin.com/v2/emailAddress?q=members&projection=(elements*(handle~))",
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=10,
    )

    profile_data = profile.json()
    email_data = email_res.json().get("elements", [{}])
    email = email_data[0].get("handle~", {}).get("emailAddress", "")

    # Fallback to a synthetic email if LinkedIn doesn't provide one
    if not email:
        email = f"{profile_data.get('id', 'unknown')}@linkedin.local"

    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(
            email=email,
            provider="linkedin",
            name=profile_data.get("localizedFirstName"),
        )
        db.session.add(user)
        db.session.commit()

    token = create_token(user.id)
    return jsonify(
        {"token": token, "user": {"email": user.email, "name": user.name, "id": user.id}}
    )


# === PROTECTED ROUTE: current user info ===
@app.route("/api/auth/me", methods=["GET"])
@token_required
def me(current_user: User):
    """Return the profile of the currently authenticated user."""
    return jsonify(
        {
            "user": {
                "id": current_user.id,
                "email": current_user.email,
                "name": current_user.name,
                "provider": current_user.provider,
            }
        }
    )


if __name__ == "__main__":
    # Development entrypoint
    print("Auth Service + SQLite running on http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)