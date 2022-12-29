from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from config.consts import TG_BOT_TOKEN



storage = MemoryStorage()

bot = Bot(token=TG_BOT_TOKEN)  # type: ignore
dp = Dispatcher(bot, storage=storage)