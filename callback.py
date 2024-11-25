from aiogram.types import CallbackQuery, Message
from aiogram import Router, F
import keyboards
from keyboards import Pagination, paginator, Services, pre_buy_kb, ready_to_buy, home_kb, orders_kb, main_kb
from contextlib import suppress
from aiogram.exceptions import TelegramBadRequest
from api import get_services, get_fullname, get_info_id, make_order, get_order_info, get_orders_info, cancill
from aiogram.types import InputMediaPhoto as IMP, URLInputFile
import database as db
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from decimal import Decimal as dec


rt = Router()


# Обработка пагинации
@rt.callback_query(Pagination.filter())
async def pagination_handler(call: CallbackQuery, callback_data: Pagination):
    page = callback_data.page
    current_level = callback_data.current_level
    condition = callback_data.condition
    action = callback_data.action
    if action == 'cancel':
        with suppress(TelegramBadRequest):
            input_photo = URLInputFile(url='https://masterpiecer-images.s3.yandex.net/0a6b97ed730b11ee98d5222e7fa838a6:upscaled')
            img = IMP(media=input_photo)
            await call.message.edit_media(media=img, reply_markup=await paginator(page=page, current_level=current_level, condition=condition))
    else:
        with suppress(TelegramBadRequest):
            await call.message.edit_reply_markup(reply_markup=await paginator(page=page, current_level=current_level, condition=condition))


# Обработка нажатия кнопки в "Услуги"
@rt.callback_query(Services.filter())
async def services_handler(call: CallbackQuery, callback_data: Services):
    current_level = callback_data.current_level
    condition = callback_data.condition
    if current_level == 3:
        full_name = await get_fullname(condition)
        service_id = await get_services(4, full_name)
        txt = await get_services(3, full_name)
        await call.answer(full_name)
        input_photo = URLInputFile(url='https://masterpiecer-images.s3.yandex.net/6de65abc763c11ee9986baea8797b5f2:upscaled')
        img = IMP(media=input_photo, caption=txt, parse_mode='HTML')
        await call.message.edit_media(img, reply_markup=await pre_buy_kb(service_id))
    else:
        if current_level == 1:
            push_up = await get_fullname(condition, 'network')
        else:
            push_up = await get_fullname(condition, 'category')
        await call.answer(push_up)
        with suppress(TelegramBadRequest):
            await call.message.edit_reply_markup(reply_markup=await paginator(current_level=current_level, condition=condition))


@rt.callback_query(F.data == 'referal_system')
async def referal_system_menu(call: CallbackQuery):
    txt = ('Реферальная система очень проста.🎃\nТы получаешь 5 % с каждого пополнения счёта от рефералов. Этот кэш прилетает тебе '
           'мгновенно на твой счёт.👛 Ограничений никаких нет, можешь сразу всё потратить, а можешь копить до лучших времён!🎱\n'
           'Твоя персональная ссылка:')
    await call.message.answer(txt)
    await call.message.answer(f'`https://t.me/Boost_Panelka_BOT?start=kentId{call.from_user.id}`', parse_mode='MARKDOWN')

# orders management
@rt.callback_query(F.data == 'orders')
async def orders(call: CallbackQuery, state: FSMContext):
    orders_ = await db.get_orders()
    orders_info = await get_orders_info(orders_)
    await db.update_orders(orders_info)
    user_orders = await db.get_orders(call.from_user.id)
    txt = ''
    for order in user_orders:
        edit_txt = f'''
ID: ```{order[2]}```
Стоимость: {order[3]}
Кол-во: {order[4]}
Статус: {order[5]}
=======================
'''
        txt += edit_txt
    await call.message.answer(txt, parse_mode='MARKDOWN')
    await call.message.answer('Введите ID заказа для взаимодействия:', reply_markup=home_kb)
    await state.set_state(Form.orders)


