from flask import Flask
from flask_logify import FlaskLogging


app = Flask(__name__)
app.config['LOG_FILE_CONF'] = 'log.yaml'

logging = FlaskLogging()
logging.init_app(app)

app.run()
