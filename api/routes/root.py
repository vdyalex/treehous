from http import HTTPStatus
from flask import Blueprint, jsonify
from flask_jwt_extended import (
    current_user,
    jwt_required,
)


blueprint = Blueprint("root", __name__)


@blueprint.route("/", methods=["GET"])
@jwt_required()
def index():
    if not current_user:
        response = jsonify(status="FAILED", message="No user authenticated")
        return response, HTTPStatus.UNAUTHORIZED

    user = {"id": current_user.id, "email": current_user.email}
    response = jsonify(user=user)

    return response, HTTPStatus.OK
