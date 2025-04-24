# - *- coding: utf- 8 - *-
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from tgbot.services.sqlite import get_settings, get_payments, get_all_categories, get_positions, get_items, \
get_pod_category, get_pod_categories, get_position
from design import products, profile, faq, support, refill, faq_chat_inl, faq_news_inl, support_inl, ref_system, promocode, \
last_purchases_text, back, close_text, refill_link_inl, refill_check_inl, qiwi_text, yoomoney_text, lava_text, lzt_text, crystalPay_text
from tgbot.data import config
from tgbot.utils.utils_functions import get_admins
from tgbot.services.sqlite import get_all_categories, get_positions, get_category, get_pod_category, get_position, \
get_items, buy_item, update_user, add_purchase
from tgbot.services.sqlite import get_payments
from tgbot.services.sqlite import get_variants
from tgbot.services.sqlite import get_variant_by_params
from tgbot.services.sqlite import get_position_by_short_id
from tgbot.services.sqlite import db_execute
from tgbot.services.sqlite import db_fetchone

from tgbot.utils.translator import auto_translate


# # # #  Смена языкаCallbackQueryHandler





def sub():
    s = InlineKeyboardMarkup()
    s.row(InlineKeyboardButton(text='Подписаться', url=config.channel_url))
    s.row(InlineKeyboardButton(text="Проверить✅", callback_data='subprov'))

    return s

def user_menu(user_id):
    keyboard = InlineKeyboardMarkup()

    kb = []
    
    kb.append(InlineKeyboardButton(auto_translate(user_id, "🛍️ Купить"), callback_data="products:open"))
    print(f"DEBUG: auto_translate = {auto_translate}")  # Проверяем данные
    print(f"DEBUG: user_id = {user_id}")  # Проверяем данные
    kb.append(InlineKeyboardButton(auto_translate(user_id, "👤 Профиль"), callback_data="profile"))
    kb.append(InlineKeyboardButton(faq, callback_data="faq:open"))
    kb.append(InlineKeyboardButton(auto_translate(user_id, "💎Support"), callback_data="support:open"))
    kb.append(InlineKeyboardButton(auto_translate(user_id,"🌍 Язык"), callback_data="change_language"))
    kb.append(InlineKeyboardButton(auto_translate(user_id, "⚙️ Меню Администратора"), callback_data="admin_menu"))

    keyboard.add(kb[0], kb[1])
    keyboard.add(kb[2], kb[3])
    keyboard.add(kb[4])

    if user_id in get_admins():
        keyboard.add(kb[5])

    return keyboard


def faq_inl():
    keyboard = InlineKeyboardMarkup()
    kb = []
    news = get_settings()['news']
    chat = get_settings()['chat']

    kb.append(InlineKeyboardButton(faq_chat_inl, url=chat))
    kb.append(InlineKeyboardButton(faq_news_inl, url=news))

    keyboard.add(kb[0], kb[1])

    return keyboard

def support_inll():
    keyboard = InlineKeyboardMarkup()
    kb = []
    kb.append(InlineKeyboardButton(support_inl, url=get_settings()['support']))

    keyboard.add(kb[0])

    return keyboard

def chat_inl():
    keyboard = InlineKeyboardMarkup()
    kb = []
    link = get_settings()['chat']

    kb.append(InlineKeyboardButton(faq_chat_inl, url=link))

    keyboard.add(kb[0])

    return keyboard

def news_inl():
    keyboard = InlineKeyboardMarkup()
    kb = []
    link = get_settings()['news']

    kb.append(InlineKeyboardButton(faq_news_inl, url=link))

    keyboard.add(kb[0])

    return keyboard

def profile_inl(user_id):
    keyboard = InlineKeyboardMarkup()
    kb = []

    kb.append(InlineKeyboardButton(auto_translate(user_id, "💎 Реферальная система"), callback_data="ref_system"))

    kb.append(InlineKeyboardButton(auto_translate(user_id, "⭐ Последние покупки"), callback_data="last_purchases"))
    kb.append(InlineKeyboardButton(auto_translate(user_id, "⬅ Back"), callback_data="back_to_user_menu"))

    keyboard.add(kb[0])
    keyboard.add(kb[1])
    keyboard.add(kb[2])

    return keyboard

