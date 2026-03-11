import os
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from handlers.state import adding_file
from handlers.creating import fill_invoice
from context.keyboard import cancel_kb, confirm_kb, services_kb

router = Router()


TEMPLATE_PATH = os.environ.get(
    "INVOICE_TEMPLATE",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "invoice.docx")
)



def extract_value(line: str) -> str:
    """'ИНН: 123456' → '123456',  '123456' → '123456'"""
    if ":" in line:
        return line.split(":", 1)[1].strip()
    return line.strip()



@router.message(Command("start"))
async def global_start(message: Message, state: FSMContext):
    await state.clear()
    from context.keyboard import main_menu_kb
    await message.answer("👋 Главное меню:", reply_markup=main_menu_kb())


@router.message(Command("cancel"))
async def global_cancel(message: Message, state: FSMContext):
    current = await state.get_state()
    if current is None:
        await message.answer("Нечего отменять.")
        return

    step = current.split(":")[-1]


    skip_map = {
        "invoice_number": (
            adding_file.invoice_date, "invoice_number",
            "📅 *Шаг 2/9* — Введите дату счёта (например: 01.01.2025):", "cancel"
        ),
        "invoice_date": (
            adding_file.buyer_req, "invoice_date",
            "🏢 *Шаг 3/9* — Введите реквизиты покупателя.\n\n"
            "`Название орг.\nИНН\nОГРН\nРасчётный счёт\nБанк\nКорр. счёт\nБИК`", "cancel"
        ),
        "buyer_req": (
            adding_file.services, "buyer_req",
            "🛠 *Шаг 4/9* — Добавьте услугу:\n`Название\nЦена`", "services"
        ),
        "contract_number": (
            adding_file.contract_date, "contract_number",
            "📅 *Шаг 6/9* — Введите дату договора:", "cancel"
        ),
    }

    entry = skip_map.get(step)
    if entry is None:
        await message.answer("На этом шаге пропуск недоступен.")
        return

    next_state, field, next_prompt, kb_type = entry

    if field == "buyer_req":
        await state.update_data(
            buyer_org="", buyer_inn="", buyer_ogrn="",
            buyer_account="", buyer_bank="", buyer_correspondent="", buyer_bik="",
            services=[]
        )
    else:
        await state.update_data(**{field: ""})

    await state.set_state(next_state)
    kb = services_kb() if kb_type == "services" else cancel_kb()
    await message.answer(next_prompt, parse_mode="Markdown", reply_markup=kb)



async def start_filling(message_or_cb, state: FSMContext):
    await state.clear()
    await state.set_state(adding_file.invoice_number)
    text = "📄 *Шаг 1/9* — Введите номер счёта:"
    if isinstance(message_or_cb, CallbackQuery):
        await message_or_cb.message.answer(text, parse_mode="Markdown", reply_markup=cancel_kb())
    else:
        await message_or_cb.answer(text, parse_mode="Markdown", reply_markup=cancel_kb())


@router.message(adding_file.invoice_number)
async def get_invoice_number(message: Message, state: FSMContext):
    await state.update_data(invoice_number=message.text.strip())
    await state.set_state(adding_file.invoice_date)
    await message.answer("📅 *Шаг 2/9* — Введите дату счёта (например: 01.01.2025):", parse_mode="Markdown")



@router.message(adding_file.invoice_date)
async def get_invoice_date(message: Message, state: FSMContext):
    await state.update_data(invoice_date=message.text.strip())
    await state.set_state(adding_file.buyer_req)
    await message.answer(
        "🏢 *Шаг 3/9* — Введите реквизиты покупателя.\n\n"
        "Принимается с подписями или без:\n\n"
        "`Название орг.: ООО Ромашка\n"
        "ИНН: 123456789\n"
        "ОГРН: 1234567890123\n"
        "Расчётный счёт: 40702810000000000000\n"
        "Банк: Альфа-Банк\n"
        "Корр. счёт: 30101810200000000000\n"
        "БИК: 044525593`",
        parse_mode="Markdown"
    )



@router.message(adding_file.buyer_req)
async def get_buyer_req(message: Message, state: FSMContext):
    lines = [l.strip() for l in message.text.strip().splitlines() if l.strip()]
    if len(lines) < 7:
        await message.answer(
            "⚠️ Нужно 7 строк. Попробуйте ещё раз:\n\n"
            "`Название орг.\nИНН\nОГРН\nРасчётный счёт\nБанк\nКорр. счёт\nБИК`",
            parse_mode="Markdown"
        )
        return

    values = [extract_value(l) for l in lines]

    await state.update_data(
        buyer_org=values[0],
        buyer_inn=values[1],
        buyer_ogrn=values[2],
        buyer_account=values[3],
        buyer_bank=values[4],
        buyer_correspondent=values[5],
        buyer_bik=values[6],
        services=[]
    )
    await state.set_state(adding_file.services)
    await message.answer(
        "🛠 *Шаг 4/9* — Добавьте услугу в формате:\n\n"
        "`Название услуги\nЦена (число)`",
        parse_mode="Markdown",
        reply_markup=services_kb()
    )


