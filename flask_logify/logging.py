import sys
import yaml

import logging.config
import logging.handlers

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
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """

        :param app:
        """
        if not hasattr(app, 'extensions'):
            app.extensions = dict()
        app.extensions['logging'] = self

        app.config.setdefault('LOG_APP_NAME', 'flask')
        app.config.setdefault('LOG_LOGGER_NAME', 'development')

        app.before_request_funcs.setdefault(None, []).append(hook_log_request)
        app.after_request_funcs.setdefault(None, []).append(hook_log_response)

        if 'LOG_FILE_CONF' in app.config:
            log_file = app.config['LOG_FILE_CONF']
            with open(log_file) as f:
                try:
                    dictionary = yaml.safe_load(f)
                except (ParserError, ScannerError) as exc:
                    print(exc, file=sys.stderr)
                    sys.exit(1)

            logging.config.dictConfig(dictionary)

            app.logger = logging.getLogger(app.config['LOG_LOGGER_NAME'])
        else:
            app.logger.warning("No 'LOG_FILE_CONF' provided using default configuration")


class FlaskSysLogHandler(logging.handlers.SysLogHandler):
    def emit(self, record):
        """

        :param record:
        """
        with current_app.app_context():
            priority = self.encodePriority(self.facility, self.mapPriority(record.levelname))
            record.ident = current_app.config['LOG_APP_NAME'] + "[" + str(priority) + "]:"
            super(FlaskSysLogHandler, self).emit(record)
