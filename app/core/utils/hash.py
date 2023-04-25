import hashlib


def sha256(data: str):
    return hashlib.sha256(data.encode('utf8')).hexdigest()
