import os.path
import zipfile

import pytest

from src.instrument import Instrumenter, SdkDownloadManager

pytestmark = [
    pytest.mark.parametrize(
        "sdk, framework",
        [
            ("ios_classic", "EyesiOSHelper.xcframework"),
            ("ios_ufg", "UFG_lib.xcframework"),
        ],
    )
]


def test_instrument_app(path_to_app, sdk, framework):
    with SdkDownloadManager.from_sdk_name(sdk) as sdk_data:
        instrumenter = Instrumenter(
            path_to_app,
            sdk_data,
        )
        instrumenter.instrumentify()
    assert os.path.exists(os.path.join(path_to_app, "Frameworks", framework))


def test_instrument_ipa_no_signing(path_to_ipa, sdk, framework, tmpdir):
    with SdkDownloadManager.from_sdk_name(sdk) as sdk_data:
        instrumenter = Instrumenter(
            path_to_ipa,
            sdk_data,
        )
        instrumenter.instrumentify()

    path, ipa_name = os.path.split(path_to_ipa)
    os.chdir(path)
    with zipfile.ZipFile(ipa_name) as zfile:
        zfile.extractall(str(tmpdir))

    assert os.path.exists(
        os.path.join(
            str(tmpdir), "Payload", "awesomeopensource.app", "Frameworks", framework
        )
    )
