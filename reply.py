from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


async def display_general_menu():
    general_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Изменить шаблон сообщений"),
                KeyboardButton(text="Список админов")
            ],
            [
                KeyboardButton(text="Изменить интервал сбора информации"),
                KeyboardButton(text="Настройки адрессов"),
                KeyboardButton(text="Настройки групп")
            ],
        ],
        resize_keyboard=True
    )

    return general_keyboard

async def admins_edit(admins):
    try:
        builder = ReplyKeyboardBuilder()
        
        builder.row(KeyboardButton(text="Главное меню"))
        builder.row(KeyboardButton(text="Добавить админа"))

        row_buttons = []
        for admin in admins:
            button_text = f"Удалить админа {admin.tg_id}"
            row_buttons.append(KeyboardButton(text=button_text))
            
            if len(row_buttons) == 2:
                builder.row(*row_buttons)
                row_buttons = []
        
        if row_buttons:
            builder.row(*row_buttons)

        return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)
    
    except Exception as err:
        print(err)
        return builder.as_markup()

async def display_cancel():
    general_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Отмена")
            ],
        ],
        resize_keyboard=True
    )

    return general_keyboard



async def display_groups(groups):
    try:
        builder = ReplyKeyboardBuilder()
        
        builder.row(KeyboardButton(text="Отмена"))

        row_buttons = []
        for group in groups:
            button_text = f"{group.name} | {group.tg_id}"
            row_buttons.append(KeyboardButton(text=button_text))
            
            if len(row_buttons) == 2:
                builder.row(*row_buttons)
                row_buttons = []
        
        if row_buttons:
            builder.row(*row_buttons)

        return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)
    
    except Exception as err:
        print(err)
        return builder.as_markup()
    
async def display_addresses(addresses):
    try:
        builder = ReplyKeyboardBuilder()
        
        builder.row(KeyboardButton(text="Отмена"))

        row_buttons = []
        for address in addresses:
            button_text = address
            row_buttons.append(KeyboardButton(text=button_text))
            
            if len(row_buttons) == 2:
                builder.row(*row_buttons)
                row_buttons = []
        
        if row_buttons:
            builder.row(*row_buttons)

        return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)
    
    except Exception as err:
        print(err)
        return builder.as_markup()


async def group_edit(group):
    group_status_text = "Деактивировать группу" if group.status else "Активировать группу"
    general_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Отмена")
            ],
            [
                KeyboardButton(text="Отвязать группу"),
                KeyboardButton(text=group_status_text)
            ],
            [
                KeyboardButton(text="Установить минимальную сумму транзакции"),
                KeyboardButton(text="Установить максимальную сумму транзакции")
            ],
        ],
        resize_keyboard=True
    )

    return general_keyboard

async def addresses_edit():
    general_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Главное меню")
            ],
            [
                KeyboardButton(text="Добавить новый адресс"),
                KeyboardButton(text="Редактировать существующий адресс")
            ],
        ],
        resize_keyboard=True
    )

    return general_keyboard

async def address_edit(address):
    incoming_text = "Выключить анализ входящих транзакций" if address.transactions_to else "Включить анализ входящих транзакций"
    outgoing_text = "Выключить анализ исходящих транзакций" if address.transactions_from else "Включить анализ исходящих транзакций"
    
    general_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Отмена")
            ],
            [
                KeyboardButton(text="Переименовать адресс"),
                KeyboardButton(text="Удалить адресс")
            ],
            [
                KeyboardButton(text=incoming_text),
                KeyboardButton(text=outgoing_text)
            ]
        ],
        resize_keyboard=True
    )

    return general_keyboard