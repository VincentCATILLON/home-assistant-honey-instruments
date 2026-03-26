"""API client for Honey Instruments."""

from __future__ import annotations

import logging
from typing import Any

import aiohttp

from .const import API_BASE_URL, API_DEVICES_ENDPOINT, API_LOGIN_ENDPOINT

_LOGGER = logging.getLogger(__name__)


class HoneyInstrumentsApiError(Exception):
    """Base exception for Honey Instruments API errors."""


class HoneyInstrumentsAuthError(HoneyInstrumentsApiError):
    """Authentication failed."""


class HoneyInstrumentsApi:
    """Client for the Honey Instruments REST API."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        email: str,
        password: str,
        access_token: str | None = None,
    ) -> None:
        """Initialize the API client."""
        self._session = session
        self._email = email
        self._password = password
        self._access_token = access_token

    @property
    def access_token(self) -> str | None:
        """Return the current access token."""
        return self._access_token

    async def authenticate(self) -> str:
        """Login and retrieve an access token."""
        url = f"{API_BASE_URL}{API_LOGIN_ENDPOINT}"
        payload = {"email": self._email, "password": self._password}

        try:
            async with self._session.post(url, json=payload) as resp:
                if resp.status == 401:
                    raise HoneyInstrumentsAuthError("Invalid email or password")
                resp.raise_for_status()
                data = await resp.json()
        except aiohttp.ClientError as err:
            raise HoneyInstrumentsApiError(
                f"Error communicating with API: {err}"
            ) from err

        token = data.get("access_token")
        if not token:
            raise HoneyInstrumentsAuthError("No access_token returned by the API")

        self._access_token = token
        _LOGGER.debug("Successfully authenticated with Honey Instruments API")
        return token

    async def _request(self, method: str, endpoint: str, **kwargs: Any) -> Any:
        """Make an authenticated API request, re-authenticating on 401."""
        if not self._access_token:
            await self.authenticate()

        url = f"{API_BASE_URL}{endpoint}"
        headers = {"X-API-KEY": self._access_token}

        try:
            async with self._session.request(
                method, url, headers=headers, **kwargs
            ) as resp:
                if resp.status == 401:
                    _LOGGER.debug("Token expired, re-authenticating")
                    await self.authenticate()
                    headers["X-API-KEY"] = self._access_token
                    async with self._session.request(
                        method, url, headers=headers, **kwargs
                    ) as retry_resp:
                        retry_resp.raise_for_status()
                        return await retry_resp.json()
                resp.raise_for_status()
                return await resp.json()
        except aiohttp.ClientError as err:
            raise HoneyInstrumentsApiError(
                f"Error communicating with API: {err}"
            ) from err

    async def get_devices(self) -> list[dict[str, Any]]:
        """Retrieve the list of devices (balances)."""
        return await self._request("GET", API_DEVICES_ENDPOINT)

    async def get_device_data(self, device_id: int) -> list[dict[str, Any]]:
        """Retrieve the latest messages for a device."""
        return await self._request("GET", f"{API_DEVICES_ENDPOINT}/{device_id}")
