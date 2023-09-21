# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

import time
from aiogram import executor
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from bot import dispatcher
from carpet_timer import register_activity_tracker


MAX_RETRIES = 5
DELAY = 10


async def on_startup(main_disp):
    print('Бот стартував.')
    await register_activity_tracker(main_disp)


async def on_shutdown(_):
    print('Бот завершив роботу.')

RETRIES = 0
if __name__ == '__main__':
    from handlers import (
        register_stand_prod_handlers, register_handlers_client,
        reg_equip_order_handlers, register_expres_prod_handlers,
        reg_serv_order_handlers
    )

    register_handlers_client(dispatcher)
    register_stand_prod_handlers(dispatcher)
    reg_equip_order_handlers(dispatcher)
    register_expres_prod_handlers(dispatcher)
    reg_serv_order_handlers(dispatcher)
    dispatcher.middleware.setup(LoggingMiddleware())

    while RETRIES < MAX_RETRIES:
        try:
            executor.start_polling(
                dispatcher, on_startup=on_startup, on_shutdown=on_shutdown
            )
            break  # Успішне виконання - вийти з циклу
        except TimeoutError:
            print(f"Timeout Error! Restarting Bot in {DELAY} seconds...")
            time.sleep(DELAY)
            DELAY *= 2  # Збільшуємо час затримки експоненційно
            RETRIES += 1
