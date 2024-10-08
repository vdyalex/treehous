from dynaconf import Dynaconf, Validator

settings = Dynaconf(
    settings_files=["settings.toml", ".secrets.toml"],
    load_dotenv=True,
    validators=[
        Validator(
            "DEBUG",
            required=True,
            is_type_of=bool,
        ),
        Validator("APP_SECRET_KEY", default="e56d917072f27c087ebd1156e730379ef121f306"),
        Validator("JWT_SECRET_KEY", default="bdc5f12073c02f7841bcea2edbfb9f262f2ef14a"),
        Validator("SQLALCHEMY_DATABASE_URI", default="sqlite:///users.db"),
    ],
)
