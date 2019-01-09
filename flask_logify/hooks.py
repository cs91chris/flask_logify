import json

from flask import request
from flask import current_app as app


def hook_log_request():
    """

    """
    if request.environ.get('HTTP_X_FORWARDED_FOR'):
        request.environ['REMOTE_ADDR'] = request.environ['HTTP_X_FORWARDED_FOR']
    elif request.environ.get('HTTP_X_REAL_IP'):
        request.environ['REMOTE_ADDR'] = request.environ['HTTP_X_REAL_IP']

    remote_address = request.environ['REMOTE_ADDR']
    app.logger.info(
        "INCOMING REQUEST: %s %s %s %s",
        remote_address,
        request.method,
        request.scheme,
        request.full_path
    )

    app.logger.debug("REQUEST HEADERS\n%s", request.headers)

    data = request.get_data(as_text=True)
    if data:
        if request.headers.get('Content-Type') == 'application/json':
            try:
                data = json.dumps(json.loads(data), indent=4)
            except json.decoder.JSONDecodeError:
                app.logger.warning("request body type does not match Content-Type")

        app.logger.debug("REQUEST BODY\n%s", data)


def hook_log_response(response):
    """

    :param response:
    :return:
    """
    code = int(response.status_code / 100)
    log = app.logger.debug

    if code in (1, 2, 3):
        log = app.logger.info
    if code == 4:
        log = app.logger.warning
    if code == 5:
        log = app.logger.error

    log("RESPONSE STATUS: %s", response.status)
    app.logger.debug("RESPONSE HEADERS\n%s", response.headers)
    return response
