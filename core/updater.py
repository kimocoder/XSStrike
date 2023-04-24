import os
import re
from requests import get

from core.config import changes
from core.colors import run, que, good, info, end, green
from core.log import setup_logger

logger = setup_logger(__name__)


def updater():
    logger.run('Checking for updates')
    latestCommit = get(
        'https://raw.githubusercontent.com/s0md3v/XSStrike/master/core/config.py').text

    if changes not in latestCommit:  # just a hack to see if a new version is available
        changelog = re.search(r"changes = '''(.*?)'''", latestCommit)
        changelog = changelog[1].split(';')
        logger.good('A new version of XSStrike is available.')
        changes_str = 'Changes:\n'
        for change in changelog:  # prepare changes to print
            changes_str += '%s>%s %s\n' % (green, end, change)
        logger.info(changes_str)
        currentPath = os.getcwd().split('/')  # if you know it, you know it
        folder = currentPath[-1]  # current directory name
        path = '/'.join(currentPath)  # current directory path
        choice = input(f'{que} Would you like to update? [Y/n] ').lower()

        if choice != 'n':
            logger.run('Updating XSStrike')
            os.system(f'git clone --quiet https://github.com/s0md3v/XSStrike {folder}')
            os.system(
                f'cp -r {path}/{folder}/* {path} && rm -r {path}/{folder}/ 2>/dev/null'
            )
            logger.good('Update successful!')
    else:
        logger.good('XSStrike is up to date!')
