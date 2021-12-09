from __future__ import print_function, unicode_literals

import sys
import time
from contextlib import contextmanager

try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen

import os

INSTRUMENTED_URL = (
    "https://raw.githubusercontent.com/applitools/applitoolsify/main/src/instrument.py"
)


@contextmanager
def instrumenter():
    instrument_module = "_{}_instrument".format(str(time.time()).split(".")[0])
    cur_dir = sys.path[0]
    instrument_path = os.path.join(cur_dir, "{}.py".format(instrument_module))
    try:
        resp = urlopen(INSTRUMENTED_URL)
        if resp.code != 200:
            print("! Failed to download script")
            sys.exit(1)
        with open(instrument_path, "wb") as f:
            f.write(resp.read())

        from importlib import import_module

        instrument = import_module(instrument_module)
        yield getattr(instrument, "run")
    except Exception as err:
        print("! Failed to execute script.")
        import traceback

        traceback.print_exc()
    finally:
        try:
            os.remove(instrument_path)
        except OSError:
            pass


def main():
    with instrumenter() as run:
        run()


if __name__ == "__main__":
    main()
