from aiogram import Router, Bot, F
from aiogram.filters import  Command, CommandStart
from utils import General, GroupEdit, AddressEdit
from aiogram.types import Message, InlineKeyboardMarkup
from typing import Optional
from aiogram.fsm.context import FSMContext
import reply
import re
from os import getenv
from dotenv import load_dotenv
import aiohttp
import database
from init import bot
load_dotenv()

import json

def get_admin_list():
    with open('admin_list.json', 'r') as f:
        return json.load(f)

BOT_TOKEN = getenv('BOT_TOKEN')

router = Router()

@router.message(lambda message: message.text and message.text[0] == '@')
async def reg_group_handler(message: Message):
    try:
        admin_list = get_admin_list()
        if message.from_user.id in admin_list:
        
            if (message.chat.type == 'group' or message.chat.type == 'supergroup'):
                bot_info = await bot.get_me()
                
                if f"@{bot_info.username}" == message.text.strip() or f"@{bot_info.username} " == message.text.strip():
                    tg_id = message.chat.id
                    group_name = message.chat.full_name
                    
                    res = await database.reg_group(tg_id, group_name) 
                    if res:
                        await message.answer("Группу успешно привязано к боту.")
                    else:
                        await message.answer("Группа уже привязана к боту.")
    except Exception as err:
        print(f"Error: {err}")

@router.message((F.text == "/start") | (F.text == "Главное меню"))
async def general_menu(message: Message):
    try:
        admin_list = get_admin_list()
        if message.from_user.id in admin_list:

            await message.answer("Главное меню успешно открыто.", reply_markup=await reply.display_general_menu())
    except Exception as err:
        print(err)

@router.message(F.text == "Изменить шаблон сообщений")
async def change_template_message(message: Message, state: FSMContext):
    try:
        admin_list = get_admin_list()
        if message.from_user.id in admin_list:

            config = await database.get_config()
            await message.answer("Введите текст для отправки при рассылке транзакций:\n\n"
                                 "Хэш транзакции: {trans_hash}\n"
                                 "Ссылка на транзакцию: {trans_link}\n"
                                 "Блок транзакции: {trans_block}\n"
                                 "Отправитель: {trans_from}\n"
                                 "Получатель: {trans_to}\n"
                                 "Сумма перевода: {trans_value}\n"
                                 "Сума перевода в ETH: {trans_eth}\n"
                                 "Цена газа: {trans_gas}\n"
                                 "Общая сумма транзакций в группе: {group_trans_sum}\n"
                                 "Время транзакции: {trans_timestamp}\n\n"
                                 "Для добавления тексту стилей используйте HTML тэги:\n\n"
                                 "<b>Жирный</b>\n"
                                 "<i>Курсив</i>\n"
                                 "<u>Подчёркнутый</u>\n"
                                 '<a href="{trans_link}">Гиперссылка</a>\n\n'
                                 f"Текущий текст:\n\n{config.template_message}",
                                  reply_markup=await reply.display_cancel())
            await state.set_state(General.template_message)
    except Exception as err:
        print(err)

@router.message(F.text == "Изменить интервал сбора информации")
async def change_collect_interval(message: Message, state: FSMContext):
    try:
        admin_list = get_admin_list()
        if message.from_user.id in admin_list:

            config = await database.get_config()
            await message.answer(f"Введите интервал сбора информации по транзакциям в минутах в формате От До.\nПример: '5 10'.\nТекущий интервал: {config.info_collect_interval_from} {config.info_collect_interval_to}", reply_markup=await reply.display_cancel())
            await state.set_state(General.collect_info_interval)
    except Exception as err:
        print(err)

@router.message(F.text == "Настройки групп")
async def groups_edit(message: Message, state: FSMContext):
    try:
        admin_list = get_admin_list()
        if message.from_user.id in admin_list:

            groups = await database.get_all_groups()
            await message.answer("Выберите группу для редактирования.\n\nФормат отображения: Название группы | Телеграм ID группы", reply_markup=await reply.display_groups(groups))
            await state.set_state(GroupEdit.group_tg_id)
    except Exception as err:
        print(err)

