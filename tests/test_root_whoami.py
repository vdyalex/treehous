import unittest


def test_root_whoami_successfully_fetch(client, authentication):
    """Should successfully fetch the logged user"""

    case = unittest.TestCase()

    user_email = client.application.config["TEST_USER_EMAIL"]

    response = client.get("/", headers=authentication.headers)

    result = response.get_json()
    expect = {
        "user": {
            "id": 1,
            "email": user_email,
        }
    }

    case.assertEqual(response.status_code, 200)
    case.assertDictEqual(expect, result)


def test_root_whoami_fail_fetch(client, deauthentication):
    """Should identify wrong session when logging in a user"""

    case = unittest.TestCase()

    header_name = client.application.config["JWT_HEADER_NAME"]

    response = client.get("/", headers=deauthentication.headers)

    result = response.get_json()
    expect = {
        "status": "FAILED",
        "message": "Unable to authenticate",
        "errors": [f"Missing {header_name} Header"],
    }

    case.assertEqual(response.status_code, 401)
    case.assertDictEqual(expect, result)
