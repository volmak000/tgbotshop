# - *- coding: utf- 8 - *-
import asyncio
from tgbot.utils.utils_functions import get_admins
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery
from tgbot.services.sqlite import get_user
from design import no_cats, available_cats, no_products, current_cat, current_pod_cat, open_pos_text, here_count_products, \
choose_buy_product, no_balance, no_product, no_num_count, choose_buy_products, gen_products, yes_buy_items, otmena_buy, edit_prod
from tgbot.keyboards.inline_user import back_to_user_menu, user_menu, open_products, open_positions, open_pod_cat_positions, \
pos_buy_inl, choose_buy_items
from tgbot.services.sqlite import get_all_categories, get_positions, get_category, get_pod_category, get_position, \
get_items, buy_item, update_user, add_purchase
from tgbot.data.loader import dp, bot
from tgbot.utils.utils_functions import split_messages, get_date, get_unix, send_admins
from contextlib import suppress
from aiogram.utils.exceptions import MessageCantBeDeleted
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from tgbot.utils.crypto import convert_rub_to_crypto  # Импорт функции конвертации
from tgbot.keyboards.inline_user import payment_method_menu
from tgbot.keyboards.inline_user import crypto_currency_menu
from tgbot.keyboards.inline_user import color_selection_keyboard
from tgbot.keyboards.inline_user import storage_selection_keyboard
from tgbot.services.sqlite import get_payments
from tgbot.services.sqlite import get_variants
from tgbot.services.sqlite import get_variant_by_params
from tgbot.services.sqlite import get_position_by_short_id
from tgbot.services.sqlite import db_execute
from tgbot.services.sqlite import db_fetchone

from tgbot.utils.translator import auto_translate

COLOR_MAP = {
    "blk": "Black",
    "whe": "White",
    "red": "Red",
    "ble": "Blue",
    "grn": "Green",
    "yew": "Yellow",
    "pue": "Purple",
    "pik": "Pink",
    "sir": "Silver",
    "spy": "Space Gray",
    "mit": "Midnight",
    "stt": "Starlight",
    "god": "Gold",
    "gre": "Graphite",
    "sie": "Sierra Blue",
    "aln": "Alpine Green",
    "dee": "Deep Purple",
    "nam": "Natural Titanium",
    "blm": "Blue Titanium",
    "whm": "White Titanium",
    "blm": "Black Titanium"
}


@dp.callback_query_handler(text="products:open", state="*")
async def open_products_users(call: CallbackQuery, state: FSMContext):
    await state.finish()
    user_id = call.from_user.id  # Получаем ID пользователя

    if len(get_all_categories()) < 1:
        await call.message.delete()
        await call.message.answer(no_cats, reply_markup=back_to_user_menu())
    else:
        await call.message.delete()
        await call.message.answer(auto_translate(user_id, f"<b>Доступные на данный момент категории:</b>"), reply_markup=open_products())

@dp.callback_query_handler(text_startswith="open_category:", state="*")
async def open_cat_for_buy(call: CallbackQuery, state: FSMContext):
    await state.finish()
    user_id = call.from_user.id  # Получаем ID пользователя
    cat_id = call.data.split(":")[1]
    category = get_category(cat_id)
    
    if len(get_positions(cat_id)) < 1:
        await call.message.delete()
        await call.message.answer(no_products, reply_markup=back_to_user_menu())
    else:
        await call.message.delete()

        if category['photo']:
            await call.message.answer_photo(photo=category['photo'], caption=auto_translate(user_id, "<b>Текущая категория: {name}:</b>").format(name=get_category(cat_id)['name']), reply_markup=open_positions(cat_id))
        else:
            await call.message.answer(auto_translate(user_id, f"<b>Текущая категория: {name}:</b>").format(name=get_category(cat_id)['name']), reply_markup=open_positions(cat_id))

