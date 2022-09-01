import dataclasses
from concurrent.futures import ThreadPoolExecutor
from hashlib import md5
from pathlib import Path

from artifactory import ArtifactoryPath

CUR_DIR = Path(__file__).parent.absolute()
SDKS_DIR_PATH = CUR_DIR / "src" / "SDKS"


def encode_file_md5(file_name):
    try:
        with open(file_name, "rb") as file:
            hasher = md5()
            for chunk in iter(lambda: file.read(4096), b""):
                hasher.update(chunk)
            return hasher.hexdigest()
    except FileNotFoundError:
        return None


@dataclasses.dataclass
class SdkDownloadData:
    name: str
    download_url: str

    @property
    def sdk_location(self):
        return SDKS_DIR_PATH.joinpath(self.name)

    def download(self):
        art_file = ArtifactoryPath(self.download_url)
        filestat = art_file.stat()
        created_at = filestat.ctime.strftime("%Y%m%d%H%M")
        sdk_full_path = SDKS_DIR_PATH / f"{created_at}-{self.name}"

        if sdk_full_path.exists() and encode_file_md5(sdk_full_path) == filestat.md5:
            print(f"* Skip downloading of {self.name} as already exists.")
            return

        print(f"* Downloading {self.name}")
        with art_file.open() as remote_file:
            with open(sdk_full_path, "wb") as local_file:
                local_file.write(remote_file.read())
        print(f"{self.name} was downloaded!")


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


def download_and_extract_sdks():
    with ThreadPoolExecutor() as executor:
        executor.map(lambda s: s.download(), SUPPORTED_FRAMEWORKS)


if __name__ == "__main__":
    download_and_extract_sdks()