def back_to_profile():
    keyboard = InlineKeyboardMarkup()

    keyboard.add(InlineKeyboardButton(back, callback_data="profile"))

    return keyboard

def back_to_user_menu():
    keyboard = InlineKeyboardMarkup()

    keyboard.add(InlineKeyboardButton(back, callback_data="back_to_user_menu"))

    return keyboard


def close_inl():
    keyboard = InlineKeyboardMarkup()
    kb = []

    kb.append(InlineKeyboardButton(close_text, callback_data="close_text_mail"))

    keyboard.add(kb[0])

    return keyboard

def refill_open_inl(way, amount, link, id):
    keyboard = InlineKeyboardMarkup()
    kb = []

    kb.append(InlineKeyboardButton(refill_link_inl, url=link))
    kb.append(InlineKeyboardButton(refill_check_inl, callback_data=f"check_opl:{way}:{amount}:{id}"))

    keyboard.add(kb[0])
    keyboard.add(kb[1])

    return keyboard

def refill_inl():
    keyboard = InlineKeyboardMarkup()
    kb = []
    qiwi = get_payments()['pay_qiwi']
    yoomoney = get_payments()['pay_yoomoney']
    lava = get_payments()['pay_lava']
    crystal = get_payments()['pay_crystal']
    lolz = get_payments()['pay_lolz']

    if qiwi == "True":
        kb.append(InlineKeyboardButton(qiwi_text, callback_data="refill:qiwi"))
    if yoomoney == "True":
        kb.append(InlineKeyboardButton(yoomoney_text, callback_data="refill:yoomoney"))
    if lava == "True":
        kb.append(InlineKeyboardButton(lava_text, callback_data="refill:lava"))
    if lolz == "True":
        kb.append(InlineKeyboardButton(lzt_text, callback_data="refill:lolz"))
    if crystal == "True":
        kb.append(InlineKeyboardButton(crystalPay_text, callback_data="refill:crystal"))

    if len(kb) == 5:
        keyboard.add(kb[0])
        keyboard.add(kb[1], kb[2])
        keyboard.add(kb[3], kb[4])
    elif len(kb) == 4:
        keyboard.add(kb[0], kb[1])
        keyboard.add(kb[2], kb[3])
    elif len(kb) == 3:
        keyboard.add(kb[0])
        keyboard.add(kb[1], kb[2])
    elif len(kb) == 2:
        keyboard.add(kb[0], kb[1])
    elif len(kb) == 1:
        keyboard.add(kb[0])

    keyboard.add(InlineKeyboardButton(back, callback_data="back_to_user_menu"))

    return keyboard

def back_to_user_menu():
    keyboard = InlineKeyboardMarkup()
    kb = []

    keyboard.add(InlineKeyboardButton(back, callback_data="back_to_user_menu"))

    return keyboard

def open_products():
    keyboard = InlineKeyboardMarkup()

    for category in get_all_categories():
        name = category['name']
        cat_id = category['id']
        keyboard.add(InlineKeyboardButton(name, callback_data=f"open_category:{cat_id}"))

    keyboard.add(InlineKeyboardButton(back, callback_data="back_to_user_menu"))

    return keyboard

def open_pod_cat_positions(pod_cat_id):
    keyboard = InlineKeyboardMarkup()

    for pos in get_positions(pod_cat_id=pod_cat_id):
        name = pos['name']
        pos_id = pos['id']
        price = pos['price']
        items = f"{len(get_items(position_id=pos_id))}шт"
        if pos['infinity'] == "+":
            items = "[Безлимит]"
        keyboard.add(InlineKeyboardButton(f"{name} | {price}₽ | {items}", callback_data=f"open_pos:{pos_id}"))

    keyboard.add(InlineKeyboardButton(back, callback_data=f"open_category:{get_pod_category(pod_cat_id)['cat_id']}"))

    return keyboard
