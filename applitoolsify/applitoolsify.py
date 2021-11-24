from __future__ import print_function, unicode_literals
import os
import plistlib
import shutil
import subprocess
import sys
import tempfile
import zipfile
from argparse import ArgumentParser
from enum import Enum
from io import BytesIO
from urllib.request import urlopen

__version__ = "0.1.0"

FILES_COPY_SKIP_LIST = [".DS_Store"]
VERBOSE = False


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


def validate_ipa_with_certificates(
    path_to_app, signing_certificate_name, provisioning_profile
):
    # type: (str, str|None, str|None)->bool
    valid = True
    if not path_to_app.endswith(".ipa"):
        # validate only `ipa` apps
        return True
    if signing_certificate_name is None:
        print("! No signing certificate. {} will not be signed.".format(path_to_app))
        valid = False
    if provisioning_profile is None:
        print(
            "! No provisioning certificate. {} will not be signed.".format(path_to_app)
        )
        valid = False
    if sys.platform != "darwin":
        print("! Not supported platform. Signing supported only on macOS")
        valid = False
    return valid


def print_verbose(*args, **kwargs):
    if VERBOSE:
        print(*args, **kwargs)


def copytree(src, dst, symlinks=False, ignore=None):
    # type: (str, str, bool, bool|None) -> None
    for item in os.listdir(src):
        if item in FILES_COPY_SKIP_LIST:
            continue
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)


class SdkParams(Enum):
    ios_classic = "ios_classic"
    ios_ufg = "ios_ufg"


class SdkData(object):
    """DTO with SDK data to download and extract"""

    def __init__(self, name, download_url):
        # type: (str, str) -> None
        self.name = name
        self.download_url = download_url
        self.sdk_location = None

    def __str__(self):
        return "SdkData<{}>".format(self.name)

    def add_sdk_location(self, path):
        # type: (str) -> SdkData
        self.sdk_location = path
        return self


SUPPORTED_FRAMEWORKS = {
    SdkParams.ios_ufg: SdkData(
        **{
            "name": "UFG_lib.xcframework",
            "download_url": "https://applitools.jfrog.io/artifactory/ufg-mobile/UFG_lib.xcframework.zip",
        }
    ),
    SdkParams.ios_classic: SdkData(
        **{
            "name": "EyesiOSHelper.xcframework",
            "download_url": "https://applitools.jfrog.io/artifactory/iOS/EyesiOSHelper/EyesiOSHelper.zip",
        }
    ),
}


class SdkDownloadManager(object):
    """Download and extract selected SDK"""

    def __init__(self, sdk_data):
        # type: (SdkData) -> None
        self.sdk_data = sdk_data
        # TODO: change it to tmp?
        self.sdks_dir = os.path.join(sys.path[0], "APPLITOOLS_SDKS")
        self.sdk_data.add_sdk_location(os.path.join(self.sdks_dir, self.sdk_data.name))

    @classmethod
    def from_sdk_name(cls, sdk_name):
        # type: (str) -> SdkDownloadManager
        sdk = SdkParams(sdk_name)
        sdk_data = SUPPORTED_FRAMEWORKS[sdk]
        return cls(sdk_data)

    def download_and_extract(self):
        # type: () -> SdkData
        if os.path.exists(self.sdk_data.sdk_location):
            print_verbose(
                "We've detected saved version of `{}` in `{}`".format(
                    self.sdk_data.name, self.sdk_data.sdk_location
                )
            )

        print_verbose(
            "Downloading `{}` to `{}`".format(
                self.sdk_data.name, self.sdk_data.sdk_location
            )
        )
        # always download latest sdk
        with urlopen(self.sdk_data.download_url) as zipresp:
            with zipfile.ZipFile(BytesIO(zipresp.read())) as zfile:
                extracted_path = self._extract_specific_folder(
                    self.sdks_dir, zfile, extract_dir_name=self.sdk_data.name
                )
        if extracted_path != self.sdk_data.sdk_location:
            raise RuntimeError(
                "Mismatch of extract desired location and actual sdk location location."
            )
        return self.sdk_data

    @staticmethod
    def _extract_specific_folder(extract_to_path, zfile, extract_dir_name):
        # type: (str, zipfile.ZipFile, str) -> str
        target_dir = os.path.join(extract_to_path, extract_dir_name)

        # if `extract_dir_name` dir not present in archive raise an exception
        if not all(
            True
            for m in zfile.filelist
            if m.is_dir() and extract_dir_name in m.filename
        ):
            raise RuntimeError("`{}` not present in archive")

        # find index of searched dir to split in the future
        extract_dir_name_index = -1
        for member in zfile.filelist:
            if not member.is_dir():
                continue

            splitted_path = member.filename.split("/")
            try:
                found_dir_index = splitted_path.index(extract_dir_name)
            except ValueError:
                continue
            if found_dir_index != -1:
                extract_dir_name_index = found_dir_index
                break

        for member in zfile.filelist:
            splitted_path = member.filename.split("/")
            filename = "/".join(splitted_path[extract_dir_name_index:])
            # skip top directories
            if not filename.startswith(extract_dir_name):
                continue
            targetpath = os.path.join(extract_to_path, filename)
            # Create all upper directories if necessary.
            upperdirs = os.path.dirname(targetpath)
            if upperdirs and not os.path.exists(upperdirs):
                os.makedirs(upperdirs)

            if member.is_dir():
                if not os.path.isdir(targetpath):
                    os.mkdir(targetpath)
                continue

            with zfile.open(member) as source, open(targetpath, "wb") as target:
                shutil.copyfileobj(source, target)
        return target_dir


