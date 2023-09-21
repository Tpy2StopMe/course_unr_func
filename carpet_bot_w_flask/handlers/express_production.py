# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

import re
import asyncio
from keyboards.client_kb import (
    standard_prod_menu, production_menu, confirm_menu, main_menu,
    carpet_menu
    )
from bot.bot import bot
from aiogram import types, Dispatcher
from aiogram.types import InputMediaPhoto, ReplyKeyboardRemove
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from google_sheet import GoogleSheet
from config_data.config import owner_id, carpet_images_data, carpets_orders

OWNER_ID = owner_id

gs = GoogleSheet()


# Carpet order state
class Express(StatesGroup):

    carpet_type = State()
    length = State()
    width = State()
    color_quantity = State()
    await_step_difficult = State()
    step_difficult = State()
    user_name = State()
    phone_number = State()
    confirmation = State()


async def start_express_production(message: types.Message):
    await Express.carpet_type.set()
    await message.answer(
        "Будь-ласка, оберіть тип килима:",
        reply_markup=carpet_menu
    )


async def express_media_group(images_list, chat_id, target_bot):
    media = [InputMediaPhoto(media=img_url) for img_url in images_list]
    await target_bot.send_media_group(chat_id=chat_id, media=media)


async def send_design_difficulty(message, state: FSMContext):
    carpet_images = gs.fetch_carpet_images(carpet_images_data)
    simple_images = carpet_images["simple"]
    middle_images = carpet_images["middle"]
    hard_images = carpet_images["hard"]

    design_levels = [
        ("Перший рівень складності дизайну👇:", simple_images),
        ("Другий рівень складності дизайну👇:", middle_images),
        ("Третій рівень складності дизайну👇:", hard_images)
    ]

    for title, images in design_levels:
        await asyncio.sleep(1)
        await message.answer(title)
        await asyncio.sleep(3)
        await express_media_group(images, message.chat.id, message.bot)

    await message.answer(
        "Будь-ласка, оберіть варіант Ваших очікувань від дизайну: "
        "Перший1️⃣, другий2️⃣ чи третій3️⃣."
    )
    current_state = await state.get_state()

    await asyncio.sleep(35)

    if current_state == await state.get_state():
        await message.answer(
            "P.S.\n"
            "Якщо Вам важко визначитись, просто оберіть варіант, " +
            "який найбільше спободовася і підтвердіть замовлення☺️" +
            "\nМи з Вами зв'яжемося і усе з'ясуємо😎"
        )


async def express_carpet_type(message: types.Message, state: FSMContext):
    await state.update_data(
        carpet_type=message.text, production_type="Термінове замовлення")

    carpet_prompt = "діаметр" if message.text == "Круглий килим" else "довжину"
    await Express.length.set()
    await message.answer(
        f"Будь-ласка, вкажіть {carpet_prompt} килима у сантиметрах:",
        reply_markup=standard_prod_menu
    )


async def express_length(message: types.Message, state: FSMContext):
    try:
        await state.update_data(length=float(message.text))
        if (await state.get_data()).get('carpet_type') == "Круглий килим":
            await Express.step_difficult.set()
            await send_design_difficulty(message, state)
        else:
            await Express.width.set()
            await message.answer(
                "Будь-ласка, вкажіть ширину килима у сантиметрах:")
    except ValueError:
        await message.answer("Будь-ласка, вкажіть довжину числом:")


async def express_width(message: types.Message, state: FSMContext):
    try:
        await state.update_data(width=float(message.text))
        await Express.step_difficult.set()
        await send_design_difficulty(message, state)
    except ValueError:
        await message.answer("Будь-ласка, вкажіть ширину числом:")


async def express_step_difficult(message: types.Message, state: FSMContext):
    value = message.text
    if value.lower() in ["1", "2", "3", "перший", "другий", "третій"]:
        await state.update_data(complexity=value)
        await Express.color_quantity.set()
        await message.answer("Будь-ласка, вкажіть кількість кольорів🌈:")
    else:
        await message.answer(
            'Будь-ласка, оберіть один із трьох варіантів:')


async def express_color_quantity(message: types.Message, state: FSMContext):
    try:
        color_quantity = int(message.text)
        await state.update_data(
            color_quantity=color_quantity)
        await express_details(message, state)
    except ValueError:
        await message.answer(
            "Будь-ласка, вкажіть кількість кольорів цілим числом:")


