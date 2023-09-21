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
from config_data.config import owner_id, equipments_orders  # , equipments_data
from updater.google_updater import fetch_equipments

# Constants
OWNER_ID = owner_id
CART_TEXT = "Кошик"

gs = GoogleSheet()
# EQUIPMENTS = gs.fetch_data(equipments_data)



class OrderEquipment(StatesGroup):
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

    markup.add(*[KeyboardButton(product) for product in fetch_equipments()])

    if cart and not cart.is_empty():
        markup.add(KeyboardButton(CART_TEXT))

    markup.add(KeyboardButton("Повернутися"))

    return markup


def get_cart_keyboard(cart: ShoppingCart) -> ReplyKeyboardMarkup:
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(*[KeyboardButton(product) for product in cart.items.keys()])
    return markup


# async def fetch_equipments():
#     equipments = gs.fetch_data(equipments_data)
#     return equipments


async def cmd_start(message: types.Message, state: FSMContext):
    # global EQUIPMENTS
    # EQUIPMENTS = await fetch_equipments()
    cart = ShoppingCart()
    await state.update_data(cart=cart)
    await OrderEquipment.ChoosingProduct.set()
    markup = get_keyboard()
    await message.answer("Оберіть товар:", reply_markup=markup)


async def process_product_choice(message: types.Message, state: FSMContext):
    print(f"Chosen product key: {message.text}")
    print(f"All equipment data: {fetch_equipments()}")
    product_description = fetch_equipments()[message.text]["description"]
    product_price = fetch_equipments()[message.text]["price"]
    print(product_price)
    product_image_url = fetch_equipments()[message.text].get("image_url", None)

    text = (f"{product_description}\n\nЦіна: {product_price} грн."
            "\n\nБажаєте додати товар?")

    if product_image_url:
        await message.answer_photo(photo=product_image_url)
    await message.answer(text, reply_markup=eq_conf_menu)
    await state.update_data(chosen_product=message.text)
    await state.set_state(OrderEquipment.ConfirmingOrder.state)


