from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from context.message import ans
from context.keyboard import main_menu_kb, cancel_kb

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()   # сбрасываем FSM при /start
    await message.answer(
        text="👋 Добро пожаловать!\n\nВыберите действие:",
        reply_markup=main_menu_kb()
    )


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text=ans.cancel or "❌ Действие отменено.",
        reply_markup=main_menu_kb()
    )