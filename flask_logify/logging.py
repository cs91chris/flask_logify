import json
import logging
import logging.config
import sys
from functools import wraps

import yaml
from yaml.parser import ParserError
from yaml.scanner import ScannerError

from .builders import LogTextBuilder


class FlaskLogging:
    def __init__(self, app=None, **kwargs):
        """

        :param app:
        """
        self._conf = {}

        if app is not None:
            self.init_app(app, **kwargs)

    @property
    def conf(self):
        """

        :return:
        """
        return self._conf

    def init_app(self, app, builder=LogTextBuilder(), **kwargs):
        """

        :param app: Flask app instance
        :param builder:
        :param kwargs: extra logging configuration
        """
        if not hasattr(app, 'extensions'):
            app.extensions = dict()
        app.extensions['logify'] = self

        self.set_default_config(app)

        if builder:
            app.before_request_funcs.setdefault(None, []).append(builder.dump_request)
            app.after_request_funcs.setdefault(None, []).append(builder.dump_response)

        if 'LOG_FILE_CONF' in app.config:
            try:
                self.conf_from_file(app.config['LOG_FILE_CONF'])
            except OSError as exc:
                app.logger.exception(exc, stack_info=False)

            try:
                self._conf.update(kwargs)
                logging.config.dictConfig(self._conf)
                app.logger = logging.getLogger(app.config['LOG_LOGGER_NAME'])
            except ValueError as exc:
                app.logger.error('bad configuration file: {}'.format(app.config['LOG_FILE_CONF']))
                app.logger.error('the configuration below\n{}'.format(self._conf))
                app.logger.exception(exc, stack_info=False)
        else:
            app.logger.warning("No 'LOG_FILE_CONF' provided using default configuration")

        if app.config.get('DEBUG') is True:
            app.logger.setLevel('DEBUG')
            self.set_werkzeug_handlers(app.logger.handlers)

    def conf_from_file(self, filename):
        """

        :param filename:
        """
        with open(filename) as f:
            try:
                self._conf = yaml.safe_load(f)
            except (ParserError, ScannerError) as yex:
                try:
                    self._conf = json.load(f)
                except (TypeError, json.JSONDecodeError) as jex:
                    print(yex, file=sys.stderr)
                    print(jex, file=sys.stderr)
                    sys.exit(1)

    @staticmethod
    def disabled(filter_class, loggers=None, **options):
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
            # noinspection PyUnresolvedReferences
            loggers += list(logging.root.manager.loggerDict.keys())

        def response(fun):
            for log in loggers:
                logger = logging.getLogger(log or '')
                logger.addFilter(filter_class(**options))

            @wraps(fun)
            def wrapper(*args, **kwargs):
                return fun(*args, **kwargs)

            return wrapper

        return response

    @staticmethod
    def set_default_config(app):
        """

        param app: Flask app instance
        """
        app.config.setdefault('LOG_REQ_HEADERS', [])
        app.config.setdefault('LOG_RESP_HEADERS', [])
        app.config.setdefault('LOG_SKIP_DUMP', not app.config.get('DEBUG'))
        app.config.setdefault('LOG_RESP_FORMAT', "{level} STATUS {status} {headers} {body}")
        app.config.setdefault('LOG_REQ_FORMAT', "{address} {method} {scheme} {path} {headers} {body}")
        app.config.setdefault('LOG_APP_NAME', 'flask')
        app.config.setdefault('LOG_LOGGER_NAME', '{}-{}'.format(
            app.config['LOG_APP_NAME'],
            app.config.get('FLASK_ENV') or 'development'
        ))

    @staticmethod
    def set_werkzeug_handlers(handlers):
        """

        :param handlers:
        """
        werkzeug_logger = logging.getLogger('werkzeug')
        werkzeug_logger.setLevel(logging.DEBUG)
        for hdl in handlers:
            werkzeug_logger.addHandler(hdl)
