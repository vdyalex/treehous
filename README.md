# Treehous

Code challenge made for Treehous.

## Challenge

**Coding Question:** Create a Flask API endpoint for user registration and password updates. JWT authentication should also be included.

**Input Format:** The API should accept user details like email and password for registration, and for password updates, it should require the user's email and new password.

**Output Format:** The API should return a confirmation message for successful registration or password update, along with appropriate status codes

## Solution

### Dependencies

- **Flask** ([flask.palletsprojects.com](https://flask.palletsprojects.com)): Web API framework
- **Poetry** ([python-poetry.org](https://python-poetry.org)): Package manager
- **SQLAlchemy** ([sqlalchemy.org](https://sqlalchemy.org)): ORM library for connecting on SQL databases
- **Pydantic** ([pydantic.dev](https://docs.pydantic.dev)): Data validation library
- **Flask JWT** ([flask-jwt-extended.readthedocs.io](https://flask-jwt-extended.readthedocs.io)): Extension of JSON Web Tokens for Flask
- **Dynaconf** ([dynaconf.com](https://dynaconf.com)): Application configuration manager

### Endpoints

#### `GET /`

When the user is authenticated via cookie session, this endpoint returns the data from the logged user.

#### `POST /auth/login`

Accepts `email` and `password`. Should create a user with that data.

> _Includes validation for existing users for avoiding collision, althought in real life it might be exploited._

#### `POST /auth/logout`

Deauthenticate the currently logged user by invalidating the session. Fails in case there is no active session.

#### `POST /auth/token/refresh`

Used to refresh the `access_token`. It allows the JWT negotiation to keep valid for most of clients, expiring the `access_token` which is retrieved with the `refresh_token`.

**References:** https://auth0.com/blog/refresh-tokens-what-are-they-and-when-to-use-them

> **Note:** Refresh Tokens aren't recommended to be stored in browser sessions (cookies) due to its sensitivity to generate a new Access Token. It's currently implemented in that way for simplifying the implementation and quickly test on Postman.

#### `POST /user/create`

Should create a user based on the accepted `email` and `password`. It must have a `password_confirmation` identical to the `password`.

> _Includes validation for existing users for avoiding collision, althought in real life it might be exploited._

#### `PATCH /user/password/update`

Should update the password of the currently logged user. It must have a `password_confirmation` identical to the `password`, and beyond that, a field to confirm the `current_password`.

## Running

For running the project, it's required to have Python 3+ and Poetry.

After ensuring those tools are correctly installed in your machine, you can proceed.

### Download the source code

```bash
git clone git@github.com:vdyalex/treehous.git treehous
cd treehous
```

### Install dependendencies

```bash
poetry install
```

### Start the web server

```bash
poetry run python main.py
```

### Make requests

```bash
curl --location 'http://127.0.0.1:5000/user/create' \
--header 'Content-Type: application/json' \
--data-raw '{ "email": "john.doe@gmail.com", "password": "FooBar123@", "password_confirmation": "FooBar123@" }'
```

After those instructions, the project should be available at the port 5000 and the API might be accessed using the Postman or cURL in development mode.

## Inconsistencies

There are a few inconsistencies identified in the requirements mentioned at the [Challenge](#challenge).

### Requested endpoints

The challenge requested only one endpoint, when actually it was required to have:

1. User registration
1. Password updates
1. Authentication, since it requires JWT
1. Refresh the JWT token
1. Confirmation of logged user, since the authentication via JWT doesn't confirm by itself who's the logged user

### Misleading authentication instructions

Since it requires a JWT token, it isn't required to have user's email. The identification of the authenticated used is already in the JWT

### Exploitation flaws in the API design

The password update is required to have email and new password, but it would lead to exploitation and impersonation, since the protection should exist either via JWT authentication and/or previous password confirmation.

### Timeline

The code challenge was requested to have only 30 minutes of duration, but given the requirements, it's impossible to perform these tasks in such a limited amount of time, that would include at least:

- Setting up the environment
- Boostrapping the application
- Installing dependencies
- Creating routes
- Configuring the ORM/database
- Defining the validators
- Implementing the requirements
- Debugging and testing the application against the requirements
- Documenting and explaning the solution
- Submitting the response

Those are considered the bare minimum, and is far from being accomplished in 30 minutes.

## Notes

🚫 **Disclaimer:** This application is not intended to be used in production environment.