def open_positions(cat_id):
    keyboard = InlineKeyboardMarkup()

    for pod_cat in get_pod_categories(cat_id):
        name = pod_cat['name']
        pod_cat_id = pod_cat['id']
        keyboard.add(InlineKeyboardButton(name, callback_data=f"open_pod_cat:{pod_cat_id}"))
    for pos in get_positions(cat_id):
        if pos['pod_category_id'] is not None:
            continue
        name = pos['name']
        pos_id = pos['id']
        price = pos['price']
        items = f"{len(get_items(position_id=pos_id))}шт"
        if pos['infinity'] == "+":
            items = "[Безлимит]"
        keyboard.add(InlineKeyboardButton(f"{name}", callback_data=f"open_pos:{pos_id}"))

    keyboard.add(InlineKeyboardButton(back, callback_data=f"products:open"))

    return keyboard

def pos_buy_inl(pos_id, color, storage, price, user_id):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(auto_translate(user_id, "🛍️ Купить"), callback_data=f"buy_pos1:{pos_id}:{color}:{storage}:{price}"))
    keyboard.add(InlineKeyboardButton(back, callback_data=f"open_category:{get_position(pos_id)['category_id']}"))
    return keyboard

def choose_buy_items(pos_id, amount):
    keyboard = InlineKeyboardMarkup()
    kb = []

    kb.append(InlineKeyboardButton(f"✅", callback_data=f"buy_items:yes:{pos_id}:{amount}"))
    kb.append(InlineKeyboardButton(f"❌", callback_data=f"buy_items:no:{pos_id}:{amount}"))

    keyboard.add(kb[0], kb[1])

    return keyboard
    
def payment_method_menu(pos_id, amount_rub, color, storage):
    keyboard = InlineKeyboardMarkup()
    
    # Кодируем данные в короткую строку
    short_color = color[:3].lower()  # Оставляем 3 буквы от цвета (например, "чер")
    short_storage = storage.replace("GB", "")  # Убираем "GB" (например, "256")
    
    keyboard.add(InlineKeyboardButton("💳 Карта", callback_data=f"pay:card:{pos_id}:{amount_rub}:{short_color}:{short_storage}"))
    keyboard.add(InlineKeyboardButton("₿ Криптовалюта", callback_data=f"pay:crypto:{pos_id}:{amount_rub}:{short_color}:{short_storage}"))
    
    return keyboard
    
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import Dispatcher

def crypto_currency_menu(pos_id, amount_rub, color, storage, user_id, main_key=None):
    keyboard = InlineKeyboardMarkup()
    payments = get_payments()  # Получаем доступные криптовалюты
    
    crypto_groups = {
        "USDT": {"USDT_ERC20": "USDT (ERC20)", "USDT_TRC20": "USDT (TRC20)", "USDT_BEP20": "USDT (BEP20)"},
        "USDC": {"USDC_ERC20": "USDC (ERC20)", "USDC_TRC20": "USDC (TRC20)", "USDC_SOL": "USDC (SOL)"}
    }
    
    other_crypto = {
        "btc": "BTC",
        "ETH": "ETH",
        "TRX": "TRX",
        "BNB": "BNB",
        "BUSD": "BUSD",
        "SOL": "SOL",
        "LTC": "Litecoin"
    }
    
    if main_key and main_key in crypto_groups:
        # Отображаем подменю с вариантами сети
        for key, name in crypto_groups[main_key].items():
            callback_data = f"pay_crypto:{key}:{pos_id}:{round(float(amount_rub), 2)}:{color}:{storage}"
            keyboard.add(InlineKeyboardButton(name, callback_data=callback_data))
        
        # Кнопка назад
        keyboard.add(InlineKeyboardButton("⬅ Назад", callback_data=f"crypto_menu:{pos_id}:{amount_rub}:{color}:{storage}"))
    else:
        # Основное меню криптовалют
        for main_key, sub_options in crypto_groups.items():
            available = any(payments.get(f"pay_{sub_key}") == "True" for sub_key in sub_options)
            if available:
                keyboard.add(InlineKeyboardButton(main_key, callback_data=f"crypto_menu:{pos_id}:{amount_rub}:{color}:{storage}:{main_key}"))
        
        # Добавляем остальные криптовалюты
        for key, name in other_crypto.items():
            if payments.get(f"pay_{key}") == "True":  
                callback_data = f"pay_crypto:{key}:{pos_id}:{round(float(amount_rub), 2)}:{color}:{storage}"
                keyboard.add(InlineKeyboardButton(name, callback_data=callback_data))
        
        # Кнопка назад
        keyboard.add(InlineKeyboardButton(auto_translate(user_id, "⬅ Назад"), callback_data=f"buy_pos1:{pos_id}"))
    
    return keyboard

