# services/feedback_service.py
import os
from pymongo import MongoClient
from datetime import datetime


mongodb_url = os.getenv("MONGODB_URL")
client = MongoClient(mongodb_url)
db = client["gowowschat_db"]
feedback_col = db["response_feedback"]

def normalize(text):
    return text.strip().lower()

def add_feedback(response_type, pdf_path, query, rating, user="anonymous", session_id=None):
    feedback_col.insert_one({
        "type": response_type,
        "pdf_path": pdf_path,
        "query": normalize(query),
        "rating": rating,
        "user": user,
        "session_id": session_id,
        "rated_on": datetime.utcnow()
    })

def get_rating_stats(response_type, pdf_path, query):
    norm_query = normalize(query)
    pipeline = [
        {
            "$match": {
                "type": response_type,
                "pdf_path": pdf_path,
                "$expr": {
                    "$eq": [
                        { "$toLower": { "$trim": { "input": "$query" } } },
                        norm_query
                    ]
                }
            }
        },
        {
            "$group": {
                "_id": None,
                "avg_rating": { "$avg": "$rating" },
                "total_ratings": { "$sum": 1 }
            }
        }
    ]
    result = list(feedback_col.aggregate(pipeline))
    return result[0] if result else {"avg_rating": None, "total_ratings": 0}

