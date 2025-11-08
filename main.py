import os
import logging
from dotenv import load_dotenv
from telegram import Update, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, filters, MessageHandler, InlineQueryHandler
from telegram.request import HTTPXRequest
from uuid import uuid4

load_dotenv()
bot_token = os.getenv('BOT_TOKEN')

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    回复 /start 命令
    """
    text = "I'm a bot, please talk to me!"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)


async def caps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    回复 /caps 命令

    返回参数的大写
    """
    text_caps = " ".join(context.args).upper()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text_caps)


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    回复收到的所有非命令消息
    """
    text = update.message.text
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)


async def inline_caps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    回复 inline 查询
    """
    query = update.inline_query.query
    if not query:
        return
    results = []
    results.append(
        InlineQueryResultArticle(
            id=str(uuid4()), title="Caps", input_message_content=InputTextMessageContent(query.upper())
        )
    )
    await context.bot.answer_inline_query(update.inline_query.id, results)


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    回复所有未知的命令
    """
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")


def main():
    application = ApplicationBuilder().token(bot_token).build()

    start_handler = CommandHandler("start", start)  # 创建 /start 命令 handler
    caps_handler = CommandHandler("caps", caps)
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    inline_caps_handler = InlineQueryHandler(inline_caps)
    unknown_handler = MessageHandler(filters.COMMAND, unknown)

    application.add_handler(start_handler)  # 监听 /start 命令
    application.add_handler(caps_handler)  # 监听 /caps 命令
    application.add_handler(echo_handler)  # 监听所有非命令消息
    application.add_handler(inline_caps_handler)  # 监听 inline 查询
    application.add_handler(unknown_handler)  # 监听所有未知的命令（必须放在最后）
    application.run_polling()


if __name__ == "__main__":
    main()
