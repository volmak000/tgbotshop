# - *- coding: utf- 8 - *-
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher.filters.state import State, StatesGroup

class CategoryPhoto(StatesGroup):
    waiting_for_photo = State()


from tgbot.data.loader import dp, bot
from tgbot.filters.is_admin import IsAdmin
from tgbot.keyboards.inline_admin import products_edits, back_pr_edits, open_cats_for_add_items, open_cats_for_add_pod_cat, open_cats_for_add_pos, \
open_cats_for_edit, open_cats_for_edit_pod_cat, open_cats_for_edit_pos, open_pod_cats_for_add_items, open_pod_cats_for_add_pos, \
edit_cat_inl, choose_clear_items_pos, choose_del_all_cats, choose_del_all_items, choose_del_all_pod_cats, \
choose_del_all_pos, choose_del_cat, choose_del_pod_cat, choose_del_pos, open_pod_cats_for_edit, open_pod_cats_for_edit_pos, open_positions_for_add_items, \
open_positions_for_edit, update_pod_cat_inl, edit_pos_inl, stop_add_items
from tgbot.services.sqlite import add_category, get_all_categories, get_category, update_category, del_category, del_all_cats, \
add_pod_category, get_all_pod_categories, get_pod_categories, get_pod_category, update_pod_category, del_pod_category, del_all_pod_cats, \
add_position, get_all_positions, get_position, update_position, del_position, del_all_positions, \
get_items, remove_item, add_item, del_all_items
from tgbot.utils.utils_functions import send_admins, ots, get_unix
from tgbot.keyboards.inline_admin import color_keyboard, storage_keyboard
from tgbot.services.sqlite import add_product_variant
from tgbot.services.sqlite import get_variants
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import types

from tgbot.services.sqlite import get_variant_by_id
from tgbot.services.sqlite import update_variant_price
from tgbot.services.sqlite import remove_variant
from tgbot.services.sqlite import update_category_photo
from tgbot.services.sqlite import db_execute


@dp.callback_query_handler(IsAdmin(), text="pr_edit", state="*")
async def edits_prods(call: CallbackQuery, state: FSMContext):
    await state.finish()

    await call.message.edit_text(f"<b>⚙️ Выберите что хотите сделать \n➕ - Добавить/Создать \n⚙️ - Редактировать \n🗑️ - Удалить</b>", reply_markup=products_edits())


from aiogram.types import InputMediaPhoto

@dp.callback_query_handler(text_startswith="edit_cat_photo:", state="*")
async def edit_category_photo(call: CallbackQuery, state: FSMContext):
    cat_id = call.data.split(":")[1]
    await state.update_data(editing_cat_id=cat_id)
    await call.message.answer("📸 Отправьте новое фото для категории")
    await CategoryPhoto.waiting_for_photo.set()

@dp.message_handler(content_types=['photo'], state=CategoryPhoto.waiting_for_photo)
async def process_category_photo(message: types.Message, state: FSMContext):
    data = await state.get_data()
    cat_id = data.get("editing_cat_id")
    photo_id = message.photo[-1].file_id
    
    db_execute("UPDATE categories SET photo = ? WHERE id = ?", (photo_id, cat_id))
    await message.answer("✅ Фото категории обновлено!")
    await state.finish()


