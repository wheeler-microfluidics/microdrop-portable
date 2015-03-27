import sys

from run_exe import run_exe
from path_helpers import path
from microdrop_utility.user_paths import home_dir


def find_relative_paths(root):
    '''
    Find values in configuration file that look like relative
    paths to Microdrop data directory.
    '''
    path_nodes = []

    def process_node(node, parents=None):
        if parents is None:
            parents = []
        for k, v in node.iteritems():
            if isinstance(v, dict):
                process_node(v, parents + [k])
            elif isinstance(v, str) and v.startswith('Microdrop\\'):
                # Assume this value is a relative path to Microdrop data
                # directory.
                path_nodes.append(parents + [k])

    process_node(root)
    return path_nodes


def replace_relative_paths(config):
    '''
    Replace relative path configuration values with absolute paths.
    '''
    # Find values in configuration file that look like relative
    # paths to Microdrop data directory.
    relative_path_keys = find_relative_paths(config)
    # Add `data_dir` key manually, since the default relative `data_dir`
    # value doesn't end with '\'.
    relative_path_keys.append(['data_dir'])

    for k in relative_path_keys:
        section = config
        for k_i in k[:-1]:
            section = section[k_i]
        section[k[-1]] = home_dir().joinpath(section[k[-1]])


def validate_data_dir(default_root):
    data_dir = home_dir().joinpath('Microdrop')
    config_path = data_dir.joinpath('microdrop.ini')

    # Case 1: `Documents/Microdrop` directory exists, and contains
    # `microdrop.ini`.  Do nothing.

    # Case 2: No `Documents/Microdrop` directory.
    # Copy `Microdrop` from installation to `Documents`.
    if not data_dir.isdir():
        default_root.joinpath('Microdrop').copytree(data_dir)

    # Case 3: `Documents/Microdrop` directory exists, but does not
    # contain `microdrop.ini`.
    # Ask user to either:
    #
    #  1. Rename existing `Microdrop` directory.
    #  2. Use existing `Microdrop` directory.
    #
    # If user chooses option 1, rename existing `Documents/Microdrop`
    # directory to `Documents/Microdrop.<timestamp>` and copy
    # `Microdrop` from installation to `Documents`.
    #
    # If user chooses option 2, copy `Microdrop/microdrop.ini` from
    # installation to `Documents/Microdrop` directory.
    elif not config_path.isfile():
        default_root.joinpath('Microdrop',
                              'microdrop.ini').copy(config_path)


def main():
    installation_root = path(__file__).expand().parent.parent
    validate_data_dir(installation_root)
    config_path = home_dir().joinpath('Microdrop', 'microdrop.ini')

    exe = '"%s"' % sys.executable

    run_exe(exe, '"%s" "%s"' %
            (installation_root.joinpath('scripts', 'update_microdrop.py'),
             config_path),
            try_admin=True)

    run_exe(exe, r'-m microdrop', try_admin=True,
            working_dir=config_path.parent.parent)


if __name__ == '__main__':
    main()
