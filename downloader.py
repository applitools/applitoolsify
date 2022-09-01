import dataclasses
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.request import urlopen

CUR_DIR = Path(__file__).parent.absolute()
SDKS_DIR_PATH = CUR_DIR / "src" / "SDKS"


@dataclasses.dataclass
class SdkDownloadData:
    name: str
    download_url: str

    @property
    def sdk_location(self):
        return SDKS_DIR_PATH.joinpath(self.name)


SUPPORTED_FRAMEWORKS = [
    SdkDownloadData(
        name="NMG_lib.zip",
        download_url="https://applitools.jfrog.io/artifactory/nmg/android/instrumentation/NMG_lib.zip",
    ),
    SdkDownloadData(
        name="UFG_lib.xcframework.zip",
        download_url="https://applitools.jfrog.io/artifactory/nmg/ios/instrumentation/UFG_lib.xcframework.zip",
    ),
    SdkDownloadData(
        name="EyesiOSHelper.xcframework.zip",
        download_url="https://applitools.jfrog.io/artifactory/iOS/EyesiOSHelper/EyesiOSHelper.zip",
    ),
]


def downloader(sdk_data: SdkDownloadData):
    print(f"* Downloading {sdk_data.name}")
    with urlopen(sdk_data.download_url) as zipresp:
        with open(SDKS_DIR_PATH / sdk_data.name, "wb") as f:
            f.write(zipresp.read())
    print(f"{sdk_data.name} was downloaded!")


def download_and_extract_sdks():
    with ThreadPoolExecutor() as executor:
        executor.map(downloader, SUPPORTED_FRAMEWORKS)


if __name__ == "__main__":
    download_and_extract_sdks()
