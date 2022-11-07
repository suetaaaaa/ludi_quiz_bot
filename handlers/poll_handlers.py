from aiogram import Dispatcher
from aiogram.types import (InlineKeyboardButton, InlineKeyboardMarkup,
                           PollAnswer)

from config.bot_exec import bot, dp
from database.db_connection import conn, cur
from filters.state_filter import IsQuestionsState
from states.polls import Polls



async def next_poll(poll: PollAnswer):
	user_id = poll.user.id
	state = dp.current_state(chat=poll.user.id, user=poll.user.id)

	questions = []
	data = cur.execute(f'SELECT * FROM quiz_{user_id}')
	for value in data:
		questions.append(value)

	user_answer = poll.option_ids[0]
	correct_answer = questions[0][6]
	
	async with state.proxy() as state_data:

		if user_answer == correct_answer:
			state_data['correct_answers'] += 1
		else:
			pass
		
		cur.execute(f'DELETE FROM quiz_{user_id} WHERE id = (SELECT id FROM quiz_{user_id} ORDER BY rowid ASC LIMIT 1)')
		conn.commit()

		questions = []
		data = cur.execute(f'SELECT * FROM quiz_{user_id}')
		for value in data:
			questions.append(value)

		try:
			await bot.send_poll(
				chat_id=user_id,
				question=questions[0][1],
				options=[questions[0][2], questions[0][3], questions[0][4], questions[0][5]],
				type='quiz',
				correct_option_id=questions[0][6],
				is_anonymous=False,  # type: ignore
				explanation=questions[0][7]
			)
		except:
			if state_data['correct_answers'] >= 3:
				adult_btn = InlineKeyboardButton(text='ЗАБРАТЬ ПРИЗ', url='https://narodnyclub.ru/', callback_data='winner')
				inkb = InlineKeyboardMarkup(row_width=1).add(adult_btn)
				text_to_send = 'Отлично! Тебя ждёт подарок🎁'

				await bot.send_message(chat_id=poll.user.id, text=text_to_send, reply_markup=inkb)

				cur.execute(f'DROP TABLE user_{user_id}')
				cur.execute(f'DROP TABLE quiz_{user_id}')
				conn.commit()

				await state.finish()
			else:
				adult_btn = InlineKeyboardButton(text='Поробовать еще раз!', callback_data='adult')
				inkb = InlineKeyboardMarkup(row_width=1).add(adult_btn)
				text_to_send = 'В этот раз не получилось. Не расстраивайся, ты можешь пройти викторину ещё раз.'

				await bot.send_message(chat_id=poll.user.id, text=text_to_send, reply_markup=inkb)

				cur.execute(f'DELETE FROM user_{user_id} WHERE id IN (SELECT id FROM user_{user_id} LIMIT 7)')
				cur.execute(f'DROP TABLE quiz_{user_id}')
				conn.commit()

				await Polls.start.set()



def register_poll_handlers(dp: Dispatcher):
	dp.register_poll_answer_handler(next_poll, IsQuestionsState(is_questions_state=False))
