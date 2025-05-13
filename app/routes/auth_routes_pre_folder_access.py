from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from services.auth_service import (
    hash_password,
    verify_password,
    create_token,
    get_user_by_username,
    user_col
)

def register_auth_routes(app):
    auth_bp = Blueprint("auth", __name__)

    @auth_bp.route("/register", methods=["POST"])
    def register():
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")
        display_name = data.get("display_name", username)

        if not username or not password:
            return jsonify({"error": "Username and password are required"}), 400

        if get_user_by_username(username):
            return jsonify({"error": "Username already exists"}), 409

        user_col.insert_one({
            "username": username,
            "password_hash": hash_password(password),
            "role": "user",
            "display_name": display_name,
            "active": True
        })

        return jsonify({"message": f"User '{username}' registered successfully."})

    @auth_bp.route("/login", methods=["POST"])
    def login():
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")

        user = get_user_by_username(username)
        if not user or not verify_password(password, user["password_hash"]):
            return jsonify({"error": "Invalid username or password"}), 401

        token = create_token({
            "username": user["username"],
            "role": user["role"],
            "display_name": user.get("display_name", "")
        })

        return jsonify({"token": token})

    @auth_bp.route("/me", methods=["GET"])
    @jwt_required()
    def me():
        identity = get_jwt_identity()
        user = get_user_by_username(identity)
        if not user:
            return jsonify({"error": "User not found"}), 404

        return jsonify({
            "email": user.get("email", ""),
            "display_name": user.get("display_name", ""),
            "role": user.get("role", "user"),
        })

    @auth_bp.route("/users", methods=["GET"])
    @jwt_required()
    def list_users():
        claims = get_jwt()
        if claims.get("role") != "admin":
            return jsonify({"error": "Unauthorized"}), 403
        users = list(user_col.find({}, {"_id": 0, "username": 1, "display_name": 1, "role": 1}))
        return jsonify({"users": users})

    @auth_bp.route("/update-role", methods=["POST"])
    @jwt_required()
    def update_user_role():
        claims = get_jwt()
        if claims.get("role") != "admin":
            return jsonify({"error": "Unauthorized"}), 403

        data = request.get_json()
        username = data.get("username")
        new_role = data.get("role")

        if new_role not in ["admin", "super_user", "user"]:
            return jsonify({"error": "Invalid role"}), 400

        result = user_col.update_one(
            {"username": username},
            {"$set": {"role": new_role}}
        )

        if result.modified_count == 0:
            return jsonify({"error": "User not found or role unchanged"}), 404

        return jsonify({"message": f"Updated role for {username} to {new_role}."})

    @auth_bp.route("/reset-password", methods=["POST"])
    @jwt_required()
    def reset_password():
        claims = get_jwt()
        if claims.get("role") != "admin":
            return jsonify({"error": "Unauthorized"}), 403

        data = request.get_json()
        username = data.get("username")
        new_password = data.get("password")  # 👈 fixed key from "new_password" to "password"

        if not username or not new_password:
            return jsonify({"error": "Missing fields"}), 400

        hashed = hash_password(new_password)

        result = user_col.update_one(
            {"username": username},
            {"$set": {"password_hash": hashed}}
        )

        if result.modified_count == 0:
            return jsonify({"error": "User not found or password unchanged"}), 404

        return jsonify({"message": f"Password reset for {username}."})

    app.register_blueprint(auth_bp)
