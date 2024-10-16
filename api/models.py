from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.hybrid import hybrid_property
from werkzeug.security import check_password_hash, generate_password_hash


db = SQLAlchemy()


class UserModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(32), unique=True, nullable=False)
    _password = db.Column("password", db.String(64), nullable=False)

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def password(self, password):
        self._password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def create(self):
        try:
            db.session.add(self)
            db.session.commit()

        except SQLAlchemyError as exception:
            db.session.rollback()
            raise exception

    def update(self):
        try:
            db.session.commit()

        except SQLAlchemyError as exception:
            db.session.rollback()
            raise exception
