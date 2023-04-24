import copy
import re
from urllib.parse import urlparse, quote, unquote

from core.arjun import arjun
from core.browserEngine import browser_engine, kill_browser, init_browser
from core.checker import checker
from core.colors import good, bad, end, info, green, red, que
import core.config
from core.config import xsschecker, minEfficiency
from core.dom import dom
from core.filterChecker import filterChecker
from core.generator import generator
from core.htmlParser import htmlParser
from core.requester import requester
from core.utils import getUrl, getParams, getVar
from core.wafDetector import wafDetector
from core.log import setup_logger

logger = setup_logger(__name__)


def scan(target, paramData, encoding, headers, delay, timeout, skipDOM, find, skip):
    GET, POST = (False, True) if paramData else (True, False)
    # If the user hasn't supplied the root url with http(s), we will handle it
    if not target.startswith('http'):
        try:
            response = requester(f'https://{target}', {}, headers, GET, delay, timeout)
            target = f'https://{target}'
        except:
            target = f'http://{target}'
    logger.debug(f'Scan target: {target}')
    response = requester(target, {}, headers, GET, delay, timeout).text

    # initialize browser
    init_browser()

    if not skipDOM:
        logger.run('Checking for DOM vulnerabilities')
        if highlighted := dom(response):
            logger.good('Potentially vulnerable objects found')
            logger.red_line(level='good')
            for line in highlighted:
                logger.no_format(line, level='good')
            logger.red_line(level='good')
    host = urlparse(target).netloc  # Extracts host out of the url
    logger.debug(f'Host to scan: {host}')
    url = getUrl(target, GET)
    logger.debug(f'Url to scan: {url}')
    params = getParams(target, paramData, GET)
    logger.debug_json('Scan parameters:', params)
    if find:
        params = arjun(url, GET, headers, delay, timeout)
    if not params:
        logger.error('No parameters to test.')
        quit()
    if WAF := wafDetector(
        url, {list(params.keys())[0]: xsschecker}, headers, GET, delay, timeout
    ):
        logger.error(f'WAF detected: {green}{WAF}{end}')
    else:
        logger.good(f'WAF Status: {green}Offline{end}')

    for paramName in params.keys():
        paramsCopy = copy.deepcopy(params)
        logger.info(f'Testing parameter: {paramName}')
        paramsCopy[paramName] = encoding(xsschecker) if encoding else xsschecker
        response = requester(url, paramsCopy, headers, GET, delay, timeout)
        occurences = htmlParser(response, encoding)
        positions = occurences.keys()
        logger.debug(f'Scan occurences: {occurences}')
        if not occurences:
            logger.error('No reflection found')
            continue
        else:
            logger.info('Reflections found: %i' % len(occurences))

        logger.run('Analysing reflections')
        efficiencies = filterChecker(
            url, paramsCopy, headers, GET, delay, occurences, timeout, encoding)
        logger.debug(f'Scan efficiencies: {efficiencies}')
        logger.run('Generating payloads')
        vectors = generator(occurences, response.text)
        total = sum(len(v) for v in vectors.values())
        if total == 0:
            logger.error('No vectors were crafted.')
            continue
        logger.info('Payloads generated: %i' % total)
        progress = 0
        for confidence, vects in vectors.items():
            for vect in vects:
                if core.config.globalVariables['path']:
                    vect = vect.replace('/', '%2F')
                progress += 1
                logger.run('Progress: %i/%i\r' % (progress, total))
                if not GET:
                    vect = unquote(vect)
                response = requester(url, paramsCopy, headers, GET, delay, timeout).text
                if success := browser_engine(response):
                    logger.good(f'Payload: {vect}')
                    if not skip:
                        choice = input(f'{que} Would you like to continue scanning? [y/N] ').lower()
                        if choice != 'y':
                            kill_browser()
                            quit()
        logger.no_format('')
    kill_browser()
