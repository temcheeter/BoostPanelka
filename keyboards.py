from aiogram.utils.keyboard import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardButton,
    InlineKeyboardBuilder
)
from aiogram.filters.callback_data import CallbackData
from api import get_services, get_service_name

# services = ('Telegram', 'TikTok', 'YouTube', 'Instagram', 'VK', 'Twitch', 'Spotify', 'Twitter', 'Facebook', 'Whatsapp', 'Discord', 'Kick')


main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='👠Услуги👠')
        ],
        [
            KeyboardButton(text='🤳Профиль🤳')
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder='мейн меню)'
)


home_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='⤵Домой⤵')
        ]
    ],
    resize_keyboard=True,
)


async def profile_kb():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='💰Пополнить баланс💰', callback_data='top_up'))
    builder.row(InlineKeyboardButton(text='🤑Реферальная система🤑', callback_data='referal_system'))
    builder.row(InlineKeyboardButton(text='🧮Ордеры🧮', callback_data='orders'))
    return builder.as_markup()


class Pagination(CallbackData, prefix='pag'):
    action: str
    page: int
    current_level: int
    condition: str


class Services(CallbackData, prefix='srvc'):
    current_level: int
    condition: str

class Orders(CallbackData, prefix='ord'):
    level: int


async def anigilator(service: str):
    while len(service.encode()) > 57:
        service = service[:-2]
    return service


async def paginator(page: int = 0, condition: str = '', current_level: int = 0):
    start_offset = page * 4
    limit = 4
    builder = InlineKeyboardBuilder()
    end_offset = start_offset + limit
    services = await get_services(current_level, condition)
    for service in services[start_offset:end_offset]:
        name = await anigilator(service)
        text = service
        builder.row(
            InlineKeyboardButton(text=text, callback_data=Services(current_level=current_level + 1, condition=name).pack()),
            width=2
        )
    buttons_row = []
    if page > 0:  # Проверка, что страница не первая
        buttons_row.append(InlineKeyboardButton(text="⬅", callback_data=Pagination(action="prev", page=page - 1, current_level=current_level, condition=condition[:25]).pack()))  # Добавление кнопки "назад"
    else:
        if len(services) / 4 == len(services) // 4:
            page_num = len(services) // 4 - 1
        else:
            page_num = len(services) // 4
        buttons_row.append(InlineKeyboardButton(text="⬅", callback_data=Pagination(action="prev", page=page_num, current_level=current_level, condition=condition[:25]).pack()))  # На последнюю страницу
    if end_offset < len(services):  # Проверка, что ещё есть услуги для следующей страницы
        buttons_row.append(InlineKeyboardButton(text="➡", callback_data=Pagination(action="next", page=page + 1, current_level=current_level, condition=condition[:25]).pack()))  # Добавление кнопки "вперед"
    else:  # Если пользователи закончились
        buttons_row.append(InlineKeyboardButton(text="➡", callback_data=Pagination(action="next", page=0, current_level=current_level, condition=condition[:25]).pack()))  # Возвращение на первую страницу
    builder.row(*buttons_row)
    builder.row(InlineKeyboardButton(text='🔙 Назад', callback_data=Pagination(action='cancel', page=0, current_level=0, condition=condition[:25]).pack()))
    return builder.as_markup()


async def pre_buy_kb(id):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='💍Купить', callback_data=f'buy_{id}'))
    builder.row(InlineKeyboardButton(text='Спросить у поддержки🗝', callback_data='support'))
    builder.row(InlineKeyboardButton(text='🔙 Назад', callback_data=Pagination(action='cancel', page=0, current_level=0, condition='').pack()))
    return builder.as_markup()



async def ready_to_buy():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='✅Подтверждаю покупку', callback_data='ready_to_buy1'))
    return builder.as_markup()


# async def services1_kb():
#     services_keyboard = InlineKeyboardBuilder(
#
#     )


# while True:
#     kb = services1_kb()
#     asyncio.sleep(10)