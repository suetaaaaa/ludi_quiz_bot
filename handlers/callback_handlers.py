import random

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import (CallbackQuery, InlineKeyboardButton,
                           InlineKeyboardMarkup)

from config.bot_exec import bot
from database.db_connection import conn, cur
from states.polls import Polls



async def select_all_questions(user_id):
	cur.execute(f'CREATE TABLE user_{user_id}(id INTEGER, question TEXT, answer_1 TEXT, answer_2 TEXT, answer_3 TEXT, answer_4 TEXT, correct_answer INTEGER, explanation TEXT)')
	conn.commit()

	data = cur.execute('SELECT * FROM questions')
	questions = []
	for value in data:
		questions.append(str(value))
	random.shuffle(questions)
	q_sql = ', '.join(questions)

	cur.execute(f'INSERT INTO user_{user_id} VALUES{q_sql}')
	conn.commit()
	cur.execute(f'CREATE TABLE quiz_{user_id} AS SELECT * FROM user_{user_id} LIMIT 7')
	conn.commit()

	data = cur.execute(f'SELECT * FROM quiz_{user_id}')
	questions = []
	for value in data:
		questions.append(value)
	
	return questions


async def adult(call: CallbackQuery):
	await call.message.delete()

	user_id = call.from_user.id

	start_btn = InlineKeyboardButton(text='НАЧАТЬ', callback_data='start_quiz')
	rules_btn = InlineKeyboardButton(text='ПРАВИЛА', callback_data='rules')
	inkb = InlineKeyboardMarkup(row_width=1).add(start_btn).add(rules_btn)
	text_to_send = 'Уже знаешь правила? Тогда начинай!'

	await bot.send_message(chat_id=user_id, text=text_to_send, reply_markup=inkb)


async def not_adult(call: CallbackQuery):
	user_id = call.from_user.id

	cur.execute(f"INSERT INTO blacklist(user_id) VALUES('{user_id}')")
	conn.commit()
	
	await call.answer('Тебе сюда нельзя :(', show_alert=True)
	await call.message.delete()


async def start_quiz(call: CallbackQuery, state: FSMContext):
	user_id = call.from_user.id

	await call.answer('Начинаем викторину!')
	await call.message.delete()
	await Polls.questions.set()

	async with state.proxy() as state_data:
		state_data['correct_answers'] = 0

	
	try:
		questions = await select_all_questions(user_id=user_id)

		await call.message.answer_poll(
			question=questions[0][1],
			options=[questions[0][2], questions[0][3], questions[0][4], questions[0][5]],
			type='quiz',
			correct_option_id=questions[0][6],
			is_anonymous=False,
			explanation=questions[0][7]
		)
	except:
		cur.execute(f'CREATE TABLE IF NOT EXISTS quiz_{user_id} AS SELECT * FROM user_{user_id} LIMIT 7')
		conn.commit()

		data = cur.execute(f'SELECT * FROM quiz_{user_id}')
		questions = []
		for value in data:
			questions.append(value)

		if len(questions) == 7:
			await call.message.answer_poll(
				question=questions[0][1],
				options=[questions[0][2], questions[0][3], questions[0][4], questions[0][5]],
				type='quiz',
				correct_option_id=questions[0][6],
				is_anonymous=False,
				explanation=questions[0][7]
			)
		else:
			cur.execute(f'DROP TABLE user_{user_id}')
			cur.execute(f'DROP TABLE quiz_{user_id}')
			conn.commit()

			questions = await select_all_questions(user_id=user_id)

			await call.message.answer_poll(
				question=questions[0][1],  # type: ignore
				options=[questions[0][2], questions[0][3], questions[0][4], questions[0][5]],  # type: ignore
				type='quiz',
				correct_option_id=questions[0][6],  # type: ignore
				is_anonymous=False,
				explanation=questions[0][7]  # type: ignore
			)


async def rules(call: CallbackQuery):
	await call.message.delete()

	user_id = call.from_user.id

	data = cur.execute('SELECT * FROM rules')
	rules = []
	for rule in data:
		rules.append(rule)

	start_btn = InlineKeyboardButton(text='НАЧАТЬ', callback_data='start_quiz')
	rules_btn = InlineKeyboardButton(text='ПРОЧИТАТЬ ЕЩЁ РАЗ', callback_data='rules')
	inkb = InlineKeyboardMarkup(row_width=1).add(start_btn).add(rules_btn)
	text_to_send = rules[0][0]

	await bot.send_message(chat_id=user_id, text=text_to_send, reply_markup=inkb)



def register_callback_handlers(dp: Dispatcher):
	dp.register_callback_query_handler(adult, text='adult', state=Polls.start)
	dp.register_callback_query_handler(not_adult, text='not_adult', state='*')
	dp.register_callback_query_handler(start_quiz, text='start_quiz', state=Polls.start)
	dp.register_callback_query_handler(rules, text='rules', state='*')
