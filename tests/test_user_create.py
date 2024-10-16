import unittest


def test_user_create_successfully_create(client):
    """Should successfully create a user"""

    case = unittest.TestCase()

    user_email = "john.doe@gmail.com"
    user_password = "FooBar123"

    payload = {
        "email": user_email,
        "password": user_password,
        "password_confirmation": user_password,
    }

    response = client.post("/user/create", json=payload)

    result = response.get_json()
    expect = {
        "status": "SUCCESS",
        "message": f"User {user_email} was successfully created",
    }

    case.assertEqual(response.status_code, 201)
    case.assertDictEqual(expect, result)


def test_user_create_duplicated_record(client):
    """Should identify duplicated records when creating a user"""

    case = unittest.TestCase()

    user_email = client.application.config["TEST_USER_EMAIL"]
    user_password = "FooBar123"

    payload = {
        "email": user_email,
        "password": user_password,
        "password_confirmation": user_password,
    }

    response = client.post("/user/create", json=payload)

    result = response.get_json()
    expect = {
        "status": "FAILED",
        "message": f"User {user_email} already exists",
    }

    case.assertEqual(response.status_code, 409)
    case.assertDictEqual(expect, result)


def test_user_create_invalid_input_data(client):
    """Should identify invalid input data when creating a user"""

    case = unittest.TestCase()

    user_email = "lacostegmailcom"
    user_password = "FooBar"
    user_password_confirmation = "Lambda456"

    payload = {
        "email": user_email,
        "password": user_password,
        "password_confirmation": user_password_confirmation,
    }

    response = client.post("/user/create", json=payload)

    result = response.get_json()
    expect = {
        "status": "FAILED",
        "message": "Invalid payload",
        "errors": [
            {
                "input": user_password,
                "loc": ["password"],
                "msg": "String should have at least 8 characters",
                "type": "string_too_short",
            },
            {
                "input": user_password_confirmation,
                "loc": ["password_confirmation"],
                "msg": "Value error, Passwords do not match",
                "type": "value_error",
            },
            {
                "input": user_email,
                "loc": ["email"],
                "msg": "value is not a valid email address: An email address must have an @-sign.",
                "type": "value_error",
            },
        ],
    }

    case.assertEqual(response.status_code, 400)
    case.assertDictEqual(expect, result)