@router.message(adding_file.services)
async def get_service(message: Message, state: FSMContext):
    lines = [l.strip() for l in message.text.strip().splitlines() if l.strip()]
    if len(lines) < 2:
        await message.answer(
            "⚠️ Нужно 2 строки:\n`Название\nЦена`",
            parse_mode="Markdown"
        )
        return

    try:
        price = float(lines[1].replace(",", "."))
    except ValueError:
        await message.answer("⚠️ Цена — число (например 1500.00).")
        return

    data = await state.get_data()
    services = data.get("services", [])
    services.append({"name": lines[0], "price": price, "quantity": 1, "unit": "шт", "vat": "без НДС"})
    await state.update_data(services=services)
    await message.answer(
        f"✅ Услуга добавлена ({len(services)} шт.). Добавить ещё или завершить?",
        reply_markup=services_kb()
    )


@router.callback_query(F.data == "add_more_service", adding_file.services)
async def cb_add_more(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "🛠 Введите следующую услугу:\n`Название\nЦена`",
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data == "done_services", adding_file.services)
async def cb_done_services(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if not data.get("services"):
        await callback.message.answer("⚠️ Добавьте хотя бы одну услугу.")
        await callback.answer()
        return
    await state.set_state(adding_file.contract_number)
    await callback.message.answer("📋 *Шаг 5/9* — Введите номер договора:", parse_mode="Markdown")
    await callback.answer()



@router.message(adding_file.contract_number)
async def get_contract_number(message: Message, state: FSMContext):
    await state.update_data(contract_number=message.text.strip())
    await state.set_state(adding_file.contract_date)
    await message.answer("📅 *Шаг 6/9* — Введите дату договора (например: 01.01.2025):", parse_mode="Markdown")



@router.message(adding_file.contract_date)
async def get_contract_date(message: Message, state: FSMContext):
    await state.update_data(contract_date=message.text.strip())
    data = await state.get_data()

    services_text = "\n".join(
        f"  {i+1}. {s['name']} — {s['price']} × {s['quantity']}"
        for i, s in enumerate(data.get("services", []))
    )
    summary = (
        f"📝 *Проверьте данные:*\n\n"
        f"🔢 Счёт № `{data.get('invoice_number')}` от `{data.get('invoice_date')}`\n\n"
        f"🏢 *Покупатель:* {data.get('buyer_org')}\n"
        f"  ИНН: {data.get('buyer_inn')}\n"
        f"  ОГРН: {data.get('buyer_ogrn')}\n"
        f"  Р/С: {data.get('buyer_account')}\n"
        f"  Банк: {data.get('buyer_bank')}\n"
        f"  К/С: {data.get('buyer_correspondent')}\n"
        f"  БИК: {data.get('buyer_bik')}\n\n"
        f"🛠 *Услуги:*\n{services_text}\n\n"
        f"📋 Договор № `{data.get('contract_number')}` от `{data.get('contract_date')}`"
    )
    await message.answer(summary, parse_mode="Markdown", reply_markup=confirm_kb())


@router.callback_query(F.data == "confirm_invoice")
async def cb_confirm(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await state.clear()

    if not os.path.exists(TEMPLATE_PATH):
        await callback.message.answer(
            f"❌ Шаблон не найден:\n`{TEMPLATE_PATH}`\n\n"
            "Положите `invoice.docx` рядом с `creating.py` "
            "или задайте переменную окружения `INVOICE_TEMPLATE`.",
            parse_mode="Markdown"
        )
        await callback.answer()
        return

    import tempfile
    import subprocess

    tmp_dir = tempfile.mkdtemp()
    docx_path = os.path.join(tmp_dir, f"invoice_{callback.from_user.id}.docx")
    pdf_path  = os.path.join(tmp_dir, f"invoice_{callback.from_user.id}.pdf")

    def cleanup():

        for p in (docx_path, pdf_path):
            try:
                if os.path.exists(p):
                    os.remove(p)
            except Exception:
                pass
        try:
            os.rmdir(tmp_dir)
        except Exception:
            pass


    try:
        fill_invoice(TEMPLATE_PATH, docx_path, data)
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        cleanup()
        await callback.message.answer(
            f"❌ Ошибка при заполнении шаблона:\n`{e}`\n\n`{tb[-600:]}`",
            parse_mode="Markdown"
        )
        await callback.answer()
        return


    try:
        result = subprocess.run(
            [
                "libreoffice", "--headless", "--convert-to", "pdf",
                "--outdir", tmp_dir, docx_path
            ],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0 or not os.path.exists(pdf_path):
            raise RuntimeError(result.stderr or "LibreOffice вернул пустой результат")
    except FileNotFoundError:
        cleanup()
        await callback.message.answer(
            "❌ LibreOffice не найден.\n\n"
            "Локально: установите LibreOffice и убедитесь, что `libreoffice` доступен в PATH.\n"
            "В Docker: используйте образ с LibreOffice (см. Dockerfile).",
            parse_mode="Markdown"
        )
        await callback.answer()
        return
    except Exception as e:
        cleanup()
        await callback.message.answer(f"❌ Ошибка конвертации в PDF:\n`{e}`", parse_mode="Markdown")
        await callback.answer()
        return


    try:
        document = FSInputFile(pdf_path, filename="invoice.pdf")
        await callback.message.answer_document(document=document, caption="✅ Счёт сформирован!")
    except Exception as e:
        await callback.message.answer(f"❌ Ошибка при отправке файла:\n`{e}`", parse_mode="Markdown")
    finally:
        cleanup()

    await callback.answer()


@router.callback_query(F.data == "cancel_invoice")
async def cb_cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    from context.keyboard import main_menu_kb
    await callback.message.answer("❌ Заполнение отменено.", reply_markup=main_menu_kb())
    await callback.answer()