@dp.callback_query_handler(text_startswith="open_pod_cat:", state="*")
async def open_pod_cat(call: CallbackQuery, state: FSMContext):
    await state.finish()

    pod_cat_id = call.data.split(":")[1]

    if len(get_positions(pod_cat_id=pod_cat_id)) < 1:
        await call.message.delete()
        await call.message.answer(no_products)
    else:
        await call.message.delete()
        await call.message.answer(current_pod_cat.format(name=get_pod_category(pod_cat_id)['name']), reply_markup=open_pod_cat_positions(pod_cat_id))

@dp.callback_query_handler(text_startswith="open_pos:", state="*")
async def open_pos(call: CallbackQuery, state: FSMContext):
    await state.finish()
    pos_id = call.data.split(":")[1]
    pos = get_position(pos_id)
    cat = get_category(pos['category_id'])
    user_id = call.from_user.id  # Получаем ID пользователя
    # Проверяем доступные цвета для товара
    variants = get_variants(pos_id)
    colors = list(set(v['color'] for v in variants))

    if not colors:
        await call.message.answer(auto_translate(user_id, "❌ Нет доступных вариаций для этого товара."))
        return

    # Получаем клавиатуру, текст и фото
    keyboard, text, photo = color_selection_keyboard(colors, pos_id, pos, user_id)

    await state.update_data(product_id=pos_id)

    if photo and photo != "-":
        await call.message.delete()
        await bot.send_photo(chat_id=call.from_user.id, photo=photo, caption=text, reply_markup=keyboard, parse_mode="HTML")
    else:
        await call.message.answer(text, reply_markup=keyboard, parse_mode="HTML")

####

@dp.callback_query_handler(text_startswith="select_color:", state="*")
async def select_color(call: CallbackQuery, state: FSMContext):
    _, color, product_id = call.data.split(":")
    pos = get_position(product_id)
    user_id = call.from_user.id  # Получаем ID пользователя
    variants = get_variants(product_id)
    storages = list(set(v['storage_capacity'] for v in variants if v['color'] == color))

    # Получаем клавиатуру и текст с фото
    keyboard, text, photo = storage_selection_keyboard(storages, product_id, color, pos, user_id)

    await state.update_data(color=color)
    
    if photo and photo != "-":
        await call.message.delete()
        await bot.send_photo(chat_id=call.from_user.id, photo=photo, caption=text, reply_markup=keyboard, parse_mode="HTML")
    else:
        await call.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")


@dp.callback_query_handler(text_startswith="select_storage:", state="*")
async def select_storage(call: CallbackQuery, state: FSMContext):
    _, storage, product_id, color = call.data.split(":")
    variant = get_variant_by_params(product_id, color, storage)

    await state.update_data(storage=storage, price=variant['price'])
    pos = get_position(product_id)
    cat = get_category(pos['category_id'])
    user_id = call.from_user.id  # Получаем ID пользователя
    msg = auto_translate(user_id, f"""
<b>💎 Категория:</b> {cat['name']}
<b>🛍️ Продукт: </b> {pos['name']}
<b>💰 Цена: </b> {variant['price']} USD
<b>🎨 Цвет: </b> {color}
<b>💾 Память: </b> {storage} 

🎲 <b>Описание:</b> {pos['description'] or '❗️ Не указано'}
""")
    

    keyboard = pos_buy_inl(product_id, color, storage, variant['price'], user_id)

    if pos['photo'] and pos['photo'] != "-":
        try:
            await call.message.delete()
        except Exception:
            pass  # Если сообщение уже удалено, пропускаем ошибку

        await bot.send_photo(chat_id=call.from_user.id, photo=pos['photo'], caption=msg, reply_markup=keyboard, parse_mode="HTML")
    else:
        try:
            await call.message.edit_text(msg, reply_markup=keyboard, parse_mode="HTML")
        except aiogram.utils.exceptions.BadRequest:
            await call.message.answer(msg, reply_markup=keyboard, parse_mode="HTML")




