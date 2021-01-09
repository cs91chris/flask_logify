import logging
import logging.config
from functools import wraps

import flask
import yaml

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

    def init_app(self, app, builder=LogTextBuilder()):
        """

        :param app: Flask app instance
        :param builder:
        """
        if not hasattr(app, 'extensions'):
            app.extensions = dict()
        app.extensions['logify'] = self

        self.set_default_config(app)
        self.set_request_id(app)

        if builder:
            app.before_request_funcs.setdefault(None, []).append(builder.dump_request)
            app.after_request_funcs.setdefault(None, []).append(builder.dump_response)

        if app.config['LOG_FILE_CONF']:
            try:
                with open(app.config['LOG_FILE_CONF']) as f:
                    self._conf = yaml.safe_load(f)
            except (OSError, IOError, yaml.YAMLError) as exc:
                app.logger.exception(exc, stack_info=False)
        elif app.config['LOGGING']:
            self._conf = app.config['LOGGING']

        if self._conf:
            try:
                logging.config.dictConfig(self._conf)
                app.logger = logging.getLogger(app.config['LOG_LOGGER_NAME'])
            except ValueError as exc:
                app.logger.error('bad configuration file: {}'.format(app.config['LOG_FILE_CONF']))
                app.logger.error('the configuration below\n{}'.format(self._conf))
                app.logger.exception(exc, stack_info=False)
        else:
            app.logger.warning("No logging configuration provided using default configuration")

    @staticmethod
    def set_request_id(app):
        """
        Register request id in flask g

        param app: Flask app instance
        """

        @app.before_request
        def req_id():
            h = flask.current_app.config['REQUEST_ID_HEADER']
            header = "HTTP_{}".format(h.upper().replace('-', '_'))
            flask.g.request_id = flask.request.environ.get(header)

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
        app.config.setdefault('LOG_FILE_CONF', None)
        app.config.setdefault('LOGGING', None)
        app.config.setdefault('LOG_REQ_HEADERS', [])
        app.config.setdefault('LOG_RESP_HEADERS', [])
        app.config.setdefault('REQUEST_ID_HEADER', 'X-Request-ID')
        app.config.setdefault('LOG_SKIP_DUMP', not app.config.get('DEBUG'))
        app.config.setdefault('LOG_RESP_FORMAT', "{level} STATUS {status} {headers} {body}")
        app.config.setdefault('LOG_REQ_FORMAT', "{address} {method} {scheme} {path} {headers} {body}")
        app.config.setdefault('LOG_APP_NAME', 'flask')
        app.config.setdefault('LOG_LOGGER_NAME', '{}-{}'.format(
            app.config['LOG_APP_NAME'],
            app.config.get('FLASK_ENV') or 'development'
        ))
