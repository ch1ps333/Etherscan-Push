from aiogram import Bot, Dispatcher
from os import getenv
from dotenv import load_dotenv

load_dotenv()

bot = Bot(getenv('BOT_TOKEN'))
dp = Dispatcher()