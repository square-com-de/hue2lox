"""Prepare NEW private state only; never start a service or access hardware."""
import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'src'))
sys.dont_write_bytecode = True
from installer_messages import message, localized_print as print
from install_state import initialize

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--state-directory', required=True)
    parser.add_argument('--certificate-directory', required=True)
    parser.add_argument('--secret-directory', required=True)
    parser.add_argument('--host', required=True)
    parser.add_argument('--uid', type=int)
    parser.add_argument('--gid', type=int)
    args = parser.parse_args()
    try:
        initialize(args.state_directory, args.certificate_directory, args.secret_directory,
                   args.host, args.uid, args.gid)
    except (ValueError, OSError) as error:
        parser.exit(1, message('Preparation failed: ' + str(error)) + '\n')
    print('Fresh private state prepared. No service started; no bridge requests sent.')
