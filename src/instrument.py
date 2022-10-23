from __future__ import print_function, unicode_literals

import argparse
import os
import plistlib
import shutil
import subprocess
import sys
import tempfile
import traceback
import zipfile
from enum import Enum
from io import BytesIO
from pathlib import Path
from urllib.request import urlopen

__version__ = "0.2.0"

FILES_COPY_SKIP_LIST = [".DS_Store"]
VERBOSE = False


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


def print_verbose(*args, **kwargs):
    if VERBOSE:
        print(*args, **kwargs)


class SdkParams(Enum):
    ios_classic = "ios_classic"
    ios_nmg = "ios_nmg"
    android_nmg = "android_nmg"


class SdkData(object):
    """DTO with SDK data to download and extract."""

    def __init__(self, name, download_url):
        # type: (str, str) -> None
        self.name = name
        self.download_url = download_url
        self.sdk_location = None  # type: Path | None

    def __str__(self):
        return "SdkData<{}>".format(self.name)

    def add_sdk_location(self, path):
        # type: (Path) -> SdkData
        self.sdk_location = path
        return self


SUPPORTED_FRAMEWORKS = {
    SdkParams.android_nmg: SdkData(
        **{
            "name": "NMG_lib",
            "download_url": "https://applitools.jfrog.io/artifactory/nmg/android/instrumentation/NMG_lib-gb3294df.zip",
        }
    ),
    SdkParams.ios_nmg: SdkData(
        **{
            "name": "UFG_lib.xcframework",
            "download_url": "https://applitools.jfrog.io/artifactory/nmg/ios/instrumentation/UFG_lib.xcframework.zip",
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
    """Download and extract selected SDK."""

    def __init__(self, sdk_data):
        # type: (SdkData) -> None
        self.sdk_data = sdk_data
        # TODO: change it to tmp?
        self.sdks_dir = Path(sys.path[0])  # curr dir
        self.sdk_data.add_sdk_location(self.sdks_dir.joinpath(self.sdk_data.name))

    @classmethod
    def from_sdk_name(cls, sdk_name):
        # type: (str) -> SdkDownloadManager
        sdk = SdkParams(sdk_name)
        sdk_data = SUPPORTED_FRAMEWORKS[sdk]
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
        if self.sdk_data.sdk_location.exists():
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
                extracted_path = Archiver.extract_specific_folder(
                    self.sdks_dir, zfile, extract_dir_name=self.sdk_data.name
                )
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
        # type: (Path, SdkData, str, str) -> None
        self.path_to_app = path_to_app
        self.sdk_data = sdk_data
        self.signing_certificate_name = signing_certificate_name
        self.provisioning_profile = provisioning_profile

    @property
    def app_frameworks(self):
        # type: () -> Path
        raise NotImplementedError

    @property
    def sdk_in_app_frameworks(self):
        # type: () -> Path
        return self.app_frameworks.joinpath(self.sdk_data.name)

    def instrumentify(self):
        # type: () -> bool
        raise NotImplementedError


class AndroidInstrumentifyStrategy(_InstrumentifyStrategy):
    """
    Patch Android `apk` with default SDK (XXX: Support multiple sdks).

    This is a very basic implementation essentially calling the main
    script for android injector provided in the zip file
    """

    ARTIFACT_DIR = "instrumented-apk"

    @property
    def app_frameworks(self):
        # Not used for android, kept bc required
        return self.path_to_app.joinpath("Frameworks")

    def instrumentify(self):
        # type: () -> bool
        print("Preparing application...")
        cur_path = Path(os.getcwd())
        # os.chdir is required because we want to create our directories under applitoolsify NMG_lib dir
        # but still allow them to run in standalone mode
        os.chdir(self.sdk_data.sdk_location)
        work_dir = Path(os.getcwd())
        # Prepare output directory
        artifact_dir = work_dir.parent.joinpath(self.ARTIFACT_DIR)
        artifact_dir.mkdir(parents=True, exist_ok=True)
        # This is the module we downloaded, see source in injection
        import NMG_lib
        # Get log location from nmg library, after import this file should
        # exist because logger creates it when loaded
        log_loc = NMG_lib.common.env.LOG_LOCATION
        log_tgt = artifact_dir.joinpath("android-nmg.log")
        out_dir = ""
        try:
            out_dir = NMG_lib.main.run(self.path_to_app)
        except Exception as e:
            # next line should not happen unless a bug occurs, but leave for safe practice
            # in production
            # sometimes log file doesn't present which raise an exception during copying
            if os.path.exists(log_loc):
                shutil.copyfile(log_loc, log_tgt)
                print(f"Instrumentation failed with error: {e}. Please submit `{log_tgt}` to applitools")
            else:
                print(f"Instrumentation failed with error: {e}. No log file")
            return False

        apk_loc = (Path(out_dir).joinpath("final.apk").joinpath("out-aligned-signed.apk"))
        print("Collecting artifacts")
        shutil.copyfile(log_loc, log_tgt)
        target_file = artifact_dir.joinpath("ready.apk")
        ret = shutil.move(apk_loc, target_file)
        del NMG_lib
        os.chdir(cur_path)
        return ret == target_file


class IOSAppPatcherInstrumentifyStrategy(_InstrumentifyStrategy):
    """Patch IOS `app` with specific SDK."""

    @property
    def app_frameworks(self):
        return Path(self.path_to_app).joinpath("Frameworks")

    def instrumentify(self):
        # type: () -> bool
        return shutil.copytree(self.sdk_data.sdk_location, self.sdk_in_app_frameworks)


class IOSIpaInstrumentifyStrategy(_InstrumentifyStrategy):
    """Patch IOS `ipa` with specific SDK and sign with a specified certificate."""

    SECURITY = "/usr/bin/security"
    CODESIGN = "/usr/bin/codesign"

    def __init__(self, *args, **kwargs):
        super(IOSIpaInstrumentifyStrategy, self).__init__(*args, **kwargs)

        self.tmp_dir = tempfile.mkdtemp()
        self.extracted_dir_path = Path(self.tmp_dir).joinpath("extracted")
        self.entitlements_file_path = Path(self.tmp_dir).joinpath("entitlements.plist")
        self._app_in_payload = None
        with zipfile.ZipFile(self.path_to_app) as zfile:
            zfile.extractall(self.extracted_dir_path)

    @property
    def app_in_payload(self):
        # type: () -> str
        if self._app_in_payload is None:
            payload_in_app = self.extracted_dir_path.joinpath("Payload")
            apps_in_payolad = os.listdir(payload_in_app)
            if len(apps_in_payolad) > 1:
                raise RuntimeError("Payload contains more then one app")
            self._app_in_payload = payload_in_app.joinpath(apps_in_payolad[0])
        return self._app_in_payload

    @property
    def app_frameworks(self):
        return Path(self.app_in_payload).joinpath("Frameworks")

    def instrumentify(self):
        # type: () -> bool
        if not shutil.copytree(self.sdk_data.sdk_location, self.sdk_in_app_frameworks):
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
        profile_in_app_path = Path(self.app_in_payload).joinpath(
            "embedded.mobileprovision"
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
            # Need to be in current folder to archive
            os.chdir(self.extracted_dir_path)
            Archiver.zip_dir(".", self.path_to_app)
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
            for root, dirs, files in os.walk(dirpath):
                if os.path.basename(root)[0] == ".":
                    continue  # skip hidden directories
                for f in files:
                    if f[-1] == "~" or (f[0] == "." and f != ".htaccess"):
                        # skip backup files and all hidden files except .htaccess
                        continue
                    zfile.write(os.path.join(root, f))

    @staticmethod
    def extract_specific_folder(extract_to_path, zfile, extract_dir_name):
        # type: (Path, zipfile.ZipFile, str) -> Path
        target_dir = extract_to_path.joinpath(extract_dir_name)

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
            targetpath = extract_to_path.joinpath(filename)
            # Create all upper directories if necessary.
            upperdirs = targetpath.parent
            if upperdirs and not upperdirs.exists():
                os.makedirs(upperdirs)

            if Archiver.is_dir_in_zip(member):
                if not targetpath.is_dir():
                    os.mkdir(targetpath)
                continue

            with zfile.open(member) as source, open(targetpath, "wb") as target:
                shutil.copyfileobj(source, target)
            # Required to get android scripts working
            os.chmod(targetpath, 0o775)
        return target_dir


class Instrumenter(object):
    """Allow to instrumentify specific application with Applitools SDK."""

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
        self.path_to_app = Path(path_to_app).absolute()
        self.app_name = path_to_app
        self.app_ext = self.path_to_app.suffix
        self.sdk_data = sdk_data
        self._instrumenter = self.instrument_strategies[self.app_ext.lstrip(".")](
            path_to_app=self.path_to_app,
            sdk_data=sdk_data,
            signing_certificate_name=signing_certificate_name,
            provisioning_profile=provisioning_profile,
        )

    def was_already_instrumented(self):
        # type: () -> bool
        if self._instrumenter.sdk_in_app_frameworks.exists():
            return True
        else:
            return False

    def instrumentify(self):
        # type: () -> bool
        # Obviously need refactoring
        android = self.app_ext.lstrip(".") == "apk"
        if not android and self.was_already_instrumented():
            print_verbose("App already instrumented. Updating...")
            # remove old installation
            shutil.rmtree(self._instrumenter.sdk_in_app_frameworks)
        if not self._instrumenter.instrumentify():
            print("Failed to instrument `{}`".format(self.path_to_app))
            return False
        print_verbose(
            "`{}` framework was added to `{}`".format(
                self.sdk_data.name, self._instrumenter.sdk_in_app_frameworks
            )
        )
        if android:
            print(
                "Application is ready at {}".format(
                    AndroidInstrumentifyStrategy.ARTIFACT_DIR + os.sep + "ready.apk"
                )
            )
        else:
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
