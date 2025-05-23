# - *- coding: utf- 8 - *-
import colorama
from aiogram import executor, Dispatcher
import asyncio
from aiogram import Bot
from aiogram.types import BotCommand
from tgbot.handlers import dp
from tgbot.middlewares import setup_middlewares
from tgbot.services.sqlite import create_db
from tgbot.data.loader import scheduler
from tgbot.utils.other_functions import update_profit_week, update_profit_day, autobackup_db








colorama.init()

from tgbot.keyboards.inline_user import register_crypto_handlers

register_crypto_handlers(dp)  # Регистрируем обработчик
# Запуск шедулеров
async def scheduler_start():
    scheduler.add_job(update_profit_week, "cron", day_of_week="mon", hour=00)
    scheduler.add_job(update_profit_day, "cron", hour=00)
    scheduler.add_job(autobackup_db, "cron", hour=00)

# Выполнение функции после запуска бота
async def on_startup(dp: Dispatcher):

    await scheduler_start()
    
    print(colorama.Fore.GREEN + "=======================")
    print(colorama.Fore.RED + "Bot Was Started")
    print(colorama.Fore.LIGHTBLUE_EX + "Developer/Coder: @volmak_vdk")
    print(colorama.Fore.RESET)


async def set_commands():


    commands = [
        BotCommand(command="start", description="Start"),

    ]
    
    await dp.bot.set_my_commands(commands)
    print("Команды установлены!")
    
asyncio.run(set_commands())
# Выполнение функции после выключения бота
async def on_shutdown(dp: Dispatcher):

    await dp.storage.close()
    await dp.storage.wait_closed()
    await (await dp.bot.get_session()).close()
    



if __name__ == "__main__":
    create_db()
    setup_middlewares(dp)
    scheduler.start()
    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown, skip_updates=True)
