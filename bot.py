from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler
from database import User, session

# توکن ربات خود را از BotFather دریافت کنید
TOKEN = '7447969182:AAFKN2kS_BfNWtyohGGjZ_1PRAZ7eqE-eRU'

# لیست ادمین‌ها
ADMINS = ['ADMIN_TELEGRAM_ID_1', 'ADMIN_TELEGRAM_ID_2']

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text('سلام! لطفا نام خود را وارد کنید:')

async def handle_message(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    user_message = update.message.text

    user = session.query(User).filter_by(telegram_id=str(chat_id)).first()
    if not user:
        user = User(telegram_id=str(chat_id))
        session.add(user)
        session.commit()

    if not user.first_name:
        user.first_name = update.message.from_user.first_name
        session.commit()
        await update.message.reply_text('لطفا نام خانوادگی خود را وارد کنید:')
    elif not user.last_name:
        user.last_name = user_message
        session.commit()
        await update.message.reply_text('لطفا ایمیل خود را وارد کنید:')
    elif not user.email:
        user.email = user_message
        session.commit()
        await update.message.reply_text('لطفا شماره موبایل خود را وارد کنید:')
    elif not user.phone_number:
        user.phone_number = user_message
        session.commit()
        await update.message.reply_text('ثبت نام شما کامل شد. برای ادامه دکمه موافقت با قوانین را بزنید.', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("موافقت با قوانین", callback_data='accept_rules')]]))
    else:
        # ارسال نام و ID کاربر به خود او
        await send_user_info(update.message)

async def send_user_info(message):
    user_id = message.from_user.id
    user_name = message.from_user.full_name
    response_message = f"نام: {user_name}\nID: {user_id}"
    await message.reply_text(response_message)

async def handle_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    if query.data == 'accept_rules':
        await query.message.reply_text('با تشکر. ثبت نام شما با موفقیت انجام شد.')
        await show_main_menu(query.message, context)

async def show_main_menu(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("همایش‌های آتی", callback_data='upcoming_events')],
        [InlineKeyboardButton("شارژ حساب", callback_data='charge_wallet')],
        [InlineKeyboardButton("برداشت موجودی", callback_data='withdraw_balance')],
        [InlineKeyboardButton("ویرایش اطلاعات حساب", callback_data='edit_account')],
        [InlineKeyboardButton("تماس با ادمین", callback_data='contact_admin')],
        [InlineKeyboardButton("موجودی کیف پول", callback_data='wallet_balance')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.reply_text('منوی اصلی:', reply_markup=reply_markup)

async def list_users(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    if str(chat_id) not in ADMINS:
        await update.message.reply_text('شما مجاز به انجام این کار نیستید.')
        return

    users = session.query(User).all()
    if not users:
        await update.message.reply_text('هیچ کاربری ثبت نشده است.')
        return

    user_list = []
    for user in users:
        user_info = (
            f"ID: {user.id}\n"
            f"نام: {user.first_name}\n"
            f"نام خانوادگی: {user.last_name}\n"
            f"ایمیل: {user.email}\n"
            f"شماره موبایل: {user.phone_number}\n"
            f"آیدی تلگرام: {user.telegram_id}\n"
            f"موجودی کیف پول: {user.wallet_balance}\n"
            "-------------------------"
        )
        user_list.append(user_info)

    await update.message.reply_text("\n".join(user_list))

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()

    start_handler = CommandHandler('start', start)
    message_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message)
    callback_handler = CallbackQueryHandler(handle_callback)
    list_users_handler = CommandHandler('list_users', list_users)

    app.add_handler(start_handler)
    app.add_handler(message_handler)
    app.add_handler(callback_handler)
    app.add_handler(list_users_handler)

    app.run_polling()
