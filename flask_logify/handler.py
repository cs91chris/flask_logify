from logging.handlers import SysLogHandler

from flask import current_app


class FlaskSysLogHandler(SysLogHandler):
    def __init__(self, **kwargs):
        """

        :param kwargs:
        """
        super().__init__(**kwargs)
        self.facility = kwargs.get('facility') or SysLogHandler.LOG_USER
        with current_app.app_context():
            self._app_name = current_app.config['LOG_APP_NAME']

    def emit(self, record):
        """

        :param record:
        """
        priority = self.encodePriority(self.facility, self.mapPriority(record.levelname))
        record.ident = "{}[{}]:".format(self._app_name, str(priority))
        super(FlaskSysLogHandler, self).emit(record)
