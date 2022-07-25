# Telegram Routesetting bot Python

v2.0*SQL-based*version*is*already*in*process... 

Telegram bot to organize and keep the statistics of Routesetting process. It can schedule daily, weekly and monthly events, and users can interact  with it by state-machine menus, polls/buttons/messages.  Statistics are sent in an Excel table for visibility 

Works with: Python 3.8, UTF-16

```bash
Telegram-Routesetting-bot-python/> pip install -r requirements.txt
```

## How to run
Add files `token.txt`, `Bot_owner_data`, `chat_data`, with your TGBot Token, TelegramID of bot owner and chat_id resp. to the "data" directory
```bash
Telegram-Routesetting-bot-python/> echo $tg_token > ./data/token.txt
Telegram-Routesetting-bot-python/> echo $bot_owner_tg_id > ./data/bot_owner_data
Telegram-Routesetting-bot-python/> echo $tg_chat_id > ./data/chat_data
```

```bash
Telegram-Routesetting-bot-python/> python ./src/main.py
```

## Launch tests
```bash
Telegram-Routesetting-bot-python/> python ./tests/test_table_tools.py
```
