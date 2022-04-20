import logging
import os
import sys
import time
from http import HTTPStatus
from typing import Dict, List

import requests
import telegram
from dotenv import load_dotenv
from telegram import Bot

import exceptions

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
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


def send_message(bot: Bot, message: str) -> None:
    """Sending a message."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except Exception as error:
        logger.error(f'Сообщение не отправлено: {error}')
    else:
        logger.info(f'Отправлено сообщение: "{message}"')


def get_api_answer(current_timestamp: int) -> Dict:
    """API service endpoint request."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    homework_statuses = requests.get(
        ENDPOINT, headers=HEADERS, params=params
    )
    if homework_statuses.status_code == HTTPStatus.NOT_FOUND:
        raise exceptions.APIError(
            f'Недоступен Эндпоинт {ENDPOINT}'
        )
    if homework_statuses.status_code != HTTPStatus.OK:
        raise exceptions.APIError(
            f'Проблемы с Эндпоинтом {ENDPOINT}'
        )
    return homework_statuses.json()


def check_response(response: Dict) -> List:
    """API response validation."""
    if type(response) != dict:
        raise TypeError('В ответе API отсутсвует словарь')
    if not response:
        raise exceptions.EmptyDict('В ответе API пустой словарь')
    if 'homeworks' not in response:
        raise exceptions.KeyNotExists('В словаре отсутствует ключ homeworks')
    homeworks = response.get('homeworks')
    if type(homeworks) != list:
        raise TypeError('Домашки не в виде списка')
    return homeworks


def parse_status(homework: Dict) -> str:
    """Receipt homework status."""
    homework_name = homework['homework_name']
    if 'status' not in homework:
        raise exceptions.KeyNotExists(
            'В словаре отсутствует ключ status'
        )
    homework_status = homework['status']
    if homework_status not in HOMEWORK_STATUSES:
        raise exceptions.KeyNotExists(
            'Недокументированный статус домашней работы'
        )
    verdict = HOMEWORK_STATUSES[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens() -> bool:
    """Checking the availability of environment variables."""
    if (PRACTICUM_TOKEN is None or TELEGRAM_TOKEN is None
            or TELEGRAM_CHAT_ID is None):
        message = 'Отсутствует одна из переменных окружения'
        logger.critical(message)
        return False
    return True


def main() -> None:
    """Main logic of the bot."""
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    previous_message = ''

    while True:
        try:
            if check_tokens() is False:
                raise exceptions.HasNoTokens(
                    'Отсутствует переменная окружения!'
                )
            response = get_api_answer(current_timestamp)
            homeworks = check_response(response)

            if(homeworks):
                for homework in homeworks:
                    send_message(bot, parse_status(homework))
            else:
                logger.debug('Новые статусы отсутствуют')

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.error(message)
            if message != previous_message:
                send_message(bot, message)
            previous_message = message

        else:
            current_timestamp = int(time.time())

        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