class _InstrumentifyStrategy(object):
    """Base Patch Strategy class. Helps to instrumentify app with specific SDK."""

    def __init__(
        self, path_to_app, sdk_data, signing_certificate_name, provisioning_profile
    ):
        # type: (str, SdkData, str, str) -> None
        self.path_to_app = path_to_app
        self.sdk_data = sdk_data
        self.signing_certificate_name = signing_certificate_name
        self.provisioning_profile = provisioning_profile

    @property
    def sdk_in_app_framework(self):
        # type: () -> str
        raise NotImplemented

    def instrumentify(self):
        raise NotImplemented


class IOSAppPatcherInstrumentifyStrategy(_InstrumentifyStrategy):
    """Patch IOS `app` with specific SDK"""

    @property
    def sdk_in_app_framework(self):
        # type: () -> str
        return os.path.join(self.path_to_app, "Frameworks", self.sdk_data.name)

    def instrumentify(self):
        copytree(self.sdk_data.sdk_location, self.sdk_in_app_framework)


class IOSIpaInstrumentifyStrategy(_InstrumentifyStrategy):
    """Patch IOS `ipa` with specific SDK and sign with a specified certificate"""

    SECURITY = "/usr/bin/security"
    CODESIGN = "/usr/bin/codesign"
    DITTO = "/usr/bin/ditto"

    def __init__(self, *args, **kwargs):
        super(IOSIpaInstrumentifyStrategy, self).__init__(*args, **kwargs)

        self.tmp_dir = tempfile.mkdtemp()
        self.extracted_dir_path = os.path.join(self.tmp_dir, "extracted")
        self.entitlements_file_path = os.path.join(self.tmp_dir, "entitlements.plist")
        self._app_in_payload = None
        with zipfile.ZipFile(self.path_to_app) as zfile:
            zfile.extractall(self.extracted_dir_path)

    @property
    def app_in_payload(self):
        # type: () -> str
        if self._app_in_payload is None:
            payload_in_app = os.path.join(self.extracted_dir_path, "Payload")
            apps_in_payolad = os.listdir(payload_in_app)
            if len(apps_in_payolad) > 1:
                raise RuntimeError("Payload contains more then one app")
            self._app_in_payload = apps_in_payolad[0]
        return self._app_in_payload

    @property
    def sdk_in_app_framework(self):
        # type: () -> str
        return os.path.join(self.app_in_payload, "Frameworks", self.sdk_data.name)

    def instrumentify(self):
        copytree(self.sdk_data.sdk_location, self.sdk_in_app_framework)
        self._resign()
        self._repackage()

    def __extract_entitlements(self, profile_in_app_path):
        pl_str = subprocess.check_output(
            [self.SECURITY, "cms", "-D", "-i", profile_in_app_path]
        )
        pl = plistlib.loads(pl_str)
        ent = pl["Entitlements"]
        with open(self.entitlements_file_path, "wb") as f:
            plistlib.dump(ent, f)

    def __find_files_to_sign(self):
        # type: () -> list[str]
        to_sign_files = []
        for root, dirs, files in os.walk(self.extracted_dir_path):
            for name in files:
                _, ext = os.path.splitext(name)
                if ext.lstrip(".").lower() in ["app", "appex", "framework", "dylib"]:
                    to_sign_files.append(name)
        return to_sign_files

    def __sign_files(self, to_sign_files):
        # type: (list[str]) -> None
        for to_sign in to_sign_files:
            subprocess.check_call(
                [
                    self.CODESIGN,
                    "--continue",
                    "-f",
                    "-s",
                    self.signing_certificate_name,
                    "--entitlements",
                    self.entitlements_file_path,
                    to_sign,
                ]
            )

    def _resign(self):
        profile_in_app_path = os.path.join(
            self.app_in_payload, "embedded.mobileprovision"
        )
        shutil.copy2(self.provisioning_profile, profile_in_app_path)
        print_verbose(
            "Resigning with certificate: {}".format(self.signing_certificate_name)
        )
        to_sign_files = self.__find_files_to_sign()
        self.__extract_entitlements(profile_in_app_path)
        self.__sign_files(to_sign_files)
        self._repackage()

    def _repackage(self):
        subprocess.check_call(
            [
                self.DITTO,
                "-c",
                "-k",
                "--sequesterRsrc",
                "--keepParent",
                os.path.join(self.extracted_dir_path, "Payload"),
                self.path_to_app,
            ]
        )


