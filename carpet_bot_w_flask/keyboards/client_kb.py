# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def create_reply_keyboard(labels, include_back=True):
    buttons = [KeyboardButton(label) for label in labels]
    if include_back:
        buttons.append(KeyboardButton("Повернутися"))
    reply_keyboard = ReplyKeyboardMarkup(
        resize_keyboard=True, row_width=2, one_time_keyboard=True,
        input_field_placeholder="Оберіть розділ"
    )
    reply_keyboard.add(*buttons)
    return reply_keyboard


# Define all menu labels
menu_labels = {
    "main": [
        "Навчання", "Виробництво", "Послуги та обладнання",
        "Доставка", "Про нас"
    ],
    "tools": [
        "Замовити обладнання", "Замовити послуги",
    ],
    "production": [
        "Термінове замовлення", "Стандартний термін виготовлення"
    ],
    "learning": ["Онлайн курс", "Мастер-клас"],
    "order_confirm": ["Підтверджую замовлення", "Скасовую замовлення"],
    "carpet_confirm": ["Квадратний килим", "Круглий килим"],
    "back": ["Повернутися"],
    "equip_conf_order": ["Так", "Повернутися"],
    "equip_delete": ["Так", "Ні"],
    "cart_view": ["Видалити товар",
                  "Підтвердити замовлення", "Продовжити покупки"],
    "decision_keyboard": ["Продовжити покупки", "Кошик"],
    # new
    "about_us": ["Історія 'Milk Needle'", "Соціальні мережі",
                 "Наша майстерня та розклад", "Відгуки"],
    "social networks": ["Instagram", "Tik-Tok",
                        "YouTube", "Telegram"],
    "delivery": ["Укрпошта", "Нова пошта", "За кордон"]
}

# Define which menus should have a back button
menus_without_back = {'main', 'back', "order_confirm", "cart_view",
                      "equip_conf_order", "equip_delete", "decision_keyboard"}

# Generate keyboards based on labels
menus = {
    menu_name: create_reply_keyboard(
        labels, menu_name not in menus_without_back
        )
    for menu_name, labels in menu_labels.items()
}

# Menu mapping
main_menu = menus['main']

# Обладнання
tools_menu = menus['tools']
price_menu = menus['back']

# Доставка
delivery_menu = menus['delivery']
ukr_poshta = menus['back']
nova_poshta = menus['back']
abroad = menus['back']

# Вирбництво
production_menu = menus['production']
express_prod_menu = menus['back']
standard_prod_menu = menus['back']

# Навчанная
learning_menu = menus['learning']
online_menu = menus['back']
master_class = menus['back']

# Підтведження замовлення:
confirm_menu = menus["order_confirm"]

# Вибір килима:
carpet_menu = menus["carpet_confirm"]

# Для обладнання:
eq_conf_menu = menus["equip_conf_order"]
eq_del_menu = menus["equip_delete"]
cart_menu = menus["cart_view"]
eq_decis_menu = menus["decision_keyboard"]

# Про нас
about_us_menu = menus['about_us']
social_menu = menus['social networks']
feedbacks_menu = menus['back']
schedule_menu = menus['back']
insta_menu = menus['back']
tik_tok_menu = menus['back']
you_tube_menu = menus['back']
telegram_menu = menus['back']
milk_needle = menus['back']
