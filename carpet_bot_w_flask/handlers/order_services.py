# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

import re
from typing import Optional

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from shopping_cart import ShoppingCart
from google_sheet import GoogleSheet
from keyboards import (tools_menu, main_menu, eq_conf_menu,
                       eq_del_menu, cart_menu, eq_decis_menu)
from bot import bot
from config_data.config import owner_id, services_orders  # services_data
from updater.google_updater import fetch_services

# Constants
OWNER_ID = owner_id
CART_TEXT = "Кошик"

gs = GoogleSheet()
# SERVICES = gs.fetch_data(services_data)


class OrderServices(StatesGroup):
    ChoosingProduct = State()
    ConfirmingOrder = State()
    SettingQuantity = State()
    Decision = State()
    CartOverview = State()
    DeletingProductChoice = State()
    DeletingQuantity = State()
    ContinueDelete = State()
    GettingName = State()
    GettingPhone = State()


def get_keyboard(cart: Optional[ShoppingCart] = None):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

    markup.add(*[KeyboardButton(product) for product in fetch_services()])

    if cart and not cart.is_empty():
        markup.add(KeyboardButton(CART_TEXT))

    markup.add(KeyboardButton("Повернутися"))

    return markup


def get_cart_keyboard(cart: ShoppingCart) -> ReplyKeyboardMarkup:
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(*[KeyboardButton(product) for product in cart.items.keys()])
    return markup


# async def fetch_services():
#     services = gs.fetch_data(services_data)
#     return services


async def cmd_start(message: types.Message, state: FSMContext):
    # global SERVICES
    # SERVICES = await fetch_services()
    cart = ShoppingCart()
    await state.update_data(cart=cart)
    await OrderServices.ChoosingProduct.set()
    markup = get_keyboard()
    await message.answer("Оберіть послугу:", reply_markup=markup)


async def process_product_choice(message: types.Message, state: FSMContext):
    product_description = fetch_services()[message.text]["description"]
    product_price = fetch_services()[message.text]["price"]
    product_image_url = fetch_services()[message.text].get("image_url", None)

    if isinstance(product_price, (int, float)):
        text = (f"{product_description}\n\nЦіна: {product_price} грн."
                "\n\nБажаєте додати послугу?")
    else:
        text = (f"{product_description}\n\nЦіна {product_price.lower()}."
                "\n\nБажаєте додати послугу?")

    if product_image_url:
        await message.answer_photo(photo=product_image_url)
    await message.answer(text, reply_markup=eq_conf_menu)
    await state.update_data(chosen_product=message.text)
    await state.set_state(OrderServices.ConfirmingOrder.state)


