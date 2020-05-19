import secrets
import string


def create_strong_password(length=20):
    """
    Creates a cryptographically strong password
    """
    assert length >= 10
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for i in range(length))
    return password
