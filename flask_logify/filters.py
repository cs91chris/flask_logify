import logging


class FilterByArgs(logging.Filter):
    def __init__(self, name='', *args):
        """

        :param path:
        :param args:
        """
        super().__init__(name)
        self._excluded = args

    def filter(self, record):
        """

        :param record:
        :return: False if message must be filtered
        """
        for i in self._excluded:
            if i in record.getMessage():
                return False

        return True


class PathFilter(FilterByArgs):
    def __init__(self, path, name=''):
        """

        :param path:
        :param name:
        """
        # ensure sub-paths are not accidentally excluded from logging
        super().__init__(
            name,
            "\"{}\"".format(path),  # json format
            "{} ".format(path),
            "{}?".format(path)
        )
