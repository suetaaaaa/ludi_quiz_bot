from aiogram.dispatcher.filters import BoundFilter
from aiogram.types import PollAnswer

from config.bot_exec import dp



class IsQuestionsState(BoundFilter):
	key = 'is_questions_state'

	def __init__(self, is_questions_state):
		self.is_questions_state = is_questions_state

	async def check(self, poll: PollAnswer):
		state = dp.current_state(chat=poll.user.id, user=poll.user.id)
		curr_state = await state.get_state()
		
		return curr_state == 'Polls:questions'



dp.filters_factory.bind(IsQuestionsState)
