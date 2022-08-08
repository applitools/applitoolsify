import shutil
import sys
import zipfile
from io import BytesIO
from pathlib import Path
from urllib.request import urlopen

from applitoolsify.archiver import Archiver
from applitoolsify.config import SUPPORTED_FRAMEWORKS
from applitoolsify.entities import SdkData, SdkParams
from applitoolsify.utils import print_verbose


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
                "Mismatch of extract desired location and actual sdk location."
            )
        return self.sdk_data
