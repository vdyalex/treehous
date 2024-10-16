from email_validator import EmailNotValidError
from pydantic import (
    BaseModel,
    Field,
    field_validator,
)
from pydantic.networks import EmailStr, validate_email


class EmailValidator(BaseModel):
    email: EmailStr = Field(...)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        try:
            validate_email(value)
        except EmailNotValidError as exception:
            raise ValueError("Invalid email format") from exception

        return value


class PasswordConfirmationValidator(BaseModel):
    password: str = Field(..., min_length=8)
    password_confirmation: str = Field(..., min_length=8)

    @field_validator("password_confirmation")
    @classmethod
    def validate_password_confirmation(cls, value, info):
        original = info.data.get("password")

        if value != original:
            raise ValueError("Passwords do not match")

        return value


class UserLoginValidator(EmailValidator):
    password: str = Field(..., min_length=8)


class UserCreateValidator(EmailValidator, PasswordConfirmationValidator):
    pass


class UserPasswordUpdateValidator(PasswordConfirmationValidator):
    previous_password: str = Field(..., min_length=8)
