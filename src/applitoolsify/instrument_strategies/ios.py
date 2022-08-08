import os
import plistlib
import shutil
import subprocess
import sys
import tempfile
import traceback
import zipfile
from pathlib import Path

from applitoolsify.archiver import Archiver
from applitoolsify.config import VERBOSE
from applitoolsify.utils import print_verbose

from .base import BaseInstrumentifyStrategy


class IOSAppInstrumentifyStrategy(BaseInstrumentifyStrategy):
    """Patch IOS `app` with specific SDK."""

    @property
    def app_frameworks(self):
        return Path(self.path_to_app).joinpath("Frameworks")

    def instrumentify(self):
        # type: () -> bool
        return shutil.copytree(self.sdk_data.sdk_location, self.sdk_in_app_frameworks)


class IOSIpaInstrumentifyStrategy(BaseInstrumentifyStrategy):
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
