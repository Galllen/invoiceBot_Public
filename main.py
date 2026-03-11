import asyncio
import logging

from aiogram import Dispatcher, Router, Bot
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command
from aiogram.types import Message

from context.start import router as rt_start
from context.keyboard import main_menu_kb
from handlers.pulling import router as rt_pulling

from config import config

rout = Router()


@rout.message(Command("cancel"))
async def cmd_cancel(message: Message):
    await message.answer("❌ Действие отменено. Нажмите /start.")


async def main():
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=config.bot_token)

    stor = MemoryStorage()
    dp = Dispatcher(storage=stor)

    print("Bot starting...")


    dp.include_router(rt_pulling)
    dp.include_router(rt_start)
    dp.include_router(rout)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())