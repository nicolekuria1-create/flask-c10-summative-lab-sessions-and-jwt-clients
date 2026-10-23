from marshmallow import Schema, ValidationError, fields, validate


class SignupSchema(Schema):
    username = fields.Str(required=True, validate=validate.Length(min=3, max=80))
    password = fields.Str(required=True, load_only=True, validate=validate.Length(min=6))


class LoginSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)


class NoteCreateSchema(Schema):
    title = fields.Str(required=True, validate=validate.Length(min=1, max=150))
    content = fields.Str(required=True, validate=validate.Length(min=1))
    mood = fields.Str(required=False, allow_none=True, validate=validate.Length(max=30))


class NoteUpdateSchema(Schema):
    title = fields.Str(required=False, validate=validate.Length(min=1, max=150))
    content = fields.Str(required=False, validate=validate.Length(min=1))
    mood = fields.Str(required=False, allow_none=True, validate=validate.Length(max=30))

    def validate_payload(self, data):
        if not data:
            raise ValidationError("At least one field is required for update")
