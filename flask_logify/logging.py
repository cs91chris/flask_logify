import sys
import yaml

import logging.config
from logging.handlers import SysLogHandler

from yaml.parser import ParserError
from yaml.scanner import ScannerError

from flask import current_app

from flask_logify.hooks import hook_log_request
from flask_logify.hooks import hook_log_response


class FlaskLogging:
    def __init__(self, app=None):
        """

        :param app:
        """
        self._conf = {}

        if app is not None:
            self.init_app(app)

    @property
    def conf(self):
        """

        :return:
        """
        return self._conf

    def init_app(self, app, **kwargs):
        """

        :param app: Flask app instance
        :param kwargs: extra logging configuration
        """
        if not hasattr(app, 'extensions'):
            app.extensions = dict()
        app.extensions['logging'] = self

        app.config.setdefault('LOG_APP_NAME', 'flask')
        app.config.setdefault('LOG_LOGGER_NAME', 'development')

        app.before_request_funcs.setdefault(None, []).append(hook_log_request)
        app.after_request_funcs.setdefault(None, []).append(hook_log_response)

        if 'LOG_FILE_CONF' in app.config:
            with open(app.config['LOG_FILE_CONF']) as f:
                try:
                    self._conf = yaml.safe_load(f)
                except (ParserError, ScannerError) as exc:
                    print(exc, file=sys.stderr)
                    sys.exit(1)

            app.logger = logging.getLogger(app.config['LOG_LOGGER_NAME'])
        else:
            app.logger.warning("No 'LOG_FILE_CONF' provided using default configuration")

        self._conf.update(kwargs)
        logging.config.dictConfig(self._conf)


class FlaskSysLogHandler(SysLogHandler):
    def __init__(self, **kwargs):
        """

        :param kwargs:
        """
        super().__init__(**kwargs)
        self.facility = kwargs.get('facility') or SysLogHandler.LOG_USER

    def emit(self, record):
        """

        :param record:
        """
        with current_app.app_context():
            priority = self.encodePriority(self.facility, self.mapPriority(record.levelname))
            record.ident = "{}[{}]:".format(current_app.config['LOG_APP_NAME'], str(priority))
            super(FlaskSysLogHandler, self).emit(record)
