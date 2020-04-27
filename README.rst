Flask-Logify
==============

Advanced Logging configuration for flask application based on yaml file.

See `logging.config <https://docs.python.org/3/library/logging.config.html>`__

Quickstart
~~~~~~~~~~

Install ``flask_logify`` using ``pip``:

::

   $ pip install Flask-Logify

.. _section-1:

Example usage
^^^^^^^^^^^^^

An example of log file configuration is under example folder.
Only yaml format is supported.

.. code:: python

    from flask import Flask
    from flask_logify import FlaskLogging


    app = Flask(__name__)
    app.config['LOG_FILE_CONF'] = 'log.yaml'

    logging = FlaskLogging()
    with app.app_context():
        logging.init_app(app)

    app.run()

Go to http://127.0.0.1:5000/ and see log messages like configured

.. _section-2:

Configuration
^^^^^^^^^^^^^

1. ``LOG_FILE_CONF``: *(default: None)* absolute path of configuration file
2. ``LOG_APP_NAME``: *(default: flask)* the PROGRAM field of the log messages
3. ``LOG_LOGGER_NAME``: *(default: flask-development)* usually is flask-{FLASK_ENV}

License MIT
