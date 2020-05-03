from flask import Flask

from flask_logify import FlaskLogging, log_disabled_by_path


def create_app():
    app = Flask(__name__)
    app.config['DEBUG'] = True
    app.config['LOG_FILE_CONF'] = 'log.yaml'
    app.config['LOG_LOGGER_NAME'] = 'flask-development'
    logging = FlaskLogging()

    with app.app_context():
        logging.init_app(app)

    @app.route('/health')
    @log_disabled_by_path()
    def health():
        return 'status OK'

    return app


if __name__ == '__main__':
    create_app().run()