@router.message(F.text == "Настройки адрессов")
async def addresses_edit(message: Message, state: FSMContext):
    try:
        admin_list = get_admin_list()
        if message.from_user.id in admin_list:

            await message.answer("Выберите действие", reply_markup=await reply.addresses_edit())
    except Exception as err:
        print(err)

@router.message(F.text == "Добавить новый адресс")
async def add_address(message: Message, state: FSMContext):
    try:
        admin_list = get_admin_list()
        if message.from_user.id in admin_list:

            groups = await database.get_all_groups()
            await message.answer("Выберите группу, к которой хотите привязать адресс.\n\nФормат отображения: Название группы | Телеграм ID группы", reply_markup=await reply.display_groups(groups))
            await state.set_state(AddressEdit.group_tg_id_add)
    except Exception as err:
        print(err)

@router.message(F.text == "Редактировать существующий адресс")
async def add_address(message: Message, state: FSMContext):
    try:
        admin_list = get_admin_list()
        if message.from_user.id in admin_list:

            groups = await database.get_all_groups()
            await message.answer("Выберите группу, адресс с которой вы хотите отредактировать.\n\nФормат отображения: Название группы | Телеграм ID группы", reply_markup=await reply.display_groups(groups))
            await state.set_state(AddressEdit.group_tg_id_edit)
    except Exception as err:
        print(err)

@router.message(F.text == "Список админов")
async def admin_list(message: Message, state: FSMContext):
    try:
        admin_list = get_admin_list()
        if message.from_user.id in admin_list:
        
            admins = await database.get_admins()
            await message.answer("Список админов успешно открыт.", reply_markup=await reply.admins_edit(admins))
    except Exception as err:
        print(err)

@router.message(F.text == "Добавить админа")
async def add_admin(message: Message, state: FSMContext):
    try:
        admin_list = get_admin_list()
        if message.from_user.id in admin_list:
        
            await message.answer("Введите ID пользователя.")
            await state.set_state(General.admin_tg_id)
    except Exception as err:
        print(err)

@router.message(F.text.regexp(r"^Удалить админа (\d+)$"))
async def delete_admin(message: Message, state: FSMContext):
    try:
        admin_list = get_admin_list()
        if message.from_user.id in admin_list:

            match = re.match(r"^Удалить админа (\d+)$", message.text)
            if match:
                admin_id = int(match.group(1))
                

                result = await database.remove_admin(admin_id)
                
                if result:
                    await message.answer(f"Админ с ID {admin_id} успешно удален.", reply_markup=await reply.display_general_menu())
                else:
                    await message.answer(f"Не удалось удалить админа с ID {admin_id}. Проверьте правильность ID.", reply_markup=await reply.display_general_menu())
            else:
                await message.answer("Неверный формат. Используйте 'Удалить админа ID'.", reply_markup=await reply.display_general_menu())
    except Exception as err:
        print(err)



