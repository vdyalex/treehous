from dynaconf import Dynaconf, Validator

validators = [
    Validator("DEBUG", is_type_of=bool, default=True),
    Validator("APP_SECRET_KEY", is_type_of=str, default=""),
    Validator("JWT_SECRET_KEY", is_type_of=str, default=""),
    Validator("SQLALCHEMY_DATABASE_URI", is_type_of=str, default="sqlite:///users.db"),
    Validator("SQLALCHEMY_TRACK_MODIFICATIONS", is_type_of=bool, default=True),
]

settings = Dynaconf(
    settings_files=["settings.toml", ".secrets.toml"],
    load_dotenv=True,
    validators=validators,
)
