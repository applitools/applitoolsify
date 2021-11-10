import os
import shutil
from argparse import ArgumentParser, Action
from enum import Enum
from io import BytesIO
import zipfile
import pdb
import sys
from urllib.request import urlopen

from applitoolsify.__version__ import __version__


print(sys.path[0])


def copytree(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)


def yes_no(answer):
    yes = {"yes", "y", "ye", ""}
    no = {"no", "n"}

    while True:
        choice = input(answer).lower()
        if choice in yes:
            return True
        elif choice in no:
            return False
        else:
            print("Please respond with 'yes' or 'no'")


class SdkParams(Enum):
    ios_classic = "ios_classic"
    ios_ufg = "ios_ufg"


class SdkData(object):
    def __init__(self, name, download_url):
        self.name = name
        self.download_url = download_url
        self.sdk_location = None

    def __str__(self):
        return "SdkData<{}>".format(self.name)

    def add_sdk_location(self, path):
        # type: (str) -> SdkData
        self.sdk_location = path
        return self


SUPPORTED_FRAMEWORKS = {
    SdkParams.ios_ufg: SdkData(
        **{
            "name": "UFG_lib.xcframework",
            "download_url": "https://applitools.jfrog.io/artifactory/ufg-mobile/UFG_lib.xcframework.zip",
            # "stores_at_path": None,
        }
    ),
    SdkParams.ios_classic: SdkData(
        **{
            "name": "EyesiOSHelper.xcframework",
            "download_url": "https://applitools.jfrog.io/artifactory/iOS/EyesiOSHelper/EyesiOSHelper.zip",
            # "stores_at_path": None,
        }
    ),
}


class SdkDownloadManager(object):
    def __init__(self, sdk_data, force_update):
        # type: (SdkData, bool) -> None
        self.force_update = force_update
        self.sdk_data = sdk_data
        self.sdks_dir = os.path.join(sys.path[0], "APPLITOOLS_SDKS")
        self.sdk_data.add_sdk_location(os.path.join(self.sdks_dir, self.sdk_data.name))

    @classmethod
    def from_sdk_name(cls, sdk_name, force_update):
        sdk = SdkParams(sdk_name)
        sdk_data = SUPPORTED_FRAMEWORKS[sdk]
        return cls(sdk_data, force_update)

    def download_and_extract(self):
        # type: () -> SdkData
        if not self.force_update:
            # return path to sdk if already downloaded
            if os.path.exists(self.sdk_data.sdk_location):
                return self.sdk_data

        # download sdk if not present or `force_update` called
        with urlopen(self.sdk_data.download_url) as zipresp:
            with zipfile.ZipFile(BytesIO(zipresp.read())) as zfile:
                extracted_path = self._extract_specific_folder(
                    self.sdks_dir, zfile, extract_dir_name=self.sdk_data.name
                )
        if extracted_path != self.sdk_data.sdk_location:
            raise RuntimeError(
                "Mismatch of extract desired location and actual sdk location location."
            )
        return self.sdk_data

    @staticmethod
    def _extract_specific_folder(extract_to_path, zfile, extract_dir_name):
        # type: (str, zipfile.ZipFile, str) -> str
        target_dir = os.path.join(extract_to_path, extract_dir_name)

        # if `extract_dir_name` dir not present in archive raise an exception
        if not all(
            True
            for m in zfile.filelist
            if m.is_dir() and extract_dir_name in m.filename
        ):
            raise RuntimeError("`{}` not present in archive")

        extract_dir_name_index = -1
        for member in zfile.filelist:
            if not member.is_dir():
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
            targetpath = os.path.join(extract_to_path, filename)
            # Create all upper directories if necessary.
            upperdirs = os.path.dirname(targetpath)
            if upperdirs and not os.path.exists(upperdirs):
                os.makedirs(upperdirs)

            if member.is_dir():
                if not os.path.isdir(targetpath):
                    os.mkdir(targetpath)
                continue

            with zfile.open(member) as source, open(targetpath, "wb") as target:
                shutil.copyfileobj(source, target)
        return target_dir


class ValidatePathToApp(Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if not os.path.exists(values):
            raise ValueError("`path_to_app` does not exist")
        if not values.endswith(".app") and not values.endswith(".ipa"):
            raise ValueError("`path_to_app` parameter must be an `.app` or `.ipa` file")
        setattr(namespace, self.dest, values)


def cli_parser():
    parser = ArgumentParser(
        prog="python -m applitoolsify",
        description="Applitoolsify the app with UFG_lib or EyesiOSHelper SDK.",
    )
    # options
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version="%(prog)s {}".format(__version__),
        help="Version of the app",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose mode")
    parser.add_argument(
        "-f", "--force-update", action="store_true", help="Force update framework"
    )

    # main params
    parser.add_argument(
        "path_to_app",
        type=str,
        action=ValidatePathToApp,
        help="Path to the `.app` or `.ipa` for applitoolsify",
    )
    parser.add_argument(
        "sdk",
        choices=[e.value for e in SdkParams],
        # action=ManageSdkFrameworks,
        help="Select SDK for applitoolsify",
    )

    # optional signing
    parser.add_argument(
        "signing_certificate_name",
        nargs="?",
        help="TODO",
    )
    parser.add_argument(
        "provisioning_profile",
        nargs="?",
        help="TODO",
    )
    parser.set_defaults(command=lambda _: parser.print_help())
    return parser


def find_dirs_with_name(root_path, dirname):
    all_files = []
    for root, dirs, files in os.walk(root_path):
        for cur_dirname in dirs:
            if cur_dirname.lower() == dirname.lower():
                all_files.append(os.path.join(root, dirname))
    return all_files


def run():
    args = cli_parser().parse_args()
    path_to_app = args.path_to_app
    sdk_data = SdkDownloadManager.from_sdk_name(
        args.sdk, args.force_update
    ).download_and_extract()

    if path_to_app.endswith(".app"):
        framework_path = os.path.join(path_to_app, "Frameworks")
        if not os.path.exists(framework_path):
            os.mkdir(framework_path)
        else:
            sdk_files = os.listdir(sdk_data.sdk_location)
            potential_patched_path = os.path.join(framework_path, sdk_data.name)
            find_dirs_with_name(potential_patched_path, "")
            if yes_no("App already patched. Re-patch?"):
                shutil.rmtree(potential_patched_path)
        copytree(sdk_data.sdk_location, framework_path)
        print("{} framework was added to {}".format(sdk_data.name, framework_path))
    print("{} is ready for use with the {}".format(path_to_app, sdk_data.name))


run()