async def process_confirm_order(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    chosen_product = user_data['chosen_product']
    await message.answer(
        f'Ви обрали "{chosen_product}". Вкажіть бажану кількість:',
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(OrderEquipment.SettingQuantity.state)


async def process_set_quantity(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    chosen_product = user_data['chosen_product']

    if message.text.isdigit() and int(message.text) > 0:
        quantity = int(message.text)
        cart = user_data['cart']
        cart.add(chosen_product, quantity)
        await state.update_data(cart=cart)
        await OrderEquipment.Decision.set()
        await message.answer(
            f'Ви обрали "{chosen_product}" у кількості {quantity} шт.'
            ' Бажаєте продовжити чи перейти до кошику для замовлення?',
            reply_markup=eq_decis_menu
        )
    else:
        await message.answer("Вкажіть дійсну кількість (більше нуля).")


async def process_return(message: types.Message, state: FSMContext):
    await state.set_state(OrderEquipment.ChoosingProduct.state)
    user_data = await state.get_data()
    cart = user_data.get('cart')
    markup = get_keyboard(cart)
    await message.answer("Оберіть товар:", reply_markup=markup)


async def process_continue_shopping(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    cart = user_data.get('cart')
    markup = get_keyboard(cart)
    await message.answer("Оберіть інший товар:", reply_markup=markup)
    await state.set_state(OrderEquipment.ChoosingProduct.state)


async def process_view_cart(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    cart = user_data.get('cart')
    cart_content = cart.summary(fetch_equipments())
    await OrderEquipment.CartOverview.set()
    await message.answer(f"Ваш кошик:\n{cart_content}",
                         reply_markup=cart_menu)


async def process_delete_product_choice(
        message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    cart = user_data.get('cart')
    await OrderEquipment.DeletingProductChoice.set()
    products_keyboard = get_cart_keyboard(cart)
    await message.answer("Оберіть товар для видалення:",
                         reply_markup=products_keyboard)


# видалив state: OrderFSM.CartOverview
async def process_starter_getting_name(
        message: types.Message):
    await OrderEquipment.GettingName.set()
    await message.answer("Вкажіть Ваше ім'я:")


async def process_continue_shopping_from_cart(
        message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    cart = user_data.get('cart')
    markup = get_keyboard(cart)
    await OrderEquipment.ChoosingProduct.set()
    await message.answer("Оберіть наступний товар:", reply_markup=markup)


async def process_select_delete_product(
        message: types.Message, state: FSMContext):
    await state.update_data(product_to_delete=message.text)
    await message.answer(
        f'Яку кількість "{message.text}" Ви бажаєте видалити?',
        reply_markup=types.ReplyKeyboardRemove()
    )
    await OrderEquipment.DeletingQuantity.set()


async def process_return_to_cart_from_delete_choice(message: types.Message):
    await message.answer("Перегляд кошика.")
    await OrderEquipment.CartOverview.set()


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
            "Ваш кошик порожній. Оберіть товар з меню:",
            reply_markup=get_keyboard()
            )
        await OrderEquipment.ChoosingProduct.set()
        return

    await message.answer(
        f'Ви видалили "{product_to_delete}" у кількості {quantity} шт.' +
        ' Продовжити видалення інших товарів?',
        reply_markup=eq_del_menu
    )
    await OrderEquipment.ContinueDelete.set()


async def process_continue_delete(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    cart = user_data.get('cart')

    if cart.is_empty():
        await message.answer(
            "Ваш кошик порожній. Оберіть товар з меню:",
            reply_markup=get_keyboard()
            )
        await OrderEquipment.ChoosingProduct.set()
        return

    await OrderEquipment.DeletingProductChoice.set()
    products_keyboard = get_cart_keyboard(cart)
    await message.answer(
        "Оберіть товар для видалення:",
        reply_markup=products_keyboard
        )


async def process_stop_delete(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    cart = user_data.get('cart')
    cart_content = cart.summary(fetch_equipments())
    await OrderEquipment.CartOverview.set()
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
        await OrderEquipment.GettingPhone.set()
        await message.answer("Будь-ласка, вкажіть Ваш номер телефону📱:")
    else:
        await message.answer("Будь ласка, вкажіть ім'я.")


async def process_getting_phone(message: types.Message, state: FSMContext):
    phone = message.text
    phone_pattern = re.compile(r'^(\+380\d{9}|38\d{10}|80\d{9}|0\d{9})$')

    if phone_pattern.match(phone):
        user_data = await state.get_data()
        user_data["phone_number"] = phone
        cart = user_data.get('cart')
        order_summary = cart.summary(fetch_equipments())
        order_number = gs.get_next_order_id(equipments_orders)
        equipment_details = {
            "Номер замовлення": order_number,
            "Ім'я": user_data.get('name'),
            "Номер телефону": user_data.get('phone_number'),
            "Вартість": cart.total_cost(fetch_equipments())
        }

        for key in fetch_equipments():
            equipment_details[key] = cart.get(key)
        gs.write_order(equipment_details=equipment_details,
                       sheet_name=equipments_orders)

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


def reg_equip_order_handlers(production_disp: Dispatcher):
    # Для виведення кошика
    production_disp.register_message_handler(
        process_view_cart,
        text=CART_TEXT,
        state=OrderEquipment
    )
    ####
    production_disp.register_message_handler(
        cmd_return_to_main, text="Повернутися",
        state=OrderEquipment.ChoosingProduct
    )

    # Для команди "Замовити обладнання"
    production_disp.register_message_handler(
        cmd_start, text="Замовити обладнання"
    )

    # Для вибору продукту
    production_disp.register_message_handler(
        process_product_choice,
        lambda message: message.text in fetch_equipments(),
        state=OrderEquipment.ChoosingProduct
    )

    # Для підтвердження замовлення
    production_disp.register_message_handler(
        process_confirm_order,
        text="Так",
        state=OrderEquipment.ConfirmingOrder
    )

    # Для повернення
    production_disp.register_message_handler(
        process_return,
        text="Повернутися",
        state=(OrderEquipment.ConfirmingOrder)
    )

    # Для встановлення кількості
    production_disp.register_message_handler(
        process_set_quantity,
        state=OrderEquipment.SettingQuantity
    )

    # Для продовження покупок
    production_disp.register_message_handler(
        process_continue_shopping,
        text="Продовжити покупки",
        state=OrderEquipment.Decision
    )

    # Для видалення товару
    production_disp.register_message_handler(
        process_delete_product_choice,
        text="Видалити товар",
        state=OrderEquipment.CartOverview
    )

    # Для підтвердження замовлення в кошику
    production_disp.register_message_handler(
        process_starter_getting_name,
        text="Підтвердити замовлення",
        state=OrderEquipment.CartOverview
    )

    # Для продовження покупок з кошика
    production_disp.register_message_handler(
        process_continue_shopping_from_cart,
        text="Продовжити покупки",
        state=OrderEquipment.CartOverview
    )

    # Для вибору продукту до видалення
    production_disp.register_message_handler(
        process_select_delete_product,
        lambda message: message.text in fetch_equipments(),
        state=OrderEquipment.DeletingProductChoice
    )

    # Для повернення до кошика після вибору видалення
    production_disp.register_message_handler(
        process_return_to_cart_from_delete_choice,
        text="Повернутися до кошика",
        state=OrderEquipment.DeletingProductChoice
    )

    # Для введення кількості до видалення
    production_disp.register_message_handler(
        process_deleting_quantity,
        lambda message: message.text.isdigit(),
        state=OrderEquipment.DeletingQuantity
    )

    # Для підтвердження видалення
    production_disp.register_message_handler(
        process_continue_delete,
        text="Так",
        state=OrderEquipment.ContinueDelete
    )

    # Для відміни видалення
    production_disp.register_message_handler(
        process_stop_delete,
        text="Ні",
        state=OrderEquipment.ContinueDelete
    )

    # Для введення імені
    production_disp.register_message_handler(
        process_getting_name,
        state=OrderEquipment.GettingName,
        content_types=types.ContentTypes.TEXT
    )

    # Для введення номера телефону
    production_disp.register_message_handler(
        process_getting_phone,
        state=OrderEquipment.GettingPhone,
        content_types=types.ContentTypes.TEXT
    )

    # Для обробки всіх інших текстових повідомлень
    production_disp.register_message_handler(
        default_msg,
        state=OrderEquipment,
        content_types=types.ContentTypes.TEXT
    )
