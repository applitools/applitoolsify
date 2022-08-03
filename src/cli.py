import argparse
import sys
from pathlib import Path

from .config import __version__
from .entities import SdkParams
from .instrumenter import Instrumenter
from .sdk_downloader import SdkDownloadManager


def validate_path_to_app(value):
    # type: (str)->bool
    path = Path(value)
    if not path.exists():
        print("! Path `{}` does not exist".format(value))
        return False
    if path.suffix not in [".app", ".ipa", ".apk"]:
        print(
            "! Supported only `*.app`, `*.ipa` or `*.apk` apps. You provided: `{}`".format(
                value
            )
        )
        return False
    return True


def cli_parser():
    # type: () -> argparse.ArgumentParser

    parser = argparse.ArgumentParser(
        prog="python applitoolsify.py",
        description="Applitoolsify (v{}) with UFG_lib or EyesiOSHelper SDK.".format(
            __version__
        ),
        add_help=False,
    )
    # options
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s {}".format(__version__),
        help=argparse.SUPPRESS,
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose mode")

    # main params
    parser.add_argument(
        "path_to_app",
        type=str,
        help="Path to the `.app`, `.ipa` or `.apk` for applitoolsify",
    )
    parser.add_argument(
        "sdk",
        choices=[e.value for e in SdkParams],
        help="Select SDK for applitoolsify",
    )

    # optional signing
    # parser.add_argument(
    #     "signing_certificate_name",
    #     nargs="?",
    #     help="Name of the Certificate to be Used",
    # )
    # parser.add_argument(
    #     "provisioning_profile",
    #     nargs="?",
    #     help="Provisioning Profile to be Used",
    # )
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    return parser


def run():
    args = cli_parser().parse_args()
    if not validate_path_to_app(args.path_to_app):
        sys.exit(1)

    if args.verbose:
        global VERBOSE
        VERBOSE = True

    print("Instrumentation start")
    print("Getting assets...")
    with SdkDownloadManager.from_sdk_name(args.sdk) as sdk_data:
        instrumenter = Instrumenter(
            args.path_to_app,
            sdk_data,
            getattr(args, "signing_certificate_name", None),
            getattr(args, "provisioning_profile", None),
        )
        instrumenter.instrumentify()


if __name__ == "__main__":
    run()
