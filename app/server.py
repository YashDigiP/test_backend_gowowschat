from dotenv import load_dotenv
import os

# 🌍 Dynamically load .env file based on environment
env = os.getenv("ENV", "development")
env_file = f".env.{env}"
print(f"📦 Loading environment: {env_file}")
load_dotenv(dotenv_path=env_file)

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from routes import register_routes


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:8080"}}, supports_credentials=True)

# 🔐 Add JWT config
app.config["JWT_SECRET_KEY"] = "super-secret"  # TODO: change this before production!
app.config["DEBUG"] = True  # Enable auto-reload in development
jwt = JWTManager(app)

# ✅ Register all routes
register_routes(app)

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "http://localhost:5173"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    return response
    


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    app.run(host="0.0.0.0", port=port, debug=True)
