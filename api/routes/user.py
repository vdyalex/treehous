from http import HTTPStatus
from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    current_user,
    jwt_required,
    set_access_cookies,
    set_refresh_cookies,
)
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from api.models import UserModel
from api.validators import UserCreateValidator, UserPasswordUpdateValidator

blueprint = Blueprint("user", __name__, url_prefix="/user")


@blueprint.route("/create", methods=["POST"])
def user_create():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    password_confirmation = data.get("password_confirmation")

    existing_user = UserModel.query.filter_by(email=email).one_or_none()

    # NOT RECOMMENDED DUE TO THE EXPLOITATION OF AN API
    if existing_user:
        response = jsonify(
            status="FAILED",
            message=f"User {existing_user.email} already exists",
        )
        return response, HTTPStatus.CONFLICT

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
        return response, HTTPStatus.BAD_REQUEST

    try:
        new_user.create()
    except SQLAlchemyError as exception:
        response = jsonify(
            status="FAILED", message="Error while creating user", errors=str(exception)
        )
        return response, HTTPStatus.INTERNAL_SERVER_ERROR

    response = jsonify(
        status="SUCCESS",
        message=f"User {new_user.email} was successfully created",
    )

    access_token = create_access_token(identity=new_user.id)
    refresh_token = create_refresh_token(identity=new_user.id)

    set_access_cookies(response, access_token)
    set_refresh_cookies(response, refresh_token)

    return response, HTTPStatus.CREATED


@blueprint.route("/password/update", methods=["PATCH"])
@jwt_required()
def user_password_update():
    data = request.get_json()
    password = data.get("password")
    password_confirmation = data.get("password_confirmation")
    previous_password = data.get("previous_password")

    user = UserModel.query.filter_by(id=current_user.id).one_or_none()

    if not user:
        response = jsonify(status="FAILED", message="User not found")
        return response, HTTPStatus.NOT_FOUND

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
        return response, HTTPStatus.BAD_REQUEST

    if not user.check_password(previous_password):
        response = jsonify(status="FAILED", message="Previous password is invalid")
        return response, HTTPStatus.PRECONDITION_FAILED

    try:
        user.password = password
        user.update()
    except SQLAlchemyError as exception:
        response = jsonify(
            status="FAILED", message="Error while updating user", errors=str(exception)
        )
        return response, HTTPStatus.INTERNAL_SERVER_ERROR

    response = jsonify(status="SUCCESS", message="User successfully updated")

    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)

    set_access_cookies(response, access_token)
    set_refresh_cookies(response, refresh_token)

    return response, HTTPStatus.OK
