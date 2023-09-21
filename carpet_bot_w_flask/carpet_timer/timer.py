# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
import asyncio
from datetime import datetime
from collections import defaultdict
from aiogram.utils.exceptions import (
    BotBlocked, ChatNotFound, RetryAfter)
from aiogram import types, Dispatcher
from aiogram.dispatcher.middlewares import BaseMiddleware
from keyboards import main_menu

# зберігання часу активності та останнього повідомлення
last_activity = {}  # {user_id: {'time': datetime, 'message': message.text}}
ignored_users = {}
MAX_SEND_ATTEMPTS = 3  # 3 спроби
send_attempts = defaultdict(int)  # кількість спроб для кожного юзера


class UserActivityMiddleware(BaseMiddleware):
    async def on_pre_process_message(self, message: types.Message, data: dict):
        user_id = message.from_user.id

        # Перевірка на відмінність повідомлення
        if user_id in ignored_users and ignored_users[user_id] != message.text:
            ignored_users.pop(user_id, None)  # Прибрати з ігнорованих

        # Якщо користувач у списку ігнорованих, ігноруємо його повідомлення
        elif user_id in ignored_users:
            return

        # Виключаємо вітаючі повідомлення
        if message.text != "Щиро раді вас вітати☺️":
            last_activity[user_id] = (
                {'time': datetime.now(), 'message': message.text})


async def check_user_activity(dispatcher: Dispatcher):
    bot = dispatcher.bot
    storage = dispatcher.storage
    while True:
        await asyncio.sleep(1800)
        now = datetime.now()
        for user_id, data in list(last_activity.items()):
            if (now - data['time']).seconds >= 1800:
                if send_attempts[user_id] >= MAX_SEND_ATTEMPTS:
                    # Якщо ми досягли максимальної кількості спроб, видаляємо
                    last_activity.pop(user_id, None)
                    send_attempts.pop(user_id, None)
                    continue

                user_data = await storage.get_data(user=user_id)
                if user_data:
                    await storage.finish(user=user_id)

                try:
                    await bot.send_message(
                        user_id,
                        "Ви повернулись до головного меню 😴",
                        reply_markup=main_menu
                    )
                except (TimeoutError,
                        BotBlocked,
                        ChatNotFound,
                        RetryAfter):
                    send_attempts[user_id] += 1
                    continue

                ignored_users[user_id] = data['message']
                last_activity.pop(user_id, None)


async def register_activity_tracker(timer_disp):
    timer_disp.middleware.setup(UserActivityMiddleware())
    asyncio.ensure_future(check_user_activity(timer_disp))
