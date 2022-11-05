from aiogram import Dispatcher
from aiogram.types import CallbackQuery, \
						InlineKeyboardMarkup, InlineKeyboardButton

from config.bot_exec import bot
from database.db_connection import conn, cur

import random



async def adult(call: CallbackQuery):
	await call.message.delete()

	start_btn = InlineKeyboardButton(text='НАЧАТЬ', callback_data='start_quiz')
	rules_btn = InlineKeyboardButton(text='ПРАВИЛА', callback_data='rules')
	inkb = InlineKeyboardMarkup(row_width=1).add(start_btn).add(rules_btn)
	text_to_send = 'Уже знаешь правила? Тогда начинай!'

	await bot.send_message(chat_id=call.from_user.id, text=text_to_send, reply_markup=inkb)


async def not_adult(call: CallbackQuery):
	username = call.from_user.username

	cur.execute(f"INSERT INTO blacklist(username) VALUES('{username}')")
	conn.commit()
	
	await call.answer('Тебе сюда нельзя((', show_alert=True)
	await call.message.delete()


async def start_quiz(call: CallbackQuery):

	await call.answer('Начинаем викторину!')
	await call.message.delete()


	username = call.from_user.username

	data = cur.execute('SELECT * FROM questions')

	questions = []
	for value in data:
		questions.append(str(value))

	random.shuffle(questions)

	while len(questions) > 7:
		questions.pop()
	
	q_sql = ', '.join(questions)

	cur.execute(f'DROP TABLE IF EXISTS {username}')
	cur.execute(f'CREATE TABLE IF NOT EXISTS {username}(id INTEGER, question TEXT, answer_1 TEXT, answer_2 TEXT, answer_3 TEXT, answer_4 TEXT, correct_answer INTEGER, explanation TEXT)')
	cur.execute(f'INSERT INTO {username} VALUES{q_sql}')
	conn.commit()

	questions = []
	data = cur.execute(f'SELECT * FROM {username}')
	for value in data:
		questions.append(value)

	await call.message.answer_poll(
		question=questions[0][1],
		options=[questions[0][2], questions[0][3], questions[0][4], questions[0][5]],
		type='quiz',
		correct_option_id=questions[0][6],
		is_anonymous=False,
		explanation=questions[0][7]
	)


async def rules(call: CallbackQuery):
	await call.message.delete()

	data = cur.execute('SELECT * FROM rules')
	rules = []
	for rule in data:
		rules.append(rule)

	start_btn = InlineKeyboardButton(text='НАЧАТЬ', callback_data='start_quiz')
	rules_btn = InlineKeyboardButton(text='ПРОЧИТАТЬ ЕЩЁ РАЗ', callback_data='rules')
	inkb = InlineKeyboardMarkup(row_width=1).add(start_btn).add(rules_btn)
	text_to_send = rules[0][0]

	await bot.send_message(chat_id=call.from_user.id, text=text_to_send, reply_markup=inkb)



def register_callback_handlers(dp: Dispatcher):
	dp.register_callback_query_handler(adult, text='adult')
	dp.register_callback_query_handler(not_adult, text='not_adult')
	dp.register_callback_query_handler(start_quiz, text='start_quiz')
	dp.register_callback_query_handler(rules, text='rules')