@router.message(General.template_message)
async def change_template_message_(message: Message, state: FSMContext):
    try:
        if message.text:
            if message.text == 'Отмена':
                await message.answer("Вы успешно отменили изменение шаблонного сообщения и вернулись в главное меню.", reply_markup=await reply.display_general_menu())
            else:
                try:
                    res = await database.change_template(message.text)
                    if res:
                        formatted_message = message.text.format(
                            trans_hash='0xbb144c5b5b7897fde53b708ca38cedd6eee69c14ebf561018d98247e43c771dd',
                            trans_link='https://etherscan.io/tx/0xbb144c5b5b7897fde53b708ca38cedd6eee69c14ebf561018d98247e43c771dd',
                            trans_block='3434',
                            trans_from='0x4838B106FCe9647Bdf1E7877BF73cE8B0BAD5f97',
                            trans_to='0x4675C7e5BaAFBFFbca748158bEcBA61ef3b0a263',
                            trans_value='434',
                            trans_eth='0.60',
                            trans_gas='0.60',
                            trans_timestamp="2024-06-17 17:06:38",
                            group_trans_sum='19340'
                        )
                        await message.answer(f"Вы успешно изменили шаблонное сообщение на:\n\n{formatted_message}", reply_markup=await reply.display_general_menu(), parse_mode='HTML')
                    else:
                        await message.answer("Произошла ошибка, попробуйте позже.", reply_markup=await reply.display_general_menu())

                    await state.clear()
                except Exception as err:
                    await message.answer(f"Шаблонный текст не был изменён, ошибка:\n\n{err}\n\nПопробуйте ещё раз.")
        else:
            await message.answer("Попробуйте ещё раз, вам необходимо прислать текст.")
    except Exception as err:
        print(err)

@router.message(General.collect_info_interval)
async def change_collect_interval_(message: Message, state: FSMContext):
    try:
        if message.text == 'Отмена':
            await message.answer("Вы успешно отменили изменение интервала сбора информации и вернулись в главное меню.", reply_markup=await reply.display_general_menu())
            await state.clear()
        else:
            args = message.text.split(' ')
            if len(args) == 2 and args[0].isdigit() and args[1].isdigit():
                interval1 = int(args[0])
                interval2 = int(args[1])
                
                res = await database.change_interval(interval1, interval2)
                if res:
                    await message.answer(
                        "Вы успешно изменили интервал и вернулись в главное меню.",
                        reply_markup=await reply.display_general_menu()
                    )
                    await state.clear()
                else:
                    await message.answer(
                        "Произошла ошибка, проверьте правильность ввода.",
                        reply_markup=await reply.display_general_menu()
                    )
                    await state.clear()
            else:
                await message.answer("Введите два числа, разделенных пробелом.")

    except Exception as err:
        print(err)

@router.message(General.admin_tg_id)
async def add_admin_(message: Message, state: FSMContext):
    try:
        if message.text == 'Отмена':
            await message.answer("Вы успешно отменили добавление администратора и вернулись в главное меню.", reply_markup=await reply.display_general_menu())
            await state.clear()
        else:
            if message.text.isdigit():
                res = await database.add_admin(message.text)
                if res:
                    await message.answer("Вы успешно добавили администратора и вернулись в главное меню.", reply_markup=await reply.display_general_menu())
                    await state.clear()
                else:
                    await message.answer("Данный пользователь уже является администратора, введите другой ID.")
            else:
                await message.answer("Введите ID.")
    except Exception as err:
        print(err)

@router.message(GroupEdit.group_tg_id)
async def groups_edit_(message: Message, state: FSMContext):
    try:
        if message.text == 'Отмена':
            await message.answer("Вы успешно отменили редактирование группы и вернулись в главное меню.", reply_markup=await reply.display_general_menu())
            await state.clear()
        else:
            pattern = r"^(?P<group_name>[\w\s]+) \| (?P<group_id>-?\d+)$"
            
            match = re.match(pattern, message.text)
            if match:
                group_name = match.group('group_name')
                await state.update_data(group_tg_id=match.group('group_id'))
                group_info = await database.get_group(match.group('group_id'))
                await message.answer(f"Выберите действие по отношению к группе {group_name}.", reply_markup=await reply.group_edit(group_info))
                await state.set_state(GroupEdit.group_action)
            else:
                await message.answer("Поиск не соответствует формату 'Имя группы | ID группы'")
    except Exception as err:
        print(f"Ошибка: {err}")

