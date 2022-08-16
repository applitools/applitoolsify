from enum import Enum
from pathlib import Path
from typing import Optional

FILES_COPY_SKIP_LIST = [".DS_Store"]
VERBOSE = False


class SdkParams(Enum):
    ios_classic = "ios_classic"
    ios_nmg = "ios_nmg"
    android_nmg = "android_nmg"


class SdkData:
    """DTO with SDK data to download and extract."""

    def __init__(self, name: str):
        self.name = name
        self.sdk_location: Optional[Path] = None

    def add_sdk_location(self, path: Path) -> "SdkData":
        self.sdk_location = path
        return self
