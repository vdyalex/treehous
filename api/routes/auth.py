from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    current_user,
    jwt_required,
    set_access_cookies,
    set_refresh_cookies,
    unset_jwt_cookies,
)
from pydantic import ValidationError

from api.models import UserModel
from api.validators import UserLoginValidator


blueprint = Blueprint("auth", __name__, url_prefix="/auth")


@blueprint.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    try:
        UserLoginValidator(
            email=email,
            password=password,
        )
    except ValidationError as exception:
        response = jsonify(
            status="FAILED",
            message="Invalid payload",
            errors=exception.errors(include_url=False, include_context=False),
        )
        return response, 400

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


@blueprint.route("/token/refresh")
@jwt_required(refresh=True)
def token_refresh():
    response = jsonify(
        status="SUCCESS",
        message=f"Access token refreshed for the user {current_user.email}",
    )

    access_token = create_access_token(identity=current_user.id)
    set_access_cookies(response, access_token)
    return response, 200


@blueprint.route("/logout", methods=["POST"])
@jwt_required(optional=True)
def logout():
    if not current_user:
        response = jsonify(status="FAILED", message="There is no authenticated user")
        return response, 401

    response = jsonify(status="SUCCESS", message="User was successfully logged out")
    unset_jwt_cookies(response)
    return response, 200