# Обработчик нажатий на кнопки меню
async def crypto_callback_handler(call: types.CallbackQuery):
    data = call.data.split(":")
    
    if data[0] == "crypto_menu":
        pos_id = data[1]
        amount_rub = data[2]
        color = data[3]
        storage = data[4]
        user_id = call.from_user.id

        # Проверяем, передан ли main_key (если длина data больше 5, значит, это подменю)
        main_key = data[5] if len(data) > 5 else None

        # Обновляем клавиатуру в сообщении
        keyboard = crypto_currency_menu(pos_id, amount_rub, color, storage, user_id, main_key)
        await call.message.edit_reply_markup(reply_markup=keyboard)

# Регистрация хендлера в aiogram
def register_crypto_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(crypto_callback_handler, Text(startswith="crypto_menu"))


#def color_selection_keyboard(colors, product_id):
#    keyboard = InlineKeyboardMarkup()
#    for color in colors:
#        keyboard.add(InlineKeyboardButton(color, callback_data=f"select_color:{color}:{product_id}"))
#    return keyboard

def color_selection_keyboard(colors, product_id, pos, user_id):
    """Клавиатура выбора цвета с фото и инфо о товаре."""
    keyboard = InlineKeyboardMarkup()
    for color in colors:
        keyboard.add(InlineKeyboardButton(color, callback_data=f"select_color:{color}:{product_id}"))

    # Получаем категорию
    cat = get_category(pos['category_id'])
    cat_name = cat['name'] if cat else "Неизвестно"

    # Диапазон цен
    variants = get_variants(product_id)
    prices = [v['price'] for v in variants]
    min_price, max_price = min(prices), max(prices)
    price_range = f"{min_price}-{max_price} USD"

    text = auto_translate(user_id, f"""
💎 <b>Категория:</b> {cat_name}
🛍️ <b>Продукт:</b> {pos['name']}
💰 <b>Цена:</b> {price_range}

<b>Выберите цвет:</b>
""")

    return keyboard, text, pos.get("photo")
    


#def storage_selection_keyboard(storages, product_id, color):
#    keyboard = InlineKeyboardMarkup()
#    for storage in storages:
#        keyboard.add(InlineKeyboardButton(storage, callback_data=f"select_storage:{storage}:{product_id}:{color}"))
#    return keyboard

def storage_selection_keyboard(storages, product_id, color, pos, user_id):
    """Клавиатура выбора памяти с фото, инфо о товаре и ценами на кнопках."""
    keyboard = InlineKeyboardMarkup()

    # Получаем категорию
    cat = get_category(pos['category_id'])
    cat_name = cat['name'] if cat else "Неизвестно"
    variants = get_variants(product_id)
    prices = [v['price'] for v in variants]
    min_price, max_price = min(prices), max(prices)
    price_range = f"{min_price}-{max_price} USD"

    for storage in storages:
        variant = get_variant_by_params(product_id, color, storage)
        price = variant["price"] if variant else "N/A"
        keyboard.add(InlineKeyboardButton(f"{storage} - {price} USD", callback_data=f"select_storage:{storage}:{product_id}:{color}"))
        
    text = auto_translate(user_id, f"""
💎 <b>Категория:</b> {cat_name}
🛍️ <b>Продукт:</b> {pos['name']}
💰 <b>Цена:</b> {price_range}

<b>Выберите объем памяти:</b>
""")


    return keyboard, text, pos.get("photo")