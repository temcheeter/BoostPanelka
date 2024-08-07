import asyncio
from config import *
from aiogram import Dispatcher, Bot, F
from aiogram.types import Message
from aiogram.filters import CommandStart
from keyboards import main_kb, paginator
from random import choice
from handlers import profile
import callback
import database as db
from test import updater
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.context import FSMContext
from aiogram.fsm.context import StorageKey


bot = Bot(token, default=DefaultBotProperties(parse_mode='HTML'))
dp = Dispatcher()
dp.include_routers(profile.rt, callback.rt)
asyncio.run(db.check_db())


@dp.message(CommandStart())
async def start(msg: Message):
    await msg.answer('Сап, бро🤙. Я бот по smm накрутке. От подписчиков в TikTok до голосов в Telegram) '
                     'Цены чисто символические, кстати можешь чекнуть ❤', reply_markup=main_kb)
    if not await db.get_user_info(msg.from_user.id):
        ref_id = msg.text.split('kentId')[-1]
        if ref_id[0] != '/' and ref_id != msg.from_user.id:
            await db.add_user(msg.from_user.id, 0, 0, ref_id)
        else:
            await db.add_user(msg.from_user.id, 0, 0)


    # await asyncio.sleep(5)
    # await msg.answer('Псс, тут поговаривают, что после 3 покупок ты сможешь стать Смешариком!! Не упусти свой шанс🤩')


@dp.message(F.text == '/admin')
async def admin(msg: Message):
    if msg.from_user.id in admin_id:
        img = choice(admin_gif)
        await msg.answer_animation(img)
    else:
        await msg.answer('Зелен')


@dp.message(F.text == '❤Помощь❤')
async def support(msg: Message):
    await msg.answer_sticker('CAACAgIAAxkBAAOtZmhe2ZwR2Me5Y-4wHeR5FrI155MAAp8VAAJdWchLRA2tcFujbLk1BA')
    await msg.answer('Всегда хотел поговорить с клиентом😁! Расскажи, как ощущения от бота ;) @worker_workaem')


@dp.message(F.text == '👠Услуги👠')
async def support(msg: Message):
    await msg.answer_photo('https://masterpiecer-images.s3.yandex.net/0a6b97ed730b11ee98d5222e7fa838a6:upscaled', reply_markup=await paginator())


@dp.message(F.text == '⤵Домой⤵')
async def to_home(msg: Message='', user_id=0):
    if not user_id:
        user_id = msg.from_user.id
    state_with: FSMContext = FSMContext(
    storage=dp.storage,
    key=StorageKey(
        chat_id=user_id,
        user_id=user_id,
        bot_id=bot.id))
    await state_with.clear()
    await msg.answer('Дом милый дом😊', reply_markup=main_kb)


# @dp.message()
# def sticker(msg: Message):
#     print(msg.sticker.file_id)


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


async def main_wrapper():
    global services
    await asyncio.gather(
        main(),
        updater()
    )


if __name__ == '__main__':
    asyncio.run(main_wrapper())
