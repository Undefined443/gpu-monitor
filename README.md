# GPU Monitor

## Usage

1. 设置 Telegram Bot Token：

   ```sh
   vim .env
   ```

   ```sh
   BOT_TOKEN="your-telegram-bot-token"
   CHAT_ID="your-telegram-user-id"
   ```

2. 启动 monitor：

   ```sh
   uv run gpu_monitor.py
   ```
