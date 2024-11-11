from aiogram.fsm.state import StatesGroup, State

class General(StatesGroup):
    template_message = State()
    collect_info_interval = State()
    admin_tg_id = State()
    get_photo = State()
    get_gif = State()

class GroupEdit(StatesGroup):
    group_tg_id = State()
    group_action = State()
    min_amount = State()
    max_amount = State()

class AddressEdit(StatesGroup):
    group_tg_id_add = State()
    group_tg_id_edit = State()
    address_name_add = State()
    address_name_edit = State()
    address = State()
    address_action = State()
