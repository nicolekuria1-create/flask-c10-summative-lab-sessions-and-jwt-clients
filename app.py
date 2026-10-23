import os
from functools import wraps

from flask import Flask, jsonify, request, session
from flask_restful import Api, Resource
from marshmallow import ValidationError

from config import Config
from extensions import bcrypt, db, migrate
from models import Note, User
from schemas import LoginSchema, NoteCreateSchema, NoteUpdateSchema, SignupSchema


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)

    api = Api(app)

    def login_required(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user_id = session.get("user_id")
            if not user_id:
                return {"error": "Unauthorized"}, 401
            user = User.query.get(user_id)
            if not user:
                session.clear()
                return {"error": "Unauthorized"}, 401
            return fn(user, *args, **kwargs)

        return wrapper

    class SignupResource(Resource):
        def post(self):
            schema = SignupSchema()
            try:
                data = schema.load(request.get_json() or {})
            except ValidationError as err:
                return {"errors": err.messages}, 400

            if User.query.filter_by(username=data["username"]).first():
                return {"error": "Username already taken"}, 409

            user = User(username=data["username"])
            user.set_password(data["password"])
            db.session.add(user)
            db.session.commit()

            session["user_id"] = user.id
            return user.to_dict(), 201

    class LoginResource(Resource):
        def post(self):
            schema = LoginSchema()
            try:
                data = schema.load(request.get_json() or {})
            except ValidationError as err:
                return {"errors": err.messages}, 400

            user = User.query.filter_by(username=data["username"]).first()
            if not user or not user.check_password(data["password"]):
                return {"error": "Invalid username or password"}, 401

            session["user_id"] = user.id
            return user.to_dict(), 200

    class LogoutResource(Resource):
        @login_required
        def delete(self, _current_user):
            session.clear()
            return "", 204

    class CheckSessionResource(Resource):
        def get(self):
            user_id = session.get("user_id")
            if not user_id:
                return {"error": "Unauthorized"}, 401

            user = User.query.get(user_id)
            if not user:
                session.clear()
                return {"error": "Unauthorized"}, 401
            return user.to_dict(), 200

    class NotesResource(Resource):
        @login_required
        def get(self, current_user):
            page = request.args.get("page", default=1, type=int)
            per_page = request.args.get("per_page", default=10, type=int)
            per_page = min(max(per_page, 1), 50)

            pagination = (
                Note.query.filter_by(user_id=current_user.id)
                .order_by(Note.created_at.desc())
                .paginate(page=page, per_page=per_page, error_out=False)
            )

            return {
                "items": [note.to_dict() for note in pagination.items],
                "page": pagination.page,
                "per_page": pagination.per_page,
                "total": pagination.total,
                "pages": pagination.pages,
            }, 200

        @login_required
        def post(self, current_user):
            schema = NoteCreateSchema()
            try:
                data = schema.load(request.get_json() or {})
            except ValidationError as err:
                return {"errors": err.messages}, 400

            note = Note(
                title=data["title"],
                content=data["content"],
                mood=data.get("mood"),
                user_id=current_user.id,
            )
            db.session.add(note)
            db.session.commit()
            return note.to_dict(), 201

    class NoteByIDResource(Resource):
        @login_required
        def get(self, current_user, note_id):
            note = Note.query.filter_by(id=note_id, user_id=current_user.id).first()
            if not note:
                return {"error": "Note not found"}, 404
            return note.to_dict(), 200

        @login_required
        def patch(self, current_user, note_id):
            schema = NoteUpdateSchema()
            payload = request.get_json() or {}

            try:
                data = schema.load(payload)
            except ValidationError as err:
                return {"errors": err.messages}, 400

            if not data:
                return {"error": "At least one field is required for update"}, 400

            note = Note.query.filter_by(id=note_id, user_id=current_user.id).first()
            if not note:
                return {"error": "Note not found"}, 404

            for field in ["title", "content", "mood"]:
                if field in data:
                    setattr(note, field, data[field])

            db.session.commit()
            return note.to_dict(), 200

        @login_required
        def delete(self, current_user, note_id):
            note = Note.query.filter_by(id=note_id, user_id=current_user.id).first()
            if not note:
                return {"error": "Note not found"}, 404

            db.session.delete(note)
            db.session.commit()
            return "", 204

    @app.get("/")
    def index():
        return jsonify({"message": "Flask auth backend is running"})

    api.add_resource(SignupResource, "/signup")
    api.add_resource(LoginResource, "/login")
    api.add_resource(LogoutResource, "/logout")
    api.add_resource(CheckSessionResource, "/check_session")
    api.add_resource(NotesResource, "/notes")
    api.add_resource(NoteByIDResource, "/notes/<int:note_id>")

    return app


app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5555))
    app.run(host="0.0.0.0", port=port, debug=True)
