import sys
import logging.config

import yaml
from yaml.parser import ParserError
from yaml.scanner import ScannerError

from .hooks import hook_log_request, hook_log_response


class FlaskLogging:
    def __init__(self, app=None, **kwargs):
        """

        :param app:
        """
        self._conf = {}
        self._log_request = None
        self._log_response = None

        if app is not None:
            self.init_app(app, **kwargs)

    @property
    def conf(self):
        """

        :return:
        """
        return self._conf

    def init_app(self, app, log_req=None, log_res=None, **kwargs):
        """

        :param app: Flask app instance
        :param log_req: custom function that logs request
        :param log_res: custom function that logs response
        :param kwargs: extra logging configuration
        """
        self._log_request = log_req or hook_log_request
        self._log_response = log_res or hook_log_response

        if not hasattr(app, 'extensions'):
            app.extensions = dict()
        app.extensions['logify'] = self

        app.config.setdefault('LOG_APP_NAME', 'flask')
        app.config.setdefault('LOG_LOGGER_NAME', 'flask-development')

        app.before_request_funcs.setdefault(None, []).append(self._log_request)
        app.after_request_funcs.setdefault(None, []).append(self._log_response)

        if 'LOG_FILE_CONF' in app.config:
            try:
                with open(app.config['LOG_FILE_CONF']) as f:
                    try:
                        self._conf = yaml.safe_load(f)
                    except (ParserError, ScannerError) as exc:
                        print(exc, file=sys.stderr)
                        sys.exit(1)
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
            werkzeug_logger = logging.getLogger('werkzeug')
            werkzeug_logger.setLevel(logging.DEBUG)
            for hdl in app.logger.handlers:
                werkzeug_logger.addHandler(hdl)
