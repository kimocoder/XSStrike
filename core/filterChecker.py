from core.checker import checker


def filterChecker(url, params, headers, GET, delay, occurences, timeout, encoding):
    positions = occurences.keys()
    # adding < > to environments anyway because they can be used in all contexts
    environments = {'<', '>'}
    sortedEfficiencies = {i: {} for i in range(len(positions))}
    for i in occurences:
        occurences[i]['score'] = {}
        context = occurences[i]['context']
        if context == 'attribute':
            if (
                occurences[i]['details']['type'] == 'value'
                and occurences[i]['details']['name'] == 'srcdoc'
            ):
                environments.add('&lt;')  # so let's add the html entity
                environments.add('&gt;')  # encoded versions of < and >
            if occurences[i]['details']['quote']:
                environments.add(occurences[i]['details']['quote'])
        elif context == 'comment':
            environments.add('-->')
        elif context == 'script':
            environments.add(occurences[i]['details']['quote'])
            environments.add('</scRipT/>')
    for environment in environments:
        if environment:
            efficiencies = checker(
                url, params, headers, GET, delay, environment, positions, timeout, encoding)
            efficiencies.extend([0] * (len(occurences) - len(efficiencies)))
            for occurence, efficiency in zip(occurences, efficiencies):
                occurences[occurence]['score'][environment] = efficiency
    return occurences
