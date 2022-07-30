#!/usr/bin/env python
import os
import sys
import time
from contextlib import contextmanager
from urllib.request import urlretrieve

# stop writ *.pyc files to prevent from caching
sys.dont_write_bytecode = True


if sys.version_info < (3, 7):
    raise SystemError("Minimum required Python version is 3.7")

__version__ = "0.1.0"


def _run_from_local():
    from src.instrument import run

    return run


def _run_from_remote():
    instrumented_url = "https://raw.githubusercontent.com/applitools/applitoolsify/main/src/instrument.py"

    instrument_module = "_{}_instrument".format(str(time.time()).split(".")[0])
    cur_dir = sys.path[0]
    instrument_path = os.path.join(cur_dir, "{}.py".format(instrument_module))
    try:
        # download and save into current folder instrumented module
        urlretrieve(instrumented_url, instrument_path)

        # import downloaded module
        from importlib import import_module

        instrument = import_module(instrument_module)
        return getattr(instrument, "run")
    except Exception as err:
        print(f"! Failed to execute script: {err}")
        import traceback

        traceback.print_exc()
    finally:
        # remove *.py and *.pyc files
        for path in [instrument_path, instrument_path + "c"]:
            try:
                os.remove(path)
            except OSError:
                pass


@contextmanager
def _instrumenter(debug_with_local_run=False):
    if debug_with_local_run:
        yield _run_from_local()
    else:
        yield _run_from_remote()


def main():
    with _instrumenter(
        debug_with_local_run=os.environ.get("APPLITOOLSIFY_DEBUG", False)
    ) as run:
        run()


if __name__ == "__main__":
    main()
