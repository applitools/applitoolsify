from enum import Enum
from pathlib import Path


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
