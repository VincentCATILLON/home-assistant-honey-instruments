from logging import Logger, getLogger

from homeassistant.const import Platform

LOGGER: Logger = getLogger(__package__)

DOMAIN = "honey_instruments"
NAME = "Honey Instruments"
MANUFACTURER = "Honey Instruments"
VERSION = "1.0.0"

PLATFORMS: list[Platform] = [Platform.SENSOR]

API_BASE_URL = "https://api.honeyinstruments.com"
API_LOGIN_ENDPOINT = "/v1/login"
API_DEVICES_ENDPOINT = "/v1/devices"

CONF_EMAIL = "email"
CONF_PASSWORD = "password"
CONF_ACCESS_TOKEN = "access_token"
CONF_SCAN_INTERVAL = "scan_interval"

DEFAULT_SCAN_INTERVAL = 3600
MIN_SCAN_INTERVAL = 600
MAX_SCAN_INTERVAL = 86400

VERSION_MAP = {0: "Sigfox", 1: "LoRa", 2: "Satellite"}
