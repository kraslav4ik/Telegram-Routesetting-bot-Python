# Telegram Routesetting bot Python
Telegram bot to organize and keep the statistics of Routesetting process. It can schedule daily, weekly and monthly events, and users can interact  with it by state-machine menus, polls/buttons/messages.  Statistics are sent in an Excel table for visibility 

Works with: Python 3.8, UTF-16

## How to run
Add files `token.txt`, `Bot_owner_data`, `chat_data`, with your TGBot Token, TelegramID of bot owner and chat_id resp. to the "data" directory
```bash
RoutesetterBot/> echo $tg_token > ./data/token.txt
RoutesetterBot/> echo $bot_owner_tg_id > ./data/bot_owner_data
RoutesetterBot/> echo $tg_chat_id > ./data/chat_data
```

```bash
RoutesetterBot/> python ./src/main.py
```

## Launch tests
```bash
RoutesetterBot/> python ./tests/test_table_tools.py
```
