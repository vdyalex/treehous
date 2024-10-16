import pytest
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.test import Cookie
from werkzeug.datastructures import Headers

from app import create_app


@pytest.fixture(scope="module", autouse=True)
def client():
    app = create_app(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite:///tests.db",
        TEST_USER_EMAIL="admin@gmail.com",
        TEST_USER_PASSWORD="Tre3H@us#",
    )

    from api.models import db, UserModel

    with app.app_context():
        db.create_all()

        existing_user = UserModel.query.filter_by(
            email=app.config["TEST_USER_EMAIL"]
        ).one_or_none()

        if not existing_user:
            new_user = UserModel(
                email=app.config["TEST_USER_EMAIL"],
                password=app.config["TEST_USER_PASSWORD"],
            )

            try:
                new_user.create()
            except SQLAlchemyError:
                pytest.fail("Failure on running fixtures")

    context = app.app_context()

    context.push()

    yield app.test_client()

    with app.app_context():
        db.session.remove()
        db.drop_all()

    context.pop()


class Authentication:
    success = False
    access_token = None
    refresh_token: None

    def __init__(self, config):
        self.headers = Headers()
        self.header_name = config["JWT_HEADER_NAME"]
        self.header_type = config["JWT_HEADER_TYPE"]

    def set(self, access_token, refresh_token):
        self.success = None not in (access_token, refresh_token)
        self.access_token = access_token
        self.refresh_token = refresh_token

        parts = [self.header_type, self.access_token]
        header_value = " ".join([v for v in parts if v])

        self.headers.add(self.header_name, header_value)

    def clear(self):
        self.success = False
        self.access_token = None
        self.refresh_token = None

        self.headers.clear()


@pytest.fixture()
def authentication(client):

    user_email = client.application.config["TEST_USER_EMAIL"]
    user_password = client.application.config["TEST_USER_PASSWORD"]

    access_cookie_name = client.application.config["JWT_ACCESS_COOKIE_NAME"]
    refresh_cookie_name = client.application.config["JWT_REFRESH_COOKIE_NAME"]

    payload = {"email": user_email, "password": user_password}
    response = client.post("/auth/login", json=payload)

    auth = Authentication(client.application.config)

    if not response.status_code == 200:
        return auth

    access_cookie = client.get_cookie(access_cookie_name)
    refresh_cookie = client.get_cookie(refresh_cookie_name)

    access_token = access_cookie.value if isinstance(access_cookie, Cookie) else None
    refresh_token = refresh_cookie.value if isinstance(refresh_cookie, Cookie) else None

    auth.set(access_token, refresh_token)

    return auth


@pytest.fixture()
def deauthentication(client, authentication):

    response = client.post("/auth/logout", headers=authentication.headers)

    if response.status_code == 200:
        authentication.clear()

    return authentication