class Instrumenter(object):
    """Allow to instrumentify specific application with Applitools SDK"""

    instrument_strategies = {"app": IOSAppPatcherInstrumentifyStrategy, "ipa": IOSIpaInstrumentifyStrategy}

    def __init__(
        self,
        path_to_app,
        sdk_data,
        signing_certificate_name=None,
        provisioning_profile=None,
    ):
        # type: (str, SdkData, str, str) -> None
        self.path_to_app = path_to_app
        self.app_name = os.path.basename(path_to_app)
        _, self.app_ext = os.path.splitext(path_to_app)
        self.sdk_data = sdk_data
        self._instrumenter = self.instrument_strategies[self.app_ext.lstrip(".")](
            path_to_app=path_to_app,
            sdk_data=sdk_data,
            signing_certificate_name=signing_certificate_name,
            provisioning_profile=provisioning_profile,
        )

    def was_already_instrumented(self):
        # type: () -> bool
        if os.path.exists(self._instrumenter.sdk_in_app_framework):
            return True
        else:
            return False

    def instrumentify(self):
        if self.was_already_instrumented():
            print_verbose("App already instrumented. Updating...")
            # remove old installation
            shutil.rmtree(self._instrumenter.sdk_in_app_framework)
        self._instrumenter.instrumentify()
        print_verbose(
            "`{}` framework was added to `{}`".format(
                self.sdk_data.name, self._instrumenter.sdk_in_app_framework
            )
        )
        print(
            "`{}` is ready for use with the `{}`".format(
                self.path_to_app, self.sdk_data.name
            )
        )


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


def main():
    args = cli_parser().parse_args()

    if not validate_path_to_app(args.path_to_app):
        return
    # if not validate_ipa_with_certificates(
    #     args.path_to_app, args.signing_certificate_name, args.provisioning_profile
    # ):
    #     return

    if args.verbose:
        global VERBOSE
        VERBOSE = True

    sdk_data = SdkDownloadManager.from_sdk_name(
        args.sdk
    ).download_and_extract()

    instrumenter = Instrumenter(
        args.path_to_app,
        sdk_data,
        args.signing_certificate_name,
        args.provisioning_profile,
    )
    instrumenter.instrumentify()


if __name__ == "__main__":
    main()
