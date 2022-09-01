import argparse
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from hashlib import md5
from pathlib import Path

from artifactory import ArtifactoryPath

sys.path.append(str(Path(__file__).parent / "src"))
from applitoolsify.sdk_manager import AVAILABLE_FRAMEWORKS  # noqa: E402

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


class SdkDownloadData:
    def __init__(self, name: str, download_url: str):
        self.name = name
        self.download_url = download_url
        self.version = None  # type: None|str

    def download(self):
        art_file = ArtifactoryPath(self.download_url)
        filestat = art_file.stat()
        created_at = filestat.ctime.strftime("%Y%m%d%H%M")
        self.version = created_at[:-4]
        sdk_full_path = SDKS_DIR_PATH / f"{self.version}-{self.name}"

        if sdk_full_path.exists() and encode_file_md5(sdk_full_path) == filestat.md5:
            print(f"* Skip downloading of {self.name} as already exists.")
            return

        print(f"* Downloading {self.name}")
        with art_file.open() as remote_file:
            with open(sdk_full_path, "wb") as local_file:
                local_file.write(remote_file.read())
        print(f"{self.name} was downloaded!")


FRAMEWORKS_TO_DOWNLOAD = [
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
        executor.map(lambda s: s.download(), FRAMEWORKS_TO_DOWNLOAD)


def update_readme():
    with open(CUR_DIR / "README.md", "r") as f:
        filedata = f.read()
        for sdk in AVAILABLE_FRAMEWORKS.values():
            filedata = re.sub(
                r"{} \(\d+\)".format(sdk.name), f"{sdk.name} ({sdk.version})", filedata
            )

    with open(CUR_DIR / "README.md", "w") as f:
        f.write(filedata)


def cli_parser():
    # type: () -> argparse.ArgumentParser
    parser = argparse.ArgumentParser(
        prog="python build.py",
        add_help=False,
    )

    parser.add_argument(
        "--download",
        action="store_true",
        help="Download SDKs to local folder",
    )

    parser.add_argument(
        "--update-readme",
        action="store_true",
        help="Update README.md SDKs version",
    )

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    return parser


def run():
    args = cli_parser().parse_args()
    if args.download:
        download_and_extract_sdks()

    if args.update_readme:
        update_readme()


if __name__ == "__main__":
    run()
