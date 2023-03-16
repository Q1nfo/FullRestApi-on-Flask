import base64
import hashlib
import hmac
from typing import Union

from flask import current_app, request
# .
# =====================CREATE FUNC WHICH ALLOWS INTEGRATE SECURITY IN API=============================================


def __generate_password_digest(password: str) -> bytes:
    return hashlib.pbkdf2_hmac(
        hash_name='sha256',
        password=password.encode('utf-8'),
        salt=current_app.config['PWD_HASH_SALT'],
        iterations=current_app.config['PWD_HASH_ITERATIONS'],
    )


def generate_password_hash(password: str) -> str:
    return base64.b64encode(__generate_password_digest(password)).decode('utf-8')


def compare_passwords(password_hash: Union[str, bytes], password: str):
    return hmac.compare_digest(
        base64.b64decode(password_hash), __generate_password_digest(password)
    )


def code_on_base_64(string: str):
    """TRANSLATE BASIC AUTH TOKEN IN ASCII"""
    message = string
    message_bytes = message.encode('ascii')
    base64_bytes = base64.b64encode(message_bytes)
    base64_message = base64_bytes.decode('ascii')
    return base64_message


def check_user(data: str):

    """SERIALIZE DATA USER FROM BASIC AUTH TOKEN"""

    if data is None or data == '':
        return False

    data = data.split('Basic ')[-1]
    base64_bytes = data.encode('ascii')
    message_bytes = base64.b64decode(base64_bytes)
    message = message_bytes.decode('ascii').split(':')
    return {
        'login': message[0],
        'password': message[1]
    }