# # # до эт рб вар

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Меню выбора способа оплаты
def payment_method_menu(pos_id, amount_rub, color, storage, user_id):
    keyboard = InlineKeyboardMarkup()
    
    short_color = color[:2] + color[-1].lower()  # Первые 3 буквы от цвета
    short_storage = storage.replace("TB", "").replace("GB", "")  # Убираем "GB"
    
    card_callback = f"pay_method:card:{pos_id}:{amount_rub}:{short_color}:{short_storage}"
    crypto_callback = f"pay_method:crypto:{pos_id}:{amount_rub}:{short_color}:{short_storage}"
    
    print(f"DEBUG: card_callback = {card_callback}")  # Проверяем данные
    print(f"DEBUG: crypto_callback = {crypto_callback}")  # Проверяем данные
    
    keyboard.add(InlineKeyboardButton(auto_translate(user_id, "💳 bank card"), callback_data=card_callback))
    keyboard.add(InlineKeyboardButton(auto_translate(user_id, "₿ Криптовалюта"), callback_data=crypto_callback))
    
    return keyboard


# Меню выбора криптовалюты


# Кнопка "Я оплатил"
def confirm_payment_button(pos_id, color, storage, price):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("✅ I Paid", callback_data=f"confirm_payment:{pos_id}:{color}:{storage}:{price}"))
    return keyboard

# Кнопки для админа (Принять/Отклонить)
def admin_payment_decision(pos_id, user_id, color, storage, price):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("✅ Принять", callback_data=f"accept_card:{user_id}:{pos_id}:{color}:{storage}:{price}"))
    keyboard.add(InlineKeyboardButton("❌ Отклонить", callback_data=f"decline_card:{user_id}"))
    return keyboard
# Кнопки финального подтверждения оплаты
def final_admin_decision(user_id, pos_id):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("✅ Подтвердить оплату", callback_data=f"final_approve:{user_id}:{pos_id}"))
    keyboard.add(InlineKeyboardButton("❌ Отклонить оплату", callback_data=f"final_decline:{user_id}"))
    return keyboard

