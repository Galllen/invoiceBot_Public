from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from handlers.pulling import start_filling

router = Router()


@router.callback_query(F.data == "file")
async def cb_file(callback: CallbackQuery, state: FSMContext):
    await start_filling(callback, state)
    await callback.answer()


@router.callback_query(F.data == "help")
async def cb_help(callback: CallbackQuery):
    await callback.message.answer(
        "ℹ️ *Помощь*\n\n"
        "Этот бот создаёт счёт на оплату в формате .docx.\n\n"
        "Нажмите *Заполнить файл* и следуйте инструкциям. "
        "В любой момент можно нажать /cancel для отмены.",
        parse_mode="Markdown"
    )
    await callback.answer()