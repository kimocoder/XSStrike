import json
import random
import re
from urllib.parse import urlparse

import core.config
from core.config import xsschecker


def converter(data, url=False):
    if 'str' in str(type(data)):
        if not url:
            return json.loads(data)
        parts = data.split('/')[3:]
        return {part: part for part in parts}
    elif url:
        url = f'{urlparse(url).scheme}://{urlparse(url).netloc}'
        for part in list(data.values()):
            url += f'/{part}'
        return url
    else:
        return json.dumps(data)


def counter(string):
    string = re.sub(r'\s|\w', '', string)
    return len(string)


def closest(number, numbers):
    difference = [abs(list(numbers.values())[0]), {}]
    for index, i in numbers.items():
        diff = abs(number - i)
        if diff < difference[0]:
            difference = [diff, {index: i}]
    return difference[1]


def fillHoles(original, new):
    filler = 0
    filled = []
    for x, y in zip(original, new):
        if int(x) == (y + filler):
            filled.append(y)
        else:
            filled.extend([0, y])
            filler += (int(x) - y)
    return filled


def stripper(string, substring, direction='right'):
    done = False
    strippedString = ''
    if direction == 'right':
        string = string[::-1]
    for char in string:
        if char == substring and not done:
            done = True
        else:
            strippedString += char
    if direction == 'right':
        strippedString = strippedString[::-1]
    return strippedString


def extractHeaders(headers):
    headers = headers.replace('\\n', '\n')
    sorted_headers = {}
    matches = re.findall(r'(.*):\s(.*)', headers)
    for match in matches:
        header = match[0]
        value = match[1]
        try:
            if value[-1] == ',':
                value = value[:-1]
            sorted_headers[header] = value
        except IndexError:
            pass
    return sorted_headers


def replaceValue(mapping, old, new, strategy=None):
    """
    Replace old values with new ones following dict strategy.

    The parameter strategy is None per default for inplace operation.
    A copy operation is injected via strateg values like copy.copy
    or copy.deepcopy

    Note: A dict is returned regardless of modifications.
    """
    anotherMap = strategy(mapping) if strategy else mapping
    if old in anotherMap.values():
        for k in anotherMap.keys():
            if anotherMap[k] == old:
                anotherMap[k] = new
    return anotherMap


def getUrl(url, GET):
    return url.split('?')[0] if GET else url


def extractScripts(response):
    matches = re.findall(r'(?s)<script.*?>(.*?)</script>', response.lower())
    return [match for match in matches if xsschecker in match]


def randomUpper(string):
    return ''.join(random.choice((x, y)) for x, y in zip(string.upper(), string.lower()))


def flattenParams(currentParam, params, payload):
    flatted = []
    for name, value in params.items():
        if name == currentParam:
            value = payload
        flatted.append(f'{name}={value}')
    return '?' + '&'.join(flatted)


def genGen(fillings, eFillings, lFillings, eventHandlers, tags, functions, ends, badTag=None):
    vectors = []
    r = randomUpper  # randomUpper randomly converts chars of a string to uppercase
    for tag in tags:
        bait = xsschecker if tag in ['d3v', 'a'] else ''
        for eventHandler in eventHandlers:
            # if the tag is compatible with the event handler
            if tag in eventHandlers[eventHandler]:
                for function in functions:
                    for filling in fillings:
                        for eFilling in eFillings:
                            for lFilling in lFillings:
                                for end in ends:
                                    if tag in ['d3v', 'a'] and '>' in ends:
                                        end = '>'  # we can't use // as > with "a" or "d3v" tag
                                    breaker = ''
                                    if badTag:
                                        breaker = f'</{r(badTag)}>'
                                    vector = f'{breaker}<{r(tag)}{filling}{r(eventHandler)}{eFilling}={eFilling}{function}{lFilling}{end}{bait}'
                                    vectors.append(vector)
    return vectors


def getParams(url, data, GET):
    params = {}
    if '=' in url:
        data = url.split('?')[1]
        if data[:1] == '?':
            data = data[1:]
    elif data:
        if getVar('jsonData') or getVar('path'):
            params = data
        else:
            try:
                return json.loads(data.replace('\'', '"'))
            except json.decoder.JSONDecodeError:
                pass
    else:
        return None
    if not params:
        parts = data.split('&')
        for part in parts:
            each = part.split('=')
            if len(each) < 2:
                each.append('')
            try:
                params[each[0]] = each[1]
            except IndexError:
                params = None
    return params


def writer(obj, path):
    kind = str(type(obj)).split('\'')[0]
    if kind in ['list', 'tuple']:
        obj = '\n'.join(obj)
    elif kind == 'dict':
        obj = json.dumps(obj, indent=4)
    with open(path, 'w+') as savefile:
        savefile.write(str(obj.encode('utf-8')))


def reader(path):
    with open(path, 'r') as f:
        result = [line.rstrip(
                    '\n').encode('utf-8').decode('utf-8') for line in f]
    return result

def js_extractor(response):
    """Extract js files from the response body"""
    scripts = []
    matches = re.findall(r'<(?:script|SCRIPT).*?(?:src|SRC)=([^\s>]+)', response)
    for match in matches:
        match = match.replace('\'', '').replace('"', '').replace('`', '')
        scripts.append(match)
    return scripts


def handle_anchor(parent_url, url):
    scheme = urlparse(parent_url).scheme
    if url[:4] == 'http':
        return url
    elif url[:2] == '//':
        return f'{scheme}:{url}'
    elif url.startswith('/'):
        host = urlparse(parent_url).netloc
        scheme = urlparse(parent_url).scheme
        parent_url = f'{scheme}://{host}'
        return parent_url + url
    elif parent_url.endswith('/'):
        return parent_url + url
    else:
        return f'{parent_url}/{url}'


def deJSON(data):
    return data.replace('\\\\', '\\')


def getVar(name):
    return core.config.globalVariables[name]

def updateVar(name, data, mode=None):
    if mode:
        if mode == 'append':
            core.config.globalVariables[name].append(data)
        elif mode == 'add':
            core.config.globalVariables[name].add(data)
    else:
        core.config.globalVariables[name] = data

def isBadContext(position, non_executable_contexts):
    return next(
        (
            each[2]
            for each in non_executable_contexts
            if each[0] < position < each[1]
        ),
        '',
    )

def equalize(array, number):
    if len(array) < number:
        array.append('')

def escaped(position, string):
    usable = string[:position][::-1]
    if match := re.search(r'^\\*', usable):
        match = match.group()
        return len(match) == 1 or len(match) % 2 != 0
    else:
        return False
