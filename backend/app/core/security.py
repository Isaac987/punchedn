from typing import Annotated, Any, Dict

import jwt
import structlog
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, SecurityScopes
from jwt import PyJWKClient

from core.config import get_settings

_logger = structlog.get_logger()
_settings = get_settings()
_security = HTTPBearer()


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
    ) -> Dict[str, Any]:
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

            print(security_scopes.scopes)

            for scope in security_scopes.scopes:
                if scope not in scopes:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Not enough permissions",
                    )

            return payload

        except jwt.PyJWKClientError as e:
            _logger.error("jwks_fetch_failed", error=str(e))

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Unable to fetch JWKS: {str(e)}",
            )
        except jwt.ExpiredSignatureError as e:
            _logger.warning("auth_token_expired", error=str(e))

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token expired: {str(e)}",
            )
        except jwt.InvalidTokenError as e:
            _logger.warning("auth_token_invalid", error=str(e))

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}",
            )


verify_jwt = LogtoAuthenticator(
    _settings.logto_jwt_uri, _settings.logto_audience_uri, _settings.logto_issuer_uri
)
