import os
import logging
from dotenv import load_dotenv
from telegram import Update, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, filters, MessageHandler, InlineQueryHandler
from telegram.request import HTTPXRequest
from uuid import uuid4
import gpu_monitor


load_dotenv()
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


async def find_idle_gpu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    查找空闲的 GPU
    """
    idle_gpus = gpu_monitor.find_idle_gpu()
    text = "空闲 GPU："
    for gpu in idle_gpus:
        text += f"GPU {gpu['gpu_id']}\n"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    回复所有未知的命令
    """
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")


def main():
    request = HTTPXRequest(proxy=os.getenv("https_proxy"))
    application = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).request(request).build()

    start_handler = CommandHandler("start", start)  # 创建 /start 命令 handler
    caps_handler = CommandHandler("caps", caps)
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    inline_caps_handler = InlineQueryHandler(inline_caps)
    unknown_handler = MessageHandler(filters.COMMAND, unknown)
    find_idle_gpu_handler = CommandHandler("find_idle_gpu", find_idle_gpu)

    application.add_handler(start_handler)  # 监听 /start 命令
    application.add_handler(caps_handler)  # 监听 /caps 命令
    application.add_handler(echo_handler)  # 监听所有非命令消息
    application.add_handler(inline_caps_handler)  # 监听 inline 查询
    application.add_handler(find_idle_gpu_handler)  # 监听 /find_idle_gpu 命令
    application.add_handler(unknown_handler)  # 监听所有未知的命令（必须放在最后）
    application.run_polling()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