@router.message(GroupEdit.group_action)
async def groups_edit_(message: Message, state: FSMContext):
    try:
        if message.text == 'Отмена':
            await message.answer("Вы успешно отменили редактирование группы и вернулись в главное меню.", reply_markup=await reply.display_general_menu())
            await state.clear()
        else:
            data = await state.get_data()
            if message.text == "Отвязать группу":
                await state.clear()
                res = await database.delete_group(data['group_tg_id'])
                if res:
                    await message.answer("Группа успешно отвязана, привязанные кошельки не были удалены, вы можете привязать её обратно без потери данных.", reply_markup=await reply.display_general_menu())
                else:
                    await message.answer("Группу не было отвязано, возможно она уже отвязана.", reply_markup=await reply.display_general_menu())
            elif message.text == "Установить минимальную сумму транзакции":
                group = await database.get_group(data['group_tg_id'])
                await message.answer(f"Введите минимальное значение в долларах для поиска транзакций для адрессов этой группы.\n\nТекущее значение: {group.min_amount}", reply_markup=await reply.display_cancel())
                await state.set_state(GroupEdit.min_amount)
            elif message.text == "Установить максимальную сумму транзакции":
                group = await database.get_group(data['group_tg_id'])
                await message.answer(f"Введите максимальное значение в долларах для поиска транзакций для адрессов этой группы.\n\nТекущее значение: {group.max_amount}", reply_markup=await reply.display_cancel())
                await state.set_state(GroupEdit.max_amount)
            elif message.text == "Деактивировать группу":
                await database.set_group_status(data['group_tg_id'], False)
                await message.answer("Вы успешно деактивировали группу и вернулись в главное меню.", reply_markup=await reply.display_general_menu())
                await state.clear()
            elif message.text == "Активировать группу":
                await database.set_group_status(data['group_tg_id'], True)
                await message.answer("Вы успешно активировали группу и вернулись в главное меню.", reply_markup=await reply.display_general_menu())
                await state.clear()

    except Exception as err:
        print(err)

@router.message(GroupEdit.min_amount)
async def groups_edit_min_(message: Message, state: FSMContext):
    try:
        if message.text == 'Отмена':
            await message.answer("Вы успешно отменили редактирование минимальной суммы и вернулись в главное меню.", reply_markup=await reply.display_general_menu())
            await state.clear()
        else:
            if message.text.isdigit():
                data = await state.get_data()
                res = await database.set_group_amount_for_search('min', data['group_tg_id'], int(message.text) )
                if res:
                    await message.answer("Вы успешно изменили минимальную сумму для поиска транзакций, отправьте максимальное значение:", reply_markup=await reply.display_cancel())
                    await state.set_state(GroupEdit.max_amount)
                else:
                    await message.answer("Произошла ошибка, попробуйте позже.", reply_markup=await reply.display_general_menu())
                    await state.clear()
            else:
                await message.answer("Введите число.")
    except Exception as err:
        print(err)

@router.message(GroupEdit.max_amount)
async def groups_edit_max_(message: Message, state: FSMContext):
    try:
        if message.text == 'Отмена':
            await message.answer("Вы успешно отменили редактирование максимальной суммы и вернулись в главное меню.", reply_markup=await reply.display_general_menu())
            await state.clear()
        else:
            if message.text.isdigit():
                data = await state.get_data()
                res = await database.set_group_amount_for_search('max', data['group_tg_id'], int(message.text) )
                if res:
                    await message.answer("Вы успешно изменили максимальную сумму для поиска транзакций и вернулись в главное меню.", reply_markup=await reply.display_general_menu())
                    await state.clear()
                else:
                    await message.answer("Произошла ошибка, попробуйте позже.", reply_markup=await reply.display_general_menu())
                    await state.clear()
            else:
                await message.answer("Введите число.")
    except Exception as err:
        print(err)