@rt.callback_query(F.data.startswith('refill'))
async def order_refill(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    data = await state.get_data()
    order_id = data['orders']
    response = await cancill(order_id, True)
    if response:
        await call.message.answer('Да здравствует рефилл!', reply_markup=main_kb)


@rt.callback_query(F.data.startswith('refill'))
async def order_refill(call: CallbackQuery):
    user_id = call.from_user.id
    order_id = call.data.split('_')[1]
    response = await cancill(order_id, True)
    if response:
        await call.message.answer('Да здравствует рефилл!', reply_markup=main_kb)
    else:
        await call.message.answer('Ошибочка. Почему - не знаю(')


@rt.callback_query(F.data.startswith('cancel'))
async def order_refill(call: CallbackQuery):
    user_id = call.from_user.id
    order_id = call.data.split('_')[1]
    response = await cancill(order_id, False)
    if response:
        await call.message.answer('Да здравствует отмена!', reply_markup=main_kb)
    else:
        await call.message.answer('Ошибочка. Почему - не знаю(')


@rt.callback_query(F.data == 'support')
async def support(call: CallbackQuery):
    await call.message.answer_sticker('CAACAgIAAxkBAAOtZmhe2ZwR2Me5Y-4wHeR5FrI155MAAp8VAAJdWchLRA2tcFujbLk1BA')
    await call.message.answer('Всегда хотел поговорить с клиентом😁! Расскажи, как ощущения от бота ;) @worker_workaem', parse_mode=None)


@rt.callback_query(F.data == 'top_up')
async def top_up(call: CallbackQuery, state: FSMContext):
    await state.set_state(Form.payment)
    await call.message.answer('На какую сумму вы хотите пополнить баланс(рублей)?')


@rt.callback_query(F.data == 'home')
async def to_home(call: CallbackQuery):
    await call.message.answer('Дом милый дом😊', reply_markup=main_kb)

class Form(StatesGroup):
    wallet = State()
    id = State()
    price = State()
    min = State()
    max = State()
    name = State()
    quantity = State()
    link = State()
    promo_info = State()
    purchase_info = State()
    payment = State()
    deal_done = State()
    orders = State()
    order_action = State()


@rt.callback_query(F.data.startswith('buy_'))
async def buy_handler(call: CallbackQuery, state: FSMContext):
    user_info = await db.get_user_info(call.from_user.id)
    wallet = user_info[-1]
    service_id = call.data.split('_')[1]
    info = await get_info_id(service_id)
    await state.update_data(id=service_id, price=info[0], name=info[1], wallet=wallet, min=info[2], max=info[3])
    await state.set_state(Form.quantity)
    await call.message.answer('Окей, введи количество💫:', reply_markup=home_kb)


@rt.message(Form.quantity)
async def form_quantity(msg: Message, state: FSMContext):
    if msg.text.isdigit():
        data = await state.get_data()
        if data['min'] <= int(msg.text) <= data['max']:
            await state.update_data(quantity=msg.text)
            await state.set_state(Form.link)
            await msg.answer('Теперь ссылку:', reply_markup=home_kb)
            checks = await db.get_checks(msg.from_user.id)
            if checks:
                for check in checks[0]:
                    if check[2] == data['id']:
                        await state.set_state(Form.promo_info)
                        break
        else:
            await msg.answer('Неверное количество, введите снова', reply_markup=home_kb)
    else:
        await msg.answer('Неверное количество, введите снова', reply_markup=home_kb)


@rt.message(Form.link)
async def form_link(msg: Message, state: FSMContext):
    if 'https://' in msg.text or '.ru' in msg.text or '.com' in msg.text or 't.me/' in msg.text:
        await state.update_data(link=msg.text)
        checks = await db.get_checks(msg.from_user.id)
        data = await state.get_data()
        cost = dec(str(data['price'])) * int(data['quantity'])
        result_cost = cost
        promo = 'ноуп'
        if checks:
            for check in checks:
                if check[2] == data['id']:
                    promo = f'При заказе от {check[4]} получаете халявы в кол-ве {check[5]}'
                    cost = dec(str(data['price'])) * data['quantity']
                    result_cost = dec(str(data['price'])) * (data['quantity'] - check[5])
                    break
        cost.normalize()
        result_cost.normalize()
        txt = f'''
📝Название: {data['name']}
📊Кол-во: {data['quantity']}
💸Стоимость: {cost}
📑Промокод: {promo}
💵Итоговая стоимость: {result_cost}
'''
        await msg.answer(txt, reply_markup=await ready_to_buy())
    else:
        await msg.answer('Неверная ссылка', reply_markup=home_kb)


@rt.callback_query(F.data == 'ready_to_buy1')
async def ready_to_buy1(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if dec(str(data['wallet'])) > int(data['quantity']) * dec(str(data['price'])):
        await state.clear()
        response = await make_order(data['id'], data['link'], data['quantity'])
        print(response)
        order_info = await get_order_info(response['order'])
        print(order_info)
        print(order_info['charge'])
        await db.add_order(call.from_user.id, response['order'], data['name'], float(order_info['charge']) * 2, data['quantity'], order_info['status'], data['id'])
    else:
        await call.message.answer(f'На вашем балансе недостаточно средств🤷‍♂️‍. На какую сумму вы хотите пополнить баланс(число)?', reply_markup=home_kb)
        await state.set_state(Form.payment)


@rt.message(Form.payment)
async def form_payment(msg: Message, state: FSMContext):
    amount = msg.text
    if amount.isdigit():
        await msg.answer(
            f'Пришлите этот текст сюда - [@worker_workaem](https://t.me/worker_workaem)\n'
            f'`Ку👋! Хочу пополнить баланс в Boost Panelka на сумму {amount} рублей!'
            f' Мой user id - {msg.from_user.id}`',
            parse_mode='MARKDOWN', reply_markup=home_kb)
        await state.clear()
    else:
        await msg.answer('Число нужно, написано же🤦‍♂️', reply_markup=home_kb)


@rt.message(Form.orders)
async def form_orders(msg: Message, state: FSMContext):
    user_orders = await db.get_orders(msg.from_user.id)
    success = False
    for order in user_orders:
        if order[1] == msg.text:
            await msg.answer('Что сделать с заказом:', reply_markup=await orders_kb(msg.text))
            success = True
            await state.clear()
            break
    if not success:
        await msg.answer('Ордер не найден(', reply_markup=main_kb)
        await state.clear()





# @rt.message(Form.required_wallet)
# async def form_wallet(msg: Message, state: FSMContext):
#     user_info = db.get_user_info(msg.from_user.id)
#     if user_info[-1]