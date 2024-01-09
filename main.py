import logging
import os

from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext.filters import TEXT

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

kinds = [
    [
        InlineKeyboardButton("Еда", callback_data="food"),
        InlineKeyboardButton("Развлечения", callback_data="entertainments"),
    ],
    [
        InlineKeyboardButton("Транспорт", callback_data="transport"),
        InlineKeyboardButton("Оплата ЖКХ", callback_data="communal"),
    ],
    [
        InlineKeyboardButton("Одежда и обувь", callback_data="clothes"),
        InlineKeyboardButton("Домашние питомцы", callback_data="pets"),
    ],
    [
        InlineKeyboardButton("Аренда квартиры", callback_data="rent"),
        InlineKeyboardButton("Дом и интерьер", callback_data="house")
    ],
    [
        InlineKeyboardButton("Спиннеры", callback_data="spinner"),
        InlineKeyboardButton("Другое", callback_data="other")
    ],
]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="привет бро! это трекер расходов.\nты можешь здесь отслеживать свои расходы и смотреть статистику.\nвведи команду /waste, чтобы добавить расходы и команду /stats, чтобы посмотреть статистику!")
    context.user_data["statistics"] = {}


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)


async def waste_money(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Йоу, сколько ты потратил?")


async def get_money(update: Update, context: ContextTypes.DEFAULT_TYPE):
    money = update.effective_message.text
    try:
        money = float(money.replace(",", "."))
    except ValueError:
        await update.effective_message.reply_text("Введите пожалуйста число)")
        return
    context.user_data["money"] = money
    
    markup = InlineKeyboardMarkup(kinds)
    
    await update.effective_message.reply_text(text="Понял, а на что ты их потратил?",
                                              reply_markup=markup,)


async def save_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    category = update.callback_query.data
    statistics = context.user_data["statistics"]
    money = context.user_data["money"]
    if category in statistics:
        statistics[category] += money
    else:
        statistics[category] = money
    context.user_data["money"] = 0
    await update.effective_message.reply_text("Запомнил!")
    
    
async def statistics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply = ''
    stats: dict = context.user_data["statistics"]
    stats_sum = sum(stats.values())
    for kind, sum_money in stats.items():
        reply += f'{kind}: {sum_money} рублей, это {sum_money/stats_sum*100:.2f}%\n'
    await update.effective_message.reply_text(reply)
    

if __name__ == '__main__':
    TOKEN = os.environ.get("TOKEN")
    
    application = ApplicationBuilder().token(TOKEN).build()
    
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)
    
    # error_handler = MessageHandler(filters=TEXT, callback=error)
    # application.add_handler(error_handler)
    
    WasteMoney_handler = CommandHandler('waste', waste_money)
    application.add_handler(WasteMoney_handler)
    
    Statistics_handler = CommandHandler('stats', statistics)
    application.add_handler(Statistics_handler)
    
    GetMoney_handler = MessageHandler(filters=TEXT, callback=get_money)
    application.add_handler(GetMoney_handler)
    
    SaveCategory_handler = CallbackQueryHandler(callback=save_category, pattern="")
    application.add_handler(SaveCategory_handler)
    
    application.run_polling()