async def process_confirm_order(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    chosen_product = user_data['chosen_product']
    await message.answer(
        f'Ви обрали "{chosen_product}". Вкажіть бажану кількість:',
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(OrderServices.SettingQuantity.state)


async def process_set_quantity(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    chosen_product = user_data['chosen_product']

    if message.text.isdigit() and int(message.text) > 0:
        quantity = int(message.text)
        cart = user_data['cart']
        cart.add(chosen_product, quantity)
        await state.update_data(cart=cart)
        await OrderServices.Decision.set()
        await message.answer(
            f'Ви обрали "{chosen_product}" у кількості {quantity} шт.'
            ' Бажаєте продовжити чи перейти до кошику для замовлення?',
            reply_markup=eq_decis_menu
        )
    else:
        await message.answer("Вкажіть дійсну кількість (більше нуля).")


async def process_return(message: types.Message, state: FSMContext):
    await state.set_state(OrderServices.ChoosingProduct.state)
    user_data = await state.get_data()
    cart = user_data.get('cart')
    markup = get_keyboard(cart)
    await message.answer("Оберіть послуги:", reply_markup=markup)


async def process_continue_shopping(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    cart = user_data.get('cart')
    markup = get_keyboard(cart)
    await message.answer("Оберіть інші послуги:", reply_markup=markup)
    await state.set_state(OrderServices.ChoosingProduct.state)


async def process_view_cart(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    cart = user_data.get('cart')
    cart_content = cart.summary(fetch_services())
    await OrderServices.CartOverview.set()
    await message.answer(f"Ваш кошик:\n{cart_content}",
                         reply_markup=cart_menu)


async def process_delete_product_choice(
        message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    cart = user_data.get('cart')
    await OrderServices.DeletingProductChoice.set()
    products_keyboard = get_cart_keyboard(cart)
    await message.answer("Оберіть послугу для видалення:",
                         reply_markup=products_keyboard)


# видалив state: OrderFSM.CartOverview
async def process_starter_getting_name(
        message: types.Message):
    await OrderServices.GettingName.set()
    await message.answer("Вкажіть Ваше ім'я:")


async def process_continue_shopping_from_cart(
        message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    cart = user_data.get('cart')
    markup = get_keyboard(cart)
    await OrderServices.ChoosingProduct.set()
    await message.answer("Оберіть наступну послугу:", reply_markup=markup)


async def process_select_delete_product(
        message: types.Message, state: FSMContext):
    await state.update_data(product_to_delete=message.text)
    await message.answer(
        f'Яку кількість "{message.text}" Ви бажаєте видалити?',
        reply_markup=types.ReplyKeyboardRemove()
    )
    await OrderServices.DeletingQuantity.set()


async def process_return_to_cart_from_delete_choice(message: types.Message):
    await message.answer("Перегляд кошика.")
    await OrderServices.CartOverview.set()


async def process_deleting_quantity(message: types.Message, state: FSMContext):
    try:
        quantity = int(message.text)
    except ValueError:
        await message.answer("Будь ласка, вкажіть число.")
        return

    user_data = await state.get_data()
    product_to_delete = user_data.get("product_to_delete")
    cart = user_data.get('cart')

    if (product_to_delete not in cart.items or
            quantity > cart.items[product_to_delete]):
        await message.answer(
            f'Ви вказали "{product_to_delete}" більше ніж є у кошику.' +
            ' Спробуйте ще!'
            )
        return

    cart.remove(product_to_delete, quantity)
    await state.update_data(cart=cart, product_to_delete=None)

    if cart.is_empty():
        await message.answer(
            "Ваш кошик порожній. Оберіть послуги з меню:",
            reply_markup=get_keyboard()
            )
        await OrderServices.ChoosingProduct.set()
        return

    await message.answer(
        f'Ви видалили "{product_to_delete}" у кількості {quantity} шт.' +
        ' Продовжити видалення інших послуг?',
        reply_markup=eq_del_menu
    )
    await OrderServices.ContinueDelete.set()


async def process_continue_delete(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    cart = user_data.get('cart')

    if cart.is_empty():
        await message.answer(
            "Ваш кошик порожній. Оберіть послугу з меню:",
            reply_markup=get_keyboard()
            )
        await OrderServices.ChoosingProduct.set()
        return

    await OrderServices.DeletingProductChoice.set()
    products_keyboard = get_cart_keyboard(cart)
    await message.answer(
        "Оберіть послугу для видалення:",
        reply_markup=products_keyboard
        )


async def process_stop_delete(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    cart = user_data.get('cart')
    cart_content = cart.summary(fetch_services())
    await OrderServices.CartOverview.set()
    await message.answer(
        f"Ваш кошик:\n{cart_content}",
        reply_markup=cart_menu
        )


async def process_getting_name(message: types.Message, state: FSMContext):
    name = message.text.strip()
    if not re.match(r'^[a-zA-Zа-яА-ЯіІїЇєЄґҐ\s]+$', name):
        await message.answer("Будь ласка, вкажіть ім'я")
        return

    if 2 <= len(name) <= 30 and name.isalpha():
        await state.update_data(name=name)
        await OrderServices.GettingPhone.set()
        await message.answer("Будь-ласка, вкажіть ваш номер телефону📱:")
    else:
        await message.answer("Будь ласка, вкажіть ім'я.")


async def process_getting_phone(message: types.Message, state: FSMContext):
    phone = message.text
    phone_pattern = re.compile(r'^(\+380\d{9}|38\d{10}|80\d{9}|0\d{9})$')

    if phone_pattern.match(phone):
        user_data = await state.get_data()
        user_data["phone_number"] = phone
        print(phone)
        cart = user_data.get('cart')
        order_summary = cart.summary(fetch_services())
        order_number = gs.get_next_order_id(services_orders)
        equipment_details = {
            "Номер замовлення": order_number,
            "Ім'я": user_data.get('name'),
            "Номер телефону": user_data.get('phone_number'),
            "Вартість": cart.total_cost(fetch_services())
        }

        for key in fetch_services():
            equipment_details[key] = cart.get(key)
        gs.write_order(equipment_details=equipment_details,
                       sheet_name=services_orders)

        order_details_message = (
            f"Номер вашого замовлення: {order_number}\n\n"
            f"{order_summary}"
        )
        await message.answer(
            "Дякуємо за те, що обрали нас😇 "
            "\nМы зв'яжемося з Вами найближчим часом!",
            )
        await bot.send_message(message.from_user.id,
                               order_details_message,
                               reply_markup=main_menu)
        await bot.send_message(OWNER_ID, order_details_message)
        await state.finish()
    else:
        await message.answer("Будь ласка, вкажіть вірний номер телефону"
                             " у форматі +380... або 097..."
                             )


async def cmd_return_to_main(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Ви обрали☝️", reply_markup=tools_menu)


async def default_msg(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    print(message.text)
    await message.reply("Не зрозумів🙄. Спробуйте ще раз.")


def reg_serv_order_handlers(production_disp: Dispatcher):
    # Для виведення кошика
    production_disp.register_message_handler(
        process_view_cart,
        text=CART_TEXT,
        state=OrderServices
    )
    ####
    production_disp.register_message_handler(
        cmd_return_to_main, text="Повернутися",
        state=OrderServices.ChoosingProduct
    )

    # Для команди "Замовити обладнання"
    production_disp.register_message_handler(
        cmd_start, text="Замовити послуги"
    )

    # Для вибору продукту
    production_disp.register_message_handler(
        process_product_choice,
        lambda message: message.text in fetch_services(),
        state=OrderServices.ChoosingProduct
    )

    # Для підтвердження замовлення
    production_disp.register_message_handler(
        process_confirm_order,
        text="Так",
        state=OrderServices.ConfirmingOrder
    )

    # Для повернення
    production_disp.register_message_handler(
        process_return,
        text="Повернутися",
        state=(OrderServices.ConfirmingOrder)
    )

    # Для встановлення кількості
    production_disp.register_message_handler(
        process_set_quantity,
        state=OrderServices.SettingQuantity
    )

    # Для продовження покупок
    production_disp.register_message_handler(
        process_continue_shopping,
        text="Продовжити покупки",
        state=OrderServices.Decision
    )

    # Для видалення товару
    production_disp.register_message_handler(
        process_delete_product_choice,
        text="Видалити товар",
        state=OrderServices.CartOverview
    )

    # Для підтвердження замовлення в кошику
    production_disp.register_message_handler(
        process_starter_getting_name,
        text="Підтвердити замовлення",
        state=OrderServices.CartOverview
    )

    # Для продовження покупок з кошика
    production_disp.register_message_handler(
        process_continue_shopping_from_cart,
        text="Продовжити покупки",
        state=OrderServices.CartOverview
    )

    # Для вибору продукту до видалення
    production_disp.register_message_handler(
        process_select_delete_product,
        lambda message: message.text in fetch_services(),
        state=OrderServices.DeletingProductChoice
    )

    # Для повернення до кошика після вибору видалення
    production_disp.register_message_handler(
        process_return_to_cart_from_delete_choice,
        text="Повернутися до кошика",
        state=OrderServices.DeletingProductChoice
    )

    # Для введення кількості до видалення
    production_disp.register_message_handler(
        process_deleting_quantity,
        lambda message: message.text.isdigit(),
        state=OrderServices.DeletingQuantity
    )

    # Для підтвердження видалення
    production_disp.register_message_handler(
        process_continue_delete,
        text="Так",
        state=OrderServices.ContinueDelete
    )

    # Для відміни видалення
    production_disp.register_message_handler(
        process_stop_delete,
        text="Ні",
        state=OrderServices.ContinueDelete
    )

    # Для введення імені
    production_disp.register_message_handler(
        process_getting_name,
        state=OrderServices.GettingName,
        content_types=types.ContentTypes.TEXT
    )

    # Для введення номера телефону
    production_disp.register_message_handler(
        process_getting_phone,
        state=OrderServices.GettingPhone,
        content_types=types.ContentTypes.TEXT
    )

    # Для обробки всіх інших текстових повідомлень
    production_disp.register_message_handler(
        default_msg,
        state=OrderServices,
        content_types=types.ContentTypes.TEXT
    )
