from aiogram import Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, \
						PollAnswer

from config.bot_exec import bot
from database.db_connection import conn, cur



async def next_poll(poll: PollAnswer):
	user_id = poll.user.id
	
	try:
		questions = []
		data = cur.execute(f'SELECT * FROM user_{user_id}')
		for value in data:
			questions.append(value)

		user_answer = poll.option_ids[0]
		correct_answer = questions[0][6]
		
		if user_answer == correct_answer:
			cur.execute(f'DELETE FROM user_{user_id} WHERE id = (SELECT id FROM user_{user_id} ORDER BY rowid ASC LIMIT 1)')
			conn.commit()

			questions = []
			data = cur.execute(f'SELECT * FROM user_{user_id}')
			for value in data:
				questions.append(value)

			await bot.send_poll(
				chat_id=poll.user.id,
				question=questions[0][1],
				options=[questions[0][2], questions[0][3], questions[0][4], questions[0][5]],
				type='quiz',
				correct_option_id=questions[0][6],
				is_anonymous=False,  # type: ignore
				explanation=questions[0][7]
			)
		else:
			adult_btn = InlineKeyboardButton(text='Поробовать еще раз!', callback_data='adult')
			inkb = InlineKeyboardMarkup(row_width=1).add(adult_btn)
			text_to_send = 'Ой! Неверный ответ. Не расстраивайся, ты можешь пройти викторину ещё раз.'

			await bot.send_message(chat_id=poll.user.id, text=text_to_send, reply_markup=inkb)
	except:
		adult_btn = InlineKeyboardButton(text='ЗАБРАТЬ ПРИЗ', url='https://narodnyclub.ru/', callback_data='winner')
		inkb = InlineKeyboardMarkup(row_width=1).add(adult_btn)
		text_to_send = 'Отлично! Тебя ждёт подарок🎁'
		await bot.send_message(chat_id=poll.user.id, text=text_to_send, reply_markup=inkb)

		cur.execute(f'DROP TABLE IF EXISTS user_{user_id}')
		conn.commit()



def register_poll_handlers(dp: Dispatcher):
	dp.register_poll_answer_handler(next_poll)
