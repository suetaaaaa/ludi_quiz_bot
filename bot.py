from aiogram.types import Message, ReplyKeyboardRemove, \
						ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor

from config.bot_exec import dp, bot

from database.db_connection import conn, cur
from sqlite3 import IntegrityError

import random



data = cur.execute('SELECT * FROM questions')
questions = []
for value in data:
	questions.append(value)


btn_yes = KeyboardButton('Конечно!')
kb_start = ReplyKeyboardMarkup(resize_keyboard=True)
kb_start.add(btn_yes)



@dp.message_handler(commands=['start'])
async def process_start_command(msg: Message):
	
	chat_id = msg.chat.id
	name = msg.from_user.full_name

	text_to_send = f'Привет, {name}! Сыграем?'

	await bot.send_message(chat_id=chat_id, text=text_to_send, reply_markup=kb_start)
	

async def new_question():
	btn_answer_1 = KeyboardButton(questions[0][2])
	btn_answer_2 = KeyboardButton(questions[0][3])
	btn_answer_3 = KeyboardButton(questions[0][4])
	btn_answer_4 = KeyboardButton(questions[0][5])
	correct_answer = questions[0][6]
	kb_answers = ReplyKeyboardMarkup(resize_keyboard=True)
	kb_answers.add(btn_answer_1).add(btn_answer_2).add(btn_answer_3).add(btn_answer_4)

	text_to_send = questions[0][1]

	return [correct_answer, kb_answers, text_to_send]


@dp.message_handler(content_types=['text'])
async def quiz(msg: Message):
	chat_id = msg.chat.id
	
	if (msg.text == 'Конечно!') or (msg.text == 'Сыграть еще раз'):
		data = cur.execute('SELECT * FROM questions')
		questions.clear()
		for value in data:
			questions.append(value)
		nq = await new_question()
		kb = nq[1]
		text_to_send = nq[2]

		await bot.send_message(chat_id=chat_id, text=text_to_send, reply_markup=kb)
	else:
		correct_answer = questions[0][6]
		if len(questions) == 1 and msg.text == correct_answer:
			text_to_send = 'Молодец, ты справился!'
			await bot.send_message(chat_id=chat_id, text=text_to_send, reply_markup=ReplyKeyboardRemove())
			questions.clear()
			data = cur.execute('SELECT * FROM questions')
			for value in data:
				questions.append(value)
		else:
			nq = await new_question()
			correct_answer = nq[0]
			
			if msg.text == correct_answer:
				questions.pop(0)
				nq = await new_question()
				kb = nq[1]
				text_to_send = nq[2]
				await bot.send_message(chat_id=chat_id, text=text_to_send, reply_markup=kb)
			else:
				questions.clear()
				data = cur.execute('SELECT * FROM questions')
				for value in data:
					questions.append(value)

				btn_replay = KeyboardButton('Сыграть еще раз')
				kb_replay = ReplyKeyboardMarkup(resize_keyboard=True)
				kb_replay.add(btn_replay)

				text_to_send = 'Попробуй еще раз.👌🏻'
				await bot.send_message(chat_id=chat_id, text=text_to_send, reply_markup=kb_replay)





if __name__ == '__main__':
	executor.start_polling(dp)
