from flask import request, make_response
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

from flask import Flask

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

CORS(app)


db.init_app(app)

migrate = Migrate(app, db)


@app.route("/")
def home():
    return {"message": "Chatterbox API"}


@app.route("/messages", methods=["GET", "POST"])
def messages_collection():
    if request.method == "GET":
        messages = Message.query.order_by(Message.created_at.asc()).all()
        return make_response([m.to_dict() for m in messages], 200)

    data = request.get_json() or {}
    body = data.get("body")
    username = data.get("username")

    if not body or not username:
        return make_response({"errors": ["body and username are required"]}, 400)

    message = Message(body=body, username=username)
    db.session.add(message)
    db.session.commit()
    return make_response(message.to_dict(), 201)


@app.route("/messages/<int:id>", methods=["PATCH", "DELETE"])
def message_detail(id):
    message = Message.query.get(id)
    if message is None:
        return make_response({"error": "Message not found"}, 404)

    if request.method == "DELETE":
        db.session.delete(message)
        db.session.commit()
        return make_response({}, 204)

    data = request.get_json() or {}
    if not data.get("body"):
        return make_response({"errors": ["body is required"]}, 400)

    message.body = data["body"]
    db.session.commit()
    return make_response(message.to_dict(), 200)


if __name__ == "__main__":
    app.run(port=5000, debug=True)
