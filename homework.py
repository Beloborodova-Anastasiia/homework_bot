import logging
import time
from http import HTTPStatus
from typing import Dict, List

import exceptions
import requests
import settings
import telegram
from telegram import Bot
from userstypes import JsonType

PRACTICUM_TOKEN = settings.PRACTICUM_TOKEN
TELEGRAM_TOKEN = settings.TELEGRAM_TOKEN
TELEGRAM_CHAT_ID = settings.TELEGRAM_CHAT_ID
HEADERS = settings.HEADERS


logger = logging.getLogger(__name__)


def send_message(bot: Bot, message: str) -> None:
    """Sending a message."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        settings.logger.info(f'Отправлено сообщение: "{message}"')
    except Exception as error:
        settings.logger.error(f'Сообщение не отправлено: {error}')


def get_api_answer(current_timestamp: int) -> JsonType:
    """API service endpoint request."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        homework_statuses = requests.get(
            settings.ENDPOINT, headers=HEADERS, params=params
        )
        homework_statuses.raise_for_status()
    except Exception as error:
        if homework_statuses.status_code == HTTPStatus.NOT_FOUND:
            raise exceptions.APIError(
                f'Недоступен Эндпоинт {settings.ENDPOINT}: {error}'
            )
        if homework_statuses.status_code != HTTPStatus.OK:
            raise exceptions.APIError(
                f'Проблемы с Эндпоинтом {settings.ENDPOINT}: {error}'
            )
    return homework_statuses.json()


def check_response(response: JsonType) -> List:
    """API response validation."""
    if type(response) != dict:
        raise TypeError(
            f'В ответе API отсутствует словарь: response == {response}'
        )
    if not response:
        raise exceptions.EmptyDict('В ответе API пустой словарь')
    if 'homeworks' not in response.keys():
        raise KeyError('В словаре отсутствует ключ homeworks')
    homeworks = response.get('homeworks')
    if type(homeworks) != list:
        raise TypeError('Домашки не в виде списка')
    return homeworks


def parse_status(homework: Dict) -> str:
    """Receipt homework status."""
    if 'homework_name' not in homework.keys():
        raise KeyError(
            'В словаре отсутствует ключ homework_name'
        )
    if 'status' not in homework.keys():
        raise KeyError(
            'В словаре отсутствует ключ status'
        )
    homework_status = homework.get('status')
    if homework_status not in settings.HOMEWORK_STATUSES.keys():
        raise KeyError(
            'Недокументированный статус домашней работы'
        )
    homework_name = homework.get('homework_name')
    verdict = settings.HOMEWORK_STATUSES[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens() -> bool:
    """Checking the availability of environment variables."""
    if (PRACTICUM_TOKEN is None or TELEGRAM_TOKEN is None
            or TELEGRAM_CHAT_ID is None):
        message = 'Отсутствует одна из переменных окружения'
        settings.logger.critical(message)
        return False
    return True


def main() -> None:
    """Main logic of the bot."""
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    previous_message = ''
    while True:
        try:
            if check_tokens() is False:
                raise exceptions.HasNoTokens(
                    'Отсутствует переменная окружения!'
                )
            current_timestamp = int(time.time())
            response = get_api_answer(current_timestamp)
            homeworks = check_response(response)
            if homeworks:
                for homework in homeworks:
                    send_message(bot, parse_status(homework))
            else:
                settings.logger.debug('Новые статусы отсутствуют')

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            settings.logger.error(message)
            if message != previous_message:
                send_message(bot, message)
            previous_message = message

        finally:
            time.sleep(settings.RETRY_TIME)


if __name__ == '__main__':
    main()
