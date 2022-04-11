from __future__ import print_function, unicode_literals

import argparse
import errno
import os
import plistlib
import shutil
import subprocess
import sys
import tempfile
import traceback
import zipfile
from io import BytesIO

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

__version__ = "0.1.0"

FILES_COPY_SKIP_LIST = [".DS_Store"]
VERBOSE = False


def validate_path_to_app(value):
    # type: (str)->bool
    if not os.path.exists(value):
        print("! Path `{}` does not exist".format(value))
        return False
    if not value.endswith(".app") and not value.endswith(".ipa") and not value.endswith(".apk"):
        print(
            "! Supported only `*.app` or `*.ipa` apps. You provided: `{}`".format(value)
        )
        return False
    return True


def print_verbose(*args, **kwargs):
    if VERBOSE:
        print(*args, **kwargs)


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >= 2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        # possibly handle other errno cases here, otherwise finally:
        else:
            raise


def copytree(src, dst, symlinks=False, ignore=None):
    # type: (str, str, bool, bool|None) -> bool
    try:
        mkdir_p(dst)
        for item in os.listdir(src):
            if item in FILES_COPY_SKIP_LIST:
                continue
            s = os.path.join(src, item)
            d = os.path.join(dst, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, symlinks, ignore)
            else:
                shutil.copy2(s, d)
        return True
    except Exception:
        print("Failed to copy `{}` to `{}`".format(src, dst))
        if VERBOSE:
            traceback.print_exc()
        return False


class SdkParams(object):
    ios_classic = "ios_classic"
    ios_ufg = "ios_ufg"
    android_ufg = "android_ufg"
    values = [android_ufg, ios_ufg, ios_classic]

    def __init__(self, value):
        # type: (str)->None
        if value not in self.values:
            raise ValueError
        self.value = value

    def __getitem__(self, item):
        for item in self.items:
            yield item

    def __hash__(self):
        return hash(self.value)


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
    SdkParams.android_ufg: SdkData(
        **{
            "name": "injection",
            "download_url": "file:///tmp/ufglib.zip",
        }
    ),
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
        self.sdks_dir = sys.path[0]  # curr dir
        #import ipdb;ipdb.set_trace()
        self.sdk_data.add_sdk_location(os.path.join(self.sdks_dir, self.sdk_data.name))

    @classmethod
    def from_sdk_name(cls, sdk_name):
        # type: (str) -> SdkDownloadManager
        sdk = SdkParams(sdk_name)
        sdk_data = SUPPORTED_FRAMEWORKS[sdk.value]
        return cls(sdk_data)

    def __enter__(self):
        # type: () -> SdkData
        return self.download_and_extract()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.remove_sdk_data()

    def remove_sdk_data(self):
        shutil.rmtree(self.sdk_data.sdk_location)

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
        try:
            with urlopen(self.sdk_data.download_url) as zipresp:
                print("Here")
                with zipfile.ZipFile(BytesIO(zipresp.read())) as zfile:
                    #import ipdb;ipdb.set_trace()
                    extracted_path = Archiver.extract_specific_folder(
                        self.sdks_dir, zfile, extract_dir_name=self.sdk_data.name
                    )
                import ipdb;ipdb.set_trace()
        except Exception as e:
            e.print_verbose()
        if extracted_path != self.sdk_data.sdk_location:
            raise RuntimeError(
                "Mismatch of extract desired location and actual sdk location location."
            )
        return self.sdk_data


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
    def app_frameworks(self):
        return NotImplemented

    @property
    def sdk_in_app_frameworks(self):
        # type: () -> str
        return os.path.join(self.app_frameworks, self.sdk_data.name)

    def instrumentify(self):
        # type: () -> bool
        raise NotImplemented

class AndroidInstrumentifyStrategy(_InstrumentifyStrategy):
    """Patch Android `apk` with default SDK (XXX: Support multiple sdks)"""

    @property
    def app_frameworks(self):
        print("Android app_frameworks(?)")
        return os.path.join(self.path_to_app, "Frameworks")

    def instrumentify(self):
        # type: () -> bool
        print("Android instrumentify!")
        subprocess.check_call(["bash","./setup_pyenv.sh"], cwd="./injection/")
        return subprocess.check_call(["bash", "./patchnfill.sh", "../duckduckgo-5.87.0-play-debug.apk"], cwd="./injection/")

class IOSAppPatcherInstrumentifyStrategy(_InstrumentifyStrategy):
    """Patch IOS `app` with specific SDK"""

    @property
    def app_frameworks(self):
        return os.path.join(self.path_to_app, "Frameworks")

    def instrumentify(self):
        # type: () -> bool
        return copytree(self.sdk_data.sdk_location, self.sdk_in_app_frameworks)


