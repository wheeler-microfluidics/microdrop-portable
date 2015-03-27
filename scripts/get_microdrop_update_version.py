import logging
import subprocess
import re
import sys

import gtk

from microdrop_utility import Version
from microdrop_utility.gui import yesno
from configobj import ConfigObj
from path_helpers import path


def get_pypi_version_string():
# get the latest version on pypi
    name, version = (subprocess.Popen(['python-2.7.9\python.exe',
                                      'python-2.7.9\Scripts\yolk-script.py','-V',
                                      'microdrop'],
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE,
                                     stdin=subprocess.PIPE).communicate()[0]
                     .rstrip().split(' '))
    return version

def get_pypi_version():
    m = re.search('^(?P<major>\d+)(?:\.(?P<minor>\d+)){0,1}'
                  '(?:\.post(?P<micro>\d+)){0,1}(?:rc(?P<rc>\d+)){0,1}'
                  '(?:\.(?P<tags>dev)\d+){0,1}', get_pypi_version_string())
    return version_from_re(m)

def get_current_version():
    output = subprocess.Popen(['python-2.7.9\python.exe',
                               'python-2.7.9\Scripts\yolk-script.py', '-lm',
                               'microdrop', '-f', 'version'],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               stdin=subprocess.PIPE).communicate()[0].splitlines()
    for line in output:
        m = re.search('^microdrop\s*\((?P<major>\d+)(?:\.(?P<minor>\d+)){0,1}'
                      '(?:\.post(?P<micro>\d+)){0,1}(?:rc(?P<rc>\d+)){0,1}'
                      '(?:\.(?P<tags>dev)\d+){0,1}\)', line)
        if m:
            return version_from_re(m)

def version_from_re(m):
    major, minor, micro, rc, tags = (0, 0, 0, None, [])
    major = int(m.group('major'))
    if m.group('minor'):
        minor = int(m.group('minor'))
    if m.group('micro'):
        micro = int(m.group('micro'))
    if m.group('rc') is not None:
        rc = int(m.group('rc'))
    if m.group('tags'):
        tags = m.group('tags')
        tags = [tag.strip() for tag in tags.split(",")]
    return Version(major, minor, micro, tags, rc)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    config_file_path = None
    if len(sys.argv) > 1:
        config_file_path = path(sys.argv[1]).abspath()

    conf = Config(config_file_path)
    choice = None
    try:
        choice = conf.data['microdrop.app']['update_automatically']
    except:
        pass

    # default
    if choice is None:
        choice = 'check for updates, but ask before installing'

    logging.info('update_automatically="%s"' % choice)

    update_version = get_pypi_version()
    current_version = get_current_version()

    logging.info('current_version=%s, update_version=%s' %
                 (current_version, update_version))
    logging.debug('update_version.tags != current_version.tags=%s' %
                 (update_version.tags != current_version.tags))
    logging.debug('update_version <= current_version=%s' %
                 (update_version <= current_version))
    logging.debug("choice == '''don't check for updates'''=%s" % 
                 (choice == '''don't check for updates'''))
    if update_version.tags != current_version.tags or \
    update_version <= current_version or \
    choice == '''don't check for updates''':
        sys.exit(0)
    if choice == 'check for updates, but ask before installing':
        if yesno('A newer version (%s) of Microdrop is available'
                 ' (current version=%s). Would you like to update?' %
                 (update_version, current_version)) == gtk.RESPONSE_NO:
            sys.exit(0)
    print "update = %s" % get_pypi_version_string()
