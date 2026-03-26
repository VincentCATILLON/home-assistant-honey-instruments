from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
)

from .api import (
    HoneyInstrumentsApi,
    HoneyInstrumentsApiError,
    HoneyInstrumentsAuthError,
)
from .const import (
    CONF_ACCESS_TOKEN,
    CONF_EMAIL,
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    LOGGER,
    MAX_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_EMAIL): str,
        vol.Required(CONF_PASSWORD): str,
    }
)


class HoneyInstrumentsConfigFlow(ConfigFlow, domain=DOMAIN):
    """Config flow for Honey Instruments."""

    VERSION = 1

    _reauth_entry: ConfigEntry | None = None

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> HoneyInstrumentsOptionsFlow:
        """Get the options flow for this handler."""
        return HoneyInstrumentsOptionsFlow(config_entry)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step: email + password."""
        errors: dict[str, str] = {}

        if user_input is not None:
            email = user_input[CONF_EMAIL]
            password = user_input[CONF_PASSWORD]

            await self.async_set_unique_id(email.lower())
            self._abort_if_unique_id_configured()

            session = async_get_clientsession(self.hass)
            api = HoneyInstrumentsApi(session, email, password)

            try:
                access_token = await api.authenticate()
            except HoneyInstrumentsAuthError:
                errors["base"] = "invalid_auth"
            except HoneyInstrumentsApiError:
                errors["base"] = "cannot_connect"
            except Exception:
                LOGGER.exception("Unexpected exception during login")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title=f"Honey Instruments ({email})",
                    data={
                        CONF_EMAIL: email,
                        CONF_PASSWORD: password,
                        CONF_ACCESS_TOKEN: access_token,
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    async def async_step_reauth(self, entry_data: dict[str, Any]) -> ConfigFlowResult:
        """Handle re-authentication when the token has expired."""
        self._reauth_entry = self.hass.config_entries.async_get_entry(
            self.context["entry_id"]
        )
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle re-auth credentials input."""
        errors: dict[str, str] = {}

        if user_input is not None:
            assert self._reauth_entry is not None
            email = self._reauth_entry.data[CONF_EMAIL]
            password = user_input[CONF_PASSWORD]

            session = async_get_clientsession(self.hass)
            api = HoneyInstrumentsApi(session, email, password)

            try:
                access_token = await api.authenticate()
            except HoneyInstrumentsAuthError:
                errors["base"] = "invalid_auth"
            except HoneyInstrumentsApiError:
                errors["base"] = "cannot_connect"
            except Exception:
                LOGGER.exception("Unexpected exception during reauth")
                errors["base"] = "unknown"
            else:
                return self.async_update_reload_and_abort(
                    self._reauth_entry,
                    data={
                        CONF_EMAIL: email,
                        CONF_PASSWORD: password,
                        CONF_ACCESS_TOKEN: access_token,
                    },
                )

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema({vol.Required(CONF_PASSWORD): str}),
            errors=errors,
        )


class HoneyInstrumentsOptionsFlow(OptionsFlow):
    """Options flow for Honey Instruments."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        self._config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage integration options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_interval = self._config_entry.options.get(
            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
        )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_SCAN_INTERVAL, default=current_interval
                    ): NumberSelector(
                        NumberSelectorConfig(
                            mode=NumberSelectorMode.BOX,
                            min=MIN_SCAN_INTERVAL,
                            max=MAX_SCAN_INTERVAL,
                            step=60,
                            unit_of_measurement="s",
                        )
                    ),
                }
            ),
        )
