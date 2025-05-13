from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from routes import register_routes

app = Flask(__name__)
CORS(app)

# 🔐 Add JWT config
app.config["JWT_SECRET_KEY"] = "super-secret"  # TODO: change this before production!
jwt = JWTManager(app)

# ✅ Register all routes
register_routes(app)

if __name__ == "__main__":
    app.run(port=7860, debug=True)
