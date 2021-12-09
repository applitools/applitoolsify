from __future__ import print_function, unicode_literals

import sys
import time
from contextlib import contextmanager

PY2 = True if sys.version_info[0] == 2 else False

if PY2:
    from contextlib import contextmanager

    from urllib2 import urlopen as _urlopen

    @contextmanager
    def urlopen(*args, **kwargs):
        resp = _urlopen(*args, **kwargs)
        yield resp
        resp.close()


else:
    from urllib.request import urlopen

import os

INSTRUMENTED_URL = (
    "https://raw.githubusercontent.com/applitools/applitoolsify/main/src/instrument.py"
)


def _local_run():
    from src.instrument import run

    return run


def _remote_run():
    instrument_module = "_{}_instrument".format(str(time.time()).split(".")[0])
    cur_dir = sys.path[0]
    instrument_path = os.path.join(cur_dir, "{}.py".format(instrument_module))
    try:
        with urlopen(INSTRUMENTED_URL) as resp:
            if resp.code != 200:
                print("! Failed to download script")
                sys.exit(1)
            with open(instrument_path, "wb") as f:
                f.write(resp.read())

        from importlib import import_module

        instrument = import_module(instrument_module)
        return getattr(instrument, "run")
    except Exception as err:
        print("! Failed to execute script.")
        import traceback

        traceback.print_exc()
    finally:
        try:
            os.remove(instrument_path)
        except OSError:
            pass


@contextmanager
def instrumenter(local_run=False):
    if local_run:
        yield _local_run()
    else:
        yield _remote_run()


def main():
    with instrumenter() as run:
        run()


if __name__ == "__main__":
    main()
