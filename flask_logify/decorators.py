import logging
from functools import wraps

from flask_logify.filters import DisableByPathFilter


def log_disabled(filter_class, loggers=None, **options):
    """
    Disable log messages for log handler for a specific Flask routes

    :param (class) filter_class: subclass of logging.Filter
    :param (list) loggers: logger name's list
    :param (str) options: passed to filter class constructor
    :return: wrapped function
    """
    if not issubclass(filter_class, logging.Filter):
        raise ValueError(
            "'{}' must be subclass of {}".format(filter_class, logging.Filter.__name__)
        )

    if not loggers:
        loggers = [None]  # root logger has no name
        loggers += list(logging.root.manager.loggerDict.keys())

    def response(fun):
        for log in loggers:
            logger = logging.getLogger(log)
            logger.addFilter(filter_class(**options))

        @wraps(fun)
        def wrapper(*args, **kwargs):
            return fun(*args, **kwargs)
        return wrapper
    return response


def log_disabled_by_path(loggers=None, path=None):
    """

    :param loggers:
    :param path:
    :return:
    """
    def response(fun):
        @log_disabled(
            DisableByPathFilter,
            loggers=loggers,
            path=path or fun.__name__
        )
        @wraps(fun)
        def wrapper(*args, **kwargs):
            return fun(*args, **kwargs)

        return wrapper
    return response
