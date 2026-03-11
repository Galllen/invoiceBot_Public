from aiogram.fsm.state import StatesGroup, State


class adding_file(StatesGroup):
    invoice_number = State()
    invoice_date = State()
    buyer_req = State()
    services = State()
    contract_number = State()
    contract_date = State()

