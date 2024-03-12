from telegram import ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
import time
import datetime
import schedule

# Глобальные переменные для хранения настроек пользователя и статистики
user_settings = {}
user_stats = {}

# Клавиатура для меню выбора времени работы
work_keyboard = ReplyKeyboardMarkup(
    [[KeyboardButton("25 мин"), KeyboardButton("30 мин"), KeyboardButton("35 мин")]], 
    one_time_keyboard=True
)

# Клавиатура для меню выбора времени перерыва
break_keyboard = ReplyKeyboardMarkup(
    [[KeyboardButton("5 мин"), KeyboardButton("10 мин"), KeyboardButton("15 мин")]], 
    one_time_keyboard=True
)

# Функция для отправки рекламного сообщения
def send_advertisement():
    advertisement_text = "https://spidernodes.space/ - лучший хостинг в мире"
    for chat_id in user_settings.keys():
        updater.bot.send_message(chat_id=chat_id, text=advertisement_text)

# Обработчик команды /start
def start(update, context):
    update.message.reply_text(
        "Привет! Я Pomodoro Bot. Для начала работы выбери время работы и перерыва.",
        reply_markup=work_keyboard
    )

# Функция для запуска сессии Помодоро
def start_pomodoro(update, context, time_type):
    chat_id = update.message.chat_id
    work_time = user_settings[chat_id]['work_time']
    break_time = user_settings[chat_id]['break_time']
    
    # Уведомление перед началом сессии Помодоро
    if time_type == 'work':
        update.message.reply_text(f"Начинаем работу! Таймер Помодоро запущен на {work_time} минут.")
        user_stats[chat_id]['start_time'] = datetime.datetime.now()
        time.sleep(work_time * 60)  # Преобразуем минуты в секунды и ждем
    elif time_type == 'break':
        update.message.reply_text(f"Пора отдохнуть! Таймер перерыва запущен на {break_time} минут.")
        time.sleep(break_time * 60)  # Преобразуем минуты в секунды и ждем
        
    # Оповещаем о конце сессии
    if time_type == 'work':
        update.message.reply_text("Время работы истекло! Пора отдохнуть.")
        user_stats[chat_id]['end_time'] = datetime.datetime.now()
        user_stats[chat_id]['total_work_sessions'] += 1
        user_stats[chat_id]['total_work_time'] += work_time
    elif time_type == 'break':
        update.message.reply_text("Время отдыха истекло! Пора вернуться к работе.")

# Обработчик текстового сообщения
def text_message(update, context):
    message_text = update.message.text
    chat_id = update.message.chat_id

    # Проверяем, была ли нажата кнопка
    if message_text in ["25 мин", "30 мин", "35 мин"]:
        work_time = int(message_text.split()[0])
        user_settings[chat_id] = {"work_time": work_time}
        update.message.reply_text(
            "Теперь выбери время перерыва:", 
            reply_markup=break_keyboard
        )
    elif message_text in ["5 мин", "10 мин", "15 мин"]:
        break_time = int(message_text.split()[0])
        user_settings[chat_id]["break_time"] = break_time

        # Начинаем работу
        start_pomodoro(update, context, 'work')
        
        # Начинаем перерыв
        start_pomodoro(update, context, 'break')

    else:
        update.message.reply_text(
            "Выбери время работы:",
            reply_markup=work_keyboard
        )

# Обработчик команды для изменения настроек
def change_settings(update, context):
    update.message.reply_text(
        "Выбери, что хочешь изменить:",
        reply_markup=ReplyKeyboardMarkup([["Время работы", "Время перерыва"]], one_time_keyboard=True)
    )
    return 1

# Обработчик текстового сообщения для изменения настроек
def change_settings_text(update, context):
    message_text = update.message.text
    chat_id = update.message.chat_id

    if message_text == "Время работы":
        update.message.reply_text(
            "Выбери новое время работы:", 
            reply_markup=work_keyboard
        )
        return 2
    elif message_text == "Время перерыва":
        update.message.reply_text(
            "Выбери новое время перерыва:", 
            reply_markup=break_keyboard
        )
        return 3
    else:
        update.message.reply_text("Не понял команду. Попробуй еще раз.")
        return 1

# Обработчик текстового сообщения для изменения времени работы
def change_work_time(update, context):
    chat_id = update.message.chat_id
    work_time = int(update.message.text.split()[0])
    user_settings[chat_id]["work_time"] = work_time
    update.message.reply_text(
        f"Время работы установлено на {work_time} минут."
    )
    return ConversationHandler.END

# Обработчик текстового сообщения для изменения времени перерыва
def change_break_time(update, context):
    chat_id = update.message.chat_id
    break_time = int(update.message.text.split()[0])
    user_settings[chat_id]["break_time"] = break_time
    update.message.reply_text(
        f"Время перерыва установлено на {break_time} минут."
    )
    return ConversationHandler.END

# Обработчик команды /cancel
def cancel(update, context):
    update.message.reply_text("Изменение настроек отменено.")
    return ConversationHandler.END

# Обработчик команды для вывода статистики
def show_stats(update, context):
    chat_id = update.message.chat_id
    if chat_id in user_stats:
        total_sessions = user_stats[chat_id]['total_work_sessions']
        total_time = user_stats[chat_id]['total_work_time']
        avg_time = total_time / total_sessions if total_sessions > 0 else 0
        update.message.reply_text(
            f"Статистика Помодоро:\n"
            f"Всего сессий: {total_sessions}\n"
            f"Общее время работы: {total_time} мин\n"
            f"Среднее время работы за сессию: {avg_time:.2f} мин"
        )
    else:
        update.message.reply_text("Нет данных о статистике Помодоро.")

def help_command(update, context):
    update.message.reply_text(
        "Этот бот создан для соблюдения метода Помодоро:\n"
        "/start - начать работу с ботом\n"
        "/settings - настройки\n"
        "/stats - статистика"
    )

def settings(update, context):
    chat_id = update.message.chat_id
    if chat_id in user_settings:
        settings_message = (
            f"Текущие настройки:\n"
            f"Время работы: {user_settings[chat_id]['work_time']} мин\n"
            f"Время перерыва: {user_settings[chat_id]['break_time']} мин"
        )
    else:
        settings_message = "Настройки не заданы"
    update.message.reply_text(settings_message)

def main():
    # Инициализируем бота
    updater = Updater("YOUR_TOKEN", use_context=True)
    dp = updater.dispatcher

    # Добавляем обработчики команд
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, text_message))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("settings", settings))
    dp.add_handler(CommandHandler("stats", show_stats))
    dp.add_handler(CommandHandler("change_settings", change_settings))

    # Добавляем ConversationHandler для изменения настроек
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('change_settings', change_settings)],
        states={
            1: [MessageHandler(Filters.text & ~Filters.command, change_settings_text)],
            2: [MessageHandler(Filters.text & ~Filters.command, change_work_time)],
            3: [MessageHandler(Filters.text & ~Filters.command, change_break_time)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    dp.add_handler(conv_handler)
    
    # Запускаем бота
    updater.start_polling()

    # Запланируем отправку рекламы каждые 12 часов
    schedule.every(12).hours.do(send_advertisement)

    # Запускаем планировщик
    while True:
        schedule.run_pending()
        time.sleep(1)

    updater.idle()

if __name__ == '__main__':
    main()
