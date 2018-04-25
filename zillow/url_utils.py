
import requests

try:
    # python 3
    from urllib.parse import urlparse, urlunparse, urlencode
except ImportError:
    from urlparse import urlparse, urlunparse
    from urllib import urlencode

from .error import ZillowError


def request_url(url, method, data=None, **kwargs):
    """
    Request a url.

    :param url: The web location we want to retrieve.
    :param method: GET only (for now).
    :param data: A dict of (str, unicode) key/value pairs.
    :param kwargs: any extra kwargs that can be passed into requests.get(...) function
    :return:A JSON object.
    """

    if method == 'GET':
        url = _build_url(url, extra_params=data)
        try:
            return requests.get(url, **kwargs)
        except requests.RequestException as e:
            raise ZillowError(str(e))


def _build_url(url, path_elements=None, extra_params=None):
    """
    Taken from: https://github.com/bear/python-twitter/blob/master/twitter/api.py#L3814-L3836
    :param url:
    :param path_elements:
    :param extra_params:
    :return:
    """
    # Break url into constituent parts
    (scheme, netloc, path, params, query, fragment) = urlparse(url)

    # Add any additional path elements to the path
    if path_elements:
        # Filter out the path elements that have a value of None
        p = [i for i in path_elements if i]
        if not path.endswith('/'):
            path += '/'
        path += '/'.join(p)

    # Add any additional query parameters to the query string
    if extra_params and len(extra_params) > 0:
        extra_query = encode_parameters(extra_params)
        # Add it to the existing query
        if query:
            query += '&' + extra_query
        else:
            query = extra_query

    # Return the rebuilt URL
    return urlunparse((scheme, netloc, path, params, query, fragment))


def encode_parameters(parameters, input_encoding=None):
    """
    Return a string in key=value&key=value form.
    :param parameters: A dict of (key, value) tuples, where value is encoded as
        specified by input_encoding
    :return:A URL-encoded string in "key=value&key=value" form
    """

    if parameters is None:
        return None
    else:
        return urlencode(dict(
            [(k, _encode(v, input_encoding))
             for k, v in list(parameters.items())
             if v is not None]))


def _encode(s, input_encoding):
    if input_encoding is not None:
        return str(s, input_encoding).encode('utf-8')
    else:
        return str(s).encode('utf-8')
