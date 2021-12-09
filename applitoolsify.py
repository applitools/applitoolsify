from __future__ import print_function, unicode_literals

import os
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


def _run_from_local():
    from src.instrument import run

    return run


def _run_from_remote():
    instrumented_url = "https://raw.githubusercontent.com/applitools/applitoolsify/main/src/instrument.py"

    instrument_module = "_{}_instrument".format(str(time.time()).split(".")[0])
    cur_dir = sys.path[0]
    instrument_path = os.path.join(cur_dir, "{}.py".format(instrument_module))
    try:
        with urlopen(instrumented_url) as resp:
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
def _instrumenter(debug_with_local_run=False):
    if debug_with_local_run:
        yield _run_from_local()
    else:
        yield _run_from_remote()


def main():
    with _instrumenter(debug_with_local_run=False) as run:
        run()


if __name__ == "__main__":
    main()
