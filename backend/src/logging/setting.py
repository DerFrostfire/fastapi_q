import logging
import sys
import io


def loggings(name):
    stream = io.TextIOWrapper(sys.stdout.buffer)
    # Получение логгера с именем 'my_logger'
    logger = logging.getLogger(name)

    logging.basicConfig(encoding='utf-8')

    # Установка уровня логирования для логгерае
    logger.setLevel(logging.INFO)

    # Добавление обработчика, который выводит сообщения в консоль
    handler = logging.StreamHandler(stream)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

