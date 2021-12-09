from __future__ import print_function, unicode_literals

import sys
import time
from enum import Enum

try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen

import os
from argparse import ArgumentParser

__version__ = "0.1.0"

VERBOSE = False


class SdkParams(Enum):
    ios_classic = "ios_classic"
    ios_ufg = "ios_ufg"


def cli_parser():
    parser = ArgumentParser(
        prog="python -m applitoolsify",
        description="Applitoolsify the app with UFG_lib or EyesiOSHelper SDK.",
    )
    # options
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version="%(prog)s {}".format(__version__),
        help="Version of the app",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose mode")

    # main params
    parser.add_argument(
        "path_to_app",
        type=str,
        help="Path to the `.app` or `.ipa` for applitoolsify",
    )
    parser.add_argument(
        "sdk",
        choices=[e.value for e in SdkParams],
        help="Select SDK for applitoolsify",
    )

    # optional signing
    parser.add_argument(
        "signing_certificate_name",
        nargs="?",
        help="Name of the Certificate to be Used",
    )
    parser.add_argument(
        "provisioning_profile",
        nargs="?",
        help="Provisioning Profile to be Used",
    )
    parser.set_defaults(command=lambda _: parser.print_help())
    return parser


def validate_path_to_app(value):
    # type: (str)->bool
    if not os.path.exists(value):
        print("! Path `{}` does not exist".format(value))
        return False
    if not value.endswith(".app") and not value.endswith(".ipa"):
        print(
            "! Supported only `*.app` or `*.ipa` apps. You provided: `{}`".format(value)
        )
        return False
    return True


class InstrumentDownloader(object):
    URL = "https://raw.githubusercontent.com/applitools/applitoolsify/main/src/instrument.py"

    def __init__(self):
        self._instrument_module = "_{}_instrument".format(time.time_ns())
        cur_dir = sys.path[0]
        self._instrument_path = os.path.join(
            cur_dir, "{}.py".format(self._instrument_module)
        )

    def __enter__(self):
        with urlopen(self.URL) as resp:
            with open(self._instrument_path, "wb") as f:
                f.write(resp.read())

        from importlib import import_module

        instument = import_module(self._instrument_module)
        SdkDownloadManager = getattr(instument, "SdkDownloadManager")
        Instrumenter = getattr(instument, "Instrumenter")
        return (SdkDownloadManager, Instrumenter)

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            os.remove(self._instrument_path)
        except OSError:
            pass


def main():
    args = cli_parser().parse_args()

    if not validate_path_to_app(args.path_to_app):
        return

    if args.verbose:
        global VERBOSE
        VERBOSE = True

    with InstrumentDownloader() as (SdkDownloadManager, Instrumenter):
        with SdkDownloadManager.from_sdk_name(args.sdk) as sdk_data:
            instrumenter = Instrumenter(
                args.path_to_app,
                sdk_data,
                args.signing_certificate_name,
                args.provisioning_profile,
            )
            instrumenter.instrumentify()


if __name__ == "__main__":
    main()
