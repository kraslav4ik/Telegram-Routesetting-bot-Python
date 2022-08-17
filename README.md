# Telegram Routesetting bot Python


Telegram bot to organize and keep the statistics of Routesetting process. It can schedule daily, weekly and monthly events, and users can interact  with it by state-machine menus, polls/buttons/messages. Statistics are stored in SQL database. Now, project is on testing stage.

Works with: Python 3.8, UTF-16

```bash
Telegram-Routesetting-bot-python/> pip install -r requirements.txt
```

## How to run
Add file `token.txt` with your TGBot Token to the "data" directory
```bash
Telegram-Routesetting-bot-python/> echo $tg_token > ./data/token.txt
```

Add file `database_info` with information about your sql server. You can choose any database name.

```bash
Telegram-Routesetting-bot-python/> echo $username > ./data/database_info
Telegram-Routesetting-bot-python/> echo $password >> ./data/database_info
Telegram-Routesetting-bot-python/> echo $ip_adress >> ./data/database_info
Telegram-Routesetting-bot-python/> echo $any_preffered_db_name >> ./data/test_database_info

```

```bash
Telegram-Routesetting-bot-python/> python ./source/main.py
```

## Launch tests

Add file test_database_info with information about test database. You can choose any name for your test database.

```bash
Telegram-Routesetting-bot-python/> echo $username > ./data/test_database_info
Telegram-Routesetting-bot-python/> echo $password >> ./data/test_database_info
Telegram-Routesetting-bot-python/> echo $ip_adress >> ./data/test_database_info
Telegram-Routesetting-bot-python/> echo $any_preffered_db_name >> ./data/database_info
```

```bash
Telegram-Routesetting-bot-python/> python ./tests/test_SQL_tools.py
Telegram-Routesetting-bot-python/> python ./tests/test_storage.py
```


