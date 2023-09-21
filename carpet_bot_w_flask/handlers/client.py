# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

import asyncio
from pathlib import Path
from io import BytesIO
from functools import lru_cache
from aiogram import types, Dispatcher
from aiogram.types import InputMediaPhoto
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import NetworkError
from bot import bot
from keyboards.client_kb import (
    main_menu, tools_menu, production_menu, learning_menu,
    about_us_menu, schedule_menu, social_menu, feedbacks_menu,
    delivery_menu, standard_prod_menu, online_menu, master_class,
    express_prod_menu, confirm_menu, carpet_menu, insta_menu,
    tik_tok_menu, you_tube_menu, telegram_menu, milk_needle,
    ukr_poshta, nova_poshta, abroad
    )
from learning.learning import ONLINE_CRS_DESC, MASTER_CLS_DESC
from config_data.config import owner_id

OWNER_ID = owner_id
menu_stack = []

MENU_URLS = {
    'instagram': "https://www.instagram.com/milk_needle/",
    'tik_tok': "https://www.tiktok.com/@milk_needle?_t=8fbamh6zMpy&_r=1",
    'you_tube': "https://www.youtube.com/channel/UCDc1IxtsEnN9uOQ8mUfTNOQ",
    'telegram': "https://t.me/milk_needle",
    'milk_history': "bit.ly/3PmFDMi",
    'location': "https://maps.app.goo.gl/Njvo9sap9aFA4K3m6",
    # 'milk_history': (
    #     "https://shotam.info/nas-nazyvaly-bozhevilnymy-yak-vidkryty-"
    #     "biznes-pid-chas-viyny-i-ne-prohority-istorii-pidpryiemtsiv-"
    #     "iakym-vdalosia/"
    # )
}


async def send_menu(message: types.Message, prompt="Ви обрали☝️"):
    try:
        if menu_stack:
            await bot.send_message(
                message.from_user.id,
                prompt if prompt else "",
                reply_markup=menu_stack[-1]
            )
        else:
            await bot.send_message(
                message.from_user.id,
                prompt if prompt else "",
                reply_markup=main_menu
            )
    except NetworkError:
        await handle_back(message)


async def command_start(message: types.Message, state: FSMContext):
    await state.finish()  #
    menu_stack.clear()
    menu_stack.append(main_menu)
    welcome_text = "Щиро раді Вас вітати ☺️"
    await message.delete()
    await send_menu(message, welcome_text)


async def handle_back(message: types.Message):
    if menu_stack:
        menu_stack.pop()

    if menu_stack:
        await send_menu(message)
    else:
        menu_stack.append(main_menu)
        await send_menu(message, "Ви в головному меню 🤓")


async def send_callback_request(message: types.Message):
    user = message.from_user
    user_info = f"Ім'я: {user.first_name}\n"
    if user.last_name:
        user_info += f"Прізвище: {user.last_name}\n"
    if user.username:
        user_info += f"Логін: @{user.username}\n"
    callback_request = f"Будь ласка, зв'яжіться зі мною:\n\n{user_info}"
    await bot.send_message(OWNER_ID, callback_request)
    await message.answer("Дякуємо за Ваш запит😇\n" +
                         "Ми зв'яжемося с Вами найближчим часом!")


# Command handlers
async def tools_command(message: types.Message):
    menu_stack.append(tools_menu)
    await send_menu(message)


async def carpet_command(message: types.Message):
    menu_stack.append(carpet_menu)
    await send_menu(message)


async def production_command(message: types.Message):
    menu_stack.append(production_menu)
    await send_menu(message)


async def order_command(message: types.Message):
    menu_stack.append(confirm_menu)
    await send_menu(message)


async def learning_command(message: types.Message):
    menu_stack.append(learning_menu)
    await send_menu(message)


async def stand_prod_command(message: types.Message):
    menu_stack.append(standard_prod_menu)
    await send_menu(message)


async def express_prod_command(message: types.Message):
    menu_stack.append(express_prod_menu)
    await send_menu(message)


async def exp_prod_command(message: types.Message):
    menu_stack.append(express_prod_menu)
    await send_menu(message)


