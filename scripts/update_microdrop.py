import sys
import subprocess
import re
import logging

import pip_helpers

if __name__ == '__main__':
    """
    Depending on the users update settings, check PyPy for new releases of
    Microdrop and update if appropriate.
    """

    logging.basicConfig(level=logging.INFO)
    config_file = ''
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
    output = subprocess.Popen([sys.executable,
                               'scripts\get_microdrop_update_version.py',
                               config_file],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               stdin=subprocess.PIPE).communicate()[0].splitlines()
    # If the above script returned a line containing "update = version", use
    # pip to install the specified version.
    for line in output:
        m = re.match('update = (.+)$', line)
        if m:
            version = m.groups()[0]
            print 'Updating microdrop to version %s' % version
            print pip_helpers.install(['microdrop==%s' % version])
            break