@router.message(AddressEdit.group_tg_id_add)
async def add_address_(message: Message, state: FSMContext):
    try:
        if message.text == 'Отмена':
            await message.answer("Вы успешно отменили привязку адресса и вернулись в главное меню.", reply_markup=await reply.display_general_menu())
            await state.clear()
        else:
            pattern = r"^(?P<group_name>[\w\s]+) \| (?P<group_id>-?\d+)$"

            match = re.match(pattern, message.text)
            if match:
                group_name = match.group('group_name')
                group_id = match.group('group_id')
                
                await state.update_data(group_tg_id_add=group_id)
                
                await message.answer(f"Введите адресс, который желаете привязать к группе {group_name}.")
                await state.set_state(AddressEdit.address_name_add)
            else:
                await message.answer("Поиск не соответствует формату 'Имя группы | ID группы'")
    except Exception as err:
        print(f"Ошибка: {err}")


@router.message(AddressEdit.address_name_add)
async def add_address_name_(message: Message, state: FSMContext):
    try:
        if message.text == 'Отмена':
            await message.answer("Вы успешно отменили привязку адресса и вернулись в главное меню.", reply_markup=await reply.display_general_menu())
            await state.clear()
        else:
            data = await state.get_data()
            res = await database.add_address(message.text, data['group_tg_id_add'])
            if res:
                await message.answer("Вы успешно привязали адресс и вернулись в главное меню.", reply_markup=await reply.display_general_menu())
                await state.clear()
            else:
                await message.answer("Произошла ошибка, попробуйте позже.", reply_markup=await reply.display_general_menu())
                await state.clear()
    except Exception as err:
        print(f"Ошибка: {err}")


@router.message(AddressEdit.group_tg_id_edit)
async def add_address_(message: Message, state: FSMContext):
    try:
        if message.text == 'Отмена':
            await message.answer("Вы успешно отменили редактирование адресса и вернулись в главное меню.", reply_markup=await reply.display_general_menu())
            await state.clear()
        else:
            pattern = r"^(?P<group_name>[\w\s]+) \| (?P<group_id>-?\d+)$"

            match = re.match(pattern, message.text)
            if match:
                group_name = match.group('group_name')
                group_id = match.group('group_id')
                
                await state.update_data(group_tg_id_edit=group_id)
                
                addresses = await database.get_addresses(group_id)
                await message.answer("Выберите адресс, который желаете отредактировать.", reply_markup=await reply.display_addresses(addresses))
                await state.set_state(AddressEdit.address)
            else:
                await message.answer("Поиск не соответствует формату 'Имя группы | ID группы'")
    except Exception as err:
        print(f"Ошибка: {err}")

@router.message(AddressEdit.address)
async def address_edit_(message: Message, state: FSMContext):
    try:
        if message.text == 'Отмена':
            await message.answer("Вы успешно отменили редактирование адресса и вернулись в главное меню.", reply_markup=await reply.display_general_menu())
            await state.clear()
        else:
            data = await state.get_data()
            address_info = await database.get_address(message.text, data['group_tg_id_edit'])
            await message.answer("Выберите действие по отношению к адрессу.", reply_markup=await reply.address_edit(address_info))
            await state.update_data(address=message.text)
            await state.set_state(AddressEdit.address_action)

    except Exception as err:
        await message.answer("Случилась ошибка, скорее всего адресс не найден.", reply_markup=await reply.display_general_menu())
        print(err)

