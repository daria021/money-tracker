import logging
import os
from datetime import datetime

from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, CallbackQueryHandler, \
    ConversationHandler
from telegram.ext.filters import TEXT

from category.schemas import CategoryCreate
from database import engine
from keyboards.utils import chunk
from middlewares.middlewares import Middleware
from middlewares.session_middleware import SessionMiddleware
from statistics import kinds_month, statistics
from user.UserRepo import UserRepo
from user.schemas import UserCreate
from wastes.WastesRepo import WastesRepo
from category.CategoryRepo import Category, CategoryRepo
from wastes.schemas import WastesCreate

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="привет бро! это трекер расходов."
                                        "\nты можешь здесь отслеживать свои расходы и смотреть статистику."
                                        "\nвведи команду /waste, чтобы добавить расходы, "
                                        "/category, чтобы добавить категорию и команду "
                                        "/stats, чтобы посмотреть статистику. Если что-то пошло не так жми /cancel!")
    user = UserCreate(
        tg_id=update.effective_user.id,
        username=update.effective_user.username,
    )
    try:
        await UserRepo.get_user(session=context.session, user_id=update.effective_user.id)
    except NoResultFound:
        await UserRepo.create_user(session=context.session, user=user)


async def waste_money(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Йоу, сколько ты потратил?")
    return "asked_money"


async def get_money(update: Update, context: ContextTypes.DEFAULT_TYPE):
    money = update.effective_message.text
    print(money)
    try:
        money = float(money.replace(",", "."))
        print(money)
    except ValueError:
        print('lol')
        await update.effective_message.reply_text("Введите пожалуйста число)")
        return "asked_money"
    context.user_data["money"] = money
    user_id = update.effective_user.id
    kinds = await CategoryRepo.get_users_category(user_id=user_id, session=context.session)
    print(kinds)
    buttons = list(map(lambda x: x.title, kinds))
    print(buttons)
    kinds_category = chunk(buttons)
    print(kinds_category)
    kinds_category = [[InlineKeyboardButton(title, callback_data=title) for title in row] for row in kinds_category]

    markup = InlineKeyboardMarkup(kinds_category)

    print('lol?')

    await update.effective_message.reply_text(text="Понял, а на что ты их потратил?",
                                              reply_markup=markup, )
    return "asked_category"


async def save_waste(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.effective_message.reply_text("окей бро")
    category = update.callback_query.data
    money = context.user_data["money"]
    wastes = WastesCreate(
        user_id=update.effective_user.id,
        category=category,
        amount=money,
        date=datetime.now()
    )
    await WastesRepo.add_waste(wastes=wastes, session=context.session)
    context.user_data["money"] = 0
    return ConversationHandler.END


async def ask_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Какую категорию тебе добавить добавить?")
    return "asked_category_to_add"


async def add_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    title_category = update.effective_message.text
    category = CategoryCreate(
        user_id=update.effective_user.id,
        title=title_category
    )
    await CategoryRepo.add_category(session=context.session, category=category)
    await update.effective_message.reply_text("ок")
    return ConversationHandler.END


async def ask_month(update: Update, context: ContextTypes.DEFAULT_TYPE):
    markup = InlineKeyboardMarkup(kinds_month)
    print(kinds_month)
    await update.effective_message.reply_text(text="За какой месяц вы хотите получить статистику?",
                                              reply_markup=markup)
    return "asked_month"


async def save_month(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.effective_message.reply_text("Секунду!")
    month = update.callback_query.data
    print('AAAAAAAAAAAAAAAAAAAAAAAAAAAAA', month)
    print(type(month))
    graph, message = await statistics(user_id=update.effective_user.id, month=int(month), session=context.session)

    await update.effective_message.reply_photo(graph)
    await update.effective_message.reply_text(message)

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return ConversationHandler.END


if __name__ == '__main__':
    TOKEN = os.environ.get("TOKEN")

    session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    middleware = Middleware(
        [
            SessionMiddleware(session_maker),

        ],
    )

    application = ApplicationBuilder().token(TOKEN).build()

    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    WasteMoney_handler = ConversationHandler(
        entry_points=[CommandHandler('waste', waste_money), ],
        states={
            "asked_money": [MessageHandler(filters=TEXT, callback=get_money)],
            "asked_category": [CallbackQueryHandler(callback=save_waste)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    application.add_handler(WasteMoney_handler)

    AddCategory_handler = ConversationHandler(
        entry_points=[CommandHandler('category', ask_category), ],
        states={
            "asked_category_to_add": [MessageHandler(filters=TEXT, callback=add_category)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    application.add_handler(AddCategory_handler)

    Statistics_handler = ConversationHandler(
        entry_points=[CommandHandler('stats', ask_month), ],
        states={
            "asked_month": [CallbackQueryHandler(callback=save_month)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    application.add_handler(Statistics_handler)

    GetMoney_handler = MessageHandler(filters=TEXT, callback=get_money)
    application.add_handler(GetMoney_handler)

    SaveCategory_handler = CallbackQueryHandler(callback=save_waste, pattern="")
    application.add_handler(SaveCategory_handler)

    middleware.attach_to_application(application)

    application.run_polling()
