from flask import request
from flask import current_app as cap


def get_remote_addr():
    """

    :return:
    """
    if request.environ.get('HTTP_X_FORWARDED_FOR'):
        request.environ['REMOTE_ADDR'] = request.environ['HTTP_X_FORWARDED_FOR']
    elif request.environ.get('HTTP_X_REAL_IP'):
        request.environ['REMOTE_ADDR'] = request.environ['HTTP_X_REAL_IP']

    return request.environ['REMOTE_ADDR']


def dump_headers(hdr, force=False):
    """
    dumps http headers: useful for logging

    :param force:
    :param hdr: headers' dictionary
    :return: string representation of headers
            k1: v1
            k2: v2
    """
    if force or cap.config['DEBUG'] is True:
        return '\n'.join('{}: {}'.format(k, v) for k, v in hdr.items())
    else:
        return 'headers not dumped'


def dump_body(r, force=False):
    """
    dump http body as plain text

    :param r:
    :param force:
    :return:
    """
    if force or cap.config['DEBUG'] is True:
        try:
            return r.get_data(as_text=True) or 'empty data'
        except UnicodeError:
            return 'body not dumped: invalid encoding or binary'
    else:
        return 'body not dumped: app not in DEBUG mode'


def dump_request(force=False):
    """

    :param force:
    :return:
    """
    remote_address = get_remote_addr()

    return "{addr} {method} {scheme} {path}\n\n{headers}\n\n{body}\n".format(
        addr=remote_address,
        method=request.method,
        scheme=request.scheme,
        path=request.full_path,
        headers=dump_headers(request.headers, force),
        body=dump_body(request, force)
    )


def dump_response(response, force=False):
    """

    :param response:
    :param force:
    :return:
    """
    code = int(response.status_code / 100)
    if code in (1, 2, 3):
        level = 'SUCCESS'
    elif code == 4:
        level = 'WARNING'
    elif code == 5:
        level = 'ERROR'
    else:
        level = 'UNKNOWN'

    return "{level} STATUS {status}\n\n{headers}\n\n{body}\n".format(
        level=level,
        status=response.status,
        headers=dump_headers(response.headers, force),
        body=dump_body(response, force)
    )


def hook_log_request():
    """

    """
    cap.logger.info("INCOMING REQUEST: {}".format(
        dump_request()
    ))


def hook_log_response(response):
    """

    :param response:
    """
    cap.logger.debug("RESPONSE at {} {}".format(
        request.path,
        dump_response(response)
    ))
    return response
