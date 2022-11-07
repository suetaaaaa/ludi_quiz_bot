from aiogram.dispatcher.filters.state import State, StatesGroup



class Polls(StatesGroup):
	start = State()
	questions = State()
