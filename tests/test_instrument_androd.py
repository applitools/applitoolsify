import os.path
import zipfile

import pytest

from src.instrument import Instrumenter, SdkDownloadManager

pytestmark = [
    pytest.mark.parametrize(
        "sdk, framework",
        [
            ("android_nmg", "NMG_lib.zip"),
        ],
    )
]


def test_instrument_app_absolute_path(path_to_apk, sdk, framework):
    with SdkDownloadManager.from_sdk_name(sdk) as sdk_data:
        instrumenter = Instrumenter(
            path_to_apk,
            sdk_data,
        )
        assert instrumenter.instrumentify()


def test_instrument_app_relative_path(path_to_apk, sdk, framework):
    dir_with_app, app_name = os.path.split(path_to_apk)
    os.chdir(dir_with_app)
    with SdkDownloadManager.from_sdk_name(sdk) as sdk_data:
        instrumenter = Instrumenter(
            app_name,
            sdk_data,
        )
        assert instrumenter.instrumentify()
