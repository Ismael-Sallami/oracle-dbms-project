import hashlib
import os


_PEPPER = os.getenv("EKIS_PEPPER", "")

def hash_password_sha256(password: str) -> str:
    data = (password + _PEPPER).encode("utf-8")
    return hashlib.sha256(data).hexdigest()
