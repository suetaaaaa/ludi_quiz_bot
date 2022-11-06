from aiogram.types import Message, ReplyKeyboardRemove, \
						ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext

from config.bot_exec import dp
from database.db_connection import conn, cur
from states.quiz import Quiz

import random



@dp.message_handler(commands=['quiz'], state=None)
async def start_quiz(msg: Message):
	user_id = msg.from_user.id

	data = cur.execute('SELECT * FROM questions')

	questions = []
	for value in data:
		questions.append(str(value))

	random.shuffle(questions)
	q_sql = ', '.join(questions)

	cur.execute(f'DROP TABLE IF EXISTS user_{user_id}')
	cur.execute(f'CREATE TABLE IF NOT EXISTS user_{user_id}(id INTEGER, question TEXT, answer_1 TEXT, answer_2 TEXT, answer_3 TEXT, answer_4 TEXT, correct_answer TEXT)')
	cur.execute(f'INSERT INTO user_{user_id} VALUES{q_sql}')
	conn.commit()
	
	questions = []
	data = cur.execute(f'SELECT * FROM user_{user_id}')
	for value in data:
		questions.append(value)
	
	btn_answer_1 = KeyboardButton(questions[0][2])
	btn_answer_2 = KeyboardButton(questions[0][3])
	btn_answer_3 = KeyboardButton(questions[0][4])
	btn_answer_4 = KeyboardButton(questions[0][5])
	kb_answers = ReplyKeyboardMarkup(resize_keyboard=True)
	kb_answers.add(btn_answer_1).add(btn_answer_2).add(btn_answer_3).add(btn_answer_4)
	text_to_send = questions[0][1]

	await msg.answer(text=text_to_send, reply_markup=kb_answers)
	await Quiz.Q1.set()


@dp.message_handler(state=Quiz.Q1)
async def get_new_question(msg: Message, state: FSMContext):
	user_id = msg.from_user.id

	try:
		questions = []
		data = cur.execute(f'SELECT * FROM user_{user_id}')
		for value in data:
			questions.append(value)

		user_answer = msg.text
		correct_answer = questions[0][6]

		if user_answer == correct_answer:
			cur.execute(f'DELETE FROM user_{user_id} WHERE id = (SELECT id FROM user_{user_id} ORDER BY rowid ASC LIMIT 1)')
			conn.commit()

			questions = []
			data = cur.execute(f'SELECT * FROM user_{user_id}')
			for value in data:
				questions.append(value)

			btn_answer_1 = KeyboardButton(questions[0][2])
			btn_answer_2 = KeyboardButton(questions[0][3])
			btn_answer_3 = KeyboardButton(questions[0][4])
			btn_answer_4 = KeyboardButton(questions[0][5])
			kb_answers = ReplyKeyboardMarkup(resize_keyboard=True)
			kb_answers.add(btn_answer_1).add(btn_answer_2).add(btn_answer_3).add(btn_answer_4)
			text_to_send = questions[0][1]

			await msg.answer(text=text_to_send, reply_markup=kb_answers)
			await Quiz.Q1.set()
		else:
			btn_replay = KeyboardButton('Попробовать еще раз')
			kb_replay = ReplyKeyboardMarkup(resize_keyboard=True)
			kb_replay.add(btn_replay)
			text_to_send = 'Неверно☹️\nВозможно, в следующий раз получится. Попробуй еще раз!'

			await msg.answer(text=text_to_send, reply_markup=kb_replay)
			await state.finish()
	except:
		text_to_send = 'Молодец, ты справился!🥳'

		cur.execute(f'DROP TABLE user_{user_id}')
		conn.commit()
		
		await msg.answer(text=text_to_send, reply_markup=ReplyKeyboardRemove())
		await state.finish()



@dp.message_handler()
async def replay(msg: Message):
	if msg.text == 'Попробовать еще раз':
		await start_quiz(msg=msg)
	else:
		pass



if __name__ == '__main__':
	executor.start_polling(dp)
