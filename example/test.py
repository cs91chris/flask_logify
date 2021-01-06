from flask import Flask

from flask_logify import FlaskLogging
from flask_logify.builders import LogJSONBuilder
from flask_logify.filters import PathFilter


def create_app():
    app = Flask(__name__)
    app.config['DEBUG'] = True
    app.config['LOG_FILE_CONF'] = 'log.yaml'
    app.config['LOG_REQ_HEADERS'] = ['User-Agent']
    app.config['LOG_LOGGER_NAME'] = 'flask-development'
    logging = FlaskLogging()

    with app.app_context():
        logging.init_app(app, builder=LogJSONBuilder())

    @app.route('/test')
    def test():
        return {"test": "test"}

    @app.route('/health')
    @logging.disabled(PathFilter, path='/health')
    def health():
        return 'status OK'

    return app


if __name__ == '__main__':
    create_app().run()
