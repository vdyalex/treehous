from email_validator import EmailNotValidError
from flask import Flask, jsonify, request
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    create_refresh_token,
    current_user,
    jwt_required,
    set_access_cookies,
    set_refresh_cookies,
    unset_jwt_cookies,
)
from flask_sqlalchemy import SQLAlchemy
from pydantic import (
    BaseModel,
    Field,
    ValidationError,
    field_validator,
)
from pydantic.networks import EmailStr, validate_email
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.hybrid import hybrid_property
from werkzeug.security import check_password_hash, generate_password_hash

from config import settings

app = Flask(__name__)

app.secret_key = settings.APP_SECRET_KEY

app.config["SQLALCHEMY_DATABASE_URI"] = settings.SQLALCHEMY_DATABASE_URI
app.config["JWT_SECRET_KEY"] = settings.JWT_SECRET_KEY
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]

# NOT RECOMMENDED IN PRODUCTION - DISABLED SINCE THIS IS A PROJECT SAMPLE
app.config["JWT_COOKIE_CSRF_PROTECT"] = False

db = SQLAlchemy(app)
jwt = JWTManager(app)


class UserModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(32), unique=True, nullable=False)
    _password = db.Column("password", db.String(64), nullable=False)

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def password(self, password):
        self._password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class UserBaseValidator(BaseModel):
    password: str = Field(..., min_length=8)
    password_confirmation: str = Field(..., min_length=8)

    @field_validator("password_confirmation")
    @classmethod
    def validate_password_confirmation(cls, value, info):
        original = info.data.get("password")

        if value != original:
            raise ValueError("Passwords do not match")

        return value


class UserCreateValidator(UserBaseValidator):
    email: EmailStr = Field(...)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        try:
            validate_email(value)
        except EmailNotValidError as exc:
            raise ValueError("Invalid email format") from exc

        return value


class UserPasswordUpdateValidator(UserBaseValidator):
    previous_password: str = Field(..., min_length=8)


@jwt.unauthorized_loader
def unauthorized_loader(reason):
    return jsonify(status="FAILED", message="Unable to authenticate", errors=[reason])


@jwt.user_lookup_loader
def user_lookup_loader(_header, data):
    return UserModel.query.filter_by(id=data["sub"]).one_or_none()


@app.before_request
def database_create_tables():
    app.before_request_funcs[None].remove(database_create_tables)
    db.create_all()


@app.route("/", methods=["GET"])
@jwt_required()
def who_am_i():
    user = {"id": current_user.id, "email": current_user.email}
    return jsonify(user=user)


@app.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    user = UserModel.query.filter_by(email=email).one_or_none()

    if not user or not user.check_password(password):
        response = jsonify(status="FAILED", message="Error while logging in")
        return response, 401

    response = jsonify(
        status="SUCCESS",
        message=f"User {user.email} was successfully logged in",
    )

    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)

    set_access_cookies(response, access_token)
    set_refresh_cookies(response, refresh_token)
    return response, 200


@app.route("/auth/token/refresh")
@jwt_required(refresh=True)
def refresh():
    response = jsonify(
        status="SUCCESS",
        message=f"Access token refreshed for the user {current_user.email}",
    )

    access_token = create_access_token(identity=current_user.id)
    set_access_cookies(response, access_token)
    return response, 200


@app.route("/auth/logout", methods=["POST"])
@jwt_required(optional=True)
def logout():
    if not current_user:
        response = jsonify(status="FAILED", message="There is no authenticated user")
        return response, 401

    response = jsonify(status="SUCCESS", message="User was successfully logged out")
    unset_jwt_cookies(response)
    return response, 200


@app.route("/user/create", methods=["POST"])
def user_create():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    password_confirmation = data.get("password_confirmation")

    existing_user = UserModel.query.filter_by(email=email).one_or_none()

    # NOT RECOMMENDED DUE TO THE EXPLOITATION OF AN API
    if existing_user:
        response = jsonify(status="FAILED", message="User already exists")
        return response, 409

    new_user = UserModel(email=email, password=password)

    try:
        UserCreateValidator(
            email=email,
            password=password,
            password_confirmation=password_confirmation,
        )
    except ValidationError as exception:
        response = jsonify(
            status="FAILED",
            message="Invalid payload",
            errors=exception.errors(include_url=False, include_context=False),
        )
        return response, 400

    try:
        db.session.add(new_user)
        db.session.commit()

    except SQLAlchemyError as exception:
        db.session.rollback()
        response = jsonify(
            status="FAILED", message="Error while creating user", errors=str(exception)
        )
        return response, 400

    response = jsonify(
        status="SUCCESS",
        message=f"User {new_user.email} was successfully created",
    )

    access_token = create_access_token(identity=new_user.id)
    refresh_token = create_refresh_token(identity=new_user.id)

    set_access_cookies(response, access_token)
    set_refresh_cookies(response, refresh_token)

    return response, 201


@app.route("/user/password/update", methods=["PATCH"])
@jwt_required()
def user_password_update():
    data = request.get_json()
    password = data.get("password")
    password_confirmation = data.get("password_confirmation")
    previous_password = data.get("previous_password")

    user = UserModel.query.filter_by(id=current_user.id).one_or_none()

    if not user:
        response = jsonify(status="FAILED", message="User not found")
        return response, 404

    try:
        UserPasswordUpdateValidator(
            password=password,
            password_confirmation=password_confirmation,
            previous_password=previous_password,
        )
    except ValidationError as exception:
        response = jsonify(
            status="FAILED",
            message="Invalid payload",
            errors=exception.errors(include_url=False, include_context=False),
        )
        return response, 400

    if not user.check_password(previous_password):
        response = jsonify(status="FAILED", message="Previous password is invalid")
        return response, 404

    try:
        user.password = password
        db.session.commit()
    except SQLAlchemyError as exception:
        db.session.rollback()
        response = jsonify(
            status="FAILED", message="Error while updating user", errors=str(exception)
        )
        return response, 400

    response = jsonify(status="SUCCESS", message="User successfully updated")

    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)

    set_access_cookies(response, access_token)
    set_refresh_cookies(response, refresh_token)

    return response, 200


if __name__ == "__main__":
    app.run(debug=settings.DEBUG)
