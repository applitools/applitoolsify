import contextlib
import importlib.resources
import shutil
import sys
import zipfile
from io import BytesIO
from pathlib import Path
from typing import Dict

from . import archiver
from .config import SdkData, SdkParams

SDK_NAME_TO_SDK_PARAM = {
    "NMG_lib": SdkParams.android_nmg,
    "UFG_lib.xcframework": SdkParams.ios_nmg,
    "EyesiOSHelper.xcframework": SdkParams.ios_classic,
}

EXTRACTED_SDK_DIR = Path(sys.path[0]).parent.joinpath("instrumentation").absolute()


def supported_frameworks_from_resources() -> Dict[SdkParams, SdkData]:
    result = {}
    for filename in (
        f for f in importlib.resources.contents("SDKS") if f.endswith(".zip")
    ):
        _, sdk_name = filename.rstrip(".zip").split("-")
        sdk_param = SDK_NAME_TO_SDK_PARAM[sdk_name]
        result[sdk_param] = SdkData(filename)
    return result


AVAILABLE_FRAMEWORKS = supported_frameworks_from_resources()


@contextlib.contextmanager
def from_sdk_name(sdk_name: str) -> SdkData:
    sdk = SdkParams(sdk_name)
    sdk_data = AVAILABLE_FRAMEWORKS[sdk]
    sdk_data.add_sdk_location(EXTRACTED_SDK_DIR.joinpath(sdk_data.name))

    data = importlib.resources.read_binary("SDKS", sdk_data.filename)
    with zipfile.ZipFile(BytesIO(data)) as zfile:
        extracted_path = archiver.extract_specific_folder(
            EXTRACTED_SDK_DIR, zfile, extract_dir_name=sdk_data.name
        )
        if extracted_path != sdk_data.sdk_location:
            raise RuntimeError(
                "Mismatch of extract desired location and actual sdk location."
            )
    yield sdk_data
    shutil.rmtree(sdk_data.sdk_location)
