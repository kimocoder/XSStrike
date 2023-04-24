import copy
from urllib.parse import urlparse

from core.colors import green, end
from core.config import xsschecker
from core.fuzzer import fuzzer
from core.requester import requester
from core.utils import getUrl, getParams
from core.wafDetector import wafDetector
from core.log import setup_logger

logger = setup_logger(__name__)


def singleFuzz(target, paramData, encoding, headers, delay, timeout):
    GET, POST = (False, True) if paramData else (True, False)
    # If the user hasn't supplied the root url with http(s), we will handle it
    if not target.startswith('http'):
        try:
            response = requester(f'https://{target}', {}, headers, GET, delay, timeout)
            target = f'https://{target}'
        except:
            target = f'http://{target}'
    logger.debug(f'Single Fuzz target: {target}')
    host = urlparse(target).netloc  # Extracts host out of the url
    logger.debug(f'Single fuzz host: {host}')
    url = getUrl(target, GET)
    logger.debug(f'Single fuzz url: {url}')
    params = getParams(target, paramData, GET)
    logger.debug_json('Single fuzz params:', params)
    if not params:
        logger.error('No parameters to test.')
        quit()
    WAF = wafDetector(
        url, {list(params.keys())[0]: xsschecker}, headers, GET, delay, timeout)
    if WAF:
        logger.error(f'WAF detected: {green}{WAF}{end}')
    else:
        logger.good(f'WAF Status: {green}Offline{end}')

    for paramName in params.keys():
        logger.info(f'Fuzzing parameter: {paramName}')
        paramsCopy = copy.deepcopy(params)
        paramsCopy[paramName] = xsschecker
        fuzzer(url, paramsCopy, headers, GET,
               delay, timeout, WAF, encoding)
