from dotenv import load_dotenv
import os

# 🌍 Dynamically load .env file based on environment
env = os.getenv("ENV", "development")
env_file = f".env.{env}"
print(f"📦 Loading environment: {env_file}")
load_dotenv(dotenv_path=env_file)

from flask import request, Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from routes import register_routes

# 🟢 Allowed origins list
ALLOWED_ORIGINS = [
    "http://localhost:8080",
    "http://localhost:5173",
    "https://gowows-web-252628919239.asia-south1.run.app"
]

app = Flask(__name__)
# CORS(app, resources={r"/*": {"origins": ["http://localhost:8080", "http://localhost:5173", "https://gowows-web-252628919239.asia-south1.run.app"]}}, supports_credentials=True)

# 🌐 CORS Configuration
CORS(app, resources={r"/*": {"origins": ALLOWED_ORIGINS}},
     supports_credentials=True,
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "OPTIONS"])

# 🔐 Add JWT config
app.config["JWT_SECRET_KEY"] = "super-secret"  # TODO: change this before production!
app.config["DEBUG"] = True  # Enable auto-reload in development
jwt = JWTManager(app)

# ✅ Register all routes
register_routes(app)

@app.after_request
def add_cors_headers(response):
    origin = request.headers.get('Origin')
    if origin in ALLOWED_ORIGINS:

       response.headers["Access-Control-Allow-Origin"] = origin

    response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    return response
    


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)
