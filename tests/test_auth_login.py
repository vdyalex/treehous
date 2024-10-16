import unittest


def test_auth_login_successfully_authenticate(client):
    """Should successfully authenticate a user"""

    case = unittest.TestCase()

    user_email = client.application.config["TEST_USER_EMAIL"]
    user_password = client.application.config["TEST_USER_PASSWORD"]

    payload = {"email": user_email, "password": user_password}

    response = client.post("/auth/login", json=payload)

    result = response.get_json()
    expect = {
        "status": "SUCCESS",
        "message": f"User {user_email} was successfully logged in",
    }

    case.assertEqual(response.status_code, 200)
    case.assertDictEqual(expect, result)


def test_auth_login_forbidden_access_unexisting_user(client):
    """Should forbid the access of unexisting user when authenticating"""

    case = unittest.TestCase()

    user_email = "unexisting_user@random.me"
    user_password = "UNNECESSARY CREDENTIALS"

    payload = {"email": user_email, "password": user_password}

    response = client.post("/auth/login", json=payload)

    result = response.get_json()
    expect = {
        "status": "FAILED",
        "message": "Error while logging in",
    }

    case.assertEqual(response.status_code, 401)
    case.assertDictEqual(expect, result)


def test_auth_login_forbidden_access_incorrect_credentials(client):
    """Should forbid the access given incorrect credentias when authenticating"""

    case = unittest.TestCase()

    user_email = client.application.config["TEST_USER_EMAIL"]
    user_password = "UNNECESSARY CREDENTIALS"

    payload = {"email": user_email, "password": user_password}

    response = client.post("/auth/login", json=payload)

    result = response.get_json()
    expect = {
        "status": "FAILED",
        "message": "Error while logging in",
    }

    case.assertEqual(response.status_code, 401)
    case.assertDictEqual(expect, result)


def test_auth_login_invalid_input(client):
    """Should identify invalid input when authenticating"""

    case = unittest.TestCase()

    user_email = "lacostegmailcom"
    user_password = "FooBar"

    payload = {"email": user_email, "password": user_password}

    response = client.post("/auth/login", json=payload)

    result = response.get_json()
    expect = {
        "status": "FAILED",
        "message": "Invalid payload",
        "errors": [
            {
                "input": user_email,
                "loc": ["email"],
                "msg": "value is not a valid email address: An email address must have an @-sign.",
                "type": "value_error",
            },
            {
                "input": user_password,
                "loc": ["password"],
                "msg": "String should have at least 8 characters",
                "type": "string_too_short",
            },
        ],
    }

    case.assertEqual(response.status_code, 400)
    case.assertDictEqual(expect, result)
