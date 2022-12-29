from aiogram import Dispatcher
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from database.db_connection import cur
from states.polls import Polls



async def cmd_start(msg: Message):

	user_id = msg.from_user.id

	data = cur.execute('SELECT * FROM blacklist')

	banned_users = []
	for user in data:
		banned_users.append(user[1])

	if user_id not in banned_users:
		adult_btn = InlineKeyboardButton(text='Я СТАРШЕ 18 ЛЕТ', callback_data='adult')
		not_adult_btn = InlineKeyboardButton(text='МНЕ ЕЩЕ НЕТ 18', callback_data='not_adult')
		inkb = InlineKeyboardMarkup(row_width=1).add(adult_btn).add(not_adult_btn)
		text_to_send = f'Привет, {msg.from_user.first_name}!\n🔞Подтверди свой возраст🔞'

		await msg.answer(text_to_send, reply_markup=inkb)
		await Polls.start.set()
	else:
		pass



def register_message_handlers(dp: Dispatcher):
	dp.register_message_handler(cmd_start, commands=['start'], state=None)