class IOSIpaInstrumentifyStrategy(_InstrumentifyStrategy):
    """Patch IOS `ipa` with specific SDK and sign with a specified certificate"""

    SECURITY = "/usr/bin/security"
    CODESIGN = "/usr/bin/codesign"

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
            self._app_in_payload = os.path.join(payload_in_app, apps_in_payolad[0])
        return self._app_in_payload

    @property
    def app_frameworks(self):
        return os.path.join(self.app_in_payload, "Frameworks")

    def instrumentify(self):
        # type: () -> bool
        if not copytree(self.sdk_data.sdk_location, self.sdk_in_app_frameworks):
            return False

        try:
            self._resign()
        except Exception:
            print("Failed to sign. Please, sign it manually")
            if VERBOSE:
                traceback.print_exc()
            return False

        try:
            self._repackage()
        except Exception:
            print("Failed to repackage. Please, sign it manually")
            if VERBOSE:
                traceback.print_exc()
            return False
        return True

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
                if ext.lstrip(".").lower() in ["dylib"]:
                    to_sign_files.append(os.path.join(root, name))
            for dir_name in dirs:
                _, ext = os.path.splitext(dir_name)
                if ext.lstrip(".").lower() in ["app", "appex", "framework"]:
                    to_sign_files.append(os.path.join(root, dir_name))
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
        if not all([self.signing_certificate_name, self.provisioning_profile]):
            print_verbose(
                "No `signing_certificate_name` and `provisioning_profile` provided. Skip signing..."
            )
            return
        if sys.platform != "darwin":
            print("Signing with script is available only on macOS. Skip signing...")
            return
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

    def _repackage(self):
        old_path = os.getcwd()
        try:
            os.chdir(self.extracted_dir_path)
            Archiver.zip_dir("./Payload/", self.path_to_app)
        finally:
            os.chdir(old_path)


class Archiver(object):
    @staticmethod
    def is_dir_in_zip(fileinfo):
        # type: (zipfile.ZipInfo) -> bool
        hi = fileinfo.external_attr >> 16
        return (hi & 0x4000) > 0

    @staticmethod
    def zip_dir(dirpath, zippath):
        with zipfile.ZipFile(zippath, "w", zipfile.ZIP_DEFLATED) as zfile:
            for root, dirs, files in os.walk("."):
                if os.path.basename(root)[0] == ".":
                    continue  # skip hidden directories
                for f in files:
                    if f[-1] == "~" or (f[0] == "." and f != ".htaccess"):
                        # skip backup files and all hidden files except .htaccess
                        continue
                    zfile.write(os.path.join(root, f))

    @staticmethod
    def extract_specific_folder(extract_to_path, zfile, extract_dir_name):
        # type: (str, zipfile.ZipFile, str) -> str
        target_dir = os.path.join(extract_to_path, extract_dir_name)

        # if `extract_dir_name` dir not present in archive raise an exception
        if not all(
            True
            for m in zfile.filelist
            if Archiver.is_dir_in_zip(m) and extract_dir_name in m.filename
        ):
            raise RuntimeError("`{}` not present in archive")

        # find index of searched dir to split in the future
        extract_dir_name_index = -1
        for member in zfile.filelist:
            if not Archiver.is_dir_in_zip(member):
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

            if Archiver.is_dir_in_zip(member):
                if not os.path.isdir(targetpath):
                    os.mkdir(targetpath)
                continue

            with zfile.open(member) as source, open(targetpath, "wb") as target:
                shutil.copyfileobj(source, target)
            os.chmod(targetpath, 0o775)
        return target_dir


class Instrumenter(object):
    """Allow to instrumentify specific application with Applitools SDK"""

    instrument_strategies = {
        "app": IOSAppPatcherInstrumentifyStrategy,
        "ipa": IOSIpaInstrumentifyStrategy,
        "apk": AndroidInstrumentifyStrategy,
    }

    def __init__(
        self,
        path_to_app,
        sdk_data,
        signing_certificate_name=None,
        provisioning_profile=None,
    ):
        # type: (str, SdkData, str, str) -> None
        self.path_to_app = os.path.abspath(path_to_app)
        self.app_name = path_to_app
        _, self.app_ext = os.path.splitext(path_to_app)
        self.sdk_data = sdk_data
        self._instrumenter = self.instrument_strategies[self.app_ext.lstrip(".")](
            path_to_app=self.path_to_app,
            sdk_data=sdk_data,
            signing_certificate_name=signing_certificate_name,
            provisioning_profile=provisioning_profile,
        )

    def was_already_instrumented(self):
        # type: () -> bool
        if os.path.exists(self._instrumenter.sdk_in_app_frameworks):
            return True
        else:
            return False

    def instrumentify(self):
        # type: () -> bool
        #if self.was_already_instrumented():
        #    print_verbose("App already instrumented. Updating...")
            # remove old installation
        #    shutil.rmtree(self._instrumenter.sdk_in_app_frameworks)
        if not self._instrumenter.instrumentify():
            print("Failed to instrument `{}`".format(self.path_to_app))
            return False
        print_verbose(
            "`{}` framework was added to `{}`".format(
                self.sdk_data.name, self._instrumenter.sdk_in_app_frameworks
            )
        )
        print(
            "`{}` is ready for use with the `{}`".format(
                self.path_to_app, self.sdk_data.name
            )
        )
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
        choices=SdkParams.values,
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
