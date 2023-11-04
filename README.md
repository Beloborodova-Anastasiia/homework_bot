# homework_bot


### Telegram data

```
Name: homework_status_bot
Username: @HWstatus_bot
```

### Description
Python telegram bot for tracking homework's statuses. It tracks Yandex Practicum homework's statuses and sends the messages if status has changed.

### Technologies

Python 3.7

python-telegram-bot 13.7

### Local project run:

Clone a repository and navigate to it on the command line:

```
git clone https://github.com/Beloborodova-Anastasiia/homework_bot.git
```

```
cd homework_bot
```

Cоздать и активировать виртуальное окружение:

```
для Mac или Linux:
python3 -m venv venv
source venv/bin/activate
```
```
для Windows:
python -m venv venv
source venv/Scripts/activate 
```

Install dependencies from requirements.txt:

```
for Mac or Linux:
python3 -m pip install --upgrade pip
```
```
for Windows:
python -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Create env-file by template:

```
PRACTICUM_TOKEN = 'your_yandex_practicum_token'
TELEGRAM_TOKEN = '5334868661:AAFlt375JR6XcWTtRCrVsAd-b6xU2YuF7-A'
TELEGRAM_CHAT_ID = 'your_telegram_id'
```

Run project:

```
for Mac or Linux:
python3 homework.py
```
```
for Windows:
python homework.py
```

### Author

Anastasiia Beloborodova  