@router.message(AddressEdit.address_action)
async def address_edit_(message: Message, state: FSMContext):
    try:
        if message.text == 'Отмена':
            await message.answer("Вы успешно отменили редактирование адресса и вернулись в главное меню.", reply_markup=await reply.display_general_menu())
            await state.clear()
        else:
            data = await state.get_data()
            if message.text == "Удалить адресс":
                await state.clear()
                res = await database.delete_address(data["group_tg_id_edit"], data["address"])
                if res:
                    await message.answer("Адресс успешно удалён", reply_markup=await reply.display_general_menu())
                else:
                    await message.answer("Адресс не был удалён, возможно он уже удалён.", reply_markup=await reply.display_general_menu())
            elif message.text == "Переименовать адресс":
                await message.answer("Введите новый адресс.", reply_markup=await reply.display_cancel())
                await state.set_state(AddressEdit.address_name_edit)

            elif message.text == "Выключить анализ входящих транзакций":
                res = await database.set_address_to_from(data["address"], data["group_tg_id_edit"], 'to', False)
                if res:
                    await message.answer("Анализ входящих транзакций выключен", reply_markup=await reply.display_general_menu())
                else:
                    await message.answer("Произошла ошибка, попробуйте позже.", reply_markup=await reply.display_general_menu())

            elif message.text == "Включить анализ входящих транзакций":
                res = await database.set_address_to_from(data["address"], data["group_tg_id_edit"], 'to', True)
                if res:
                    await message.answer("Анализ входящих транзакций включен", reply_markup=await reply.display_general_menu())
                else:
                    await message.answer("Произошла ошибка, попробуйте позже.", reply_markup=await reply.display_general_menu())

            elif message.text == "Выключить анализ исходящих транзакций":
                res = await database.set_address_to_from(data["address"], data["group_tg_id_edit"], 'from', False)
                if res:
                    await message.answer("Анализ исходящих транзакций выключен", reply_markup=await reply.display_general_menu())
                else:
                    await message.answer("Произошла ошибка, попробуйте позже.", reply_markup=await reply.display_general_menu())

            elif message.text == "Включить анализ исходящих транзакций":
                res = await database.set_address_to_from(data["address"], data["group_tg_id_edit"], 'from', True)
                if res:
                    await message.answer("Анализ исходящих транзакций включен", reply_markup=await reply.display_general_menu())
                else:
                    await message.answer("Произошла ошибка, попробуйте позже.", reply_markup=await reply.display_general_menu())
    
    except Exception as err:
        print(err)

@router.message(AddressEdit.address_name_edit)
async def address_edit_(message: Message, state: FSMContext):
    try:
        if message.text == 'Отмена':
            await message.answer("Вы успешно отменили редактирование адресса и вернулись в главное меню.", reply_markup=await reply.display_general_menu())
            await state.clear()
        else:
            data = await state.get_data()
            res = await database.rename_address(data['address'], data['group_tg_id_edit'], message.text)
            await state.clear()
            if res:
                await message.answer("Адресс успешно переименован", reply_markup=await reply.display_general_menu())
            else:
                await message.answer("Адресс не был переименован, попробуйте позже.", reply_markup=await reply.display_general_menu())

    except Exception as err:
        print(err)





async def send_message(user: int, text: str, session: Optional[aiohttp.ClientSession] = None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    params = {
        'chat_id': user,
        'text': text,
        'parse_mode': 'HTML'
    }

    if session is None:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params) as response:
                if response.status != 200:
                    print(f"Ошибка отправки сообщения пользователю {user}: {response.status}")
                    response_text = await response.text()
                    print(f"Ответ: {response_text}")
    else:
        async with session.post(url, json=params) as response:
            if response.status != 200:
                print(f"Ошибка отправки сообщения пользователю {user}: {response.status}")
                response_text = await response.text()
                print(f"Ответ: {response_text}")

async def send_notification(template_message, chat_id, trans_hash, trans_link, trans_block, trans_from, trans_to, trans_value, trans_eth, trans_gas, group_trans_sum, trans_timestamp):
    try:
        formatted_message = template_message.format(
            trans_hash=trans_hash,
            trans_link=trans_link,
            trans_block=trans_block,
            trans_from=trans_from,
            trans_to=trans_to,
            trans_value=trans_value,
            trans_eth=trans_eth,
            trans_gas=trans_gas,
            trans_timestamp=trans_timestamp,
            group_trans_sum=group_trans_sum
        )

        formatted_message = f"{'🤑' * (int(trans_value) // 10)}\n\n{formatted_message}"
        
        async with aiohttp.ClientSession() as session:
            await send_message(chat_id, formatted_message, session)
    except Exception as err:
        print(f"Ошибка при отправке сообщения: {err}")
