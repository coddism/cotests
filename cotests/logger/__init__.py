import logging
import sys
from typing import Optional


FORMAT = '%(levelname)-7s:: %(name)s: %(message)s'
DEFAULT_FORMATTER = logging.Formatter(FORMAT)

DEFAULT_HANDLER = logging.StreamHandler(sys.stdout)
DEFAULT_HANDLER.setFormatter(DEFAULT_FORMATTER)


def create_logger(
        name: str,
        handler: Optional[logging.Handler] = None,
):
    logger = logging.Logger(name, level=logging.NOTSET)
    logger.addHandler(handler or DEFAULT_HANDLER)
    return logger


def logging_init():
    # print('LOGGER')
    # logger = logging.Logger('base', level=logging.NOTSET)
    # formatter = logging.Formatter('%(levelname)-10s:: %(name)s: %(message)s')
    # handler = logging.StreamHandler(sys.stdout)
    # handler.setFormatter(formatter)
    # logger.addHandler(handler)
    #
    # logger.info('LOGGER INIT')
    # print(logger.handlers)
    # handler.formatter = formatter
    # handler.setFormatter(formatter)
    # handler.setLevel(logging.NOTSET)
    # logger.setLevel(logging.INFO)
    # logging.getLogger("aiormq").setLevel(logging.INFO)

    # logging.Manager.getLogger()
    # logging.getLogger()

    logging.basicConfig(
        level=logging.NOTSET,
        format=FORMAT,
        stream=sys.stdout,
        # handlers=handlers,
        # force=True
    )

    # print('INIT')
    # print(type(logging.Manager))
    # print(logging.Manager.loggerDict)
    logging.info('LOGGER INIT')

logging_init()

__all__  = ('logging_init', 'DEFAULT_FORMATTER', 'DEFAULT_HANDLER', 'create_logger')
