import re

from core.config import badTags, xsschecker
from core.utils import isBadContext, equalize, escaped


def htmlParser(response, encoding):
    rawResponse = response  # raw response returned by requests
    response = response.text  # response content
    if encoding:  # if the user has specified an encoding, encode the probe in that
        response = response.replace(encoding(xsschecker), xsschecker)
    reflections = response.count(xsschecker)
    position_and_context = {}
    environment_details = {}
    clean_response = re.sub(r'<!--[.\s\S]*?-->', '', response)
    script_checkable = clean_response
    for i in range(reflections):
        if occurence := re.search(
            f'(?i)(?s)<script[^>]*>.*?({xsschecker}).*?</script>',
            script_checkable,
        ):
            thisPosition = occurence.start(1)
            position_and_context[thisPosition] = 'script'
            environment_details[thisPosition] = {'details': {'quote': ''}}
            for i in range(len(occurence.group())):
                currentChar = occurence.group()[i]
                if currentChar in ('\'', '`', '"') and not escaped(i, occurence.group()):
                    environment_details[thisPosition]['details']['quote'] = currentChar
                elif currentChar in (')', ']', '}', '}') and not escaped(i, occurence.group()):
                    break
            script_checkable = script_checkable.replace(xsschecker, '', 1)
    if len(position_and_context) < reflections:
        attribute_context = re.finditer(
            f'<[^>]*?({xsschecker})[^>]*?>', clean_response
        )
        for occurence in attribute_context:
            match = occurence.group(0)
            thisPosition = occurence.start(1)
            parts = re.split(r'\s', match)
            tag = parts[0][1:]
            for part in parts:
                if xsschecker in part:
                    Type, quote, name, value = '', '', '', ''
                    if '=' in part:
                        quote = re.search(r'=([\'`"])?', part)[1]
                        name_and_value = part.split('=')[0], '='.join(part.split('=')[1:])
                        Type = 'name' if xsschecker == name_and_value[0] else 'value'
                        name = name_and_value[0]
                        value = name_and_value[1].rstrip('>').rstrip(quote).lstrip(quote)
                    else:
                        Type = 'flag'
                    position_and_context[thisPosition] = 'attribute'
                    environment_details[thisPosition] = {
                        'details': {
                            'tag': tag,
                            'type': Type,
                            'quote': quote,
                            'value': value,
                            'name': name,
                        }
                    }
    if len(position_and_context) < reflections:
        html_context = re.finditer(xsschecker, clean_response)
        for occurence in html_context:
            thisPosition = occurence.start()
            if thisPosition not in position_and_context:
                position_and_context[occurence.start()] = 'html'
                environment_details[thisPosition] = {'details': {}}
    if len(position_and_context) < reflections:
        comment_context = re.finditer(r'<!--(?![.\s\S]*-->)[.\s\S]*(%s)[.\s\S]*?-->' % xsschecker, response)
        for occurence in comment_context:
            thisPosition = occurence.start(1)
            position_and_context[thisPosition] = 'comment'
            environment_details[thisPosition] = {'details': {}}
    database = {
        i: {
            'position': i,
            'context': position_and_context[i],
            'details': environment_details[i]['details'],
        }
        for i in sorted(position_and_context)
    }
    bad_contexts = re.finditer(r'(?s)(?i)<(style|template|textarea|title|noembed|noscript)>[.\s\S]*(%s)[.\s\S]*</\1>' % xsschecker, response)
    if non_executable_contexts := [
        [each.start(), each.end(), each.group(1)] for each in bad_contexts
    ]:
        for key in database:
            position = database[key]['position']
            if badTag := isBadContext(position, non_executable_contexts):
                database[key]['details']['badTag'] = badTag
            else:
                database[key]['details']['badTag'] = ''
    return database
