from dataclasses import dataclass


@dataclass
class AuthTokenResponse:
    authorization_code: str
    state: str