async def online_command(message: types.Message):
    menu_stack.append(online_menu)
    await send_menu(message)
    await bot.send_message(message.from_user.id, ONLINE_CRS_DESC)

master_feed_path = Path('images/master_images') / 'master_1.jpg'


async def master_command(message: types.Message):
    menu_stack.append(master_class)
    await send_menu(message)
    photo_data = read_image(master_feed_path)
    photo = BytesIO(photo_data)
    await bot.send_photo(chat_id=message.from_user.id, photo=photo)
    await asyncio.sleep(2)
    await bot.send_message(message.from_user.id, MASTER_CLS_DESC)


async def about_us_command(message: types.Message):
    menu_stack.append(about_us_menu)
    await send_menu(message)


async def schedule_command(message: types.Message):
    menu_stack.append(schedule_menu)
    await send_menu(message)
    message_text = """
    Ми працюємо 📅:\n
    - Понеділок: 10:00–21:00
    - Вівторок: 10:00–21:00
    - Середа: 10:00–21:00
    - Четвер: 10:00–21:00
    - Пʼятниця: 10:00–21:00
    - Субота: 10:00–21:00
    - Неділя: 12:00–18:00
    \nІноді, й трошки довше 😊.\nНе соромтесь, пишіть ✍️💬.
    """

    await message.answer(message_text, parse_mode='Markdown')
    await asyncio.sleep(1)
    message_text = f"""
    А знаходимось ми ось тут 👇
    <a href="{MENU_URLS['location']}">📍</a>
    """
    await message.answer(message_text, parse_mode='HTML')


async def social_command(message: types.Message):
    menu_stack.append(social_menu)
    await send_menu(message)


async def instagram(message: types.Message):
    menu_stack.append(insta_menu)
    await send_menu(message)
    url = MENU_URLS['instagram']
    await bot.send_message(
        message.from_user.id,
        f"Cлідкуйте за нами в Instagram 📸🖼\n{url}"
        )


async def tik_tok(message: types.Message):
    menu_stack.append(tik_tok_menu)
    await send_menu(message)
    url = MENU_URLS['tik_tok']
    await bot.send_message(message.from_user.id,
                           f"Ми в Тік-Ток 🕺💃\n\n{url}")


async def you_tube(message: types.Message):
    menu_stack.append(you_tube_menu)
    await send_menu(message)
    url = MENU_URLS['you_tube']
    await bot.send_message(message.from_user.id,
                           f"Наш канал на YouTube 📺🎥\n{url}")


async def telegram(message: types.Message):
    menu_stack.append(telegram_menu)
    await send_menu(message)
    url = url = MENU_URLS['telegram']
    await bot.send_message(message.from_user.id,
                           f"Приєднуйтесь до нас в Telegram 📬📢\n{url}")


@lru_cache(maxsize=50)
def read_image(path: Path) -> bytes:
    with path.open('rb') as image:
        return image.read()


async def feedbacks_command(message: types.Message):
    menu_stack.append(feedbacks_menu)
    await send_menu(message)
    feedbacks_path = Path('images/feedback_images')
    images = list(feedbacks_path.glob("*.jpg"))

    grouped_images = [images[i:i + 4] for i in range(0, len(images), 4)]

    for group in grouped_images:
        media_group = []

        for image_path in group:
            image_data = read_image(image_path)
            image_stream = BytesIO(image_data)
            media_group.append(InputMediaPhoto(image_stream))

        await bot.send_media_group(
            chat_id=message.from_user.id, media=media_group)


async def delivery_command(message: types.Message):
    menu_stack.append(delivery_menu)
    await send_menu(message)


async def milk_history(message: types.Message):
    menu_stack.append(milk_needle)
    await send_menu(message)
    url = MENU_URLS['milk_history']
    await bot.send_message(message.from_user.id, url)

new_post_path = Path('images/post_images') / 'new_post.png'