async def express_details(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text_order_data = f"""
        Терміновість: {data.get('production_type')}
        Тип килиму: {data.get('carpet_type')}
        Довжина: {data.get('length')} см
        """
        if data.get("width"):
            text_order_data += f"Ширина: {data.get('width')} см\n"
        text_order_data += f"""
        Складність дизайну: {data.get('complexity')}
        Кількість кольорів: {data.get('color_quantity')}
        """

        await message.answer(f"Ваше замовлення:\n\n{text_order_data}")
        await message.answer("Бажаєте продовжити?", reply_markup=confirm_menu)
        await Express.confirmation.set()


async def express_confirmation(message: types.Message, state: FSMContext):
    if message.text == "Скасовую замовлення":
        await message.answer(
            "Ви повернулись до головного меню🥲",
            reply_markup=main_menu
        )
        await state.finish()
        return
    if message.text == "Підтверджую замовлення":
        await Express.user_name.set()
        await message.answer(
            "Будь-ласка, вкажіть Ваше ім'я:",
            reply_markup=ReplyKeyboardRemove())


async def express_user_name(message: types.Message, state: FSMContext):
    user_name = message.text
    # check for numbers
    if not re.match(r'^[a-zA-Zа-яА-ЯіІїЇєЄґҐ\s]+$', user_name):
        await message.answer(
            "Будь ласка, вкажіть ім'я")
        return

    await state.update_data(user_name=user_name)
    await Express.phone_number.set()
    await message.answer(
        "Будь ласка, вкажіть Ваш номер телефону📱:",
        reply_markup=ReplyKeyboardRemove())


async def express_phone_number(message: types.Message, state: FSMContext):
    phone_number = message.text
    if re.match(r'^(\+380\d{9}|38\d{10}|80\d{9}|0\d{9})$', phone_number):
        await state.update_data(phone_number=phone_number)
        await message.answer(
                    "Дякуємо за те, що обрали нас😇 "
                    "\nМы зв'яжемося з Вами найближчим часом!",
                    reply_markup=main_menu
            )
        async with state.proxy() as data:
            order_number = gs.get_next_order_id(carpets_orders)
            order_details = {
                "Номер замовлення": order_number,
                "Ім'я": data.get('user_name'),
                "Номер телефону": data.get('phone_number'),
                "Терміновість": data.get('production_type'),
                "Тип": data.get('carpet_type'),
                "Довжина/ діаметр": data.get('length'),
                "Ширина": data.get('width'),
                "Складність": data.get('complexity'),
                "Кількість кольорів": data.get('color_quantity'),
            }
            gs.write_order(order_details, carpets_orders)

            # Генеруємо текст замовлення
            text_order_data = f"""
            Номер замовлення: {order_number}
            Терміновість: {data.get('production_type')}
            Тип килиму: {data.get('carpet_type')}
            Довжина: {data.get('length')} см
            """
            if data.get("width"):
                text_order_data += f"Ширина: {data.get('width')} см\n"
            text_order_data += f"""
            Складність дизайну: {data.get('complexity')}
            Кількість кольорів: {data.get('color_quantity')}
            Ім'я: {data.get('user_name')}
            Телефон: {data.get('phone_number')}
            """
            await bot.send_message(message.from_user.id, text_order_data)
            await bot.send_message(OWNER_ID, text_order_data)
            await state.finish()
    else:
        await message.answer("Будь ласка, вкажіть вірний номер телефону"
                             " у форматі +380... або 097..."
                             )

RETURN_MENUS = {
    "Express:carpet_type": production_menu,
    "Express:length": carpet_menu,
    "Express:width": carpet_menu,
    "Express:color_quantity": carpet_menu,
    "Express:step_difficult": carpet_menu,
    "Express:user_name": carpet_menu,
    "Express:phone_number": carpet_menu,
    "Express:confirmation": carpet_menu
}


async def express_return(message: types.Message, state: FSMContext):
    current_state = await state.get_state()

    if current_state is not None:
        menu_to_show = RETURN_MENUS.get(current_state, main_menu)
        if menu_to_show != production_menu:
            await Express.carpet_type.set()
            await message.answer(
                "Ви повернулись до попереднього меню."
                " Бажаєте обрати інший тип килима?",
                reply_markup=menu_to_show
                )
        else:
            await state.reset_state()
            await message.answer(
                "Ви повернулись до попереднього меню.",
                reply_markup=production_menu
                )


async def express_default_msg(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    print(message.text)
    await message.reply("Не зрозумів Вас🙄. Спробуйте ще раз.")


def register_expres_prod_handlers(express_prod_disp: Dispatcher):
    express_prod_disp.register_message_handler(
        express_return,
        text="Повернутися",
        state=Express
    )
    express_prod_disp.register_message_handler(
        express_carpet_type,
        state=Express.carpet_type
        )
    express_prod_disp.register_message_handler(
        start_express_production,
        text="Термінове замовлення"
    )
    express_prod_disp.register_message_handler(
        express_length,
        state=Express.length
    )
    express_prod_disp.register_message_handler(
        express_width,
        state=Express.width
    )
    express_prod_disp.register_message_handler(
        express_color_quantity,
        state=Express.color_quantity
    )
    express_prod_disp.register_message_handler(
        express_step_difficult,
        state=Express.step_difficult
    )
    express_prod_disp.register_message_handler(
        express_user_name,
        state=Express.user_name
    )
    express_prod_disp.register_message_handler(
        express_phone_number,
        state=Express.phone_number
    )
    express_prod_disp.register_message_handler(
        express_confirmation,
        state=Express.confirmation,
        text="Підтверджую замовлення"
    )
    express_prod_disp.register_message_handler(
        express_confirmation,
        state=Express.confirmation,
        text="Скасовую замовлення"
    )
    express_prod_disp.register_message_handler(
        express_default_msg,
        state=Express,
        content_types=types.ContentTypes.TEXT
    )
