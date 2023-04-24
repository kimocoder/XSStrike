import copy
import re

import core.config
from core.colors import red, good, green, end
from core.config import xsschecker
from core.filterChecker import filterChecker
from core.generator import generator
from core.htmlParser import htmlParser
from core.requester import requester
from core.log import setup_logger

logger = setup_logger(__name__)


def crawl(scheme, host, main_url, form, blindXSS, blindPayload, headers, delay, timeout, encoding):
    if not form:
        return
    for each in form.values():
        if url := each['action']:
            if url.startswith(main_url):
                pass
            elif url.startswith('//') and url[2:].startswith(host):
                url = f'{scheme}://{url[2:]}'
            elif url.startswith('/'):
                url = f'{scheme}://{host}{url}'
            elif re.match(r'\w', url[0]):
                url = f'{scheme}://{host}/{url}'
            if url not in core.config.globalVariables['checkedForms']:
                core.config.globalVariables['checkedForms'][url] = []
            method = each['method']
            GET = method == 'get'
            inputs = each['inputs']
            paramData = {}
            for one in inputs:
                paramData[one['name']] = one['value']
                for paramName in paramData:
                    if paramName not in core.config.globalVariables['checkedForms'][url]:
                        core.config.globalVariables['checkedForms'][url].append(paramName)
                        paramsCopy = copy.deepcopy(paramData)
                        paramsCopy[paramName] = xsschecker
                        response = requester(
                            url, paramsCopy, headers, GET, delay, timeout)
                        occurences = htmlParser(response, encoding)
                        positions = occurences.keys()
                        efficiencies = filterChecker(
                            url, paramsCopy, headers, GET, delay, occurences, timeout, encoding)
                        if vectors := generator(occurences, response.text):
                            for confidence, vects in vectors.items():
                                try:
                                    payload = list(vects)[0]
                                    logger.vuln(f'Vulnerable webpage: {green}{url}{end}')
                                    logger.vuln(f'Vector for {green}{paramName}{end}: {payload}')
                                    break
                                except IndexError:
                                    pass
                        if blindXSS and blindPayload:
                            paramsCopy[paramName] = blindPayload
                            requester(url, paramsCopy, headers,
                                      GET, delay, timeout)
