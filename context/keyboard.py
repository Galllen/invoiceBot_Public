from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton
)


def main_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📄 Заполнить файл", callback_data="file")],
        [InlineKeyboardButton(text="❓ Помощь",          callback_data="help")],
    ])


def cancel_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="/start")],
            [KeyboardButton(text="/cancel")],
        ],
        resize_keyboard=True
    )


def services_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить ещё услугу", callback_data="add_more_service")],
        [InlineKeyboardButton(text="✅ Завершить добавление", callback_data="done_services")],
    ])


def confirm_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Подтвердить и создать счёт", callback_data="confirm_invoice")],
        [InlineKeyboardButton(text="❌ Отменить",                   callback_data="cancel_invoice")],
    ])