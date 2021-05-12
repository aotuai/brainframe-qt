from dataclasses import dataclass


@dataclass
class AuthTokenResponse:
    authorization_code: str
    state: str


@dataclass
class OAuthTokens:
    access_token: str
    refresh_token: str

