import re
import requests
from tgbot.services.sqlite import get_user_lang  # Получаем язык пользователя из БД

DEEPL_API_KEY = "2f0b27a2-7f7f-4e35-98a8-d35793154542:fx"  # Замените на ваш API-ключ от DeepL
DEEPL_API_URL = "https://api-free.deepl.com/v2/translate"

def preserve_case(original, translated):
    """Сохраняет заглавную букву в начале перевода, если она была в оригинале."""
    if original and original[0].isupper():
        return translated[0].upper() + translated[1:]
    return translated

def extract_placeholders(text):
    """Прячет {TAGx} и {name}-подобные переменные, чтобы они не отображались в переведённом тексте."""
    placeholders = {}
    tag_pattern = re.compile(r"({TAG\d+})")  # Ищем {TAGx}
    var_pattern = re.compile(r"(\{\w+\})")  # Ищем переменные типа {name}

    def replacer(match):
        key = f"VAR{len(placeholders)}"  # Уникальный ключ
        placeholders[key] = match.group(0)  # Сохраняем оригинальный тег/переменную
        return key  # Заменяем на временное слово

    text_without_tags = tag_pattern.sub(replacer, text)
    text_without_tags = var_pattern.sub(replacer, text_without_tags)
    return text_without_tags, placeholders

def restore_placeholders(text, placeholders):
    """Возвращает {TAGx} и переменные обратно на место после перевода."""
    for key, tag in placeholders.items():
        text = text.replace(key, tag)
    return text

def translate_text(text, target_lang):
    """Переводит текст через DeepL API, сохраняя {TAGx}, {name} и регистр букв."""
    text_without_tags, placeholders = extract_placeholders(text)

    try:
        response = requests.post(
            DEEPL_API_URL,
            data={
                "auth_key": DEEPL_API_KEY,
                "text": text_without_tags,
                "target_lang": target_lang.upper()
            }
        )
        response_data = response.json()
        translated_text = response_data["translations"][0]["text"]
        translated_text = preserve_case(text_without_tags, translated_text)
        return restore_placeholders(translated_text, placeholders)
    except Exception as e:
        print(f"Ошибка перевода: {e}")
        return restore_placeholders(text, placeholders)

def auto_translate(user_id, text, **kwargs):
    """Переводит текст на язык пользователя, исключая переменные, но переводя описание товара."""
    user_lang = get_user_lang(user_id)
    print(f"DEBUG: user_lang = {user_lang}")
    
    if user_lang == "ru":  # Если русский, не переводим
        return text.format(**kwargs) if kwargs else text
    
    if "description" in kwargs:
        kwargs["description"] = translate_text(kwargs["description"], user_lang)  # Переводим описание товара
    
    formatted_text = text.format(**kwargs) if kwargs else text  # Подставляем переменные
    return translate_text(formatted_text, user_lang)
