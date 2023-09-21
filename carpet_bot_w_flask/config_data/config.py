# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

import configparser
from pathlib import Path

config = configparser.ConfigParser()
ini_path = Path(__file__).parent / "carpet_bot.ini"
config.read(ini_path, encoding="utf-8")


api_token = config.get("BOT", "API_TOKEN")
owner_id = config.getint("BOT", "OWNER_ID")

equipments_data = config.get("SHEETS", "EQUIPMENTS_DATA")
services_data = config.get("SHEETS", "SERVICES_DATA")
carpet_images_data = config.get("SHEETS", "CARPET_IMAGES_DATA")
equipments_orders = config.get("SHEETS", "EQUIPMENTS_ORDERS")
services_orders = config.get("SHEETS", "SERVICES_ORDERS")
carpets_orders = config.get("SHEETS", "CARPETS_ORDERS")

spreadsheet_id = config.get("GS_API", "SPREADSHEET_ID")
credentials_path = Path(config.get("GS_API", "CREDENTIALS_PATH"))
