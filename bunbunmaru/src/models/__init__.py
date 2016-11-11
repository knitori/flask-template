
from flask_login import UserMixin
from flask_scrypt import (generate_password_hash, generate_random_salt,
                          check_password_hash)

from ... import db


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password_hash = db.Column(db.String(100), nullable=False)
    password_salt = db.Column(db.String(100), nullable=False)

    @property
    def password(self):
        raise AttributeError("Can't read hashed password.")

    @password.setter
    def password(self, pw):
        pw_bin = pw.encode('utf-8')
        salt_bin = generate_random_salt(64)
        self.password_salt = salt_bin.decode('ascii')
        hash_bin = generate_password_hash(
            pw_bin, salt_bin,
            # use defaults, but specify explicitly here
            N=1 << 14, r=8, p=1, buflen=64)
        self.password_hash = hash_bin.decode('ascii')

    def check_password(self, pw):
        pw_bin = pw.encode('utf-8')
        salt_bin = self.password_salt.encode('ascii')
        hash_bin = self.password_hash.encode('ascii')
        return check_password_hash(
            pw_bin, hash_bin, salt_bin,
            # same as above
            N=1 << 14, r=8, p=1, buflen=64)
