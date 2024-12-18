from http import HTTPStatus
from flask import jsonify
from flask_jwt_extended import JWTManager

from api.models import UserModel


jwt = JWTManager()


@jwt.unauthorized_loader
def unauthorized_loader(reason):
    response = jsonify(
        status="FAILED",
        message="Unable to authenticate",
        errors=[reason],
    )
    return response, HTTPStatus.UNAUTHORIZED


@jwt.user_lookup_loader
def user_lookup_loader(_header, data):
    return UserModel.query.filter_by(id=data["sub"]).one_or_none()
