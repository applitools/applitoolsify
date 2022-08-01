import os.path
import zipfile
from pathlib import Path

import pytest

from tests.utils import applitoolsify_cmd

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
    applitoolsify_cmd(path_to_app, sdk)
    assert path_to_app.joinpath("Frameworks", framework).exists()


def test_instrument_app_relative_path(
    path_to_app_relative_to_applitoolsify, sdk, framework
):
    applitoolsify_cmd(path_to_app_relative_to_applitoolsify, sdk)
    assert (
        Path(__file__)
        .parent.parent.joinpath("IOSTestApp.app", "Frameworks", framework)
        .exists()
    )


def test_instrument_ipa_no_signing_absolute_path(path_to_ipa, sdk, framework, tmpdir):
    applitoolsify_cmd(path_to_ipa, sdk)

    path, ipa_name = os.path.split(path_to_ipa)
    os.chdir(path)
    with zipfile.ZipFile(ipa_name) as zfile:
        zfile.extractall(str(tmpdir))

    assert (
        Path(tmpdir)
        .joinpath("Payload", "IOSTestApp.app", "Frameworks", framework)
        .exists()
    )


def test_instrument_ipa_no_signing_relative_path(
    path_to_ipa_relative_to_applitoolsify, sdk, framework, tmpdir
):
    applitoolsify_cmd(path_to_ipa_relative_to_applitoolsify, sdk)

    with zipfile.ZipFile(path_to_ipa_relative_to_applitoolsify) as zfile:
        zfile.extractall(str(tmpdir))

    assert (
        Path(tmpdir)
        .joinpath("Payload", "IOSTestApp.app", "Frameworks", framework)
        .exists()
    )
