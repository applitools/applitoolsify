import os.path
import zipfile

import pytest

from src.instrument import Instrumenter, SdkDownloadManager

pytestmark = [
    pytest.mark.parametrize(
        "sdk, framework",
        [
            ("ios_classic", "EyesiOSHelper.xcframework"),
            ("ios_nmg", "UFG_lib.xcframework"),
        ],
    )
]


def test_instrument_app_absolute_path(path_to_app, sdk, framework):
    with SdkDownloadManager.from_sdk_name(sdk) as sdk_data:
        instrumenter = Instrumenter(
            path_to_app,
            sdk_data,
        )
        assert instrumenter.instrumentify()
    assert os.path.exists(os.path.join(path_to_app, "Frameworks", framework))


def test_instrument_app_relative_path(path_to_app, sdk, framework):
    dir_with_app, app_name = os.path.split(path_to_app)
    os.chdir(dir_with_app)
    with SdkDownloadManager.from_sdk_name(sdk) as sdk_data:
        instrumenter = Instrumenter(
            app_name,
            sdk_data,
        )
        assert instrumenter.instrumentify()
    assert os.path.exists(os.path.join(app_name, "Frameworks", framework))


def test_instrument_ipa_no_signing_absolute_path(path_to_ipa, sdk, framework, tmpdir):
    with SdkDownloadManager.from_sdk_name(sdk) as sdk_data:
        instrumenter = Instrumenter(
            path_to_ipa,
            sdk_data,
        )
        assert instrumenter.instrumentify()

    path, ipa_name = os.path.split(path_to_ipa)
    os.chdir(path)
    with zipfile.ZipFile(ipa_name) as zfile:
        zfile.extractall(str(tmpdir))

    assert os.path.exists(
        os.path.join(
            str(tmpdir), "Payload", "awesomeopensource.app", "Frameworks", framework
        )
    )


def test_instrument_ipa_no_signing_relative_path(path_to_ipa, sdk, framework, tmpdir):
    dir_with_ipa, ipa_name = os.path.split(path_to_ipa)
    os.chdir(dir_with_ipa)
    with SdkDownloadManager.from_sdk_name(sdk) as sdk_data:
        instrumenter = Instrumenter(
            ipa_name,
            sdk_data,
        )
        assert instrumenter.instrumentify()

    with zipfile.ZipFile(ipa_name) as zfile:
        zfile.extractall(str(tmpdir))

    assert os.path.exists(
        os.path.join(
            str(tmpdir), "Payload", "awesomeopensource.app", "Frameworks", framework
        )
    )
