# from flask import Blueprint, request, jsonify
# from flask_jwt_extended import jwt_required, get_jwt_identity
# from services.feedback_service import add_feedback, get_rating_stats
#
# def register_feedback_routes(app):
#     feedback_bp = Blueprint("feedback", __name__)
#
#     @feedback_bp.route("/rate-response", methods=["POST"])
#     @jwt_required()
#     def rate_response():
#         data = request.get_json()
#         pdf_path = data.get("pdf_path")
#         query = data.get("query")
#         rating = data.get("rating")
#         print("✅ [SERVER] Received feedback rating request")
#         print("📝 Data:", data)
#
#         if not pdf_path or not query or rating is None:
#             return jsonify({"error": "Missing required fields"}), 400
#
#         user = get_jwt_identity()
#         add_feedback("ask-kb", pdf_path, query, int(rating), user=user)
#         return jsonify({"message": "Rating saved ✅"})
#
#     @feedback_bp.route("/response-rating", methods=["GET"])
#     @jwt_required()
#     def response_rating():
#         pdf_path = request.args.get("pdf_path")
#         query = request.args.get("query")
#         print("✅ [SERVER] Received feedback response request")
#         print("📝 Data:", {"pdf_path": pdf_path, "query": query})
#         if not pdf_path or not query:
#             return jsonify({"error": "Missing pdf_path or query"}), 400
#
#         stats = get_rating_stats("ask-kb", pdf_path, query)
#         return jsonify(stats)
#
#     app.register_blueprint(feedback_bp)
