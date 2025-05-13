import certifi
from pymongo import MongoClient
from passlib.context import CryptContext
from flask_jwt_extended import create_access_token
from datetime import timedelta

# 🔌 Connect to MongoDB
client = MongoClient(
    "mongodb+srv://nirajo:Niraj1234@cluster0.bw2xzbl.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0",
    tls=True,
    tlsCAFile=certifi.where()
)
db = client["gowowschat_db"]
user_col = db["user_master"]

# 🔐 Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 🔧 Utility functions
def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def get_user_by_username(username: str):
    return user_col.find_one({"username": username})

def create_token(user):
    identity = user["username"]
    role = user.get("role", "user")
    allowed_folders = user.get("allowed_folders", [])

    if role == "admin":
        allowed_folders = ["*"]

    claims = {
        "role": role,
        "display_name": user.get("display_name", ""),
        "allowed_folders": allowed_folders
    }
    return create_access_token(identity=identity, additional_claims=claims)
