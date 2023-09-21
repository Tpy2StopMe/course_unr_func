# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config_data.config import api_token

storage = MemoryStorage()

API_TOKEN = api_token
bot = Bot(token=API_TOKEN)
dispatcher = Dispatcher(bot, storage=storage)
