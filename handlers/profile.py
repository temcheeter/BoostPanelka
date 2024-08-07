from aiogram.types import Message
from aiogram import Router, F
from keyboards import profile_kb
import database as db


rt = Router()


@rt.message(F.text == '🤳Профиль🤳')
async def profile(msg: Message):
     user_id = msg.from_user.id
     user_info = await db.get_user_info(user_id)
     orders = await db.get_orders(user_id)
     active_orders, closed_orders = 0, 0
     try:
          for i in orders:
               if i[4] == 1:
                    active_orders += 1
               else:
                    closed_orders += 1
     except: pass
     await msg.answer(f'''
👶 Имя: {msg.from_user.first_name}
🧿 ID: {user_id}
🎁 Активных заказов: {active_orders}
🛒 Заказов закрыто: {closed_orders}
💲 Баланс: {user_info[-1]}
''', reply_markup=await profile_kb())