@dp.callback_query_handler(text_startswith='buy_pos1:', state="*")
async def pos_buy(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()  # Получаем данные перед очисткой state
    user_id1 = call.message.from_user.id
    color = data.get("color", "Не указан")
    storage = data.get("storage", "Не указан")
    price = data.get("price", 0)

    await state.finish()  # Очищаем state только после получения данных
    user_id = call.from_user.id  # Получаем ID пользователя
    await call.message.answer(auto_translate(user_id, f"<b>Выберите способ оплаты:</b>\n\n💰 <b>Стоимость:</b> {price} USD\n🎨 <b>Цвет:</b> {color}\n💾 <b>Память:</b> {storage}"), 
                                 reply_markup=payment_method_menu(call.data.split(":")[1], price, color, storage, user_id))

@dp.callback_query_handler(text_startswith='pay_method:', state="*")
async def payment_method(call: CallbackQuery, state: FSMContext):
    data = call.data.split(":")
    
    if len(data) < 6:  # Исправлено: ожидаем 6 элементов (метод, pos_id, сумма, цвет, память)
        await call.message.answer("❌ Ошибка: Некорректные данные в кнопке оплаты.")
        return
    
    method, pos_id, amount_rub, color, storage = data[1:]
   # Восстанавливаем полное название цвета
    color1 = COLOR_MAP.get(color.lower(), "Неизвестный цвет")
    storage_value = int(storage)
    storage_unit = "TB" if storage_value < 10 else "GB"
    user_id = call.from_user.id  # Получаем ID пользователя
    if method == "crypto":
        await call.message.edit_text(auto_translate(user_id, "Выберите криптовалюту для оплаты:"), 
                                     reply_markup=crypto_currency_menu(pos_id, amount_rub, color, storage, user_id))
    
    elif method == "card":
        pos = get_position(pos_id)
        admin_msg_template = auto_translate(user_id, "💳 Запрос на оплату картой!\n"
                     f"👤 Пользователь: @{call.from_user.username} ({call.from_user.id})\n"
                     f"🛒 Продукт: {pos['name']}\n"
                     f"🎨 Цвет: {color1}\n"
                     f"💾 Память: {storage}{storage_unit}\n"
                     f"💵 Сумма: {amount_rub}")
                     
        admin_msg = admin_msg_template.format(
            username=call.from_user.username,
            user_id=call.from_user.id,
            product_name=pos['name'],
            color=color1,
            storage=storage,
            storage_unit=storage_unit,
            amount=amount_rub
            )
        
        for admin_id in get_admins():
            await bot.send_message(admin_id, admin_msg, 
                                   reply_markup=admin_payment_decision(pos_id, call.from_user.id, color, storage, amount_rub))  # Исправлено
        
        await call.message.edit_text(auto_translate(user_id, "⏳ Ожидайте, админ вышлет вам реквизиты для оплаты."))
        
@dp.callback_query_handler(text_startswith='pay_crypto:', state="*")
async def send_crypto_address(call: CallbackQuery, state: FSMContext):
    print(f"✅ Обработчик вызван! call.data = {call.data}")  # Отладка
    user_id = call.from_user.id  # Получаем ID пользователя
    # Разбираем callback_data
    data = call.data.split(":")
    if len(data) < 5:
        await call.answer(auto_translate(user_id, "❌ Ошибка: некорректные данные кнопки!"), show_alert=True)
        return

    crypto, pos_id, amount_rub, color, storage = data[1:]
    print(f"DEBUG: crypto={crypto}, pos_id={pos_id}, amount_rub={amount_rub}, color={color}, storage={storage}")

    # Получаем данные о товаре
    pos = get_position(pos_id)
    if not pos:
        await call.answer(auto_translate(user_id, "❌ Ошибка: Продукт не найден."), show_alert=True)
        return

    # Получаем адрес крипто-кошелька
    payments = get_payments()
    address = payments.get(f"{crypto}_adrs")
    if not address:
        await call.answer(auto_translate(user_id, "❌ Ошибка: адрес кошелька не найден."), show_alert=True)
        return

    # Конвертируем сумму в криптовалюту
    amount_crypto = round(convert_rub_to_crypto(float(amount_rub), crypto), 4)
    if amount_crypto == 0.0:
        await call.answer(auto_translate(user_id, "❌ Ошибка: не удалось получить курс криптовалюты."), show_alert=True)
        return

    # Сохраняем данные в БД
    db_execute(
        "INSERT INTO temp_payments (pos_id, user_id, crypto, amount_crypto, color, storage) VALUES (?, ?, ?, ?, ?, ?)",
        (pos_id, call.from_user.id, crypto, amount_crypto, color, storage)
    )

    # Получаем ID последнего вставленного платежа
    payment = db_fetchone("SELECT id FROM temp_payments WHERE user_id = ? ORDER BY id DESC LIMIT 1", (call.from_user.id,))
    if not payment:
        await call.answer(auto_translate(user_id, "❌ Ошибка: не удалось создать платёж."), show_alert=True)
        return
    color1 = COLOR_MAP.get(color.lower(), "Неизвестный цвет")
    storage_value = int(storage)
    storage_unit = "TB" if storage_value < 10 else "GB"
    payment_id = payment["id"]
    print(f"✅ Данные сохранены в БД (payment_id = {payment_id}) и отправлены пользователю.")

    # Отправляем пользователю данные для оплаты
    msg = auto_translate(user_id, f"""
🛍️ Продукт: {pos['name']}  
🎨 Цвет: {color1}  
💾 Память: {storage}{storage_unit}  

💰 Оплата <b> {crypto.upper()} </b>  
📍 Адрес: <code>{address} </code> 
💵 Сумма: <b>{amount_crypto} {crypto.upper()}</b>  

После отправки нажмите «✅ I Paid».
""")

    keyboard = InlineKeyboardMarkup().add(
        InlineKeyboardButton(auto_translate(user_id, "✅ I Paid"), callback_data=f"confirm_payment:{payment_id}")  # Передаём только ID!
    )

    await call.message.edit_text(msg, reply_markup=keyboard, parse_mode="HTML")




@dp.callback_query_handler(text_startswith='accept_card:', state="*")
async def accept_card_payment(call: CallbackQuery, state: FSMContext):
    _, user_id, pos_id, color, storage, price = call.data.split(":")
    
    await state.update_data(card_payment_user=user_id, 
                            card_payment_pos=pos_id,
                            selected_color=color,
                            selected_storage=storage,
                            final_price=price)
    
    await call.message.answer(auto_translate(user_id, "✅ Введите Ссылку для оплаты:"))
    await state.set_state("waiting_card_number")

@dp.message_handler(state="waiting_card_number")
async def send_card_info(msg: Message, state: FSMContext):
    data = await state.get_data()
    user_id = data.get("card_payment_user")
    pos_id = data.get("card_payment_pos")
    color = data.get("selected_color", "Не указан")
    storage = data.get("selected_storage", "Не указан")
    price = data.get("final_price", "0")
    
    await state.finish()
    color1 = COLOR_MAP.get(color.lower(), "Неизвестный цвет")
    storage_value = int(storage)
    storage_unit = "TB" if storage_value < 10 else "GB"
    pos = get_position(pos_id)

    msg_text = auto_translate(user_id, f"""💳 <b>Оплата за Продукт:</b> {pos['name']} \n 🎨 <b>Цвет:</b> {color1} \n 💾 <b>Память:</b> {storage}{storage_unit}\n <b>💵 Сумма:</b> {price} USD\n\n 📥 <b>Ссылка для оплаты:</b>\n {msg.text}\n\n После оплаты нажмите «✅ I Paid».""")
                
    
    
    await bot.send_message(chat_id=user_id, text=msg_text, reply_markup=confirm_payment_button(pos_id, color, storage, price), parse_mode="HTML")
    await msg.answer(auto_translate(user_id, "✅ Ссылка отправлена пользователю."))

@dp.callback_query_handler(text_startswith="confirm_payment", state="*")
async def confirm_payment(call: CallbackQuery, state: FSMContext):
    callback_data = call.data.split(":")
    user_id = call.from_user.id  # Получаем ID пользователя
    if len(callback_data) == 2:  # Оплата криптой (передается `payment_id`)
        _, payment_id = callback_data

        # Загружаем данные из БД
        payment = db_fetchone("SELECT * FROM temp_payments WHERE id = ?", (payment_id,))
        if not payment:
            await call.answer(auto_translate(user_id, "❌ Ошибка: данные оплаты не найдены."), show_alert=True)
            return

        pos_id = payment["pos_id"]
        crypto = payment["crypto"]
        amount_crypto = float(payment["amount_crypto"]) if payment["amount_crypto"] else None
        color = payment["color"]
        storage = payment["storage"]
        price = amount_crypto  # Для крипты `price` = `amount_crypto`

    elif len(callback_data) == 5:  # Оплата картой (передаются все данные)
        _, pos_id, color, storage, price = callback_data
        crypto = None
        amount_crypto = None

    else:
        await call.answer(auto_translate(user_id, "❌ Ошибка: Некорректные данные при подтверждении оплаты."), show_alert=True)
        return

    print(f"DEBUG: pos_id = {pos_id}, color = {color}, storage = {storage}, price = {price}, crypto = {crypto}")

    pos = get_position(pos_id)
    if pos is None:
        await call.answer(auto_translate(user_id, f"❌ Ошибка: Продукт с ID {pos_id} не найден. Попробуйте снова."), show_alert=True)
        return

    # Передаем либо `payment_id` для крипты, либо `pos_id` для карты
    final_approve_callback = f"final_approve:{call.from_user.id}:{payment_id}" if crypto else f"final_approve:{call.from_user.id}:{pos_id}:{color}:{storage}:{price}"
    color1 = COLOR_MAP.get(color.lower(), "Неизвестный цвет")
    storage_value = int(storage)
    storage_unit = "TB" if storage_value < 10 else "GB"
    # Сообщение для админа
    payment_type = f"₿ {crypto.upper()} {amount_crypto}" if crypto else f"💳 bank card {price} USD"
    admin_msg = auto_translate(user_id, f"""
⚠️ Новый платёж на проверку!  
👤 Пользователь: @{call.from_user.username} ({call.from_user.id})  
🛍️ Продукт: <b>{pos['name']}</b>  
🎨 Цвет: {color1}  
💾 Память: {storage}{storage_unit}  
💰 Цена: <b>{payment_type}</b>  
""")

    keyboard = InlineKeyboardMarkup().add(
        InlineKeyboardButton(auto_translate(user_id, "✅ Подтвердить оплату"), callback_data=final_approve_callback)
    )

    for admin_id in get_admins():
        await bot.send_message(admin_id, admin_msg, reply_markup=keyboard, parse_mode="HTML")

    await call.message.edit_text(auto_translate(user_id, "⏳ Оплата проверяется. Это может занять 5-30 минут."))











def find_full_pos_id(short_pos_id):
    pos = get_position_by_short_id(short_pos_id)  # Новый метод
    return pos['id'] if pos else None

@dp.callback_query_handler(text_startswith="final_approve", state="*")
async def final_approve(call: CallbackQuery, state: FSMContext):
    callback_data = call.data.split(":")

    if len(callback_data) == 3:  # Оплата криптой (только `payment_id`)
        _, user_id, payment_id = callback_data

        # Загружаем данные о платеже из БД
        payment = db_fetchone("SELECT * FROM temp_payments WHERE id = ?", (payment_id,))
        if not payment:
            await call.answer(auto_translate(user_id, "❌ Ошибка: данные оплаты не найдены."), show_alert=True)
            return

        pos_id = payment["pos_id"]
        crypto = payment["crypto"]
        amount_crypto = float(payment["amount_crypto"]) if payment["amount_crypto"] else None
        color = payment["color"]
        storage = payment["storage"]
        price = amount_crypto  # Для крипты `price` = `amount_crypto`

        # Удаляем запись из временных платежей после подтверждения
        db_execute("DELETE FROM temp_payments WHERE id = ?", (payment_id,))

    elif len(callback_data) == 6:  # Оплата картой (все данные передаются в callback)
        _, user_id, pos_id, color, storage, price = callback_data
        crypto = None
        amount_crypto = None

    else:
        await call.answer(auto_translate(user_id, "❌ Ошибка: некорректные данные при финальном подтверждении."), show_alert=True)
        return

    print(f"DEBUG: Подтверждение оплаты - pos_id = {pos_id}, color = {color}, storage = {storage}, price = {price}, crypto = {crypto}")

    pos = get_position(pos_id)
    if pos is None:
        await call.answer(auto_translate(user_id, f"❌ ОшибкПродуктар с ID {pos_id} не найден. Попробуйте снова."), show_alert=True)
        return

    # Отправляем пользователю сообщение о завершении покупки
    payment_type = f"₿ {crypto.upper()} {amount_crypto}" if crypto else f"💳 bank card {price} USD"
    keyboard = InlineKeyboardMarkup().add(
        InlineKeyboardButton(auto_translate(user_id, "✅ Завершить покупку"), callback_data=f"buy_pos:{pos_id}:{color}:{storage}:{price}")
    )
    color1 = COLOR_MAP.get(color.lower(), "Неизвестный цвет")
    storage_value = int(storage)
    storage_unit = "TB" if storage_value < 10 else "GB"

    await bot.send_message(user_id, auto_translate(user_id, f"""✅ Оплата подтверждена!\n
Способ: {payment_type}\n
🎨 Цвет: {color1}\n
💾 Память: {storage}{storage_unit}\n
💰 Сумма: {price} {crypto.upper() if crypto else 'USD'}"""),
                           reply_markup=keyboard)

    await call.message.edit_text(auto_translate(user_id, "✅ Оплата подтверждена, покупка зафиксирована."))









####оброботчик калбеков


@dp.callback_query_handler(lambda c: c.data.startswith("submenu_"))
async def open_submenu(call: CallbackQuery):
    _, submenu, pos_id, amount_rub, color, storage = call.data.split(":")
    keyboard = crypto_currency_menu(pos_id, amount_rub, color, storage, call.from_user.id, submenu=submenu)
    await call.message.edit_reply_markup(reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data.startswith("back_to_main"))
async def back_to_main_menu(call: CallbackQuery):
    _, pos_id, amount_rub, color, storage = call.data.split(":")
    keyboard = crypto_currency_menu(pos_id, amount_rub, color, storage, call.from_user.id)
    await call.message.edit_reply_markup(reply_markup=keyboard)


# # # #  Смена языка


@dp.callback_query_handler(text="change_language", state="*")
async def choose_language(call: CallbackQuery):
    keyboard = InlineKeyboardMarkup()
    user_id = call.from_user.id  # Получаем ID пользователя
    languages = {
        "ru": "🇷🇺 Русский",
        "en": "🇬🇧 English",
        "es": "🇪🇸 Español",
        "de": "🇩🇪 Deutsch",
        "ar": "🇸🇦 العربية"
    }
    
    for lang_code, lang_name in languages.items():
        keyboard.add(InlineKeyboardButton(lang_name, callback_data=f"set_language:{lang_code}"))

    await call.message.edit_text(auto_translate(user_id, "Выберите язык:"), reply_markup=keyboard)

@dp.callback_query_handler(text_startswith="set_language:", state="*")
async def set_language(call: CallbackQuery):
    lang_code = call.data.split(":")[1]
    user_id = call.from_user.id  # Получаем ID пользователя
    # Сохраняем язык в БД
    db_execute("UPDATE users SET lang = ? WHERE id = ?", (lang_code, call.from_user.id))
    
    await call.answer(auto_translate(user_id, "✅ Язык изменен!"))
    await call.message.edit_text(auto_translate(user_id, "✅ Язык успешно изменен!"), reply_markup=user_menu(call.from_user.id))
    
    
# # # # 





@dp.callback_query_handler(text_startswith='buy_pos:', state="*")
async def pos_buy(call: CallbackQuery, state: FSMContext):
    await state.finish()
    user_id = call.from_user.id  # Получаем ID пользователя
    callback_data = call.data.split(":", maxsplit=4)

    if len(callback_data) < 5:
        await call.message.answer(auto_translate(user_id, "❌ Ошибка: некорректные данные."))
        return

    _, pos_id, color, storage, price = callback_data
    pos = get_position(pos_id)
    user = get_user(id=call.from_user.id)
    color1 = COLOR_MAP.get(color.lower(), "Неизвестный цвет")
    storage_value = int(storage)
    storage_unit = "TB" if storage_value < 10 else "GB"
    await state.update_data(cache_pos_id_for_buy=pos_id, selected_color=color, selected_storage=storage, selected_price=price)

    # Проверяем баланс пользователя
    if user['balance'] >= float(price):
        receipt = get_unix()
        buy_time = get_date()

        # Обновляем баланс пользователя
        update_user(user['id'], balance=user['balance'] - float(price))

        # Фиксируем покупку в БД
        add_purchase(
            user['id'], user['first_name'], user['user_name'], receipt, 1, float(price),
            pos['id'], pos['name'], auto_translate(user_id, "Продукт выдан вручную"), buy_time, receipt, color, storage
        )

        # Отправляем сообщение о покупке
        msg = auto_translate(user_id, f"""
✅ Покупка завершена!
🛍️ Продукт: {pos['name']}
🎨 Цвет: {color1}
💾 Память: {storage}{storage_unit}
💵 Сумма: {price}
🧾 Чек: {receipt}
📅 Дата: {buy_time}

""")
        await call.message.edit_text(msg)

        # Уведомление админу
        admin_msg = auto_translate(user_id, f"""
💰 Новая покупка!
👤 Пользователь: @{user['user_name']} | <a href='tg://user?id={user['id']}'>{user['first_name']}</a>
💵 Сумма: {price}
🧾 Чек: {receipt}
🛍️ Продукт: {pos['name']}
🎨 Цвет: {color1}
💾 Память: {storage}{storage_unit}
""")
        await send_admins(admin_msg, True)

    else:
        await call.answer(auto_translate(user_id, "❌ Недостаточно средств на балансе!"), show_alert=True)
