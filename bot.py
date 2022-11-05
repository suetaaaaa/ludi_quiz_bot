from aiogram.utils import executor

from config.bot_exec import dp
from handlers import message_handlers, callback_handlers, poll_handlers



message_handlers.register_message_handlers(dp)
callback_handlers.register_callback_handlers(dp)
poll_handlers.register_poll_handlers(dp)



if __name__ == '__main__':
	executor.start_polling(dp, skip_updates=True)