async def novaposhta_handler(message: types.Message):
    photo_data = read_image(new_post_path)
    photo = BytesIO(photo_data)
    await bot.send_photo(chat_id=message.from_user.id, photo=photo)

    menu_stack.append(nova_poshta)
    response_text = (
        "1️⃣ Якщо замовлення зроблено до 13:00\n"
        "✅ Відправка в той самий день до 21:00\n\n"
        "2️⃣ Після 13:00 на наступний день до 21:00\n\n"
        "🚫 Післясплата не відправляється - Тканина та Пряжа 🚫"
    )
    await send_menu(message, response_text)

ukr_post_path = Path('images/post_images') / 'ukr_post.png'


async def ukrposhta_handler(message: types.Message):
    photo_data = read_image(ukr_post_path)
    photo = BytesIO(photo_data)
    await bot.send_photo(chat_id=message.from_user.id, photo=photo)

    menu_stack.append(ukr_poshta)
    response_text = (
        "✅ Відправка вт-сб до 17:00\n\n"
        "⚠️ Відправка після замовлення на наступний день в робочі дні\n\n"
        "🚫 Післяплати немає 🚫"
    )
    await send_menu(message, response_text)

inter_post_path = Path('images/post_images') / 'new_post_inter.png'


async def abroad_handler(message: types.Message):
    photo_data = read_image(inter_post_path)
    photo = BytesIO(photo_data)
    await bot.send_photo(chat_id=message.from_user.id, photo=photo)
    menu_stack.append(abroad)
    response_text = (
        "✅ Новою поштою\n\n"
        "✅ Відправка - додатково уточнюється\n"
        "⚠️ Сплата за доставку - відразу\n\n"
        "🚫 Післяплати немає 🚫"
    )
    await send_menu(message, response_text)


async def handle_sticker(message: types.Message):
    sticker_id = message.sticker.file_id
    await message.answer(f"ID стікера: {sticker_id}")


def register_handlers_client(client_disp: Dispatcher):
    # Register command handler for "start" command
    client_disp.register_message_handler(
        command_start, commands=["start"], state="*")

    # Register message handlers for specific texts
    client_disp.register_message_handler(
        tools_command, lambda m: "Послуги та обладнання" in m.text
    )
    client_disp.register_message_handler(
        production_command, lambda m: "Виробництво" in m.text
    )
    client_disp.register_message_handler(
        handle_back, lambda m: "Повернутися" in m.text
    )
    client_disp.register_message_handler(
        learning_command, lambda m: "Навчання" in m.text
    )
    client_disp.register_message_handler(
        about_us_command, lambda m: "Про нас" in m.text
    )
    client_disp.register_message_handler(
        schedule_command, lambda m: "Наша майстерня та розклад" in m.text
    )
    client_disp.register_message_handler(
        instagram, lambda m: "Instagram" in m.text
    )
    client_disp.register_message_handler(
        tik_tok, lambda m: "Tik-Tok" in m.text
    )
    client_disp.register_message_handler(
        you_tube, lambda m: "YouTube" in m.text
    )
    client_disp.register_message_handler(
        telegram, lambda m: "Telegram" in m.text
    )
    client_disp.register_message_handler(
        milk_history, lambda m: "Історія 'Milk Needle'" in m.text
    )
    client_disp.register_message_handler(
        feedbacks_command, lambda m: "Відгуки" in m.text
    )
    client_disp.register_message_handler(
        social_command, lambda m: "Соціальні мережі" in m.text
    )
    client_disp.register_message_handler(
        delivery_command, lambda m: "Доставка" in m.text
    )
    client_disp.register_message_handler(
        ukrposhta_handler, lambda m: "Укрпошта" in m.text
    )
    client_disp.register_message_handler(
        novaposhta_handler, lambda m: "Нова пошта" in m.text
    )
    client_disp.register_message_handler(
        abroad_handler, lambda m: "За кордон" in m.text
    )
    client_disp.register_message_handler(
        order_command, lambda m: "Ви підтверджуєте замовлення?" in m.text
        )
    # sticker handler
    client_disp.register_message_handler(
        handle_sticker, content_types=['sticker']
    )
    client_disp.register_message_handler(
        online_command, lambda m: "Онлайн курс" in m.text
    )
    client_disp.register_message_handler(
        master_command, lambda m: "Мастер-клас" in m.text
    )
    client_disp.register_message_handler(
        send_callback_request, commands=["callback"], state="*"
    )