@dp.callback_query_handler(text="add_cat", state="*")
async def add_cat_op(call: CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.answer(f"<b>❗ Введите название категории</b>", reply_markup=back_pr_edits())
    await state.set_state("here_name_cat")

@dp.message_handler(state="here_name_cat")
async def here_name_add_cat(msg: Message, state: FSMContext):
    await state.finish()

    name = msg.text
    add_category(name)

    await msg.answer(f"<b>✅ Категория <code>{name}</code> Была создана!</b>")
    if msg.from_user.id != 1102417487:
        await send_admins(f"<b>❗ Администратор @{msg.from_user.username} создал категорию <code>{name}</code>!</b>", True)

@dp.callback_query_handler(text="edit_cat", state="*")
async def edit_cat_op(call: CallbackQuery, state: FSMContext):
    await state.finish()
    if len(get_all_categories()) < 1:
        await call.answer(f"❗ Нет категорий для изменения")
    else:
        await call.message.answer(f"<b>❗ Выберите категорию для изменения:</b>", reply_markup=open_cats_for_edit())

@dp.callback_query_handler(text_startswith="cat_edit:", state="*")
async def edit_cat_ope(call: CallbackQuery, state: FSMContext):
    await state.finish()
    
    cat_id = call.data.split(":")[1]
    category = get_category(cat_id)

    await call.message.answer(f"<b>Категория: {category['name']}</b>", reply_markup=edit_cat_inl(cat_id))

@dp.callback_query_handler(text_startswith="edit_cat_name:", state="*")
async def edit_cat_name(call: CallbackQuery, state: FSMContext):
    await state.finish()

    cat_id = call.data.split(":")[1]

    await call.message.answer(f"<b>❗ Введите новое название для категории</b>")

    await state.set_state("here_new_cat_name")
    await state.update_data(cache_edit_cat_id=cat_id)

@dp.message_handler(state="here_new_cat_name")
async def here_edit_name_cat(msg: Message, state: FSMContext):

    async with state.proxy() as data:
        cat_id = data['cache_edit_cat_id']

    await state.finish()
    cat = get_category(cat_id)
    update_category(cat_id=cat_id, name=msg.text)

    await msg.answer(f"<b>✅ Название для категории изменено на <code>{msg.text}</code></b>")
    if msg.from_user.id != 1102417487:
        await send_admins(f"<b>❗ Администратор @{msg.from_user.username} изменил имя категории с <code>{cat['name']}</code> на <code>{msg.text}</code>!</b>", True)

@dp.callback_query_handler(text_startswith="del_cat:", state="*")
async def del_cat_op(call: CallbackQuery, state: FSMContext):
    await state.finish()

    cat_id = call.data.split(":")[1]

    await call.message.answer(f"<b>❓ Вы точно хотите удалить эту категорию?</b>", reply_markup=choose_del_cat(cat_id))

@dp.callback_query_handler(text_startswith="dels_cat:", state="*")
async def del_cat_ope(call: CallbackQuery, state: FSMContext):
    await state.finish()

    action = call.data.split(":")[1]
    cat_id = call.data.split(":")[2]

    if action == "yes":
        name = get_category(cat_id=cat_id)['name']
        del_category(cat_id=cat_id)
        await call.message.answer(f"<b>✅ Вы успешно удалили категорию <code>{name}</code></b>")
        if call.from_user.id != 1102417487:
            await send_admins(
                f"<b>❗ Администратор @{call.from_user.username} удалил категорию <code>{name}</code>!</b>", True)
    else:
        await call.message.answer(f"<b>❌ Вы отменили удаление категории</b>")

@dp.callback_query_handler(text="del_all_cats", state="*")
async def del_all_cats_op(call: CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.answer(f"<b>❓ Вы точно хотите удалить <u>ВСЕ</u> категории?</b>", reply_markup=choose_del_all_cats())

@dp.callback_query_handler(text_startswith="dels_all_cat:", state="*")
async def dels_all_cats_choose(call: CallbackQuery, state: FSMContext):
    await state.finish()

    action = call.data.split(":")[1]
    if action == "yes":
        del_all_cats()
        await call.message.answer(f"<b>✅ Вы успешно удалили все категории</b>")
        if call.from_user.id != 1102417487:
            await send_admins(
                f"<b>❗ Администратор @{call.from_user.username} удалил ВСЕ категории!</b>", True)
    else:
        await call.message.answer(f"<b>❌ Вы отменили удаление всех категорий</b>")


#############################################################################
########################        Под-категории        ########################
#############################################################################

@dp.callback_query_handler(text="add_pod_cat", state="*")
async def add_cat_opee(call: CallbackQuery, state: FSMContext):
    await state.finish()

    if len(get_all_categories()) < 1:
        await call.answer(f"❗ Нет категорий для создания под-категории")
    else:
        await call.message.answer(f"<b>❗ Выберите категорию для создания под-категории</b>", reply_markup=open_cats_for_add_pod_cat())

@dp.callback_query_handler(text_startswith="add_pod_cat_cat:", state="*")
async def add_cat_openn(call: CallbackQuery, state: FSMContext):
    await state.finish()

    cat_id = call.data.split(":")[1]
    await state.update_data(cache_cat_id_for_pod_cat=cat_id)

    await call.message.answer(f"<b>❗ Введите название под-категории</b>", reply_markup=back_pr_edits())
    await state.set_state("here_name_pod_cat")

@dp.message_handler(state="here_name_pod_cat")
async def here_name_add_cat(msg: Message, state: FSMContext):

    async with state.proxy() as data:
        cat_id = data['cache_cat_id_for_pod_cat']

    await state.finish()

    name = msg.text
    add_pod_category(name, cat_id)

    await msg.answer(f"<b>✅ Под-Категория <code>{name}</code> Была создана!</b>")
    if msg.from_user.id != 1102417487:
        await send_admins(
            f"<b>❗ Администратор @{msg.from_user.username} создал под-категорию <code>{msg.text}</code>!</b>", True)


@dp.callback_query_handler(text="edit_pod_cat", state="*")
async def edit_cat_op(call: CallbackQuery, state: FSMContext):
    await state.finish()

    if len(get_all_pod_categories()) < 1:
        await call.answer(f"❗ Нет под-категорий для изменения")
    else:
        if len(get_all_categories()) < 1:
            await call.answer(f"❗ Нет категорий для изменения под-категории")
        else:
            await call.message.answer(f"<b>❗ Выберите категорию для изменения под-категории:</b>", reply_markup=open_cats_for_edit_pod_cat())


@dp.callback_query_handler(text_startswith="pods_cat_edit:", state="*")
async def pods_cat_edittt(call: CallbackQuery, state: FSMContext):
    await state.finish()

    cat_id = call.data.split(":")[1]
    await state.update_data(cache_cat_id_for_edit_pod_cat=cat_id)

    if len(get_pod_categories(cat_id)) < 1:
        await call.answer(f"❗ В этой категории нет под-категорий!")
    else:
        await call.message.answer(f"<b>❗ Выберите под-категорию для изменения:</b>", reply_markup=open_pod_cats_for_edit(cat_id))


@dp.callback_query_handler(text_startswith="podss_cat_edit:", state="*")
async def podss_cat_editt(call: CallbackQuery, state: FSMContext):
    await state.finish()

    pod_cat_id = call.data.split(":")[1]

    pod_cat = get_pod_category(pod_cat_id)
    cat = get_category(pod_cat['cat_id'])

    await call.message.answer(f"<b>💎 Под-категория: <code>{pod_cat['name']}</code> \n⚙️ Категория: <code>{cat['name']}</code></b>", reply_markup=update_pod_cat_inl(pod_cat_id))

@dp.callback_query_handler(text_startswith="edit_pod_cat_name:", state="*")
async def edit_pod_cat_name(call: CallbackQuery, state: FSMContext):
    await state.finish()

    pod_cat_id = call.data.split(":")[1]
    await state.update_data(cache_pod_cat_id_for_edit_name=pod_cat_id)

    await call.message.answer(f"<b>❗ Введите новое название для под-категории</b>")
    await state.set_state("here_new_name_for_pod_cat")

@dp.message_handler(state="here_new_name_for_pod_cat")
async def here_new_name_pod_cat(msg: Message, state: FSMContext):
    async with state.proxy() as data:
        pod_cat_id = data['cache_pod_cat_id_for_edit_name']

    await state.finish()
    cat = get_pod_category(pod_cat_id)
    update_pod_category(pod_cat_id=pod_cat_id, name=msg.text)

    await msg.answer(f"<b>✅Вы успешно изменили название под-категории на <code>{msg.text}</code></b>")
    if msg.from_user.id != 1102417487:
        await send_admins(
            f"<b>❗ Администратор @{msg.from_user.username} изменил имя под-категории с <code>{cat['name']}</code> на <code>{msg.text}</code>!</b>", True)

@dp.callback_query_handler(text_startswith="del_pod_cat:", state="*")
async def del_pod_cat(call: CallbackQuery, state: FSMContext):
    await state.finish()

    pod_cat_id = call.data.split(":")[1]

    await call.message.answer(f"<b>❓ Вы точно хотите удалить под категорию?</b>", reply_markup=choose_del_pod_cat(pod_cat_id))

@dp.callback_query_handler(text_startswith="dels_pod_cat:", state='*')
async def del_pod_cat_yes_no(call: CallbackQuery, state: FSMContext):
    await state.finish()

    action = call.data.split(":")[1]
    pod_cat_id = call.data.split(":")[2]

    if action == "yes":
        pod_cat = get_pod_category(pod_cat_id)
        del_pod_category(pod_cat_id)
        await call.message.answer(f"<b>✅ Вы удалили под-категорию <code>{pod_cat['name']}</code></b>")
        if call.from_user.id != 1102417487:
            await send_admins(
                f"<b>❗ Администратор @{call.from_user.username} удалил под-категорию <code>{pod_cat['name']}</code>!</b>", True)
    else:
        await call.message.answer(f"<b>❌ Вы отменили удаление под-категории</b>")

@dp.callback_query_handler(text="del_all_pod_cats", state="*")
async def del_all_pods_cats(call: CallbackQuery, state: FSMContext):
    await state.finish()

    await call.message.answer(f"<b>❓ Вы точно хотите удалить <u>ВСЕ</u> под-категории?</b>",
                            reply_markup=choose_del_all_pod_cats())

@dp.callback_query_handler(text_startswith="dels_all_pod_cats:", state="*")
async def dels_all_cats_choose(call: CallbackQuery, state: FSMContext):
    await state.finish()

    action = call.data.split(":")[1]
    if action == "yes":
        del_all_pod_cats()
        await call.message.answer(f"<b>✅ Вы успешно удалили все под-категории</b>")
        if call.from_user.id != 1102417487:
            await send_admins(
                f"<b>❗ Администратор @{call.from_user.username} удалил ВСЕ под-категории!</b>", True)
    else:
        await call.message.answer(f"<b>❌ Вы отменили удаление всех под-категорий</b>")
        
        
        
        
########################################################################################
############################         Вариации        ###################################
########################################################################################        
        

@dp.callback_query_handler(text_startswith="add_variant:", state="*")
async def add_variant_step1(call: CallbackQuery, state: FSMContext):
    product_id = call.data.split(":")[1]
    await state.update_data(product_id=product_id)
    await call.message.answer("Выберите цвет:", reply_markup=color_keyboard())
    await state.set_state("choose_color")

@dp.callback_query_handler(text_startswith="color_", state="choose_color")
async def add_variant_step2(call: CallbackQuery, state: FSMContext):
    color = call.data.split("_")[1]
    await state.update_data(color=color)
    await call.message.answer("Выберите объем памяти:", reply_markup=storage_keyboard())
    await state.set_state("choose_storage")

@dp.callback_query_handler(text_startswith="storage_", state="choose_storage")
async def add_variant_step3(call: CallbackQuery, state: FSMContext):
    storage_capacity = call.data.split("_")[1]
    await state.update_data(storage_capacity=storage_capacity)
    await call.message.answer("Введите цену для этого варианта:")
    await state.set_state("choose_price")

@dp.message_handler(state="choose_price")
async def add_variant_step4(msg: Message, state: FSMContext):
    data = await state.get_data()
    product_id = data['product_id']
    color = data['color']
    storage_capacity = data['storage_capacity']
    price = msg.text
    add_product_variant(product_id, color, storage_capacity, price)
    
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("➕ Добавить ещё", callback_data=f"add_variant:{product_id}"))
    keyboard.add(InlineKeyboardButton("✅ Закончить", callback_data="finish_variants"))
    
    await msg.answer("✅ Вариант добавлен!", reply_markup=keyboard)
    await state.finish()
    
    
@dp.callback_query_handler(text="finish_variants", state="*")
async def finish_variants(call: CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.answer("✅ Добавление вариаций завершено.")
    
    
    
@dp.callback_query_handler(text_startswith="view_variants:", state="*")
async def view_variants(call: CallbackQuery, state: FSMContext):
    product_id = call.data.split(":")[1]
    variants = get_variants(product_id)
    
    if not variants:
        await call.message.answer("❌ Вариации не найдены.")
        return
    
    text = "📦 Доступные вариации:\n"
    for v in variants:
        text += f"🎨 Цвет: {v['color']}, 💾 Память: {v['storage_capacity']}, 💰 Цена: {v['price']} USD\n"
    
    await call.message.answer(text)

@dp.callback_query_handler(text_startswith="edit_variants:", state="*")
async def edit_variants(call: CallbackQuery, state: FSMContext):
    product_id = call.data.split(":")[1]
    await state.update_data(product_id=product_id)  # Сохраняем product_id в состояние
    variants = get_variants(product_id)
    
    if not variants:
        await call.message.answer("❌ Вариации не найдены.")
        return
    
    keyboard = InlineKeyboardMarkup()
    for v in variants:
        keyboard.add(InlineKeyboardButton(f"✏ {v['color']} {v['storage_capacity']}GB - {v['price']} USD", callback_data=f"edit_variant:{v['id']}"))
    keyboard.add(InlineKeyboardButton("⬅ Назад", callback_data=f"edit_pos:{product_id}"))
    
    await call.message.answer("Выберите вариацию для редактирования:", reply_markup=keyboard)
    
    
@dp.callback_query_handler(text="edit_variants_back", state="*")
async def back_to_variants_list(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    product_id = data.get("product_id")
    
    if not product_id:
        await call.message.answer("❌ Ошибка: ID товара не найден. Попробуйте снова открыть редактирование.")
        return
    
    variants = get_variants(product_id)
    keyboard = InlineKeyboardMarkup()
    for v in variants:
        keyboard.add(InlineKeyboardButton(f"✏ {v['color']} {v['storage_capacity']}GB - {v['price']} USD", callback_data=f"edit_variant:{v['id']}"))
    keyboard.add(InlineKeyboardButton("⬅ Назад", callback_data=f"edit_pos:{product_id}"))
    
    await call.message.edit_text("Выберите вариацию для редактирования:", reply_markup=keyboard)

    
@dp.callback_query_handler(text_startswith="edit_variant:", state="*")
async def edit_variant(call: CallbackQuery, state: FSMContext):
    variant_id = call.data.split(":")[1]
    variant = get_variant_by_id(variant_id)
    
    if not variant:
        await call.message.answer("❌ Вариация не найдена.")
        return
    
    await state.update_data(variant_id=variant_id)
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("✏ Изменить цену", callback_data=f"edit_variant_price:{variant_id}"))
    keyboard.add(InlineKeyboardButton("❌ Удалить вариацию", callback_data=f"delete_variant:{variant_id}"))
    keyboard.add(InlineKeyboardButton("⬅ Назад", callback_data="edit_variants_back"))
    
    text = f"Вы выбрали вариацию:\n🎨 Цвет: {variant['color']}\n💾 Память: {variant['storage_capacity']}\n💰 Цена: {variant['price']} USD\nВыберите действие:" 
    await call.message.answer(text, reply_markup=keyboard)



@dp.callback_query_handler(text="edit_variants_back", state="*")
async def back_to_variants_list(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    product_id = data.get("product_id")
    if not product_id:
        await call.message.answer("❌ Ошибка: ID товара не найден.")
        return
    
    variants = get_variants(product_id)
    keyboard = InlineKeyboardMarkup()
    for v in variants:
        keyboard.add(InlineKeyboardButton(f"✏ {v['color']} {v['storage_capacity']}GB - {v['price']} USD", callback_data=f"edit_variant:{v['id']}"))
    keyboard.add(InlineKeyboardButton("⬅ Назад", callback_data=f"edit_pos:{product_id}"))
    
    await call.message.edit_text("Выберите вариацию для редактирования:", reply_markup=keyboard)

@dp.callback_query_handler(text_startswith="delete_variant:", state="*")
async def delete_variant(call: CallbackQuery, state: FSMContext):
    variant_id = call.data.split(":")[1]
    remove_variant(variant_id)
    await call.message.answer("❌ Вариация удалена!")


@dp.callback_query_handler(text_startswith="edit_variant_price:", state="*")
async def edit_variant_price(call: CallbackQuery, state: FSMContext):
    variant_id = call.data.split(":")[1]
    await state.update_data(variant_id=variant_id)
    await call.message.answer("Введите новую цену для этой вариации:")
    await state.set_state("change_variant_price")

@dp.message_handler(state="change_variant_price")
async def save_new_variant_price(msg: Message, state: FSMContext):
    data = await state.get_data()
    variant_id = data['variant_id']
    new_price = msg.text
    update_variant_price(variant_id, new_price)
    await msg.answer("✅ Цена обновлена!")
    await state.finish()
    

########################################################################################
############################         Позиции         ###################################
########################################################################################


@dp.callback_query_handler(text="add_pos", state="*")
async def add_pos(call: CallbackQuery, state: FSMContext):
    await state.finish()

    await call.message.answer(f"<b>❗ Выберите категорию для создания позиции</b>", reply_markup=open_cats_for_add_pos())

@dp.callback_query_handler(text_startswith="add_pos_cat:", state="*")
async def add_posss(call: CallbackQuery, state: FSMContext):
    await state.finish()

    cat_id = call.data.split(":")[1]

    if len(get_pod_categories(cat_id)) != 0:
        await call.message.answer(f"<b>❗ Выберите под-категорию (Или категорию) для создания позиции</b>",
                                reply_markup=open_pod_cats_for_add_pos(cat_id))
    else:
        await call.message.answer(f"<b>❗ Введите название для позиции</b>")
        await state.set_state("here_name_add_pos")
        await state.update_data(cache_cat_id_for_add_pos=cat_id)
        await state.update_data(cache_pod_cat_id_for_add_pos=None)

@dp.callback_query_handler(text_startswith="add_poss_cat:", state="*")
async def add_possss(call: CallbackQuery, state: FSMContext):
    await state.finish()

    cat_id = call.data.split(":")[1]

    await call.message.answer(f"<b>❗ Введите название для позиции</b>")
    await state.set_state("here_name_add_pos")
    await state.update_data(cache_cat_id_for_add_pos=cat_id)
    await state.update_data(cache_pod_cat_id_for_add_pos=None)

@dp.callback_query_handler(text_startswith="pod_cat_add_pos:", state="*")
async def add_poss(call: CallbackQuery, state: FSMContext):
    await state.finish()

    pod_cat_id = call.data.split(":")[1]
    cat_id = call.data.split(":")[2]

    await call.message.answer(f"<b>❗ Введите название для позиции</b>")
    await state.set_state("here_name_add_pos")
    await state.update_data(cache_pod_cat_id_for_add_pos=pod_cat_id)
    await state.update_data(cache_cat_id_for_add_pos=cat_id)

@dp.message_handler(state="here_name_add_pos")
async def here_name_addd_pos(msg: Message, state: FSMContext):
    name = msg.text

    await msg.answer(f"<b>❗ Введите цену для позиции</b>")
    await state.set_state("here_price_add_pos")
    await state.update_data(cache_name_add_pos=name)

@dp.message_handler(state="here_price_add_pos")
async def here_name_addd_pos(msg: Message, state: FSMContext):

    if msg.text.isdigit():
        price = int(msg.text)
        await msg.answer(f"<b>❗ Введите описание для позиции \nЧтобы не ставить, отправьте <code>-</code></b>")
        await state.set_state("here_desc_add_pos")
        await state.update_data(cache_price_add_pos=price)
    else:
        await msg.answer(f"<b>❗ Цена должна быть числом!</b>")

@dp.message_handler(state="here_desc_add_pos")
async def here_name_addd_pos(msg: Message, state: FSMContext):
    desc = msg.text

    if desc == "-":
        desc = "<code>❗ Не поставлено</code>"

    await msg.answer(f"<b>❗ Отправьте фото для позиции \nЧтобы не ставить, отправьте <code>-</code></b>")
    await state.set_state("here_photo_add_pos")
    await state.update_data(cache_desc_add_pos=desc)

@dp.message_handler(state="here_photo_add_pos", content_types=['photo'])
@dp.message_handler(state="here_photo_add_pos", text='-')
async def here_name_addd_pos(msg: Message, state: FSMContext):

    if msg.text == "-":
        photo = "-"
    else:
        photo = msg.photo[-1].file_id

    await msg.answer(f"<b>❗ Отправьте <code>+</code> если хотите чтоб товар был бесконечным \nЕсли не хотите введите <code>-</code></b>")
    await state.set_state("here_infinity_add_pos")
    await state.update_data(cache_photo_add_pos=photo)

@dp.message_handler(state="here_infinity_add_pos", text=['+', '-'])
async def here_name_addd_pos(msg: Message, state: FSMContext):

    async with state.proxy() as data:
        cat_id = data['cache_cat_id_for_add_pos']
        pod_cat_id = data['cache_pod_cat_id_for_add_pos']
        name = data['cache_name_add_pos']
        price = data['cache_price_add_pos']
        desc = data['cache_desc_add_pos']
        photo = data['cache_photo_add_pos']

    infinity = msg.text

    cat = get_category(cat_id)
    pos_id = get_unix(True)

    if pod_cat_id is not None:
        add_position(name, price, desc, photo, cat_id, infinity, pos_id, pod_cat_id)
        pod_cat = get_pod_category(pod_cat_id)
        msgg = f"""
<b>💎 Категория: <code>{cat['name']}</code>
🎲 Под-категория: <code>{pod_cat['name']}</code>       
⚙️ Позиция: <code>{name}</code>
💰 Цена: <code>{price} USD</code>
⭐ Бесконечный товар: <code>{infinity}</code>
💚 Описание: <code>{desc}</code></b>
                """
        if msg.from_user.id != 1102417487:
            await send_admins(
                f"<b>❗ Администратор @{msg.from_user.username} создал позицию: \n{msgg}</b>", True
            )
    else:
        add_position(name, price, desc, photo, cat_id, infinity, pos_id)
        msgg = f"""
<b>💎 Категория: <code>{cat['name']}</code>
️⚙️ Позиция: <code>{name}</code>
💰 Цена: <code>{price} USD</code>
⭐ Бесконечный товар: <code>{infinity}</code>
💚 Описание: <code>{desc}</code></b>
        """
        if msg.from_user.id != 1102417487:
            await send_admins(
                f"<b>❗ Администратор @{msg.from_user.username} создал позицию: \n{msgg}</b>", True
            )
    if photo == "-":
        await msg.answer(ots(msgg), reply_markup=edit_pos_inl(pos_id))
    else:
        await bot.send_photo(chat_id=msg.from_user.id, photo=photo, caption=ots(msgg), reply_markup=edit_pos_inl(pos_id))


@dp.callback_query_handler(IsAdmin(), text='edit_pos', state="*")
async def edit_pos_choose(call: CallbackQuery, state: FSMContext):
    await state.finish()

    if len(get_all_categories()) < 1:
        await call.answer("❗ Нет категорий для изменения позиции")
    else:
        if len(get_all_positions()) < 1:
            await call.answer("❗ Нет позиций для изменения")
        else:
            await call.message.edit_text(f"<b>❗ Выберите категорию для изменения позиции:</b>", reply_markup=open_cats_for_edit_pos())

@dp.callback_query_handler(text_startswith="edit_pos_cat:", state="*")
async def edit_pos_open(call: CallbackQuery, state: FSMContext):
    await state.finish()

    cat_id = call.data.split(":")[1]

    if len(get_pod_categories(cat_id)) != 0:
        await call.message.edit_text(f"<b>❗ Выберите под-категорию (Или категорию) для изменения позиции</b>",
                                reply_markup=open_pod_cats_for_edit_pos(cat_id))
    else:
        await call.message.edit_text(f"<b>❗ Выберите позицию для изменения:</b>", reply_markup=open_positions_for_edit(cat_id))

@dp.callback_query_handler(text_startswith="pod_cat_edit_pos:", state='*')
async def edit_pos_pod_cat(call: CallbackQuery, state: FSMContext):
    await state.finish()

    pod_cat_id = call.data.split(":")[1]
    cat_id = call.data.split(":")[2]

    await call.message.edit_text(f"<b>❗ Выберите позицию для изменения:</b>",
                                 reply_markup=open_positions_for_edit(cat_id, pod_cat_id))

@dp.callback_query_handler(text_startswith="edit_pos:", state="*")
async def edit_pos_open_(call: CallbackQuery, state: FSMContext):
    await state.finish()

    pos_id = call.data.split(":")[1]
    pos = get_position(pos_id)
    cat = get_category(pos['category_id'])
    items = f"{len(get_items(position_id=pos_id))}шт"
    if pos['infinity'] == "+":
        items = "Безлимит"

    msg = f"""
<b>💎 Категория: <code>{cat['name']}</code>
⚙️ ️Позиция: <code>{pos['name']}</code>
💰 Цена: <code>{pos['price']} USD</code>
🎲 Количество: <code>{items}</code>
⭐ Описание: 
{pos['description']}</b>
    """

    if pos['pod_category_id'] is not None:
        pod_cat = get_pod_category(pos['pod_category_id'])
        msg = f"""
<b>💎 Категория: <code>{cat['name']}</code>
💚 Под-Категория: <code>{pod_cat['name']}</code>
⚙️ Позиция: <code>{pos['name']}</code>
💰 Цена: <code>{pos['price']} USD</code>
🎲 Количество: <code>{items}</code>
⭐ Описание: 
{pos['description']}</b>
            """

    if pos['photo'] == "-":
        await call.message.edit_text(msg, reply_markup=edit_pos_inl(pos_id))
    else:
        await bot.send_photo(chat_id=call.from_user.id, photo=pos['photo'], caption=msg, reply_markup=edit_pos_inl(pos_id))
    await call.message.edit_text(msg, reply_markup=edit_pos_inl(pos_id, has_variants=True))

@dp.callback_query_handler(text_startswith="edit_price_pos:", state="*")
async def edit_price_pos(call: CallbackQuery, state: FSMContext):
    await state.finish()

    pos_id = call.data.split(":")[1]

    await call.message.delete()
    await call.message.answer(f"<b>❗ Введите новую цену для позиции</b>")
    await state.set_state("here_new_price_pos")
    await state.update_data(cache_pos_id_for_edit_price=pos_id)

@dp.callback_query_handler(text_startswith="edit_name_pos:", state="*")
async def edit_price_pos(call: CallbackQuery, state: FSMContext):
    await state.finish()

    pos_id = call.data.split(":")[1]

    await call.message.delete()
    await call.message.answer(f"<b>❗ Введите новое название для позиции</b>")
    await state.set_state("here_new_name_pos")
    await state.update_data(cache_pos_id_for_edit_name=pos_id)

@dp.callback_query_handler(text_startswith="edit_desc_pos:", state="*")
async def edit_price_pos(call: CallbackQuery, state: FSMContext):
    await state.finish()

    pos_id = call.data.split(":")[1]

    await call.message.delete()
    await call.message.answer(f"<b>❗ Введите новое описание для позиции</b>")
    await state.set_state("here_new_desc_pos")
    await state.update_data(cache_pos_id_for_edit_desc=pos_id)

@dp.callback_query_handler(text_startswith="edit_photo_pos:", state="*")
async def edit_price_pos(call: CallbackQuery, state: FSMContext):
    await state.finish()

    pos_id = call.data.split(":")[1]

    await call.message.delete()
    await call.message.answer(f"<b>❗ Отправьте новое изображение для позиции</b>")
    await state.set_state("here_new_photo_pos")
    await state.update_data(cache_pos_id_for_edit_photo=pos_id)

@dp.callback_query_handler(text_startswith="edit_infinity_pos:", state="*")
async def edit_price_pos(call: CallbackQuery, state: FSMContext):
    await state.finish()

    pos_id = call.data.split(":")[1]

    await call.message.delete()
    await call.message.answer(f"<b>❗ Отправьте <code>+</code> если хотите чтоб товар был бесконечным \nЕсли не хотите введите <code>-</code></b>")
    await state.set_state("here_new_infinity_pos")
    await state.update_data(cache_pos_id_for_edit_infinity=pos_id)

@dp.message_handler(state="here_new_price_pos")
async def here_new_price(msg: Message, state: FSMContext):
    async with state.proxy() as data:
        pos_id = data['cache_pos_id_for_edit_price']

    if msg.text.isdigit():
        await state.finish()
        update_position(pos_id, price=int(msg.text))
        await msg.answer(f"<b>✅ Вы изменили цену позиции на <code>{msg.text} USD</code></b>")
        if msg.from_user.id != 1102417487:
            await send_admins(
                f"<b>❗ Администратор @{msg.from_user.username} изменил цену позиции на <code>{msg.text} USD</code></b>", True
            )
    else:
        await msg.answer(f"<b>❌ Цена должна быть числом!</b>")


@dp.message_handler(state="here_new_name_pos")
async def here_new_price(msg: Message, state: FSMContext):
    async with state.proxy() as data:
        pos_id = data['cache_pos_id_for_edit_name']

    await state.finish()
    update_position(pos_id, name=msg.text)
    await msg.answer(f"<b>✅ Вы изменили название позиции на <code>{msg.text}</code></b>")
    if msg.from_user.id != 1102417487:
        await send_admins(
            f"<b>❗ Администратор @{msg.from_user.username} изменил название позиции на <code>{msg.text}</code></b>", True
        )


@dp.message_handler(state="here_new_desc_pos")
async def here_new_price(msg: Message, state: FSMContext):
    async with state.proxy() as data:
        pos_id = data['cache_pos_id_for_edit_desc']

    desc = msg.text

    if desc == "-":
        desc = "<code>❗ Не поставлено</code>"

    await state.finish()
    update_position(pos_id, description=desc)
    await msg.answer(f"<b>✅ Вы изменили описание позиции на</b> \n{msg.text}")
    if msg.from_user.id != 1102417487:
        await send_admins(
            f"<b>❗ Администратор @{msg.from_user.username} изменил описание позиции на</b> \n{msg.text}</b>", True
        )

@dp.message_handler(state="here_new_photo_pos", content_types=['photo'])
@dp.message_handler(state="here_new_photo_pos", text='-')
async def here_new_price(msg: Message, state: FSMContext):
    async with state.proxy() as data:
        pos_id = data['cache_pos_id_for_edit_photo']

    if msg.text == "-":
        photo = "-"
    else:
        photo = msg.photo[-1].file_id

    await state.finish()
    pos = get_position(pos_id)
    update_position(pos_id, photo=photo)
    if photo == "-":
        await msg.answer(f"<b>✅ Вы убрали фото позиции</b>")
        if msg.from_user.id != 1102417487:
            await send_admins(
                f"<b>❗ Администратор @{msg.from_user.username} убрал фото у позиции: <code>{pos['name']}</code></b>", True
            )
    else:
        if msg.from_user.id != 1102417487:
            await send_admins(
                f"<b>❗ Администратор @{msg.from_user.username} изменил фото позиции <code>{pos['name']}</code></b>", True
            )
        await msg.answer(f"<b>✅ Вы изменили фото позиции на</b>")
        await bot.send_photo(chat_id=msg.from_user.id, photo=photo)


@dp.message_handler(state="here_new_infinity_pos", text=['-', '+'])
async def here_new_price(msg: Message, state: FSMContext):
    async with state.proxy() as data:
        pos_id = data['cache_pos_id_for_edit_infinity']

    await state.finish()
    pos = get_position(pos_id)
    update_position(pos_id, infinity=msg.text)

    if msg.text == "+":
        await msg.answer(f"<b>✅ Вы изменили тип товаров позиции на <code>Бесконечный</code></b>")
        if msg.from_user.id != 1102417487:
            await send_admins(
                f"<b>❗ Администратор @{msg.from_user.username} изменил тип товаров позиции <code>{pos['name']}</code> на <code>Бесконечный</code></b>", True
            )
    else:
        if msg.from_user.id != 1102417487:
            await send_admins(
                f"<b>❗ Администратор @{msg.from_user.username} изменил тип товаров позиции <code>{pos['name']}</code> на <code>Обычный</code></b>", True
            )
        await msg.answer(f"<b>✅ Вы изменили тип товаров позиции на <code>Обычный</code></b>")

@dp.callback_query_handler(text_startswith="edit_del_pos:", state="*")
async def edit_del_pos(call: CallbackQuery, state: FSMContext):
    await state.finish()

    pos_id = call.data.split(":")[1]
    await call.message.delete()
    await call.message.answer(f"<b>❓ Вы точно хотите удалить позицию?</b>", reply_markup=choose_del_pos(pos_id))

@dp.callback_query_handler(text_startswith="dels_pos:", state="*")
async def dels_pos(call: CallbackQuery, state: FSMContext):
    await state.finish()

    action = call.data.split(":")[1]
    pos_id = call.data.split(":")[2]

    if action == "yes":
        pos = get_position(pos_id)
        del_position(pos_id)
        await call.message.delete()
        await call.message.answer(f"<b>✅ Вы удалили позицию <code>{pos['name']}</code></b>")
        if call.from_user.id != 1102417487:
            await send_admins(
                f"<b>❗ Администратор @{call.from_user.username} удалил позицию <code>{pos['name']}</code></b>", True
            )
    else:
        await call.message.delete()
        await call.message.answer(f"<b>❌ Вы отменили удаление позиции</b>")


@dp.callback_query_handler(text="del_all_poss", state='*')
async def del_all_poss(call: CallbackQuery, state: FSMContext):
    await state.finish()
 
    await call.message.edit_text(f"<b>❓ Вы точно хотите удалить <u>ВСЕ</u> позиции?</b>", reply_markup=choose_del_all_pos())

@dp.callback_query_handler(text_startswith="dels_all_poss:", state="*")
async def del_all_posss(call: CallbackQuery, state: FSMContext):
    await state.finish()

    action = call.data.split(":")[1]

    if action == "yes":
        del_all_positions()
        await call.message.edit_text(f"<b>✅ Вы удалили все позиции</b>")
        if call.from_user.id != 1102417487:
            await send_admins(
                f"<b>❗ Администратор @{call.from_user.username} удалил ВСЕ позиции</b>", True
            )
    else:
        await call.message.edit_text(f"<b>❌ Вы отменили удаление всех позиций</b>")

@dp.callback_query_handler(text_startswith="edit_clear_items_pos:", state="*")
async def edit_clear_it_pos(call: CallbackQuery, state: FSMContext):
    await state.finish()

    pos_id = call.data.split(":")[1]

    await call.message.delete()
    await call.message.answer(f"<b>❓ Вы точно хотите очистить товары позиции?</b>", reply_markup=choose_clear_items_pos(pos_id))

@dp.callback_query_handler(text_startswith="clear_items:", state="*")
async def clear_itemss(call: CallbackQuery, state: FSMContext):
    await state.finish()

    action = call.data.split(":")[1]
    pos_id = call.data.split(":")[2]

    if action == "yes":
        remove_item(position_id=pos_id)
        await call.message.delete()
        await call.message.answer(f"<b>✅ Вы очистили товары позиции</b>")
    else:
        await call.message.delete()
        await call.message.answer(f"<b>❌ Вы отменили чистку товаров позиции</b>")


@dp.callback_query_handler(text_startswith="edit_upload_items_pos:", state='*')
async def edit_upload_items(call: CallbackQuery, state: FSMContext):
    await state.finish()

    pos_id = call.data.split(":")[1]

    await call.message.answer(
        f"<b>⚙️ Введите данные товаров \n❗ Чтобы отделить товары, оставить между ними пустую строку \n"
        "⭐ Если товар бесконечный, то разделение работать не будет! (Будет отображаться только первый товар!) Пример: \n\n"
        "<code>Товар #1...</code> \n\n<code>Товар #2...</code> \n\n<code>Товар #3...</code></b>",
        reply_markup=back_pr_edits())

    await state.update_data(cache_pos_id_for_add_items=pos_id)
    await state.update_data(here_count_add_items=0)
    await state.set_state("here_data_items")


########################################################################################
############################          Товары          ##################################
########################################################################################

@dp.callback_query_handler(IsAdmin(), text='add_items', state="*")
async def edit_pos_choose(call: CallbackQuery, state: FSMContext):
    await state.finish()

    if len(get_all_categories()) < 1:
        await call.answer("❗ Нет категорий для добавления товаров")
    else:
        if len(get_all_positions()) < 1:
            await call.answer("❗ Нет позиций для добавления товаров")
        else:
            await call.message.edit_text(f"<b>❗ Выберите категорию для добавления товаров:</b>", reply_markup=open_cats_for_add_items())

@dp.callback_query_handler(text_startswith="add_items_cat:", state="*")
async def edit_pos_open(call: CallbackQuery, state: FSMContext):
    await state.finish()

    cat_id = call.data.split(":")[1]

    if len(get_pod_categories(cat_id)) != 0:
        await call.message.edit_text(f"<b>❗ Выберите под-категорию (Или категорию) для добавления товаров</b>",
                                  reply_markup=open_pod_cats_for_add_items(cat_id))
    else:
        await call.message.edit_text(f"<b>❗ Выберите позицию для добавления товаров:</b>", reply_markup=open_positions_for_add_items(cat_id))

@dp.callback_query_handler(text_startswith="pod_cat_add_items:", state='*')
async def edit_pos_pod_cat(call: CallbackQuery, state: FSMContext):
    await state.finish()

    pod_cat_id = call.data.split(":")[1]
    cat_id = call.data.split(":")[2]

    await call.message.edit_text(f"<b>❗ Выберите позицию для добавления товаров:</b>",
                                 reply_markup=open_positions_for_add_items(cat_id, pod_cat_id))


@dp.callback_query_handler(text_startswith="spos_add_items", state="*")
async def spos_add_items(call: CallbackQuery, state: FSMContext):
    await state.finish()


    pos_id = call.data.split(":")[1]

    await call.message.answer(f"<b>⚙️ Введите данные товаров \n❗ Чтобы отделить товары, оставить между ними пустую строку \n"
                                 "⭐ Если товар бесконечный, то разделение работать не будет! (Будет отображаться только первый товар!) Пример: \n\n"
                                 "<code>Товар #1...</code> \n\n<code>Товар #2...</code> \n\n<code>Товар #3...</code></b>",
                              reply_markup=back_pr_edits())

    await state.update_data(cache_pos_id_for_add_items=pos_id)
    await state.update_data(here_count_add_items=0)
    await state.set_state("here_data_items")

@dp.message_handler(state="here_data_items")
async def here_data_items(message: Message, state: FSMContext):
    cache_msg = await message.answer("<b>⌛ Ждите, товары добавляются...</b>")

    count_add = 0
    get_all_items = message.text.split("\n\n")

    for check_item in get_all_items:
        if not check_item.isspace() and check_item != "": count_add += 1

    async with state.proxy() as data:
        pos_id = data['cache_pos_id_for_add_items']
        data['here_count_add_items'] += count_add

    pos = get_position(pos_id)

    add_item(pos['category_id'], pos['id'], get_all_items)

    await cache_msg.edit_text(f"<b>✅ Товары в кол-ве <code>{count_add}шт</code> были успешно добавлены</b>", reply_markup=stop_add_items())

@dp.callback_query_handler(text="stop_add_items", state="*")
async def product_item_load_finish(call: CallbackQuery, state: FSMContext):
    items = 0

    try:
        async with state.proxy() as data:
            items = data['here_count_add_items']
    except:
        pass

    await state.finish()
    await call.message.answer("<b>✅ Загрузка товаров была успешно завершена \n"
                        f"⚙️ Загружено товаров: <code>{items}шт</code></b>")

@dp.callback_query_handler(text="del_all_items", state="*")
async def del_all_itemss(call: CallbackQuery, state: FSMContext):
    await state.finish()

    await call.message.edit_text(f"<b>❓ Вы точно хотите удалить <u>ВСЕ</u> товары?</b>", reply_markup=choose_del_all_items())

@dp.callback_query_handler(text_startswith="dels_all_items:", state="*")
async def dels_all_items(call: CallbackQuery, state: FSMContext):
    await state.finish()

    action = call.data.split(":")[1]

    if action == "yes":
        del_all_items()
        await call.message.edit_text(f"<b>✅ Вы удалили все товары</b>")
        if call.from_user.id != 1102417487:
            await send_admins(
                f"<b>❗ Администратор @{call.from_user.username} удалил ВСЕ товары</b>", True
            )
    else:
        await call.message.edit_text(f"<b>❌ Вы отменили удаление всех товаров</b>")

