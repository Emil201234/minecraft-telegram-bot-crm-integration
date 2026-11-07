from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.enums import ButtonStyle

# ------ Кнопки ------

# buttons - auth

btn_reg_inline = InlineKeyboardButton(text="Авторизоваться 📝", style=ButtonStyle.SUCCESS, callback_data="reg")
btn_auth_link_inline = InlineKeyboardButton(text="С помощью /link", callback_data="auth_link", style=ButtonStyle.DANGER)
btn_auth_password_inline = InlineKeyboardButton(text="С помощью пароля", callback_data="auth_password", style=ButtonStyle.SUCCESS)

# buttons - menu

btn_shop = KeyboardButton(text="Просмотреть товары 🛒")
btn_about_me = KeyboardButton(text="Обо мне 🚹")
btn_tech_support = KeyboardButton(text="Тех. поддержка 🛠")
btn_suggestions = KeyboardButton(text="Предложить идею 💡")

# buttons - shop - menu

btn_privileges_inline = InlineKeyboardButton(text="Привилегии 👑", callback_data="privileges", style=ButtonStyle.PRIMARY)
btn_tokens_inline = InlineKeyboardButton(text="Токены 💵", callback_data="tokens", style=ButtonStyle.SUCCESS)
btn_donat_boxs_inline = InlineKeyboardButton(text="Кейсы 📦", callback_data="donat_boxs", style=ButtonStyle.DANGER)

btn_shop_return_inline = InlineKeyboardButton(text="Вернуться к категориям ↩️", callback_data="shop_menu")

# buttons - shop - privileges

btn_privileges_vip_inline = InlineKeyboardButton(text="VIP 🎫", callback_data="vip")
btn_privileges_premium_inline = InlineKeyboardButton(text="PREMIUM ✨", callback_data="premium")
btn_privileges_elite_inline = InlineKeyboardButton(text="ELITE 💎", callback_data="elite")

# buttons - shop - tokens

btn_tokens_500_inline = InlineKeyboardButton(text="500 Токенов 🪙", callback_data="tokens_500")
btn_tokens_1000_inline = InlineKeyboardButton(text="1000 Токенов 💴", callback_data="tokens_1000")
btn_tokens_2000_inline = InlineKeyboardButton(text="2000 Токенов 💵", callback_data="tokens_2000")
btn_tokens_5000_inline = InlineKeyboardButton(text="5000 Токенов 💸", callback_data="tokens_5000")
btn_tokens_10000_inline = InlineKeyboardButton(text="10000 Токенов 💰", callback_data="tokens_10000")

# buttons - shop - boxs

btn_boxs_privileges_inline = InlineKeyboardButton(text="Кейс с привилегиями 💎", callback_data="boxs_privileges")
btn_boxs_tokens_inline = InlineKeyboardButton(text="Кейс с токенами 💵", callback_data="boxs_tokens")
btn_boxs_money_inline = InlineKeyboardButton(text="Кейс с монетами 🪙", callback_data="boxs_money")

# ------ Клавиатуры ------

keyboard_reg_inline = InlineKeyboardMarkup(
    inline_keyboard=[
        [btn_reg_inline]
    ]
)

keyboard_choose_auth_inline = InlineKeyboardMarkup(
    inline_keyboard=[
        [btn_auth_password_inline, btn_auth_link_inline]
    ]
)

keyboard_menu_reply = ReplyKeyboardMarkup(
    keyboard=[
        [btn_about_me],
        [btn_shop],
        [btn_tech_support, btn_suggestions]
    ],
    resize_keyboard=True
)

keyboard_shop_menu_inline = InlineKeyboardMarkup(
    inline_keyboard=[
        [btn_privileges_inline],
        [btn_tokens_inline],
        [btn_donat_boxs_inline]
    ]
)

keyboard_shop_privileges_inline = InlineKeyboardMarkup(
    inline_keyboard=[
        [btn_privileges_elite_inline],
        [btn_privileges_premium_inline],
        [btn_privileges_vip_inline],
        [btn_shop_return_inline]
    ]
)

keyboard_shop_tokens_inline = InlineKeyboardMarkup(
    inline_keyboard=[
        [btn_tokens_10000_inline],
        [btn_tokens_5000_inline],
        [btn_tokens_2000_inline],
        [btn_tokens_1000_inline],
        [btn_tokens_500_inline],
        [btn_shop_return_inline]
    ]
)

keyboard_shop_boxs_inline = InlineKeyboardMarkup(
    inline_keyboard=[
        [btn_boxs_privileges_inline],
        [btn_boxs_tokens_inline],
        [btn_boxs_money_inline],
        [btn_shop_return_inline]
    ]
)


