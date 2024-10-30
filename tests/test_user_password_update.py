import unittest
from http import HTTPStatus


def test_user_password_update_successfully_update(client, authentication):
    """Should successfully update a user"""

    case = unittest.TestCase()

    new_password = "12345678"
    old_password = client.application.config["TEST_USER_PASSWORD"]

    expect = {
        "status": "SUCCESS",
        "message": "User successfully updated",
    }

    def execute(changed_password, previous_password):
        payload = {
            "password": changed_password,
            "password_confirmation": changed_password,
            "previous_password": previous_password,
        }

        response = client.patch(
            "/user/password/update",
            headers=authentication.headers,
            json=payload,
        )

        result = response.get_json()

        case.assertEqual(response.status_code, HTTPStatus.OK)
        case.assertDictEqual(expect, result)

    execute(new_password, old_password)
    execute(old_password, new_password)


def test_user_password_update_incorrect_previou_password(client, authentication):
    """Should identify incorrect previous password when changing user credentials"""

    case = unittest.TestCase()

    new_password = "12345678"
    old_password = "THIS PASSWORD IS MEANT TO BE INCORRECT"

    payload = {
        "password": new_password,
        "password_confirmation": new_password,
        "previous_password": old_password,
    }

    response = client.patch(
        "/user/password/update",
        headers=authentication.headers,
        json=payload,
    )

    result = response.get_json()
    expect = {
        "status": "FAILED",
        "message": "Previous password is invalid",
    }

    case.assertEqual(response.status_code, HTTPStatus.PRECONDITION_FAILED)
    case.assertDictEqual(expect, result)


def test_user_password_update_invalid_input_data(client, authentication):
    """Should identify invalid input data when changing user credentials"""

    case = unittest.TestCase()

    payload = {
        "password": "ABCDEF",
        "password_confirmation": "12345678",
        "previous_password": "I_DONT_REMEMBER",
    }

    response = client.patch(
        "/user/password/update",
        headers=authentication.headers,
        json=payload,
    )

    result = response.get_json()
    expect = {
        "status": "FAILED",
        "message": "Invalid payload",
        "errors": [
            {
                "input": "ABCDEF",
                "loc": ["password"],
                "msg": "String should have at least 8 characters",
                "type": "string_too_short",
            },
            {
                "input": "12345678",
                "loc": ["password_confirmation"],
                "msg": "Value error, Passwords do not match",
                "type": "value_error",
            },
        ],
    }

    case.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
    case.assertDictEqual(expect, result)
