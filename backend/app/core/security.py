import time
from collections.abc import Generator
from typing import Annotated, Any

import httpx
import jwt
import structlog
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, SecurityScopes
from jwt import PyJWKClient

from core.config import get_settings

_logger = structlog.get_logger()
_settings = get_settings()
_security = HTTPBearer()


class BearerAuth(httpx.Auth):
    """
    A httpx authentication scheme for interfacing with Logto API.
    """

    def __init__(self, token: str):
        self._token = token

    def auth_flow(
        self, request: httpx.Request
    ) -> Generator[httpx.Request, httpx.Response, None]:
        request.headers["authorization"] = f"Bearer {self._token}"
        yield request


class LogtoAPIClient:
    def __init__(
        self,
        logto_uri: str,
        app_id: str,
        app_secret: str,
        token_expiration_threshold: int = 10,
    ) -> None:
        self._logto_uri = logto_uri
        self._logto_api_uri = f"{logto_uri.rstrip('/')}/api"

        self._token: str | None = None
        self._token_expiration: float = 0
        self._token_expiration_threshold: float = token_expiration_threshold

        self._token_auth = httpx.BasicAuth(app_id, app_secret)
        self._api_auth: BearerAuth

        self._client: httpx.AsyncClient

    def connect(self):
        self._client = httpx.AsyncClient(
            base_url=self._logto_api_uri,
        )

    async def disconnect(self):
        await self._client.aclose()

    async def create_user(
        self,
        username: str,
        email: str,
        first_name: str,
        last_name: str,
    ) -> str:
        """
        Creates new Logto user and returns their Logto ID.
        Ref: https://openapi.logto.io/operation/operation-createuser
        """
        auth = BearerAuth(await self._get_access_token())
        response = await self._client.post(
            "/users",
            auth=auth,
            json={
                "primaryEmail": email,
                "username": username,
                "profile": {"givenName": first_name, "familyName": last_name},
            },
        )

        if response.status_code != 200:
            _logger.error(
                "logto_m2m_create_user_failed",
                response_status_code=response.status_code,
                response_text=response.text,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user with the identity provider.",
            )

        return response.json()["id"]

    # TODO: Define Response
    async def get_user(self, logto_id: str): ...

    async def _get_access_token(self) -> str:

        # Early return if the token exists and does not expire within the threshold time
        if self._token and self._token_expiration > (
            time.time() - self._token_expiration_threshold
        ):
            return self._token

        _logger.info("logto_fetching_new_token")

        data = {
            "grant_type": "client_credentials",
            "resource": self._logto_api_uri,
            "scope": "all",
        }

        # Get the access token
        # Ref: https://docs.logto.io/integrate-logto/interact-with-management-api#typical-scenarios-for-using-logto-management-api
        response = await self._client.post(
            f"{self._logto_uri.rstrip('/')}/oidc/token",
            auth=self._token_auth,
            data=data,
        )

        # TODO: Use a secondary app secret? Try again?
        if response.status_code != 200:
            _logger.error(
                "logto_m2m_auth_failed",
                data=data,
                response_status_code=response.status_code,
                response_text=response.text,
            )

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to authenticate with the identity provider.",
            )

        # Here is our token xD
        token = response.json()["access_token"]

        # Populate the token expiration time
        # We don't need to validate the signature since we are the user
        self._token_expiration = jwt.decode(token, options={"verify_signature": False})[
            "exp"
        ]

        return token


class LogtoAuthenticator:
    def __init__(self, jwks_uri: str, audience_uri: str, issuer_uri: str):
        self._jwks_client = PyJWKClient(jwks_uri)
        self._audience_uri = audience_uri
        self._issuer_uri = issuer_uri
        self._logger = structlog.get_logger(__name__)

    def __call__(
        self,
        credentials: Annotated[HTTPAuthorizationCredentials, Depends(_security)],
        security_scopes: SecurityScopes,
    ) -> dict[str, Any]:
        token = credentials.credentials

        try:
            signing_key = self._jwks_client.get_signing_key_from_jwt(token)

            # Hardcode the algorithm to prevent attacker influence
            # Ref: https://pyjwt.readthedocs.io/en/latest/api.html#jwt.decode
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=["ES384", "RS256"],
                issuer=self._issuer_uri,
                audience=self._audience_uri,
            )

            # Extract the scopes and tokenize
            scopes = payload.get("scope", "").split(" ")

            for scope in security_scopes.scopes:
                if scope not in scopes:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Not enough permissions",
                    )

            return payload

        except jwt.PyJWKClientError as e:
            _logger.error("jwks_fetch_failed", error=str(e))

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Unable to fetch JWKS: {e!s}",
            )
        except jwt.ExpiredSignatureError as e:
            _logger.warning("auth_token_expired", error=str(e))

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token expired: {e!s}",
            )
        except jwt.InvalidTokenError as e:
            _logger.warning("auth_token_invalid", error=str(e))

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {e!s}",
            )


_logto_api_client = LogtoAPIClient(
    str(_settings.logto_uri),
    _settings.logto_admin_app_id,
    _settings.logto_admin_app_secret.get_secret_value(),
)


def get_logto_api_client() -> LogtoAPIClient:
    return _logto_api_client


verify_jwt = LogtoAuthenticator(
    _settings.logto_jwt_uri, _settings.logto_audience_uri, _settings.logto_issuer_uri
)
