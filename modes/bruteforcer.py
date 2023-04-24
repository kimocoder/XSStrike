import copy
from urllib.parse import urlparse, unquote

from core.colors import good, green, end
from core.requester import requester
from core.utils import getUrl, getParams
from core.log import setup_logger

logger = setup_logger(__name__)


def bruteforcer(target, paramData, payloadList, encoding, headers, delay, timeout):
    GET, POST = (False, True) if paramData else (True, False)
    host = urlparse(target).netloc  # Extracts host out of the url
    logger.debug(f'Parsed host to bruteforce: {host}')
    url = getUrl(target, GET)
    logger.debug(f'Parsed url to bruteforce: {url}')
    params = getParams(target, paramData, GET)
    logger.debug_json('Bruteforcer params:', params)
    if not params:
        logger.error('No parameters to test.')
        quit()
    for paramName in params.keys():
        paramsCopy = copy.deepcopy(params)
        for progress, payload in enumerate(payloadList, start=1):
            logger.run('Bruteforcing %s[%s%s%s]%s: %i/%i\r' %
                       (green, end, paramName, green, end, progress, len(payloadList)))
            if encoding:
                payload = encoding(unquote(payload))
            paramsCopy[paramName] = payload
            response = requester(url, paramsCopy, headers,
                                 GET, delay, timeout).text
            if encoding:
                payload = encoding(payload)
            if payload in response:
                logger.info(f'{good} {payload}')
    logger.no_format('')
