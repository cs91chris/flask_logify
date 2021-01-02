Flask-Logify
==============

|download| |version|

Advanced Logging configuration for flask application based on yaml or json file.
See `logging.config <https://docs.python.org/3/library/logging.config.html>`__

NOTE: If you want to use ``flask_logify.handlers.syslog.FlaskSysLogHandler``
you must init this extension with an app context.

The dump of request or response are made by builders, there are two concrete implementations:

  1. ``LogTextBuilder``: message as plain text (configurable).
  2. ``LogJSONBuilder``: message as json format.

You can create your own builder by extending class ``LogBuilder``. In order to get the correct remote address
you can override ``LogBuilder.get_remote_address`` method or you can inject a function in ``LogBuilder`` constructor.

See example usage in `example/text.py <./flask_logify/example/text.py>`__.

``FlaskLogging`` as a decorator attribute with which you can disable log messages for a specific route,
passing a logging filter to it. For example you want disable log for health check endpoint.
See `example/text.py <./flask_logify/example/text.py>`__.


Quickstart
~~~~~~~~~~

Install ``flask_logify`` using ``pip``:

::

   $ pip install Flask-Logify

.. _section-1:

Example usage
^^^^^^^^^^^^^

An example of log file configuration is under example folder.

Only yaml or json format are supported.

.. code:: python

    from flask import Flask
    from flask_logify import FlaskLogging


    app = Flask(__name__)
    app.config['LOG_FILE_CONF'] = 'log.yaml'
    app.config['LOG_LOGGER_NAME'] = 'flask-development'

    logging = FlaskLogging()
    with app.app_context():
        logging.init_app(app)

    app.run()

Go to http://127.0.0.1:5000/ and see log messages like configured

.. _section-2:

Configuration
^^^^^^^^^^^^^
Base configuration keys:

  1. ``LOGGING``: *(default: None)* dict logging configuration
  2. ``LOG_FILE_CONF``: *(default: None)* absolute path of configuration file (has priority on LOGGING)
  3. ``LOG_APP_NAME``: *(default: flask)* the PROGRAM field of the log messages
  4. ``LOG_LOGGER_NAME``: *(default: flask-development)* usually is {LOG_APP_NAME}-{FLASK_ENV}

Text and JSON builder configuration keys:

  1. ``LOG_REQ_HEADERS``: *(default: [])* request headers to dump always
  2. ``LOG_RESP_HEADERS``: *(default: [])* response headers to dump always
  3. ``LOG_SKIP_DUMP``: *(default: not DEBUG)* if true dump of body and headers are skipped

Text builder only:

  1. ``LOG_RESP_FORMAT``: *(default: "{level} STATUS {status}\n\n{headers}\n\n{body}\n")* log message format for
     response
  2. ``LOG_REQ_FORMAT``: *(default: "{addr} {method} {scheme} {path}\n\n{headers}\n\n{body}\n")* log message format
     for request


License MIT


.. |download| image:: https://pypip.in/download/flask_logify/badge.png
.. |version| image:: https://pypip.in/version/flask_logify/badge.png
