import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
SMTP_LOGIN = os.getenv("SMTP_LOGIN")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Напишите свой email.")


async def handle_email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    email = update.message.text
    if "@" in email and "." in email:
        user_data[update.message.chat_id] = {'email': email}
        await update.message.reply_text("Email принят. Теперь напиши текст сообщения, которое нужно отправить.")
    else:
        await update.message.reply_text("Пожалуйста, введите корректный email.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    if chat_id in user_data and 'email' in user_data[chat_id]:
        email = user_data[chat_id]['email']
        message_text = update.message.text

        if send_email(email, message_text):
            await update.message.reply_text("Сообщение успешно отправлено")
        else:
            await update.message.reply_text("Ошибка отправки сообщения. Проверьте настройки SMTP.")

        del user_data[chat_id]
    else:
        await update.message.reply_text("Напишите свой email.")


def send_email(to_email: str, message_text: str) -> bool:
    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_LOGIN
        msg['To'] = to_email
        msg['Subject'] = "Уведомление от Telegram-бота"
        msg.attach(MIMEText(message_text, 'plain'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_LOGIN, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Ошибка: {e}")
        return False


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex(r"[^@]+@[^@]+\.[^@]+"), handle_email))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()


if __name__ == '__main__':
    main()
