import base64


def encode_base64url(s: str) -> str:
    encoded = base64.urlsafe_b64encode(s.encode()).decode()
    return encoded.rstrip("=")


def decode_base64url(s: str) -> str:
    s = s.strip()
    missing = len(s) % 4
    if missing:
        s += "=" * (4 - missing)
    return base64.urlsafe_b64decode(s).decode()
