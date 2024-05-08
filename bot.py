import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler, MessageHandler, Filters
import pandas as pd

# Установка уровня логгирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Обработчик команды /start
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Привет! Этот бот поможет тебе получить данные из файла Excel.')

# Обработчик команды /help
def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Используйте команду /getdata для получения данных.')

# Обработчик команды /getdata
def get_data(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Пожалуйста, введите свое ФИО:')
    # Устанавливаем состояние ввода ФИО
    return "INPUT_NAME"

# Обработчик ввода ФИО
def input_name(update: Update, context: CallbackContext) -> None:
    name = update.message.text
    context.user_data['name'] = name
    keyboard = [[InlineKeyboardButton("Январь", callback_data='january'),
                 InlineKeyboardButton("Февраль", callback_data='february')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Выберите месяц:', reply_markup=reply_markup)
    # Устанавливаем состояние выбора месяца
    return "SELECT_MONTH"

# Обработчик выбора месяца
def select_month(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    month = query.data
    context.user_data['month'] = month

    filename = f"uchet_prisyt_{month}.xlsx"
    data = pd.read_excel(filename)

    name = context.user_data['name']
    result = data[data['ФИО'].str.startswith(name)]

    if not result.empty:
        reply_text = result.to_string(index=False)
    else:
        reply_text = "Данные не найдены."

    query.edit_message_text(text=reply_text)
    return -1

# Обработчик неизвестных команд
def unknown(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Извините, я не понимаю эту команду.")

# Функция main, которая запускает бота
def main():
    # Токен бота из BotFather
    updater = Updater("6772403420:AAG5Lxu7h56JR7ydTxB0qaIBqrHkF0pQnXs", use_context=True)

    # Получаем диспетчер для регистрации обработчиков
    dp = updater.dispatcher

    # Регистрация обработчиков
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("getdata", get_data))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, input_name))
    dp.add_handler(CallbackQueryHandler(select_month))

    dp.add_handler(MessageHandler(Filters.command, unknown))

    # Запускаем бота
    updater.start_polling()

    # Остановка бота при нажатии Ctrl+C
    updater.idle()

if __name__ == '__main__':
    main()
