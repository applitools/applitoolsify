import contextlib
import importlib.resources
import shutil
import sys
import zipfile
from io import BytesIO
from pathlib import Path

from . import archiver
from .config import SdkData, SdkParams

EXTRACTED_SDK_DIR = Path(sys.path[0]).parent / "instrumentation"
SUPPORTED_FRAMEWORKS = {
    SdkParams.android_nmg: SdkData(
        name="NMG_lib",
    ),
    SdkParams.ios_nmg: SdkData(
        name="UFG_lib.xcframework",
    ),
    SdkParams.ios_classic: SdkData(
        name="EyesiOSHelper.xcframework",
    ),
}


@contextlib.contextmanager
def from_sdk_name(sdk_name: str) -> SdkData:
    sdk = SdkParams(sdk_name)
    sdk_data = SUPPORTED_FRAMEWORKS[sdk]
    sdk_data.add_sdk_location(EXTRACTED_SDK_DIR.joinpath(sdk_data.name))

    data = importlib.resources.read_binary("SDKS", f"{sdk_data.name}.zip")
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
