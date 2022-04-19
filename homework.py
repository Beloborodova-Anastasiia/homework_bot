import logging, sys
import os
import requests
import time
import datetime
from dotenv import load_dotenv
from pprint import pprint
import telegram

# from logging import StreamHandler
# from telegram import Bot, ReplyKeyboardMarkup
# from telegram.ext import CommandHandler, Filters, MessageHandler, Updater


load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practdicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


logging.basicConfig(
    level=logging.DEBUG,
    filename='main.log',
    filemode='w',
    format='%(asctime)s, %(levelname)s, %(message)s'
)

handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler.setLevel(logging.DEBUG)
handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)


def send_message(bot, message):
    """Sending a message."""
    bot.send_message(TELEGRAM_CHAT_ID, message)
    logger.info('Сообщение отправлено')


def get_api_answer(current_timestamp):
    """API service endpoint request."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        homework_statuses = requests.get(
            ENDPOINT, headers=HEADERS, params=params
        )
    except Exception as error:
        logging.error(f'Ошибка при запросе к  API: {error}')
    return homework_statuses.json()


def check_response(response):
    """API response validation."""
    try:
        homeworks = response.get('homeworks')
    except Exception as error:
        logging.error(f'Ответ API не соответствует ожиданиям: {error}')
        homeworks = None
    return homeworks


def parse_status(homework):
    """Receipt homework status."""
    homework_name = homework['homework_name']
    homework_status = homework['status']
    verdict = HOMEWORK_STATUSES[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


# pprint(check_response(get_api_answer(1)))
# www = check_response(get_api_answer(1))[4]
# print(parse_status(www))


def check_tokens():
    """Checking the availability of environment variables."""
    if (PRACTICUM_TOKEN is None or TELEGRAM_TOKEN is None
            or TELEGRAM_CHAT_ID is None):
        return False
    return True


def main():
    """Main logic of the bot."""
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    # current_timestamp = int(time.time())
    current_timestamp = int(datetime.datetime(2022, 4, 1).timestamp())

    while check_tokens():
        try:
            response = get_api_answer(current_timestamp)
            homeworks = check_response(response)
            if(homeworks):
                for homework in homeworks:
                    send_message(bot, parse_status(homework))
            current_timestamp = int(time.time())
            time.sleep(RETRY_TIME)
            print(current_timestamp)

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.error(message)
            send_message(bot, message)
            time.sleep(RETRY_TIME)
    #     else:
    # #         ...


if __name__ == '__main__':
    main()
